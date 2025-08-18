#!/usr/bin/env python3
"""
Test script to verify remote directory structure verification functionality
"""

import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the verification function
from customRSync import verify_remote_directory

def test_verification():
    """Test the remote directory verification function"""
    
    # Load environment variables
    load_dotenv()
    
    FTP_HOST = os.getenv("FTP_HOST")
    FTP_USER = os.getenv("FTP_USER")
    FTP_PASS = os.getenv("FTP_PASS")
    REMOTE_DIRECTORY = os.getenv("REMOTE_DIRECTORY")
    
    if not all([FTP_HOST, FTP_USER, FTP_PASS, REMOTE_DIRECTORY]):
        print("❌ Error: Missing required environment variables in .env file")
        print("Required: FTP_HOST, FTP_USER, FTP_PASS, REMOTE_DIRECTORY")
        return False
    
    print("🧪 Testing Remote Directory Verification")
    print("=" * 50)
    print(f"FTP Host: {FTP_HOST}")
    print(f"Remote Directory: {REMOTE_DIRECTORY}")
    print("=" * 50)
    
    ftp_credentials = (FTP_HOST, FTP_USER, FTP_PASS)
    
    # Test the verification function
    result = verify_remote_directory(REMOTE_DIRECTORY, ftp_credentials)
    
    if result:
        print("\n✅ Verification test completed successfully!")
        print("The remote directory structure matches requirements.")
    else:
        print("\n❌ Verification test failed or was cancelled.")
        print("Please check your remote directory structure.")
    
    return result

if __name__ == "__main__":
    test_verification()
