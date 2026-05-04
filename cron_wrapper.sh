#!/bin/bash

# Cron wrapper for auto_publish.sh with intelligent sync system
# This script sets up the proper environment for cron execution and enhanced logging

# Set PATH to include common locations
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Change to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set up logging
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
CRON_LOG="$LOG_DIR/cron.log"

# Add timestamp to cron log with intelligent sync info
echo "=================================================" >> "$CRON_LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting INTELLIGENT cron job" >> "$CRON_LOG"
echo "🧠 Feature: Unified intelligent sync with article-level change detection" >> "$CRON_LOG"
echo "⚡ Smart differential processing - only syncs changed content" >> "$CRON_LOG"
echo "Working directory: $(pwd)" >> "$CRON_LOG"
echo "PATH: $PATH" >> "$CRON_LOG"
echo "=================================================" >> "$CRON_LOG"

# Execute the main script with full bash path and proper error handling
/bin/bash "$SCRIPT_DIR/auto_publish.sh" >> "$CRON_LOG" 2>&1
EXIT_CODE=$?

# Log completion with enhanced status
echo "=================================================" >> "$CRON_LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Intelligent cron job completed" >> "$CRON_LOG"
echo "Exit code: $EXIT_CODE" >> "$CRON_LOG"
if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 SUCCESS: Intelligent sync system completed successfully" >> "$CRON_LOG"
else
    echo "❌ FAILED: Intelligent sync system encountered errors" >> "$CRON_LOG"
fi
echo "=================================================" >> "$CRON_LOG"
echo "" >> "$CRON_LOG"

# Write machine-readable status file for webapp monitoring
STATUS_FILE="$SCRIPT_DIR/logs/scheduler_status.json"
LAST_STATUS="success"
[ $EXIT_CODE -ne 0 ] && LAST_STATUS="failed"
mkdir -p "$SCRIPT_DIR/logs"
cat > "$STATUS_FILE" << STATUSEOF
{
  "last_run": "$(date '+%Y-%m-%dT%H:%M:%S')",
  "exit_code": $EXIT_CODE,
  "status": "$LAST_STATUS"
}
STATUSEOF
