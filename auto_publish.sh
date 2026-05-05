#!/bin/bash

# Simplified Automated Article Generation Script
# Runs daily to generate 10 trend-based articles (5 India + 5 Worldwide)
# Commands to run:
# 1. python super_article_manager.py generate trends --count 5 --per-region (for India)
# 2. python super_article_manager.py generate trends --count 5 (for Worldwide)

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

# Default region for custom keywords (change here if needed)
DEFAULT_CUSTOM_REGION="US"

# Function to generate articles from custom_keywords.txt (if it exists and has keywords)
generate_custom_keyword_articles() {
    local keywords_file="$SCRIPT_DIR/custom_keywords.txt"
    
    if [[ ! -f "$keywords_file" ]]; then
        log "No custom_keywords.txt found, skipping custom keyword generation"
        return 0
    fi
    
    # Read non-empty, non-comment lines
    local keywords=()
    while IFS= read -r line; do
        # Strip leading/trailing whitespace
        line="${line#"${line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"
        # Skip empty lines and comments
        [[ -z "$line" || "$line" == \#* ]] && continue
        keywords+=("$line")
    done < "$keywords_file"
    
    if [[ ${#keywords[@]} -eq 0 ]]; then
        log "custom_keywords.txt is empty or has only comments, skipping"
        return 0
    fi
    
    log "Found ${#keywords[@]} custom keyword(s) in custom_keywords.txt"
    for kw in "${keywords[@]}"; do
        log "  • $kw"
    done
    
    activate_venv
    cd "$SCRIPT_DIR"
    
    # Build the keywords argument (each keyword as a separate arg)
    local kw_args=()
    for kw in "${keywords[@]}"; do
        kw_args+=("$kw")
    done
    
    log "Generating articles for custom keywords (region: $DEFAULT_CUSTOM_REGION)..."
    if python3 super_article_manager.py generate keywords "${kw_args[@]}" --region "$DEFAULT_CUSTOM_REGION" >> "$LOG_FILE" 2>&1; then
        log_success "Custom keyword articles generated successfully"
        return 0
    else
        log_warning "Custom keyword article generation failed (non-blocking)"
        return 1
    fi
}

# Function to generate trend-based articles
generate_trend_articles() {
    log "Generating 5 trend-based articles for India region..."
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    cd "$SCRIPT_DIR"
    # Generate top 10 articles from highest-traffic global trends
    log "Generating 10 comprehensive AEO/SEO articles from top 10 global trends..."
    if python3 super_article_manager.py generate trends --count 10 >> "$LOG_FILE" 2>&1; then
        log_success "Generated 10 comprehensive AEO/SEO trend-based articles"
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

# Function to refresh trends data for next run (non-interactive)
refresh_trends_data() {
    log "Refreshing trends data for next run..."
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    cd "$SCRIPT_DIR"
    
    # Fetch fresh trending data for next run
    log "Fetching fresh trending data for next run..."
    if python3 fetch_fresh_trends.py >> "$LOG_FILE" 2>&1; then
        log_success "Fresh trends data refreshed successfully"
        return 0
    else
        log_warning "Fresh trends refresh failed, will use cached data next time"
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

# Function to generate enhanced differential manifest with article intelligence (STEP 2.5)
generate_differential_manifest() {
    log "Generating enhanced differential manifest with article intelligence..."
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    cd "$SCRIPT_DIR"
    if python3 generateDifferentialManifest.py >> "$LOG_FILE" 2>&1; then
        log_success "Enhanced differential manifest with article intelligence generated successfully"
        return 0
    else
        log_error "Failed to generate enhanced differential manifest"
        return 1
    fi
}

# Function to sync to FTP server with intelligent monitoring (FINAL STEP)
sync_to_ftp() {
    log "Syncing to FTP server using ultra-fast parallel upload with intelligent sync..."
    
    # Check differential sync status first
    if [[ -f "$SCRIPT_DIR/output/.differential_sync.json" ]]; then
        local files_to_sync changed_articles sync_strategy
        
        # Use Python to safely parse JSON and extract sync statistics
        local sync_stats
        sync_stats=$(python3 -c "
import json
try:
    with open('output/.differential_sync.json', 'r') as f:
        data = json.load(f)
    files_to_sync = len(data.get('changed_files', [])) + len(data.get('new_files', []))
    changed_articles = data.get('article_metadata', {}).get('changed_articles', 0) 
    sync_strategy = data.get('sync_strategy', 'unknown')
    print(f'{files_to_sync}|{changed_articles}|{sync_strategy}')
except:
    print('unknown|unknown|unknown')
" 2>/dev/null)
        
        IFS='|' read -r files_to_sync changed_articles sync_strategy <<< "$sync_stats"
        
        log "🧠 INTELLIGENT SYNC ANALYSIS:"
        log "   📊 Files to sync: $files_to_sync"
        log "   📄 Articles changed: $changed_articles"
        log "   ⚡ Strategy: $sync_strategy"
        
        if [[ "$files_to_sync" == "0" ]]; then
            log "✅ No changes detected - site is already synchronized!"
            log_success "Intelligent sync: No FTP upload needed"
            return 0
        fi
    else
        log_warning "Differential sync manifest not found, proceeding with full sync"
    fi
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    cd "$SCRIPT_DIR"
    if python3 ultraFastSync.py >> "$LOG_FILE" 2>&1; then
        log_success "Intelligent FTP sync completed successfully"
        return 0
    else
        log_error "Intelligent FTP sync failed"
        return 1
    fi
}

# Function to display intelligent sync summary
display_sync_summary() {
    log "📊 INTELLIGENT SYNC SUMMARY:"
    
    if [[ -f "$SCRIPT_DIR/output/.differential_sync.json" ]]; then
        local summary
        summary=$(python3 -c "
import json
try:
    with open('output/.differential_sync.json', 'r') as f:
        data = json.load(f)
    total_files = len(data.get('changed_files', [])) + len(data.get('new_files', []))
    changed_files = len(data.get('changed_files', []))
    new_files = len(data.get('new_files', []))
    changed_articles = data.get('article_metadata', {}).get('changed_articles', 0)
    strategy = data.get('sync_strategy', 'unknown')
    print(f'   📁 Total files synced: {total_files}')
    print(f'   🔄 Changed files: {changed_files}')
    print(f'   🆕 New files: {new_files}')
    print(f'   📄 Articles processed: {changed_articles}')
    print(f'   ⚡ Sync strategy: {strategy}')
except Exception as e:
    print(f'   ❌ Error reading sync summary: {e}')
" 2>/dev/null)
        log "$summary"
    else
        log "   ❌ Sync manifest not available"
    fi
    log ""
}

# Main execution function
main() {
    log "=== Starting Intelligent SEO Article Generation (Daily at 6PM IST) ==="
    log "🧠 New Feature: Unified intelligent sync with article-level change detection"
    log "🎯 SEO Strategy: Global trends >100K searches + India TOP 15"
    log "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Cleanup old logs
    cleanup_logs
    
    # Create backup
    backup_articles
    
    # Step 1: Generate 10 trend-based articles (5 India + 5 Worldwide) using SEO-filtered trends
    log "Step 1: Generating SEO-qualified trend-based articles..."
    if ! generate_trend_articles; then
        log_error "Failed to generate trend-based articles"
        return 1
    fi
    
    # Step 1.5a: Auto-fetch fresh AI keywords from the internet into custom_keywords.txt
    log "Step 1.5a: Fetching trending AI keywords from the internet..."
    activate_venv
    cd "$SCRIPT_DIR"
    if python3 fetch_ai_keywords.py --max=10 >> "$LOG_FILE" 2>&1; then
        log_success "AI keyword fetch completed"
    else
        log_warning "AI keyword fetch had errors (non-blocking), continuing with existing keywords..."
    fi

    # Step 1.5b: Generate articles from custom_keywords.txt (trends + auto-fetched AI keywords)
    log "Step 1.5b: Generating articles from custom keywords (if any)..."
    generate_custom_keyword_articles || log_warning "Custom keyword generation had errors, continuing..."

    # Step 1.6: Generate missing images (after trend + custom articles)
    log "Step 1.6: Generating missing images after article generation..."
    generate_missing_images "trend articles"
    
    # Step 2: Refresh trends data for next run (optional, non-blocking)
    log "Step 2: Refreshing trends data for next run..."
    if ! refresh_trends_data; then
        log_warning "Failed to refresh trends data, continuing with site generation"
    fi
    
    # Step 2.25: Generate missing images (after trends refresh)
    log "Step 2.25: Generating missing images..."
    generate_missing_images "after trends refresh"

        # Step 2.4: Generate site with intelligent differential processing
        log "Step 2.4: Generating site with intelligent sync system..."
        generate_intelligent_site() {
            log "Using intelligent differential site generation with article enhancements..."

            # Activate virtual environment
            activate_venv
            cd "$SCRIPT_DIR"

            # Use the new intelligent differential mode with enhancement
            if python3 generateSite_advanced.py generate site --differential --enhance >> "$LOG_FILE" 2>&1; then
                log_success "Intelligent differential site generation completed successfully"
                return 0
            else
                log_error "Intelligent site generation failed"
                return 1
            fi
        }

        if ! generate_intelligent_site; then
            log_error "Failed to generate site with intelligent sync system"
            return 1
        fi
    
    # Step 2.5: Generate enhanced differential manifest with article intelligence
    log "Step 2.5: Analyzing changes with intelligent sync system..."
    if ! generate_differential_manifest; then
        log_error "Failed to generate enhanced differential manifest with article intelligence"
        return 1
    fi
    
    # Step 3: Intelligent FTP sync (FINAL STEP)
    log "Step 3: Intelligent FTP sync with smart change detection..."
    if ! sync_to_ftp; then
        log_error "Failed to complete intelligent FTP sync"
        return 1
    fi
    
    # Display intelligent sync summary
    display_sync_summary
    
    log_success "=== All intelligent SEO-focused tasks completed successfully ==="
    log "🧠 New: Unified intelligent sync with article-level change detection"
    log "🎯 Generated 10 articles daily (5 India + 5 Worldwide from high-traffic trends)"
    log "⚡ Smart differential sync - only uploads changed content"
    log "📈 Next run scheduled for tomorrow at 6PM IST"
    log "=== Process completed at $(date '+%Y-%m-%d %H:%M:%S') ==="
}

# Trap to handle script interruption
trap 'log "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"
