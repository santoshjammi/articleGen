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

# Function to generate missing images with retry logic and verification
generate_missing_images() {
    local step_name="$1"
    local max_retries=3
    local wait_seconds=15
    local retry_count=0
    
    log "Generating missing images after $step_name..."
    
    while [ $retry_count -lt $max_retries ]; do
        retry_count=$((retry_count + 1))
        log "Image generation attempt $retry_count/$max_retries..."
        
        # Activate virtual environment
        activate_venv
        cd "$SCRIPT_DIR"
        
        # Run image generation
        if python3 super_article_manager.py images >> "$LOG_FILE" 2>&1; then
            log "Image generation command executed successfully"
        else
            log_warning "Image generation command returned error (attempt $retry_count)"
        fi
        
        # Verify images after generation
        log "Verifying generated images..."
        if verify_images; then
            log_success "All images verified successfully after $retry_count attempt(s)"
            return 0
        else
            if [ $retry_count -lt $max_retries ]; then
                log_warning "Image verification failed, waiting ${wait_seconds}s before retry..."
                sleep $wait_seconds
            else
                log_warning "Image verification failed after $max_retries attempts"
                log_warning "Continuing with process - some images may be missing"
                return 1
            fi
        fi
    done
    
    return 1
}

# Function to verify images (WebP format and count validation)
verify_images() {
    local dist_dir="$SCRIPT_DIR/dist"
    local error_count=0
    local missing_images=0
    local non_webp_images=0
    local total_images=0
    
    if [ ! -d "$dist_dir" ]; then
        log_error "Distribution directory not found: $dist_dir"
        return 1
    fi
    
    log "Scanning for image verification in $dist_dir..."
    
    # Count total images
    total_images=$(find "$dist_dir" -type f \( -name "*.webp" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | wc -l)
    
    # Check for non-WebP images (should be converted)
    non_webp_images=$(find "$dist_dir" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | wc -l)
    
    # Check for missing main.webp and inline_*.webp files
    local main_webp_missing=0
    local inline_webp_missing=0
    
    # Check for main.webp files in article directories
    while IFS= read -r -d '' article_dir; do
        if [ ! -f "$article_dir/main.webp" ]; then
            main_webp_missing=$((main_webp_missing + 1))
            log_warning "Missing main.webp in: $(basename "$article_dir")"
        fi
        
        # Check for inline images referenced in HTML but missing as WebP
        if [ -f "$article_dir/index.html" ]; then
            local inline_count
            inline_count=$(grep -o 'inline_[0-9]*.webp' "$article_dir/index.html" 2>/dev/null | sort -u | wc -l)
            local actual_inline
            actual_inline=$(find "$article_dir" -name "inline_*.webp" | wc -l)
            
            if [ "$inline_count" -gt "$actual_inline" ]; then
                inline_webp_missing=$((inline_webp_missing + (inline_count - actual_inline)))
                log_warning "Missing $(($inline_count - $actual_inline)) inline images in: $(basename "$article_dir")"
            fi
        fi
    done < <(find "$dist_dir" -type d -name "*" -path "*/articles/*" -print0 2>/dev/null)
    
    # Calculate total missing images
    missing_images=$((main_webp_missing + inline_webp_missing))
    
    # Log verification results
    log "📊 IMAGE VERIFICATION RESULTS:"
    log "   📸 Total images found: $total_images"
    log "   ✅ WebP format images: $((total_images - non_webp_images))"
    log "   ⚠️  Non-WebP images: $non_webp_images"
    log "   ❌ Missing main.webp: $main_webp_missing"
    log "   ❌ Missing inline.webp: $inline_webp_missing"
    log "   🔢 Total missing images: $missing_images"
    
    # Determine verification result
    if [ $missing_images -eq 0 ] && [ $non_webp_images -eq 0 ]; then
        log_success "✅ Image verification PASSED - All images present in WebP format"
        return 0
    elif [ $missing_images -lt 5 ] && [ $non_webp_images -eq 0 ]; then
        log_warning "⚠️ Image verification ACCEPTABLE - Only $missing_images missing images"
        return 0
    else
        log_warning "❌ Image verification FAILED - $missing_images missing, $non_webp_images non-WebP"
        return 1
    fi
}

# Function to generate differential manifest (STEP 2.5)
generate_differential_manifest() {
    log "Generating differential manifest (smart change detection)..."
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    cd "$SCRIPT_DIR"
    if python3 generateDifferentialManifest.py >> "$LOG_FILE" 2>&1; then
        log_success "Differential manifest generated successfully"
        return 0
    else
        log_error "Failed to generate differential manifest"
        return 1
    fi
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
    log "=== Starting SEO-Focused Article Generation (Daily at 6PM IST) ==="
    log "🎯 SEO Strategy: Global trends >100K searches + India TOP 15"
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
    
    # Step 1: Generate 15 trend-based articles per region (using SEO-filtered trends)
    log "Step 1: Generating SEO-qualified trend-based articles..."
    if ! generate_trend_articles; then
        log_error "Failed to generate trend-based articles"
        return 1
    fi
    
    # Step 1.5: Generate missing images (after trend articles)
    log "Step 1.5: Generating missing images after trend articles..."
    generate_missing_images "trend articles"
    
    # Step 2: Run workflow.py with option 2 (fetch fresh SEO-filtered trends + generate articles)
    log "Step 2: Running fresh SEO-filtered trends workflow..."
    if ! run_workflow_fresh_trends; then
        log_error "Failed to run fresh trends workflow"
        return 1
    fi
    
    # Step 2.25: Generate missing images (after fresh trends workflow)
    log "Step 2.25: Generating missing images after fresh trends workflow..."
    generate_missing_images "fresh trends workflow"
    
    # Step 2.5: Generate differential manifest (smart change detection)
    log "Step 2.5: Analyzing changes for differential sync..."
    if ! generate_differential_manifest; then
        log_error "Failed to generate differential manifest"
        return 1
    fi
    
    # Step 3: Sync to FTP server (FINAL STEP)
    log "Step 3: Syncing to FTP server..."
    if ! sync_to_ftp; then
        log_error "Failed to sync to FTP server"
        return 1
    fi
    
    log_success "=== All SEO-focused tasks completed successfully ==="
    log "🎯 Generated articles only for high-traffic trends"
    log "📈 Next run scheduled for tomorrow at 6PM IST"
    log "=== Process completed at $(date '+%Y-%m-%d %H:%M:%S') ==="
}

# Trap to handle script interruption
trap 'log "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"
