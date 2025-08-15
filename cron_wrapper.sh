#!/bin/bash

# Cron wrapper for auto_publish.sh
# This script sets up the proper environment for cron execution

# Set PATH to include common locations
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Change to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set up logging
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
CRON_LOG="$LOG_DIR/cron.log"

# Add timestamp to cron log
echo "=================================================" >> "$CRON_LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting cron job" >> "$CRON_LOG"
echo "Working directory: $(pwd)" >> "$CRON_LOG"
echo "PATH: $PATH" >> "$CRON_LOG"
echo "=================================================" >> "$CRON_LOG"

# Execute the main script with full bash path and proper error handling
/bin/bash "$SCRIPT_DIR/auto_publish.sh" >> "$CRON_LOG" 2>&1

# Log completion
echo "$(date '+%Y-%m-%d %H:%M:%S') - Cron job completed with exit code: $?" >> "$CRON_LOG"
echo "" >> "$CRON_LOG"
