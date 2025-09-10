#!/usr/bin/env python3
"""
Environment Variables Checker for SEO Article Generator
This script helps verify that all required environment variables are properly configured.
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

def check_environment():
    """Check all required environment variables"""
    print(f"{Fore.CYAN}🔍 SEO Article Generator - Environment Check{Style.RESET_ALL}")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Define required variables with their descriptions
    required_vars = {
        "GEM_API_KEY": "Gemini API Key for article generation",
        "LOCAL_DIRECTORY": "Local directory for file operations",
        "FTP_HOST": "FTP server hostname",
        "FTP_USER": "FTP username",
        "FTP_PASS": "FTP password",
        "REMOTE_DIRECTORY": "Remote directory on FTP server"
    }
    
    # Optional variables with defaults
    optional_vars = {
        "FTP_PORT": ("21", "FTP port number"),
        "MAX_WORKERS": ("16", "Maximum parallel workers"),
        "SECRET_KEY": ("Generated", "WebApp secret key"),
        "ENVIRONMENT": ("development", "Environment mode"),
        "FTP_SSL_ENABLED": ("yes", "FTP SSL enabled"),
        "FTP_SSL_VERIFY_CERT": ("no", "FTP SSL certificate verification"),
        "FTP_SSL_FORCE": ("no", "Force FTP SSL")
    }
    
    print(f"\n{Fore.YELLOW}📋 REQUIRED ENVIRONMENT VARIABLES:{Style.RESET_ALL}")
    print("-" * 40)
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Hide sensitive values
            if "PASS" in var or "KEY" in var:
                display_value = "***SET***" if value else "***NOT SET***"
            else:
                display_value = value
            print(f"{Fore.GREEN}✅ {var:<20} = {display_value}{Style.RESET_ALL}")
            print(f"   💡 {description}")
        else:
            print(f"{Fore.RED}❌ {var:<20} = NOT SET{Style.RESET_ALL}")
            print(f"   💡 {description}")
            missing_vars.append(var)
        print()
    
    print(f"\n{Fore.YELLOW}🔧 OPTIONAL ENVIRONMENT VARIABLES:{Style.RESET_ALL}")
    print("-" * 40)
    
    for var, (default, description) in optional_vars.items():
        value = os.getenv(var, default)
        if "PASS" in var or "KEY" in var:
            display_value = "***SET***" if value else "***NOT SET***"
        else:
            display_value = value
        print(f"{Fore.BLUE}ℹ️  {var:<20} = {display_value}{Style.RESET_ALL}")
        print(f"   💡 {description}")
        print()
    
    # Summary
    print("=" * 60)
    if missing_vars:
        print(f"{Fore.RED}❌ CONFIGURATION INCOMPLETE{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Missing required variables:{Style.RESET_ALL}")
        for var in missing_vars:
            print(f"  • {var}")
        print(f"\n{Fore.CYAN}💡 Please update your .env file with the missing values.{Style.RESET_ALL}")
        return False
    else:
        print(f"{Fore.GREEN}✅ ALL REQUIRED VARIABLES CONFIGURED{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚀 Your SEO Article Generator is ready to use!{Style.RESET_ALL}")
        return True

def show_env_template():
    """Show template for .env file"""
    template = """
# =============================================================================
# 🚀 SEO Article Generator - Environment Configuration Template
# =============================================================================

# --- Core Article Generation ---
GEM_API_KEY=your_gemini_api_key_here

# --- Local Directory Configuration ---
LOCAL_DIRECTORY=/Users/kgt/Desktop/Projects/articleGen/output

# --- FTP Configuration ---
FTP_HOST=your-ftp-host.com
FTP_USER=your_ftp_username
FTP_PASS=your_ftp_password
FTP_PORT=21
REMOTE_DIRECTORY=public_html

# --- Optional Settings ---
MAX_WORKERS=16
FTP_SSL_ENABLED=yes
FTP_SSL_VERIFY_CERT=no
FTP_SSL_FORCE=no
    """
    
    print(f"{Fore.CYAN}📝 .env File Template:{Style.RESET_ALL}")
    print(template)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--template":
        show_env_template()
    else:
        success = check_environment()
        sys.exit(0 if success else 1)
