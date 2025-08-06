# Automated Article Publishing System - Setup Guide

## Overview
This system automatically runs every hour to:
1. Generate 2 articles from keywords
2. Generate 2 articles from trends
3. Build the website
4. Deploy to Hostinger hosting via FTP

## Prerequisites

### Required Tools
1. **lftp** - FTP client for deployment
   ```bash
   # macOS
   brew install lftp
   
   # Ubuntu/Debian
   sudo apt-get install lftp
   
   # CentOS/RHEL
   sudo yum install lftp
   ```

2. **Python 3** with required packages
   ```bash
   pip install -r requirements.txt
   ```

### Required Files
Ensure these files exist in your project directory:
- `super_article_manager.py` - Main article generation script
- `generateSite.py` - Website generation script
- `keyword_config.json` - Keywords configuration (create if missing)

## Installation Steps

### 1. Configure Environment Variables
Copy the example environment file and configure your settings:
```bash
cp .env.example .env
```

Edit `.env` file with your actual values:
```bash
# Required: Your Gemini API key
GEMINI_API_KEY=your_actual_api_key

# Required: FTP settings for your hosting
FTP_HOST=212.1.209.3
FTP_USER=u237278792.countrysnews.com
FTP_PASS=your_actual_ftp_password
FTP_PORT=21
FTP_REMOTE_DIR=public_html
```

### 2. Make Scripts Executable
```bash
chmod +x auto_publish.sh
chmod +x setup_cron.sh
```

### 3. Create Keywords Configuration (if missing)
If `keyword_config.json` doesn't exist, create it:
```json
{
  "keywords": [
    "technology trends",
    "climate change",
    "artificial intelligence",
    "renewable energy",
    "space exploration",
    "cybersecurity",
    "cryptocurrency",
    "healthcare innovation",
    "sustainable development",
    "digital transformation"
  ]
}
```

### 4. Test the System
Before setting up automation, test manually:
```bash
./auto_publish.sh
```

Check the logs:
```bash
tail -f logs/auto_publish.log
```

### 5. Set Up Cron Job
Run the setup script to configure hourly execution:
```bash
./setup_cron.sh
```

Or manually add to crontab:
```bash
crontab -e
# Add this line:
0 * * * * /Users/kgt/Desktop/Projects/articleGen/auto_publish.sh
```

## Configuration

### Environment Variables
All sensitive configuration is stored in the `.env` file:
- `GEMINI_API_KEY` - Your Gemini API key for article generation
- `FTP_HOST` - FTP server hostname (212.1.209.3)
- `FTP_USER` - FTP username (u237278792.countrysnews.com)
- `FTP_PASS` - FTP password
- `FTP_PORT` - FTP port (default: 21)
- `FTP_REMOTE_DIR` - Remote directory (default: public_html)

### FTP Settings
The script automatically loads FTP settings from `.env`:
- Server: Loaded from `FTP_HOST`
- Username: Loaded from `FTP_USER`
- Password: Loaded from `FTP_PASS`
- Remote directory: Loaded from `FTP_REMOTE_DIR`

### Logging
Logs are stored in:
- `logs/auto_publish.log` - Main log file
- `logs/auto_publish_YYYYMMDD.log` - Daily log files

### Deduplication
The system tracks used keywords and trends:
- `used_keywords.txt` - Keywords used in last 24 hours
- `used_trends.txt` - Trends used in last 24 hours

Files are automatically cleaned every hour to remove entries older than 24 hours.

## Operation

### What Happens Each Hour
1. **Article Generation (10-15 minutes)**
   - 2 articles from unused keywords
   - 2 articles from current trends
   - Deduplication prevents repeating content

2. **Website Build (2-5 minutes)**
   - Regenerates entire website with new articles
   - Updates navigation and indexes

3. **FTP Deployment (5-10 minutes)**
   - Uploads entire Dist folder to hosting
   - Overwrites existing files

### Monitoring
Check system status:
```bash
# View recent logs
tail -50 logs/auto_publish.log

# Check if cron job is running
crontab -l

# View system resources
ps aux | grep auto_publish
```

### Manual Operations
```bash
# Run once manually
./auto_publish.sh

# Generate only keywords articles
python3 super_article_manager.py generate keywords "your keyword"

# Generate only trends articles  
python3 super_article_manager.py generate trends --count 2

# Build website only
python3 generateSite.py

# View help for article manager
python3 super_article_manager.py --help
```

## Troubleshooting

### Common Issues

1. **FTP Connection Failed**
   - Check internet connection
   - Verify FTP credentials
   - Test manual FTP connection: `lftp 212.1.209.3`

2. **Article Generation Failed**
   - Check Python dependencies: `pip install -r requirements.txt`
   - Verify API keys in environment variables
   - Check `keyword_config.json` exists

3. **Website Build Failed**
   - Ensure `generateSite.py` works manually
   - Check for missing article files
   - Verify output directory permissions

4. **Cron Job Not Running**
   - Check cron service: `sudo service cron status` (Linux)
   - Verify crontab entry: `crontab -l`
   - Check system logs: `grep CRON /var/log/syslog`

### Log Analysis
```bash
# View errors only
grep "ERROR" logs/auto_publish.log

# View today's activity
grep "$(date +%Y-%m-%d)" logs/auto_publish.log

# Monitor real-time
tail -f logs/auto_publish.log
```

## Maintenance

### Weekly Tasks
- Review logs for any persistent errors
- Check website deployment status
- Monitor disk space usage

### Monthly Tasks  
- Update keywords in `keyword_config.json`
- Review and archive old log files
- Test backup and recovery procedures

### Backup Strategy
The script automatically creates backups before major operations. Manual backup:
```bash
# Backup articles
cp perplexityArticles.json "perplexityArticles.json.backup.$(date +%Y%m%d_%H%M%S)"

# Backup entire project
tar -czf "articleGen_backup_$(date +%Y%m%d).tar.gz" .
```

## Support
For issues or modifications, check:
1. Log files in `logs/` directory
2. Script configuration in `auto_publish.sh`
3. Python script help: `python3 super_article_manager.py --help`

Remember to test changes in a development environment before applying to production!
