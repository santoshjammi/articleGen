"""
Production deployment configuration for SEO Article Generator Web App
For cloud deployment (AWS, GCP, DigitalOcean, etc.)
"""

# Production WSGI server configuration
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 5

# Security
limit_request_line = 8192
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process management
preload_app = True
pidfile = "logs/gunicorn.pid"
daemon = False

# Performance
worker_tmp_dir = "/dev/shm"  # Use RAM for better performance

# Environment
raw_env = [
    'ENVIRONMENT=production',
    'SECRET_KEY=your-production-secret-key-change-this',
]
