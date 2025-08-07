#!/bin/bash

# Automated Article Generation and Deployment Script
# Runs every hour to generate 4 new articles (2 from keywords, 2 from trends)
# and deploy to Hostinger hosting

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/auto_publish_$(date +%Y%m%d).log"
KEYWORDS_USED_FILE="$SCRIPT_DIR/keywords_used.txt"
TRENDS_USED_FILE="$SCRIPT_DIR/trends_used.txt"
VENV_DIR="$SCRIPT_DIR/venv"

# Load environment variables from .env file
if [[ -f "$SCRIPT_DIR/.env" ]]; then
    set -a  # automatically export all variables
    source "$SCRIPT_DIR/.env"
    set +a  # disable automatic export
else
    echo "ERROR: .env file not found. Please create it with FTP configuration."
    exit 1
fi

# Validate required environment variables
if [[ -z "$FTP_HOST" ]] || [[ -z "$FTP_USER" ]] || [[ -z "$FTP_PASS" ]]; then
    echo "ERROR: Missing required FTP configuration in .env file"
    echo "Required variables: FTP_HOST, FTP_USER, FTP_PASS"
    exit 1
fi

# Set default values for optional variables
FTP_PORT=${FTP_PORT:-21}
FTP_REMOTE_DIR=${FTP_REMOTE_DIR:-public_html}
FTP_SSL_ENABLED=${FTP_SSL_ENABLED:-no}
FTP_SSL_VERIFY_CERT=${FTP_SSL_VERIFY_CERT:-no}
FTP_SSL_FORCE=${FTP_SSL_FORCE:-no}

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

# Function to check if a keyword/trend has been used recently (within last 24 hours)
is_recently_used() {
    local item="$1"
    local used_file="$2"
    local hours_limit=24
    
    if [[ ! -f "$used_file" ]]; then
        return 1 # Not used (file doesn't exist)
    fi
    
    # Check if item was used within the last 24 hours
    local cutoff_time=$(date -d "$hours_limit hours ago" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -v-${hours_limit}H '+%Y-%m-%d %H:%M:%S' 2>/dev/null)
    
    while IFS='|' read -r timestamp used_item; do
        if [[ "$used_item" == "$item" ]] && [[ "$timestamp" > "$cutoff_time" ]]; then
            return 0 # Recently used
        fi
    done < "$used_file"
    
    return 1 # Not recently used
}

# Function to mark item as used
mark_as_used() {
    local item="$1"
    local used_file="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp|$item" >> "$used_file"
    
    # Keep only last 100 entries to prevent file from growing too large
    tail -n 100 "$used_file" > "${used_file}.tmp" && mv "${used_file}.tmp" "$used_file"
}

# Function to get unused keywords
get_unused_keywords() {
    local count="$1"
    local keywords=()
    
    # Sample keywords - you can expand this list or read from a file
    local all_keywords=(
        "artificial intelligence technology"
        "renewable energy solutions"
        "cryptocurrency market trends"
        "space exploration missions"
        "climate change impacts"
        "healthcare innovations"
        "electric vehicle adoption"
        "cybersecurity threats"
        "quantum computing advances"
        "biotechnology breakthroughs"
        "sustainable agriculture"
        "smart city development"
        "digital transformation"
        "machine learning applications"
        "blockchain technology"
        "5G network deployment"
        "virtual reality gaming"
        "autonomous vehicles"
        "green energy storage"
        "medical AI diagnostics"
        "robotics automation"
        "cloud computing services"
        "data privacy regulations"
        "fintech innovations"
        "e-commerce trends"
    )
    
    for keyword in "${all_keywords[@]}"; do
        if [[ ${#keywords[@]} -ge $count ]]; then
            break
        fi
        
        if ! is_recently_used "$keyword" "$KEYWORDS_USED_FILE"; then
            keywords+=("$keyword")
        fi
    done
    
    printf '%s\n' "${keywords[@]}"
}

# Function to get current trends (simulated - you can integrate with actual trend APIs)
get_current_trends() {
    local count="$1"
    local trends=()
    
    # Sample trends - in production, you might fetch these from Google Trends API, Twitter API, etc.
    local current_trends=(
        "Olympic Games 2024"
        "Presidential Election Updates"
        "Stock Market Volatility"
        "Tech Company Earnings"
        "Weather Extreme Events"
        "Celebrity News Updates"
        "Sports Championship Results"
        "Economic Policy Changes"
        "International Trade Relations"
        "Social Media Platform Updates"
        "Entertainment Industry News"
        "Scientific Research Findings"
        "Government Policy Announcements"
        "Technology Product Launches"
        "Environmental Conservation Efforts"
    )
    
    for trend in "${current_trends[@]}"; do
        if [[ ${#trends[@]} -ge $count ]]; then
            break
        fi
        
        if ! is_recently_used "$trend" "$TRENDS_USED_FILE"; then
            trends+=("$trend")
        fi
    done
    
    printf '%s\n' "${trends[@]}"
}

# Function to generate articles based on keywords
generate_keyword_articles() {
    local count="$1"
    log "Generating $count articles from keywords..."
    
    local keywords=()
    # Use read with process substitution instead of mapfile for compatibility
    while IFS= read -r line; do
        keywords+=("$line")
    done < <(get_unused_keywords "$count")
    
    if [[ ${#keywords[@]} -eq 0 ]]; then
        log_warning "No unused keywords available for article generation"
        return 1
    fi
    
    # Convert array to space-separated string for command line
    local keywords_string
    keywords_string=$(printf '"%s" ' "${keywords[@]}")
    keywords_string=${keywords_string% } # Remove trailing space
    
    log "Generating articles for keywords: ${keywords[*]}"
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    # Run keyword-based article generation using super_article_manager.py
    if python3 "$SCRIPT_DIR/super_article_manager.py" generate keywords ${keywords_string} >> "$LOG_FILE" 2>&1; then
        log_success "Generated articles for keywords: ${keywords[*]}"
        # Mark all keywords as used
        for keyword in "${keywords[@]}"; do
            mark_as_used "$keyword" "$KEYWORDS_USED_FILE"
        done
    else
        log_error "Failed to generate articles for keywords: ${keywords[*]}"
        return 1
    fi
}

# Function to generate articles based on trends
generate_trend_articles() {
    local count="$1"
    log "Generating $count articles from trends..."
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    # Use the trends generation mode from super_article_manager.py
    if python3 "$SCRIPT_DIR/super_article_manager.py" generate trends --count "$count" >> "$LOG_FILE" 2>&1; then
        log_success "Generated $count articles from trends"
        
        # Mark current trends as used (this is approximate since we don't know which exact trends were used)
        local trends=()
        while IFS= read -r line; do
            trends+=("$line")
        done < <(get_current_trends "$count")
        
        for trend in "${trends[@]}"; do
            mark_as_used "$trend" "$TRENDS_USED_FILE"
        done
    else
        log_error "Failed to generate articles from trends"
        return 1
    fi
}

# Function to generate the website
generate_website() {
    log "Generating website..."
    
    # Activate virtual environment before running Python scripts
    activate_venv
    
    cd "$SCRIPT_DIR"
    if python3 generateSite.py >> "$LOG_FILE" 2>&1; then
        log_success "Website generated successfully"
        return 0
    else
        log_error "Failed to generate website"
        return 1
    fi
}

# Function to upload to FTP using lftp
upload_to_hostinger() {
    log "Uploading to Hostinger..."
    
    # Check if lftp is installed
    if ! command -v lftp &> /dev/null; then
        log_error "lftp is not installed. Installing..."
        # Try to install lftp
        if command -v brew &> /dev/null; then
            brew install lftp >> "$LOG_FILE" 2>&1
        elif command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y lftp >> "$LOG_FILE" 2>&1
        elif command -v yum &> /dev/null; then
            sudo yum install -y lftp >> "$LOG_FILE" 2>&1
        else
            log_error "Could not install lftp. Please install it manually."
            return 1
        fi
    fi

    # Create lftp script
    local lftp_script="$SCRIPT_DIR/upload_script.lftp"
    cat > "$lftp_script" << EOF
set ftp:list-options -a
set ftp:ssl-allow $FTP_SSL_ENABLED
set ftp:ssl-force $FTP_SSL_FORCE
set ftp:ssl-protect-data $FTP_SSL_ENABLED
set ftp:ssl-protect-list $FTP_SSL_ENABLED
set ssl:verify-certificate $FTP_SSL_VERIFY_CERT
set ftp:passive-mode yes
set net:timeout 30
set net:max-retries 3
set net:reconnect-interval-base 5
set cmd:fail-exit yes

open ftp://$FTP_USER:$FTP_PASS@$FTP_HOST:$FTP_PORT

# Change to remote directory (try both with and without leading slash)
cd /$FTP_REMOTE_DIR || cd $FTP_REMOTE_DIR

# Mirror local dist directory to remote
mirror -Rev --delete --verbose --exclude-glob="*.log" --exclude-glob="*.tmp" $SCRIPT_DIR/dist .

quit
EOF

    # Execute lftp script
    if lftp -f "$lftp_script" >> "$LOG_FILE" 2>&1; then
        log_success "Successfully uploaded to Hostinger"
        rm -f "$lftp_script"
        return 0
    else
        log_error "Failed to upload to Hostinger"
        rm -f "$lftp_script"
        return 1
    fi
}

# Function to backup current articles data
backup_articles() {
    local backup_dir="$SCRIPT_DIR/backups"
    local backup_file="$backup_dir/perplexityArticles_backup_$(date +%Y%m%d_%H%M%S).json"
    
    mkdir -p "$backup_dir"
    
    if [[ -f "$SCRIPT_DIR/perplexityArticles.json" ]]; then
        cp "$SCRIPT_DIR/perplexityArticles.json" "$backup_file"
        log "Backup created: $backup_file"
        
        # Keep only last 10 backups
        ls -t "$backup_dir"/perplexityArticles_backup_*.json | tail -n +11 | xargs -r rm
    fi
}

# Function to send notification (optional - requires mail command or other notification system)
send_notification() {
    local message="$1"
    local subject="Auto Publisher Notification"
    
    # Uncomment and configure if you want email notifications
    # echo "$message" | mail -s "$subject" your-email@example.com
    
    log "Notification: $message"
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

# Function to check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    local requirements_met=true
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        requirements_met=false
    fi
    
    # Check required Python files
    local required_files=("generateSite.py" "super_article_manager.py")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
            log_error "Required file not found: $file"
            requirements_met=false
        fi
    done
    
    if [[ "$requirements_met" == false ]]; then
        log_error "System requirements not met. Exiting."
        exit 1
    fi
    
    log_success "System requirements check passed"
}

# Function to cleanup old logs
cleanup_logs() {
    log "Cleaning up old logs..."
    
    # Remove logs older than 7 days
    find "$LOG_DIR" -name "auto_publish_*.log" -mtime +7 -delete 2>/dev/null || true
    
    log "Log cleanup completed"
}

# Main execution function
main() {
    log "=== Starting Automated Article Generation and Deployment ==="
    log "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Check system requirements
    check_requirements
    
    # Cleanup old logs
    cleanup_logs
    
    # Create backup
    backup_articles
    
    # Generate articles
    local articles_generated=0
    
    # Generate 2 articles from keywords
    if generate_keyword_articles 2; then
        articles_generated=$((articles_generated + 2))
    fi
    
    # Generate 2 articles from trends
    if generate_trend_articles 2; then
        articles_generated=$((articles_generated + 2))
    fi
    
    if [[ $articles_generated -eq 0 ]]; then
        log_warning "No articles were generated. Skipping website generation and deployment."
        send_notification "No new articles generated in this cycle."
        return 1
    fi
    
    log "Generated $articles_generated new articles"
    
    # Generate website if articles were created
    if generate_website; then
        # Upload to hosting - COMMENTED OUT FOR MANUAL DEPLOYMENT
        # if upload_to_hostinger; then
        #     log_success "=== Automated publishing completed successfully ==="
        #     send_notification "Successfully published $articles_generated new articles and deployed website."
        # else
        #     log_error "Deployment failed"
        #     send_notification "Article generation succeeded but deployment failed."
        #     return 1
        # fi
        
        log_success "=== Article generation and site building completed successfully ==="
        log "Website files are ready in the 'dist' directory for manual deployment"
        send_notification "Successfully generated $articles_generated new articles and built website. Ready for manual deployment."
    else
        log_error "Website generation failed"
        send_notification "Article generation succeeded but website generation failed."
        return 1
    fi
    
    log "=== Process completed at $(date '+%Y-%m-%d %H:%M:%S') ==="
}

# Trap to handle script interruption
trap 'log "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"
