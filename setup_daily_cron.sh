#!/bin/bash

# Daily Cron Job Setup Script for Auto Publisher at 6PM IST
# This script sets up the daily cron job for automatic article generation and deployment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_PUBLISH_SCRIPT="$SCRIPT_DIR/auto_publish.sh"
CRON_WRAPPER_SCRIPT="$SCRIPT_DIR/cron_wrapper.sh"

echo "=== Daily Auto Publisher Cron Job Setup (6PM IST) ==="
echo ""

# Check if auto_publish.sh exists
if [[ ! -f "$AUTO_PUBLISH_SCRIPT" ]]; then
    echo "Error: auto_publish.sh not found at $AUTO_PUBLISH_SCRIPT"
    exit 1
fi

# Check if cron_wrapper.sh exists
if [[ ! -f "$CRON_WRAPPER_SCRIPT" ]]; then
    echo "Error: cron_wrapper.sh not found at $CRON_WRAPPER_SCRIPT"
    exit 1
fi

# Make sure the scripts are executable
chmod +x "$AUTO_PUBLISH_SCRIPT"
chmod +x "$CRON_WRAPPER_SCRIPT"

# Create daily cron job entry for 6PM IST (18:00)
DAILY_CRON_ENTRY="0 18 * * * $CRON_WRAPPER_SCRIPT"

echo "The following cron job will be added to run daily at 6PM IST:"
echo "$DAILY_CRON_ENTRY"
echo ""
echo "This will:"
echo "✅ Fetch fresh trending data globally (>100K searches)"
echo "✅ Include India's TOP 15 articles (regardless of search volume)"
echo "✅ Generate articles based on filtered trends"
echo "✅ Sync to FTP server with smart differential uploading"
echo ""

# Check if any existing cron job exists for this script
if crontab -l 2>/dev/null | grep -q "$CRON_WRAPPER_SCRIPT"; then
    echo "Existing cron job found for this project:"
    crontab -l 2>/dev/null | grep "$CRON_WRAPPER_SCRIPT"
    echo ""
    read -p "Do you want to replace the existing cron job with daily 6PM schedule? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing cron job
        crontab -l 2>/dev/null | grep -v "$CRON_WRAPPER_SCRIPT" | crontab -
        echo "Existing cron job removed."
    else
        echo "Setup cancelled."
        exit 0
    fi
fi

# Add new daily cron job
(crontab -l 2>/dev/null; echo "$DAILY_CRON_ENTRY") | crontab -

# Verify the cron job was added
if crontab -l 2>/dev/null | grep -q "$DAILY_CRON_ENTRY"; then
    echo "✅ Daily cron job successfully added!"
    echo ""
    echo "📅 Schedule: Every day at 6:00 PM IST"
    echo "📊 Criteria: Global trends >100K searches + India TOP 15"
    echo "🔄 Next run: $(date -d 'today 18:00' '+%Y-%m-%d at %H:%M:%S')"
    echo ""
    echo "Current cron jobs:"
    crontab -l 2>/dev/null | grep "$CRON_WRAPPER_SCRIPT"
    echo ""
    echo "📁 Logs will be written to: $SCRIPT_DIR/logs/"
    echo "🔍 Monitor progress: tail -f $SCRIPT_DIR/logs/cron.log"
    echo ""
    echo "To remove this cron job later, run:"
    echo "crontab -e"
else
    echo "❌ Failed to add cron job. Please check manually with 'crontab -l'"
    exit 1
fi

echo "=== Setup Complete ==="
