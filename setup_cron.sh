#!/bin/bash

# Cron Job Setup Script for Auto Publisher
# This script helps set up the hourly cron job for automatic article generation and deployment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_PUBLISH_SCRIPT="$SCRIPT_DIR/auto_publish.sh"

echo "=== Auto Publisher Cron Job Setup ==="
echo ""

# Check if auto_publish.sh exists
if [[ ! -f "$AUTO_PUBLISH_SCRIPT" ]]; then
    echo "Error: auto_publish.sh not found at $AUTO_PUBLISH_SCRIPT"
    exit 1
fi

# Make sure the script is executable
chmod +x "$AUTO_PUBLISH_SCRIPT"

# Create cron job entry
CRON_ENTRY="0 * * * * $AUTO_PUBLISH_SCRIPT >> $SCRIPT_DIR/logs/cron.log 2>&1"

echo "The following cron job will be added to run every hour:"
echo "$CRON_ENTRY"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$AUTO_PUBLISH_SCRIPT"; then
    echo "Cron job already exists for auto_publish.sh"
    echo ""
    echo "Current cron jobs:"
    crontab -l 2>/dev/null | grep "$AUTO_PUBLISH_SCRIPT"
    echo ""
    read -p "Do you want to update the existing cron job? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing cron job
        crontab -l 2>/dev/null | grep -v "$AUTO_PUBLISH_SCRIPT" | crontab -
        echo "Existing cron job removed."
    else
        echo "Setup cancelled."
        exit 0
    fi
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "Cron job added successfully!"
echo ""
echo "The script will now run every hour at minute 0 (e.g., 1:00, 2:00, 3:00, etc.)"
echo ""
echo "To verify the cron job was added, run: crontab -l"
echo "To remove the cron job later, run: crontab -e"
echo ""
echo "Logs will be saved to: $SCRIPT_DIR/logs/"
echo ""
echo "=== Setup Complete ==="

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Show next few execution times
echo "Next execution times (approximate):"
current_hour=$(date +%H)
current_minute=$(date +%M)

for i in {1..3}; do
    if [[ $current_minute -eq 0 ]]; then
        next_hour=$((current_hour + i))
    else
        next_hour=$((current_hour + i))
    fi
    
    if [[ $next_hour -ge 24 ]]; then
        next_hour=$((next_hour - 24))
        next_date=$(date -d "tomorrow" +%Y-%m-%d)
    else
        next_date=$(date +%Y-%m-%d)
    fi
    
    printf "  %s %02d:00:00\n" "$next_date" "$next_hour"
done

echo ""
echo "To test the script manually, run: $AUTO_PUBLISH_SCRIPT"
