"""
Configuration file for integrating webapp with existing articleGen system.
This ensures the webapp uses your existing functionality without modification.
"""

import os
from pathlib import Path

# Base directory (where your existing scripts are)
BASE_DIR = Path(__file__).parent

# Existing system integration paths
EXISTING_SCRIPTS = {
    "super_article_manager": BASE_DIR / "super_article_manager.py",
    "generate_local_manifest": BASE_DIR / "generateLocalManifest.py", 
    "ultra_fast_sync": BASE_DIR / "ultraFastSync.py",
    "custom_rsync": BASE_DIR / "customRSync.py",
    "trends_fetcher": BASE_DIR / "trends.py",
    "workflow": BASE_DIR / "workflow.py"
}

# Default website configuration (from your existing system)
DEFAULT_WEBSITE_CONFIG = {
    "url": "https://countrysnews.com",
    "name": "Country's News",
    "author": "News Team",
    "email": "contact@countrysnews.com",
    "description": "Latest news and trending articles from around the world"
}

# Default FTP configuration (update with your actual values)
DEFAULT_FTP_CONFIG = {
    "host": "212.1.209.3",
    "username": "",  # Will be filled by user
    "password": "",  # Will be filled by user
    "remote_directory": "/public_html",
    "max_workers": 20
}

# Content generation defaults (based on your existing system)
DEFAULT_CONTENT_CONFIG = {
    "articles_per_keyword": 3,
    "target_regions": ["US", "IN", "GB", "CA", "AU"],
    "generate_images": True,
    "article_min_length": 800,
    "seo_optimization": True,
    "use_existing_trends": True
}

# Directory structure (matches your existing system)
DIRECTORIES = {
    "output": BASE_DIR / "output",
    "dist": BASE_DIR / "dist", 
    "logs": BASE_DIR / "logs",
    "backups": BASE_DIR / "backups",
    "temp": BASE_DIR / "temp"
}

# Ensure required directories exist
def ensure_directories():
    """Create required directories if they don't exist"""
    for dir_name, dir_path in DIRECTORIES.items():
        dir_path.mkdir(exist_ok=True)

# Integration commands (using your existing scripts)
INTEGRATION_COMMANDS = {
    "generate_trends": [
        "python3", str(EXISTING_SCRIPTS["super_article_manager"]),
        "generate", "trends", "--count", "{count}", "--per-region"
    ],
    "generate_custom": [
        "python3", str(EXISTING_SCRIPTS["super_article_manager"]),
        "generate", "custom", "--keywords-file", "{keywords_file}",
        "--count", "{count}", "--seo-optimized"
    ],
    "generate_images": [
        "python3", str(EXISTING_SCRIPTS["super_article_manager"]), "images"
    ],
    "create_manifest": [
        "python3", str(EXISTING_SCRIPTS["generate_local_manifest"])
    ],
    "sync_ultra_fast": [
        "python3", str(EXISTING_SCRIPTS["ultra_fast_sync"])
    ],
    "sync_custom": [
        "python3", str(EXISTING_SCRIPTS["custom_rsync"])
    ],
    "fetch_trends": [
        "python3", str(EXISTING_SCRIPTS["trends_fetcher"])
    ]
}

# Validation functions
def validate_existing_system():
    """Validate that all required existing scripts are present"""
    missing_scripts = []
    for script_name, script_path in EXISTING_SCRIPTS.items():
        if not script_path.exists():
            missing_scripts.append(f"{script_name}: {script_path}")
    
    if missing_scripts:
        raise FileNotFoundError(
            f"Missing required scripts from existing system:\n" + 
            "\n".join(missing_scripts)
        )
    
    return True

# Environment variables for FTP (used by existing scripts)
def set_ftp_environment(ftp_config):
    """Set environment variables for FTP that existing scripts can use"""
    os.environ.update({
        "FTP_HOST": ftp_config.get("host", ""),
        "FTP_USER": ftp_config.get("username", ""),
        "FTP_PASS": ftp_config.get("password", ""),
        "FTP_REMOTE_DIR": ftp_config.get("remote_directory", "/public_html"),
        "FTP_MAX_WORKERS": str(ftp_config.get("max_workers", 20))
    })

# Security settings
SECURITY_CONFIG = {
    "secret_key": os.getenv("SECRET_KEY", "change-this-in-production"),
    "access_token_expire_minutes": 24 * 60,  # 24 hours
    "bcrypt_rounds": 12
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": DIRECTORIES["logs"] / "webapp.log",
    "max_bytes": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Rate limiting (for production)
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 60,
    "burst_limit": 100
}

if __name__ == "__main__":
    # Test configuration
    print("🔧 Testing webapp configuration...")
    
    try:
        validate_existing_system()
        print("✅ All existing scripts found")
        
        ensure_directories()
        print("✅ Directory structure ready")
        
        print("🎯 Configuration Summary:")
        print(f"   📁 Base directory: {BASE_DIR}")
        print(f"   🌐 Default website: {DEFAULT_WEBSITE_CONFIG['url']}")
        print(f"   📊 Default FTP host: {DEFAULT_FTP_CONFIG['host']}")
        print(f"   📝 Articles per keyword: {DEFAULT_CONTENT_CONFIG['articles_per_keyword']}")
        print("✅ Webapp configuration is ready!")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        exit(1)
