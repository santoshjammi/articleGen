#!/usr/bin/env python3
"""
Quick Keyword Article Generator
Simple command-line utility for generating articles from keywords.

Usage:
    python quickKeywordGen.py "artificial intelligence" "machine learning"
    python quickKeywordGen.py --region "USA" "stock market" "cryptocurrency"
    python quickKeywordGen.py --interactive
"""

import asyncio
import argparse
import sys
from keywordBasedArticleGen import generate_articles_from_keywords

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate articles from specific keywords",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "AI technology" "machine learning"
  %(prog)s --region "USA" --prompt "Focus on recent developments" "blockchain"
  %(prog)s --interactive
  %(prog)s --help
        """
    )
    
    parser.add_argument(
        'keywords',
        nargs='*',
        help='Keywords to generate articles for'
    )
    
    parser.add_argument(
        '--region', '-r',
        default='India',
        help='Target region for articles (default: India)'
    )
    
    parser.add_argument(
        '--prompt', '-p',
        default='',
        help='Custom prompt additions for article generation'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--no-skip',
        action='store_true',
        help='Generate articles even if keyword was processed before'
    )
    
    parser.add_argument(
        '--list-examples',
        action='store_true',
        help='Show keyword examples and exit'
    )
    
    return parser.parse_args()

def show_keyword_examples():
    """Show example keywords by category"""
    examples = {
        "Technology": [
            "artificial intelligence", "machine learning", "blockchain technology",
            "cybersecurity trends", "quantum computing", "5G technology"
        ],
        "Business & Finance": [
            "startup funding", "stock market analysis", "cryptocurrency market",
            "e-commerce trends", "digital marketing", "fintech innovations"
        ],
        "Health & Wellness": [
            "mental health awareness", "fitness trends 2025", "nutrition guidelines",
            "medical breakthroughs", "wellness lifestyle", "preventive healthcare"
        ],
        "Science & Environment": [
            "climate change", "renewable energy", "space exploration",
            "environmental conservation", "scientific discoveries", "green technology"
        ],
        "Sports & Entertainment": [
            "cricket world cup", "football premier league", "bollywood movies",
            "streaming platforms", "music industry", "gaming trends"
        ],
        "Education & Career": [
            "online learning", "skill development", "career guidance",
            "educational technology", "professional development", "job market trends"
        ]
    }
    
    print("\n" + "="*60)
    print("🎯 KEYWORD EXAMPLES BY CATEGORY")
    print("="*60)
    
    for category, keywords in examples.items():
        print(f"\n📂 {category.upper()}:")
        for keyword in keywords:
            print(f"   • {keyword}")
    
    print("\n💡 Tips:")
    print("   • Use specific, targeted keywords for better results")
    print("   • Mix broad and specific keywords for variety")
    print("   • Consider your target audience when choosing keywords")
    print("   • Keywords can be 1-4 words long for best results")

async def interactive_mode():
    """Interactive mode for keyword input"""
    print("\n" + "="*60)
    print("🚀 INTERACTIVE KEYWORD ARTICLE GENERATOR")
    print("="*60)
    
    # Get keywords
    print("\n📝 Enter keywords for article generation:")
    print("   (Type one keyword per line, empty line to finish)")
    
    keywords = []
    while True:
        keyword = input(f"Keyword {len(keywords) + 1}: ").strip()
        if not keyword:
            break
        keywords.append(keyword)
        
        if len(keywords) >= 10:
            continue_adding = input(f"\n⚠️  You've added {len(keywords)} keywords. Add more? (y/N): ").strip().lower()
            if continue_adding != 'y':
                break
    
    if not keywords:
        print("❌ No keywords provided!")
        return
    
    # Get region
    region = input(f"\n🌍 Target region (default: India): ").strip() or "India"
    
    # Get custom prompt
    print(f"\n✍️  Custom instructions (optional):")
    print("   Examples: 'Focus on recent news', 'Include expert opinions', 'Make it beginner-friendly'")
    custom_prompt = input("Instructions: ").strip()
    
    # Confirmation
    print(f"\n📋 Summary:")
    print(f"   Keywords: {len(keywords)} total")
    print(f"   Region: {region}")
    if custom_prompt:
        print(f"   Custom instructions: {custom_prompt}")
    
    confirm = input(f"\n✅ Generate articles for these keywords? (Y/n): ").strip().lower()
    if confirm in ['', 'y', 'yes']:
        await generate_articles_from_keywords(
            keywords=keywords,
            region=region,
            custom_prompt=custom_prompt,
            skip_existing=True  # Default to skip existing
        )
    else:
        print("❌ Operation cancelled.")

async def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Show examples and exit
    if args.list_examples:
        show_keyword_examples()
        return
    
    # Interactive mode
    if args.interactive:
        await interactive_mode()
        return
    
    # Command line mode
    if not args.keywords:
        print("❌ No keywords provided!")
        print("Use --interactive for interactive mode or provide keywords as arguments.")
        print("Use --help for more information.")
        sys.exit(1)
    
    print(f"🚀 Generating articles for {len(args.keywords)} keywords...")
    print(f"🌍 Target region: {args.region}")
    if args.prompt:
        print(f"✍️  Custom instructions: {args.prompt}")
    
    await generate_articles_from_keywords(
        keywords=args.keywords,
        region=args.region,
        custom_prompt=args.prompt,
        skip_existing=not args.no_skip
    )

if __name__ == "__main__":
    asyncio.run(main())
