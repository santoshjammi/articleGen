#!/bin/bash

# Test script to verify .env configuration and system readiness

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Testing Auto Publisher Configuration..."
echo "============================================"

# Test 1: Check if .env file exists
echo "1. Checking .env file..."
if [[ -f "$SCRIPT_DIR/.env" ]]; then
    echo "   ✅ .env file found"
else
    echo "   ❌ .env file not found"
    echo "   💡 Run: cp .env.example .env and configure it"
    exit 1
fi

# Test 2: Load and validate environment variables
echo "2. Loading environment variables..."
set -a
source "$SCRIPT_DIR/.env"
set +a

required_vars=("GEMINI_API_KEY" "FTP_HOST" "FTP_USER" "FTP_PASS")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        missing_vars+=("$var")
    fi
done

if [[ ${#missing_vars[@]} -eq 0 ]]; then
    echo "   ✅ All required environment variables are set"
    echo "   📍 FTP Host: $FTP_HOST"
    echo "   👤 FTP User: $FTP_USER"
    echo "   🔑 FTP Pass: ${FTP_PASS:0:3}***"
    echo "   🔑 Gemini API: ${GEMINI_API_KEY:0:10}***"
else
    echo "   ❌ Missing required variables: ${missing_vars[*]}"
    exit 1
fi

# Test 3: Check required Python files
echo "3. Checking required Python files..."
required_files=("super_article_manager.py" "generateSite.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -eq 0 ]]; then
    echo "   ✅ All required Python files found"
else
    echo "   ❌ Missing files: ${missing_files[*]}"
    exit 1
fi

# Test 4: Check Python 3
echo "4. Checking Python 3..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo "   ✅ $python_version"
else
    echo "   ❌ Python 3 not found"
    exit 1
fi

# Test 5: Check lftp (FTP client)
echo "5. Checking lftp..."
if command -v lftp &> /dev/null; then
    lftp_version=$(lftp --version | head -n1)
    echo "   ✅ $lftp_version"
else
    echo "   ⚠️  lftp not found - will be installed automatically"
    echo "   💡 Or install manually: brew install lftp"
fi

# Test 6: Test FTP connection (optional)
echo "6. Testing FTP connection with SSL..."
if command -v lftp &> /dev/null; then
    echo "   🔄 Testing FTP connection to $FTP_HOST with SSL..."
    
    # Create a simple test script with SSL settings
    cat > /tmp/test_ftp.lftp << EOF
set ftp:ssl-allow $FTP_SSL_ENABLED
set ftp:ssl-force $FTP_SSL_FORCE  
set ftp:ssl-protect-data $FTP_SSL_ENABLED
set ftp:ssl-protect-list $FTP_SSL_ENABLED
set ssl:verify-certificate $FTP_SSL_VERIFY_CERT
set ftp:passive-mode yes
set net:timeout 10
set net:max-retries 1
open ftp://$FTP_USER:$FTP_PASS@$FTP_HOST
ls
quit
EOF
    
    if timeout 15 lftp -f /tmp/test_ftp.lftp >/dev/null 2>&1; then
        echo "   ✅ FTP connection with SSL successful"
        echo "   🔒 SSL Settings: Enabled=$FTP_SSL_ENABLED, Verify=$FTP_SSL_VERIFY_CERT, Force=$FTP_SSL_FORCE"
    else
        echo "   ⚠️  FTP connection failed - check credentials or SSL settings"
    fi
    
    rm -f /tmp/test_ftp.lftp
else
    echo "   ⏭️  Skipping FTP test (lftp not available)"
fi

# Test 7: Check script permissions
echo "7. Checking script permissions..."
if [[ -x "$SCRIPT_DIR/auto_publish.sh" ]]; then
    echo "   ✅ auto_publish.sh is executable"
else
    echo "   ⚠️  auto_publish.sh is not executable"
    echo "   💡 Run: chmod +x auto_publish.sh"
fi

if [[ -x "$SCRIPT_DIR/setup_cron.sh" ]]; then
    echo "   ✅ setup_cron.sh is executable"
else
    echo "   ⚠️  setup_cron.sh is not executable"
    echo "   💡 Run: chmod +x setup_cron.sh"
fi

echo ""
echo "🎉 Configuration test completed!"
echo ""
echo "Next steps:"
echo "1. Fix any issues shown above"
echo "2. Run a test: ./auto_publish.sh"
echo "3. Set up automation: ./setup_cron.sh"
echo ""
