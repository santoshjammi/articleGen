#!/bin/bash

# Production deployment script for SEO Article Generator
# Use this script to deploy on cloud servers

echo "🚀 SEO Article Generator - Production Deployment"
echo "================================================"

# Check if running as root (not recommended for production)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Warning: Running as root is not recommended for production"
    echo "   Consider creating a dedicated user for the application"
fi

# System requirements check
echo "🔍 Checking system requirements..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "   Python version: $python_version"

# Check if git is available
if command -v git &> /dev/null; then
    echo "   ✅ Git available"
else
    echo "   ❌ Git not found - required for deployment"
    exit 1
fi

# Check if pip is available
if command -v pip3 &> /dev/null; then
    echo "   ✅ Pip3 available"
else
    echo "   ❌ Pip3 not found - required for dependencies"
    exit 1
fi

# Create application user (optional)
if [ ! -z "$APP_USER" ]; then
    if id "$APP_USER" &>/dev/null; then
        echo "   ✅ User $APP_USER exists"
    else
        echo "   📝 Creating user $APP_USER..."
        useradd -m -s /bin/bash "$APP_USER"
        echo "   ✅ User $APP_USER created"
    fi
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    apt-get update
    apt-get install -y python3-pip python3-venv python3-dev build-essential nginx supervisor
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum update -y
    yum install -y python3-pip python3-devel gcc nginx supervisor
elif command -v apk &> /dev/null; then
    # Alpine
    apk update
    apk add python3 py3-pip python3-dev build-base nginx supervisor
else
    echo "⚠️  Could not detect package manager. Please install dependencies manually:"
    echo "   - Python 3.8+"
    echo "   - pip3"
    echo "   - python3-dev"
    echo "   - build tools (gcc, make)"
    echo "   - nginx (optional)"
    echo "   - supervisor (optional)"
fi

# Set up application directory
APP_DIR="/opt/article-generator"
echo "📁 Setting up application directory: $APP_DIR"

# Create directory if it doesn't exist
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# If running as specific user, change ownership
if [ ! -z "$APP_USER" ]; then
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
fi

# Clone or update repository
if [ -d ".git" ]; then
    echo "📥 Updating existing repository..."
    git pull origin main
else
    echo "📥 Cloning repository..."
    # Replace with your actual repository URL
    # git clone https://github.com/your-username/articleGen.git .
    echo "   ⚠️  Please clone your repository manually:"
    echo "   git clone <your-repo-url> $APP_DIR"
fi

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r webapp_requirements.txt

# Set up environment variables
echo "🔧 Setting up environment variables..."
cat > .env << EOF
# Production Environment Variables
ENVIRONMENT=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///webapp_users.db

# FTP Configuration (update with your values)
DEFAULT_FTP_HOST=212.1.209.3
DEFAULT_FTP_REMOTE_DIR=/public_html

# Security
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Performance
MAX_WORKERS=4
TIMEOUT=120
EOF

echo "   ✅ Environment file created (.env)"
echo "   🔒 Please update the .env file with your actual values"

# Set up systemd service (for Ubuntu/CentOS)
echo "🔧 Setting up systemd service..."
cat > /etc/systemd/system/article-generator.service << EOF
[Unit]
Description=SEO Article Generator Web App
After=network.target

[Service]
Type=notify
User=${APP_USER:-www-data}
Group=${APP_USER:-www-data}
RuntimeDirectory=article-generator
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn -c gunicorn.conf.py webapp_main:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable article-generator

# Set up nginx configuration (optional)
echo "🌐 Setting up nginx configuration..."
cat > /etc/nginx/sites-available/article-generator << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=app:10m rate=10r/s;
    limit_req zone=app burst=20 nodelay;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (if any)
    location /static/ {
        alias $APP_DIR/webapp_static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/api/health;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/article-generator /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Set up SSL with Let's Encrypt (optional)
echo "🔒 SSL Setup (optional):"
echo "   To enable HTTPS with Let's Encrypt:"
echo "   1. Install certbot: apt-get install certbot python3-certbot-nginx"
echo "   2. Update server_name in nginx config with your domain"
echo "   3. Run: certbot --nginx -d your-domain.com -d www.your-domain.com"

# Set up log rotation
echo "📋 Setting up log rotation..."
cat > /etc/logrotate.d/article-generator << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ${APP_USER:-www-data} ${APP_USER:-www-data}
    postrotate
        systemctl reload article-generator
    endscript
}
EOF

# Set up monitoring (optional)
echo "📊 Setting up basic monitoring..."
cat > /etc/supervisor/conf.d/article-generator-monitor.conf << EOF
[program:article-generator-monitor]
command=$APP_DIR/venv/bin/python3 -c "
import time
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('monitor')

while True:
    try:
        response = requests.get('http://localhost:8000/api/health', timeout=30)
        if response.status_code == 200:
            logger.info('Health check passed')
        else:
            logger.warning(f'Health check failed: {response.status_code}')
    except Exception as e:
        logger.error(f'Health check error: {e}')
    time.sleep(300)  # Check every 5 minutes
"
directory=$APP_DIR
user=${APP_USER:-www-data}
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_DIR/logs/monitor.log
EOF

supervisorctl reread
supervisorctl update

# Final instructions
echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo ""
echo "📋 Next steps:"
echo "   1. Update .env file with your actual configuration"
echo "   2. Update nginx server_name with your domain"
echo "   3. Start the service: systemctl start article-generator"
echo "   4. Check status: systemctl status article-generator"
echo "   5. View logs: journalctl -u article-generator -f"
echo ""
echo "🌐 Access points:"
echo "   Application: http://your-domain.com"
echo "   Health check: http://your-domain.com/health"
echo "   API docs: http://your-domain.com/docs"
echo ""
echo "📁 Important files:"
echo "   Application: $APP_DIR"
echo "   Logs: $APP_DIR/logs/"
echo "   Environment: $APP_DIR/.env"
echo "   Nginx config: /etc/nginx/sites-available/article-generator"
echo "   Systemd service: /etc/systemd/system/article-generator.service"
echo ""
echo "🔒 Security recommendations:"
echo "   1. Set up SSL/TLS with Let's Encrypt"
echo "   2. Configure firewall (ufw or iptables)"
echo "   3. Regular security updates"
echo "   4. Monitor logs for suspicious activity"
echo "   5. Backup database regularly"
echo ""
echo "✅ Production deployment ready!"
