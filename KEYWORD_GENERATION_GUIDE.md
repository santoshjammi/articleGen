# Keyword-Based Article Generation System

This system provides multiple ways to generate high-quality, SEO-optimized articles based on specific keywords you provide. It's designed to complement your existing trend-based article generation system.

## 🚀 Quick Start

### Method 1: Interactive Mode (Easiest)
```bash
python quickKeywordGen.py --interactive
```

### Method 2: Command Line (Fastest)
```bash
python quickKeywordGen.py "artificial intelligence" "machine learning" "blockchain"
```

### Method 3: Batch Processing (Most Efficient)
```bash
python batchKeywordGen.py
```

## 📁 Files Overview

### Core Files
- **`keywordBasedArticleGen.py`** - Main article generation engine
- **`quickKeywordGen.py`** - Simple command-line interface
- **`batchKeywordGen.py`** - Batch processing with predefined keyword sets
- **`keyword_config.json`** - Configuration file with keyword batches and settings

## 🛠️ Detailed Usage

### 1. Quick Keyword Generator (`quickKeywordGen.py`)

The simplest way to generate articles from specific keywords.

#### Interactive Mode
```bash
python quickKeywordGen.py --interactive
```
- Prompts you to enter keywords one by one
- Asks for target region and custom instructions
- Great for beginners or one-off article generation

#### Command Line Mode
```bash
# Basic usage
python quickKeywordGen.py "keyword1" "keyword2" "keyword3"

# With custom region
python quickKeywordGen.py --region "USA" "stock market" "cryptocurrency"

# With custom instructions
python quickKeywordGen.py --prompt "Focus on recent developments" "AI technology"

# Force regeneration (skip duplicate check)
python quickKeywordGen.py --no-skip "existing keyword"
```

#### Get Keyword Ideas
```bash
python quickKeywordGen.py --list-examples
```

### 2. Advanced Article Generator (`keywordBasedArticleGen.py`)

The core engine with full customization options. Can be imported and used programmatically.

```python
from keywordBasedArticleGen import generate_articles_from_keywords
import asyncio

async def generate_my_articles():
    keywords = ["artificial intelligence", "machine learning"]
    await generate_articles_from_keywords(
        keywords=keywords,
        region="India",
        custom_prompt="Focus on business applications",
        skip_existing=True
    )

asyncio.run(generate_my_articles())
```

### 3. Batch Processor (`batchKeywordGen.py`)

Process predefined sets of related keywords efficiently.

#### Interactive Batch Mode
```bash
python batchKeywordGen.py
```

Then choose from:
1. Process a specific batch (e.g., "technology", "business")
2. Process multiple batches (e.g., "technology,health,sports")
3. Process all batches (⚠️ generates many articles)
4. View available custom prompts
5. Exit

#### Command Line Batch Mode
```bash
# Process specific batches
python batchKeywordGen.py technology business
python batchKeywordGen.py health sports entertainment
```

## ⚙️ Configuration (`keyword_config.json`)

### Default Settings
```json
{
    "default_settings": {
        "region": "India",
        "language": "en-IN",
        "skip_existing": true,
        "max_articles_per_batch": 10
    }
}
```

### Keyword Batches
Pre-organized keyword sets by category:
- **Technology**: AI, ML, blockchain, cybersecurity, 5G
- **Business**: startups, stock market, crypto, e-commerce
- **Health**: mental health, fitness, nutrition, medical breakthroughs
- **Sports**: cricket, football, olympics, tennis, basketball
- **Entertainment**: Bollywood, streaming, music, celebrities
- **Science**: space, climate change, renewable energy, discoveries

### Custom Prompts
Ready-to-use prompt templates:
- **news_focus**: Emphasize recent news and breaking developments
- **analysis_focus**: Deep analysis with expert insights and data
- **guide_focus**: Comprehensive how-to content with instructions
- **opinion_focus**: Editorial perspective with multiple viewpoints
- **local_focus**: Regional relevance with local examples

## 🎯 Advanced Features

### 1. Automatic Keyword Expansion
The system automatically expands your base keywords with related terms:
- "AI" → "AI in India", "AI news", "AI trends 2025", "what is AI", etc.

### 2. Smart Deduplication
- Checks existing articles to avoid duplicates
- Can be overridden with `--no-skip` flag
- Uses keyword tracking to prevent regeneration

### 3. SEO Optimization
- Meta descriptions (150-160 chars)
- Optimized titles (50-60 chars)
- Comprehensive keyword integration
- Internal linking to existing articles
- Structured data (JSON-LD)

### 4. Content Enhancement
- 1200+ word articles
- Professional inline images
- Key takeaways
- Social media hashtags
- Call-to-action text
- Reading time estimation

### 5. Image Generation
- AI-generated main images
- Multiple inline images
- Professional, news-appropriate style
- Automatic fallback to placeholder images

## 📊 Output Structure

Generated articles include:
```json
{
    "id": "unique_id",
    "slug": "url-friendly-slug",
    "title": "SEO-optimized title",
    "content": "Full HTML content with images",
    "metaDescription": "SEO description",
    "keywords": ["expanded", "keyword", "list"],
    "ogImage": "main_image_url",
    "inlineImages": [...],
    "keyTakeaways": [...],
    "socialMediaHashtags": [...],
    "sourceKeyword": "original_keyword",
    "generationMethod": "keyword_based",
    "region": "target_region"
}
```

## 🔄 Integration with Existing System

### Compatibility
- Uses same `perplexityArticles.json` file
- Compatible with existing `generateSite.py`
- Follows same article structure and schema
- Integrates with image generation system

### Workflow Integration
```bash
# 1. Generate keyword-based articles
python quickKeywordGen.py "my keywords"

# 2. Run your existing deduplication workflow
python workflow_deduplication.py

# 3. Generate the website
python generateSite.py
```

## 📝 Best Practices

### Keyword Selection
- **Specific is better**: "machine learning in healthcare" vs "technology"
- **Target audience**: Consider who will read your articles
- **Current relevance**: Choose trending or newsworthy topics
- **Length**: 1-4 words work best for keywords

### Batch Processing
- **Start small**: Try 3-5 keywords first
- **Rate limiting**: Built-in delays prevent API overload
- **Quality over quantity**: Better to generate fewer high-quality articles

### Content Customization
- **Use custom prompts**: Tailor content to your needs
- **Regional targeting**: Specify region for local relevance
- **Content type variety**: Mix news, analysis, guides, and opinion pieces

## 🚨 Important Notes

### API Requirements
- Requires `GEMINI_API_KEY` in your `.env` file
- Uses same API as your existing system
- Includes rate limiting and error handling

### File Management
- Creates automatic backups before saving
- Maintains existing article structure
- Handles duplicate prevention automatically

### Resource Usage
- Generates images for each article (can be resource-intensive)
- Processes articles sequentially to manage API usage
- Includes progress indicators and error reporting

## 🆘 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Check your `.env` file
   - Ensure the API key is valid

2. **"No keywords provided"**
   - Use interactive mode: `python quickKeywordGen.py --interactive`
   - Or provide keywords as arguments

3. **Articles not generating**
   - Check internet connection
   - Verify API key has sufficient quota
   - Try with fewer keywords

4. **Duplicate articles**
   - System automatically skips duplicates
   - Use `--no-skip` to force regeneration
   - Check `perplexityArticles.json` for existing content

### Getting Help
```bash
# Show examples
python quickKeywordGen.py --list-examples

# Show help
python quickKeywordGen.py --help
python batchKeywordGen.py --help
```

## 🎉 Example Workflows

### Workflow 1: Tech Blog Content
```bash
# Generate tech articles
python quickKeywordGen.py --region "India" \
  "artificial intelligence" "machine learning" "blockchain technology"

# Process the articles
python workflow_deduplication.py

# Generate website
python generateSite.py
```

### Workflow 2: Business News Site
```bash
# Use batch processing
python batchKeywordGen.py business

# Add custom articles
python quickKeywordGen.py --prompt "Focus on Indian market" \
  "startup funding" "IPO analysis"
```

### Workflow 3: Multi-Category Content
```bash
# Process multiple categories
python batchKeywordGen.py technology health sports business
```

This keyword-based system gives you complete control over your article topics while maintaining the same high quality and SEO optimization as your trend-based system!
