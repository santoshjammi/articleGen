#!/usr/bin/env python3
"""
Keyword Article Generation System - Summary and Quick Start
This script provides an overview of the keyword-based article generation system.
"""

import os
import sys

def show_system_overview():
    """Show overview of the entire system"""
    print("🎯 KEYWORD-BASED ARTICLE GENERATION SYSTEM")
    print("=" * 60)
    print()
    print("This system extends your existing article generation capabilities")
    print("by allowing you to create articles from specific keywords instead")
    print("of just trending topics.")
    print()
    
    # Check files
    files_status = {
        "keywordBasedArticleGen.py": "Core article generation engine",
        "quickKeywordGen.py": "Simple command-line interface",
        "batchKeywordGen.py": "Batch processing with predefined keywords",
        "keywordArticleHub.py": "Interactive main interface",
        "keyword_config.json": "Configuration and keyword batches",
        "KEYWORD_GENERATION_GUIDE.md": "Complete documentation"
    }
    
    print("📁 SYSTEM FILES:")
    print("-" * 30)
    for filename, description in files_status.items():
        status = "✅" if os.path.exists(filename) else "❌"
        print(f"{status} {filename}")
        print(f"   {description}")
        print()

def show_quick_start():
    """Show quick start instructions"""
    print("🚀 QUICK START GUIDE")
    print("-" * 30)
    print()
    print("1. 🎬 Interactive Mode (Easiest):")
    print("   python3 keywordArticleHub.py")
    print("   → Full interactive interface with all options")
    print()
    print("2. ⚡ Quick Generation:")
    print("   python3 quickKeywordGen.py --interactive")
    print("   → Simple keyword input and generation")
    print()
    print("3. 📦 Batch Processing:")
    print("   python3 batchKeywordGen.py")
    print("   → Process predefined keyword categories")
    print()
    print("4. 🖥️  Command Line:")
    print("   python3 quickKeywordGen.py \"keyword1\" \"keyword2\"")
    print("   → Direct keyword input")
    print()

def show_features():
    """Show key features"""
    print("✨ KEY FEATURES")
    print("-" * 20)
    print()
    print("🎯 Targeted Content Creation")
    print("   → Generate articles for specific keywords you choose")
    print("   → Perfect for covering particular topics or trends")
    print()
    print("🔍 Smart SEO Optimization")
    print("   → Automatic keyword expansion and integration")
    print("   → Meta descriptions, structured data, internal linking")
    print()
    print("🖼️  Professional Images")
    print("   → AI-generated main and inline images")
    print("   → Automatic alt text and captions")
    print()
    print("📦 Batch Processing")
    print("   → Process multiple related keywords efficiently")
    print("   → Predefined categories: tech, business, health, sports")
    print()
    print("🔄 Full Integration")
    print("   → Works with existing perplexityArticles.json")
    print("   → Compatible with generateSite.py and workflow scripts")
    print()
    print("🛡️  Smart Deduplication")
    print("   → Automatically avoids duplicate articles")
    print("   → Tracks processed keywords")
    print()

def show_example_usage():
    """Show example usage scenarios"""
    print("💡 EXAMPLE USAGE SCENARIOS")
    print("-" * 35)
    print()
    print("🏢 Business Blog:")
    print("   Keywords: 'startup funding', 'digital marketing', 'e-commerce trends'")
    print("   Command: python3 quickKeywordGen.py \"startup funding\" \"digital marketing\"")
    print()
    print("🔬 Tech News Site:")
    print("   Keywords: 'artificial intelligence', 'blockchain', 'cybersecurity'")
    print("   Command: python3 batchKeywordGen.py technology")
    print()
    print("🏥 Health & Wellness:")
    print("   Keywords: 'mental health', 'fitness trends', 'nutrition guidelines'")
    print("   Command: python3 batchKeywordGen.py health")
    print()
    print("📈 Financial News:")
    print("   Keywords: 'stock market analysis', 'cryptocurrency', 'investment tips'")
    print("   Command: python3 quickKeywordGen.py --region \"India\" \"stock market\" \"crypto\"")
    print()

def check_prerequisites():
    """Check if system requirements are met"""
    print("✅ PREREQUISITES CHECK")
    print("-" * 25)
    print()
    
    # Check Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"🐍 Python Version: {python_version}")
    if sys.version_info >= (3, 7):
        print("   ✅ Compatible")
    else:
        print("   ❌ Python 3.7+ required")
    print()
    
    # Check .env file
    if os.path.exists(".env"):
        print("🔑 Environment File: ✅ Found")
        # Check if GEMINI_API_KEY exists (without revealing it)
        with open(".env", "r") as f:
            env_content = f.read()
        if "GEMINI_API_KEY" in env_content:
            print("   ✅ GEMINI_API_KEY configured")
        else:
            print("   ⚠️  GEMINI_API_KEY not found in .env")
    else:
        print("🔑 Environment File: ❌ .env file not found")
        print("   Create .env file with your GEMINI_API_KEY")
    print()
    
    # Check requirements.txt
    if os.path.exists("requirements.txt"):
        print("📦 Requirements File: ✅ Found")
    else:
        print("📦 Requirements File: ⚠️  requirements.txt not found")
    print()
    
    # Check existing articles
    if os.path.exists("perplexityArticles.json"):
        print("📰 Articles Database: ✅ Found")
        try:
            import json
            with open("perplexityArticles.json", "r") as f:
                articles = json.load(f)
            print(f"   📊 {len(articles)} existing articles")
        except:
            print("   ⚠️  Error reading articles file")
    else:
        print("📰 Articles Database: ℹ️  Will be created on first use")
    print()

def main():
    """Main function"""
    print("\n" + "=" * 70)
    show_system_overview()
    print("\n" + "=" * 70)
    check_prerequisites()
    print("\n" + "=" * 70)
    show_features()
    print("\n" + "=" * 70)
    show_quick_start()
    print("\n" + "=" * 70)
    show_example_usage()
    print("\n" + "=" * 70)
    
    print("\n🎉 READY TO START!")
    print("-" * 20)
    print("Your keyword-based article generation system is ready!")
    print()
    print("🎬 Start with the interactive interface:")
    print("   python3 keywordArticleHub.py")
    print()
    print("📖 Read the complete guide:")
    print("   KEYWORD_GENERATION_GUIDE.md")
    print()
    print("💡 Need help? Use:")
    print("   python3 quickKeywordGen.py --list-examples")
    print("   python3 quickKeywordGen.py --help")
    print()

if __name__ == "__main__":
    main()
