#!/usr/bin/env python3
"""
Batch Keyword Article Generator
Processes predefined keyword batches from configuration file.
"""

import json
import asyncio
from keywordBasedArticleGen import generate_articles_from_keywords

def load_config(config_file="keyword_config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file '{config_file}' not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing configuration file: {e}")
        return None

def display_available_batches(config):
    """Display available keyword batches"""
    print("\n📦 Available keyword batches:")
    print("-" * 40)
    for category, keywords in config["keyword_batches"].items():
        print(f"🏷️  {category.upper()}: {len(keywords)} keywords")
        print(f"   Keywords: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
        print()

def display_custom_prompts(config):
    """Display available custom prompts"""
    print("\n✍️  Available custom prompts:")
    print("-" * 40)
    for name, prompt in config["custom_prompts"].items():
        print(f"🎯 {name}: {prompt}")
        print()

async def process_batch(batch_name, keywords, config):
    """Process a single keyword batch"""
    settings = config["default_settings"]
    
    print(f"\n🚀 Processing batch: {batch_name.upper()}")
    print(f"📊 Keywords: {len(keywords)}")
    print(f"🌍 Region: {settings['region']}")
    
    # Limit batch size
    max_batch = settings.get("max_articles_per_batch", 10)
    if len(keywords) > max_batch:
        print(f"⚠️  Limiting batch to {max_batch} keywords (from {len(keywords)})")
        keywords = keywords[:max_batch]
    
    await generate_articles_from_keywords(
        keywords=keywords,
        region=settings["region"],
        custom_prompt="",
        skip_existing=settings["skip_existing"]
    )

async def interactive_batch_mode():
    """Interactive mode for batch processing"""
    config = load_config()
    if not config:
        return
    
    print("\n" + "="*60)
    print("📦 BATCH KEYWORD ARTICLE GENERATOR")
    print("="*60)
    
    display_available_batches(config)
    
    while True:
        print("\nOptions:")
        print("1. Process a specific batch")
        print("2. Process multiple batches")
        print("3. Process all batches")
        print("4. View custom prompts")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            # Single batch
            batch_name = input("Enter batch name: ").strip().lower()
            if batch_name in config["keyword_batches"]:
                keywords = config["keyword_batches"][batch_name]
                await process_batch(batch_name, keywords, config)
            else:
                print(f"❌ Batch '{batch_name}' not found!")
                
        elif choice == "2":
            # Multiple batches
            batch_names = input("Enter batch names (comma-separated): ").strip().lower()
            batch_list = [name.strip() for name in batch_names.split(",")]
            
            for batch_name in batch_list:
                if batch_name in config["keyword_batches"]:
                    keywords = config["keyword_batches"][batch_name]
                    await process_batch(batch_name, keywords, config)
                else:
                    print(f"❌ Batch '{batch_name}' not found, skipping...")
                    
        elif choice == "3":
            # All batches
            confirm = input("⚠️  This will process ALL batches. Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                for batch_name, keywords in config["keyword_batches"].items():
                    await process_batch(batch_name, keywords, config)
                    print("⏳ Waiting 30 seconds between batches...")
                    await asyncio.sleep(30)  # Rate limiting
            else:
                print("Operation cancelled.")
                
        elif choice == "4":
            # View prompts
            display_custom_prompts(config)
            
        elif choice == "5":
            # Exit
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

async def command_line_batch_mode(batch_names):
    """Command line mode for batch processing"""
    config = load_config()
    if not config:
        return
    
    for batch_name in batch_names:
        batch_name = batch_name.lower()
        if batch_name in config["keyword_batches"]:
            keywords = config["keyword_batches"][batch_name]
            await process_batch(batch_name, keywords, config)
        else:
            print(f"❌ Batch '{batch_name}' not found!")

async def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode
        batch_names = sys.argv[1:]
        await command_line_batch_mode(batch_names)
    else:
        # Interactive mode
        await interactive_batch_mode()

if __name__ == "__main__":
    asyncio.run(main())
