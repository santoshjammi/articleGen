#!/bin/bash

# Simplified Automated Article Generation Script
# Runs every 6 hours to generate 15 trend-based articles and update website
# Commands to run:
# 1. python super_article_manager.py generate trends --count 15 --per-region
# 2. python workflow.py with option 2 (fetch fresh trends + generate articles)

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/auto_publish_$(date +%Y%m%d).log"
VENV_DIR="$SCRIPT_DIR/venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${BLUE}[$timestamp]${NC} $message" | tee -a "$LOG_FILE"
}

log_error() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${RED}[$timestamp] ERROR:${NC} $message" | tee -a "$LOG_FILE"
}

log_success() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${GREEN}[$timestamp] SUCCESS:${NC} $message" | tee -a "$LOG_FILE"
}

log_warning() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${YELLOW}[$timestamp] WARNING:${NC} $message" | tee -a "$LOG_FILE"
}

# Function to activate virtual environment
activate_venv() {
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        log "Activating virtual environment..."
        source "$VENV_DIR/bin/activate"
        log_success "Virtual environment activated"
    else
        log_warning "Virtual environment not found at $VENV_DIR"
        log "Using system Python instead"
    fi
}

# Function to generate trend-based articles
generate_trend_articles() {
    log "Generating 15 trend-based articles per region..."
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    cd "$SCRIPT_DIR"
    if python3 super_article_manager.py generate trends --count 15 --per-region >> "$LOG_FILE" 2>&1; then
        log_success "Generated 15 trend-based articles per region"
        return 0
    else
        log_error "Failed to generate trend-based articles"
        return 1
    fi
}

# Function to generate local manifest
generate_local_manifest() {
    log "Generating local manifest..."
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    cd "$SCRIPT_DIR"
    if python3 generateLocalManifest.py >> "$LOG_FILE" 2>&1; then
        log_success "Local manifest generated successfully"
        return 0
    else
        log_error "Failed to generate local manifest"
        return 1
    fi
}

# Function to run workflow.py with option 2 (fetch fresh trends + generate articles)
run_workflow_fresh_trends() {
    log "Running workflow.py with option 2 (fetch fresh trends + generate articles)..."
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    cd "$SCRIPT_DIR"
    # Use echo to provide option 2 to the interactive script
    if echo "2" | python3 workflow.py >> "$LOG_FILE" 2>&1; then
        log_success "Workflow.py completed successfully"
        return 0
    else
        log_error "Workflow.py failed"
        return 1
    fi
}

# Function to backup current articles data
backup_articles() {
    local backup_dir="$SCRIPT_DIR/backups"
    local backup_file="$backup_dir/perplexityArticles_backup_$(date +%Y%m%d_%H%M%S).json"
    
    mkdir -p "$backup_dir"
    
    if [[ -f "$SCRIPT_DIR/perplexityArticles_eeat_enhanced.json" ]]; then
        cp "$SCRIPT_DIR/perplexityArticles_eeat_enhanced.json" "$backup_file"
        log "Backup created: $backup_file"
        
        # Keep only last 10 backups
        ls -t "$backup_dir"/perplexityArticles_backup_*.json | tail -n +11 | xargs -r rm 2>/dev/null || true
    fi
}

# Function to cleanup old logs
cleanup_logs() {
    log "Cleaning up old logs..."
    
    # Remove logs older than 7 days
    find "$LOG_DIR" -name "auto_publish_*.log" -mtime +7 -delete 2>/dev/null || true
    
    log "Log cleanup completed"
}

# Function to sync to FTP server (FINAL STEP)
sync_to_ftp() {
    log "Syncing to FTP server using ultra-fast parallel upload..."
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    cd "$SCRIPT_DIR"
    if python3 ultraFastSync.py >> "$LOG_FILE" 2>&1; then
        log_success "FTP sync completed successfully"
        return 0
    else
        log_error "FTP sync failed"
        return 1
    fi
}

# Main execution function
main() {
    log "=== Starting Simplified Article Generation (Every 6 Hours) ==="
    log "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Cleanup old logs
    cleanup_logs
    
    # Create backup
    backup_articles
    
    # Step 0: Generate local manifest (FIRST STEP)
    log "Step 0: Generating local manifest..."
    if ! generate_local_manifest; then
        log_error "Failed to generate local manifest"
        return 1
    fi
    
    # Step 1: Generate 15 trend-based articles per region
    log "Step 1: Generating trend-based articles..."
    if ! generate_trend_articles; then
        log_error "Failed to generate trend-based articles"
        return 1
    fi
    
    # Step 2: Run workflow.py with option 2 (fetch fresh trends + generate articles)
    log "Step 2: Running fresh trends workflow..."
    if ! run_workflow_fresh_trends; then
        log_error "Failed to run fresh trends workflow"
        return 1
    fi
    
    # Step 3: Sync to FTP server (FINAL STEP)
    log "Step 3: Syncing to FTP server..."
    if ! sync_to_ftp; then
        log_error "Failed to sync to FTP server"
        return 1
    fi
    
    log_success "=== All tasks completed successfully ==="
    log "Next run should be in 6 hours"
    log "=== Process completed at $(date '+%Y-%m-%d %H:%M:%S') ==="
}

# Trap to handle script interruption
trap 'log "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"
