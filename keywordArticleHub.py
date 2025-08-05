#!/usr/bin/env python3
"""
Keyword Article Generator - Main Interface
Central hub for all keyword-based article generation functionality.
"""

import os
import sys
import json
import asyncio
from datetime import datetime

def display_banner():
    """Display the main banner"""
    print("\n" + "="*70)
    print("🎯 KEYWORD-BASED ARTICLE GENERATION SYSTEM")
    print("="*70)
    print("Generate high-quality, SEO-optimized articles from specific keywords")
    print()

def display_main_menu():
    """Display the main menu options"""
    print("📋 Choose your generation method:")
    print()
    print("1. 🚀 Quick Generation (Interactive)")
    print("   → Enter keywords manually, perfect for specific topics")
    print()
    print("2. 📦 Batch Processing")
    print("   → Use predefined keyword categories (tech, business, health, etc.)")
    print()
    print("3. ⚡ Command Line Mode")
    print("   → Direct keyword input for automation")
    print()
    print("4. 📊 View Statistics")
    print("   → See existing articles and keyword usage")
    print()
    print("5. ⚙️ Configuration")
    print("   → Manage settings and keyword batches")
    print()
    print("6. 📚 Help & Examples")
    print("   → Usage guides and keyword examples")
    print()
    print("7. 🔄 Integration Tools")
    print("   → Connect with existing workflow")
    print()
    print("8. ❌ Exit")
    print()

def show_statistics():
    """Show article statistics"""
    try:
        if not os.path.exists("perplexityArticles.json"):
            print("❌ No articles file found!")
            return
            
        with open("perplexityArticles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        # Basic stats
        total_articles = len(articles)
        keyword_based = len([a for a in articles if a.get("generationMethod") == "keyword_based"])
        trend_based = total_articles - keyword_based
        
        # Keyword analysis
        source_keywords = set()
        categories = {}
        recent_articles = 0
        today = datetime.now().strftime("%Y-%m-%d")
        
        for article in articles:
            if article.get("sourceKeyword"):
                source_keywords.add(article["sourceKeyword"])
            if article.get("category"):
                cat = article["category"]
                categories[cat] = categories.get(cat, 0) + 1
            if article.get("publishDate") == today:
                recent_articles += 1
        
        print("\n📊 ARTICLE STATISTICS")
        print("-" * 50)
        print(f"📰 Total Articles: {total_articles}")
        print(f"🎯 Keyword-based: {keyword_based}")
        print(f"📈 Trend-based: {trend_based}")
        print(f"🔑 Unique Keywords: {len(source_keywords)}")
        print(f"📅 Generated Today: {recent_articles}")
        print()
        
        if categories:
            print("📂 Categories:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   • {cat}: {count} articles")
        
        if source_keywords:
            print(f"\n🔍 Recent Keywords:")
            recent_keywords = list(source_keywords)[-10:]
            for keyword in recent_keywords:
                print(f"   • {keyword}")
                
    except Exception as e:
        print(f"❌ Error reading statistics: {e}")

def show_configuration():
    """Show and manage configuration"""
    print("\n⚙️ CONFIGURATION MANAGEMENT")
    print("-" * 40)
    
    if os.path.exists("keyword_config.json"):
        try:
            with open("keyword_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("✅ Configuration file found")
            print(f"🌍 Default region: {config['default_settings']['region']}")
            print(f"📦 Keyword batches: {len(config['keyword_batches'])}")
            print(f"✍️  Custom prompts: {len(config['custom_prompts'])}")
            
            print("\n📦 Available batches:")
            for batch_name, keywords in config["keyword_batches"].items():
                print(f"   • {batch_name}: {len(keywords)} keywords")
                
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")
    else:
        print("❌ Configuration file not found!")
        create_config = input("Create default configuration? (Y/n): ").strip().lower()
        if create_config in ['', 'y', 'yes']:
            print("Creating default configuration...")
            os.system("python -c \"import json; print('Config creation would go here')\"")

def show_help_menu():
    """Show help and examples submenu"""
    print("\n📚 HELP & EXAMPLES")
    print("-" * 30)
    print("1. View keyword examples by category")
    print("2. Show usage examples")
    print("3. View complete documentation")
    print("4. Troubleshooting guide")
    print("5. Back to main menu")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        os.system("python quickKeywordGen.py --list-examples")
    elif choice == "2":
        show_usage_examples()
    elif choice == "3":
        show_documentation()
    elif choice == "4":
        show_troubleshooting()
    elif choice == "5":
        return
    else:
        print("❌ Invalid choice")

def show_usage_examples():
    """Show usage examples"""
    print("\n💡 USAGE EXAMPLES")
    print("-" * 40)
    print()
    print("🚀 Quick Interactive Generation:")
    print("   python quickKeywordGen.py --interactive")
    print()
    print("⚡ Command Line Generation:")
    print("   python quickKeywordGen.py \"AI technology\" \"machine learning\"")
    print()
    print("🌍 Custom Region:")
    print("   python quickKeywordGen.py --region \"USA\" \"stock market\"")
    print()
    print("✍️  Custom Instructions:")
    print("   python quickKeywordGen.py --prompt \"Focus on recent news\" \"cryptocurrency\"")
    print()
    print("📦 Batch Processing:")
    print("   python batchKeywordGen.py technology business")
    print()
    print("🔄 Integration with Workflow:")
    print("   python quickKeywordGen.py \"my keywords\"")
    print("   python workflow_deduplication.py")
    print("   python generateSite.py")

def show_documentation():
    """Show documentation file"""
    if os.path.exists("KEYWORD_GENERATION_GUIDE.md"):
        print("\n📖 Opening complete documentation...")
        print("File: KEYWORD_GENERATION_GUIDE.md")
        print("\nWould you like to:")
        print("1. View in terminal (basic)")
        print("2. Open in default editor")
        print("3. Just show file path")
        
        choice = input("Choice (1-3): ").strip()
        if choice == "1":
            os.system("head -50 KEYWORD_GENERATION_GUIDE.md")
        elif choice == "2":
            os.system("open KEYWORD_GENERATION_GUIDE.md")
        elif choice == "3":
            print(f"📄 Documentation: {os.path.abspath('KEYWORD_GENERATION_GUIDE.md')}")
    else:
        print("❌ Documentation file not found!")

def show_troubleshooting():
    """Show troubleshooting guide"""
    print("\n🆘 TROUBLESHOOTING GUIDE")
    print("-" * 40)
    print()
    print("❌ Common Issues:")
    print()
    print("1. 'GEMINI_API_KEY not found'")
    print("   → Check your .env file")
    print("   → Ensure API key is valid and active")
    print()
    print("2. 'No keywords provided'")
    print("   → Use: python quickKeywordGen.py --interactive")
    print("   → Or provide keywords as arguments")
    print()
    print("3. 'Articles not generating'")
    print("   → Check internet connection")
    print("   → Verify API quota/limits")
    print("   → Try with fewer keywords")
    print()
    print("4. 'Module not found errors'")
    print("   → Install requirements: pip install -r requirements.txt")
    print("   → Check Python environment")
    print()
    print("📞 Need more help?")
    print("   → Check KEYWORD_GENERATION_GUIDE.md")
    print("   → Review error messages carefully")
    print("   → Test with simple examples first")

def integration_tools():
    """Show integration tools menu"""
    print("\n🔄 INTEGRATION TOOLS")
    print("-" * 30)
    print("1. Run complete workflow (keywords → deduplication → site)")
    print("2. Check keyword compatibility with existing articles")
    print("3. Backup current articles before generation")
    print("4. Merge keyword articles with existing content")
    print("5. Back to main menu")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        run_complete_workflow()
    elif choice == "2":
        check_keyword_compatibility()
    elif choice == "3":
        backup_articles()
    elif choice == "4":
        print("Merge functionality integrated automatically")
    elif choice == "5":
        return
    else:
        print("❌ Invalid choice")

def run_complete_workflow():
    """Run the complete workflow"""
    print("\n🔄 COMPLETE WORKFLOW")
    print("-" * 30)
    
    keywords = input("Enter keywords (space-separated): ").strip().split()
    if not keywords:
        print("❌ No keywords provided!")
        return
    
    region = input("Target region (default: India): ").strip() or "India"
    
    print(f"\n🚀 Starting complete workflow...")
    print(f"📝 Keywords: {', '.join(keywords)}")
    print(f"🌍 Region: {region}")
    print()
    
    # Build command
    keyword_args = ' '.join([f'"{k}"' for k in keywords])
    commands = [
        f'python quickKeywordGen.py --region "{region}" {keyword_args}',
        'python workflow_deduplication.py',
        'python generateSite.py'
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"Step {i}/3: {cmd}")
        confirm = input("Continue? (Y/n): ").strip().lower()
        if confirm not in ['', 'y', 'yes']:
            print("Workflow stopped.")
            return
        os.system(cmd)
        print()

def check_keyword_compatibility():
    """Check keyword compatibility"""
    print("\n🔍 KEYWORD COMPATIBILITY CHECK")
    print("-" * 40)
    
    if not os.path.exists("perplexityArticles.json"):
        print("✅ No existing articles - all keywords are compatible")
        return
    
    try:
        with open("perplexityArticles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        existing_keywords = set()
        for article in articles:
            if article.get("sourceKeyword"):
                existing_keywords.add(article["sourceKeyword"].lower())
        
        print(f"📊 Found {len(existing_keywords)} existing keywords")
        
        test_keywords = input("\nEnter keywords to check (space-separated): ").strip().split()
        if not test_keywords:
            return
        
        print("\n🔍 Compatibility Results:")
        for keyword in test_keywords:
            if keyword.lower() in existing_keywords:
                print(f"   ⚠️  '{keyword}' - Already exists (will be skipped)")
            else:
                print(f"   ✅ '{keyword}' - New keyword (will be generated)")
                
    except Exception as e:
        print(f"❌ Error checking compatibility: {e}")

def backup_articles():
    """Create backup of articles"""
    if not os.path.exists("perplexityArticles.json"):
        print("❌ No articles file to backup!")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"perplexityArticles_backup_{timestamp}.json"
    
    try:
        os.system(f"cp perplexityArticles.json {backup_name}")
        print(f"✅ Backup created: {backup_name}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

async def main():
    """Main interactive interface"""
    display_banner()
    
    while True:
        display_main_menu()
        choice = input("Select option (1-8): ").strip()
        
        if choice == "1":
            # Quick Generation
            print("\n🚀 Starting interactive generation...")
            os.system("python quickKeywordGen.py --interactive")
            
        elif choice == "2":
            # Batch Processing
            print("\n📦 Starting batch processing...")
            os.system("python batchKeywordGen.py")
            
        elif choice == "3":
            # Command Line Mode
            keywords = input("\n⚡ Enter keywords (space-separated): ").strip()
            if keywords:
                region = input("Target region (default: India): ").strip() or "India"
                keyword_list = ' '.join([f'"{k}"' for k in keywords.split()])
                os.system(f'python quickKeywordGen.py --region "{region}" {keyword_list}')
            else:
                print("❌ No keywords provided!")
                
        elif choice == "4":
            # Statistics
            show_statistics()
            
        elif choice == "5":
            # Configuration
            show_configuration()
            
        elif choice == "6":
            # Help & Examples
            show_help_menu()
            
        elif choice == "7":
            # Integration Tools
            integration_tools()
            
        elif choice == "8":
            # Exit
            print("\n👋 Thank you for using the Keyword Article Generator!")
            print("Generated articles are saved to perplexityArticles.json")
            print("Run 'python generateSite.py' to build your website.")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-8.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your setup and try again.")
