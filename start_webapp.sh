#!/bin/bash

# SEO Article Generator Web App Startup Script
# This script starts the FastAPI web application

echo "🚀 Starting SEO Article Generator Web App"
echo "=" * 50

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing webapp dependencies..."
pip install -r webapp_requirements.txt

# Set environment variables for production
export SECRET_KEY=${SECRET_KEY:-"your-secret-key-change-this-in-production-$(date +%s)"}
export ENVIRONMENT=${ENVIRONMENT:-"development"}

# Database setup
echo "🗄️  Initializing database..."
python3 -c "
import sqlite3
from pathlib import Path

db_path = Path('webapp_users.db')
if not db_path.exists():
    conn = sqlite3.connect(db_path)
    conn.execute('SELECT 1')  # Test connection
    conn.close()
    print('✅ Database initialized')
else:
    print('✅ Database already exists')
"

# Create logs directory if it doesn't exist
mkdir -p logs

echo ""
echo "🌐 Web App Configuration:"
echo "   📁 Static files: webapp_static/"
echo "   🎨 Templates: webapp_templates/"
echo "   🗄️  Database: webapp_users.db"
echo "   📋 Logs: logs/"
echo ""

# Start the application
echo "🚀 Starting FastAPI server..."
echo "📍 URL: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with uvicorn
uvicorn webapp_main:app --host 0.0.0.0 --port 8000 --reload --log-level info

echo ""
echo "👋 Server stopped"
