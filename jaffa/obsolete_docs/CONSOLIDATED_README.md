# Consolidated Article Generation System

A unified, powerful article generation system that combines all previous functionality into a single, easy-to-use module.

## 🌟 Features

- **🔥 Trend-Based Generation** - Auto-generate from trending keywords
- **🎯 Keyword-Based Generation** - Create articles from specific keywords  
- **📦 Batch Processing** - Process multiple keywords in organized batches
- **🤖 Interactive Mode** - User-friendly guided article creation
- **📊 Statistics & Analytics** - Track your content generation
- **🔗 SEO Optimization** - Built-in SEO best practices
- **🖼️ Image Generation** - AI-generated images for all articles
- **🔄 Smart Deduplication** - Avoid duplicate content automatically

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd articleGen

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### Basic Usage

```bash
# Generate articles from trending keywords
python article_generator.py trends

# Generate from specific keywords
python article_generator.py keywords "artificial intelligence" "machine learning"

# Interactive mode (recommended for beginners)
python article_generator.py interactive

# Process keyword batches
python article_generator.py batch technology health

# View statistics
python article_generator.py stats
```

## 📖 Detailed Usage

### 1. Trend-Based Generation

Generate articles from currently trending keywords:

```bash
# Generate from top 3 trending keywords (default)
python article_generator.py trends

# Generate from top 10 trending keywords
python article_generator.py trends --count 10

# Use specific articles file
python article_generator.py trends --file "my_articles.json"
```

### 2. Keyword-Based Generation

Create articles from your own keywords:

```bash
# Basic keyword generation
python article_generator.py keywords "keyword1" "keyword2" "keyword3"

# With custom region
python article_generator.py keywords --region "USA" "stock market" "cryptocurrency"

# With custom instructions
python article_generator.py keywords --prompt "Focus on business applications" "AI technology"

# Force regeneration (skip duplicate check)
python article_generator.py keywords --no-skip "existing keyword"
```

### 3. Batch Processing

Process organized keyword categories:

```bash
# List available batches
python article_generator.py batch

# Process specific batches
python article_generator.py batch technology health business

# Use custom configuration
python article_generator.py batch --config "my_config.json" technology
```

### 4. Interactive Mode

Perfect for beginners or one-off articles:

```bash
python article_generator.py interactive
```

This will guide you through:
- Entering keywords one by one
- Selecting target region
- Adding custom instructions

### 5. Statistics & Monitoring

```bash
# View article statistics
python article_generator.py stats

# Check specific file
python article_generator.py stats --file "custom_articles.json"
```

## ⚙️ Configuration

### Keyword Batches (`keyword_config.json`)

```json
{
    "default_settings": {
        "region": "India",
        "language": "en-IN",
        "skip_existing": true,
        "max_articles_per_batch": 10
    },
    "keyword_batches": {
        "technology": [
            "artificial intelligence",
            "machine learning", 
            "blockchain technology",
            "cybersecurity",
            "5G technology"
        ],
        "business": [
            "startup funding",
            "digital marketing",
            "e-commerce trends",
            "stock market analysis"
        ],
        "health": [
            "mental health awareness",
            "fitness trends",
            "nutrition science",
            "medical breakthroughs"
        ]
    },
    "custom_prompts": {
        "technology": "Focus on practical applications and business impact",
        "health": "Emphasize evidence-based information and expert opinions"
    }
}
```

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
DEFAULT_REGION=India
DEFAULT_LANGUAGE=en-IN
```

## 📊 Output Format

Generated articles include:

```json
{
    "id": "unique_id",
    "slug": "url-friendly-slug", 
    "title": "SEO-optimized title",
    "content": "Full HTML content with embedded images",
    "metaDescription": "SEO meta description",
    "keywords": ["expanded", "keyword", "list"],
    "ogImage": "main_image_url",
    "thumbnailImageUrl": "thumbnail_url",
    "inlineImages": [
        {
            "url": "image_url",
            "alt": "alt_text",
            "caption": "image_caption",
            "placementHint": "after paragraph 3"
        }
    ],
    "keyTakeaways": ["key", "points", "from", "article"],
    "socialMediaHashtags": ["#relevant", "#hashtags"],
    "callToActionText": "Engaging CTA text",
    "structuredData": "JSON-LD schema markup",
    "sourceKeyword": "original_keyword",
    "generationMethod": "keyword_based|trend_based",
    "region": "target_region",
    "readingTimeMinutes": 8,
    "wordCount": 1500,
    "publishDate": "2025-01-05"
}
```

## 🔄 Migration from Old System

If you're upgrading from the old multi-file system:

```bash
# Run the migration script
python migrate_to_consolidated.py
```

This will:
- ✅ Backup your old files safely
- ✅ Merge article data from all sources
- ✅ Create backward-compatible wrappers
- ✅ Generate a detailed migration report

### Old vs New Commands

| Old Command | New Command |
|-------------|-------------|
| `python generateArticles.py` | `python article_generator.py trends` |
| `python perplexitySEOArticleGen.py` | `python article_generator.py trends` |
| `python quickKeywordGen.py "keyword"` | `python article_generator.py keywords "keyword"` |
| `python quickKeywordGen.py --interactive` | `python article_generator.py interactive` |
| `python batchKeywordGen.py` | `python article_generator.py batch` |
| `python keywordBasedArticleGen.py` | `python article_generator.py keywords` |

## 🎯 Advanced Features

### Custom Prompts

Tailor content generation to your needs:

```bash
python article_generator.py keywords \
  --prompt "Write from a technical perspective for developers" \
  "API design" "microservices"
```

### Regional Targeting  

Generate region-specific content:

```bash
python article_generator.py keywords \
  --region "Australia" \
  "renewable energy" "climate policy"
```

### Batch Customization

Create your own keyword batches:

```json
{
    "keyword_batches": {
        "my_niche": [
            "specific keyword 1",
            "specific keyword 2"
        ]
    },
    "custom_prompts": {
        "my_niche": "Focus on practical tips and case studies"
    }
}
```

## 🛠️ Integration

### Programmatic Usage

```python
from article_generator import generate_articles_from_keywords
import asyncio

async def generate_my_content():
    await generate_articles_from_keywords(
        keywords=["AI in healthcare", "telemedicine"],
        region="India",
        custom_prompt="Focus on recent developments",
        skip_existing=True
    )

asyncio.run(generate_my_content())
```

### Workflow Integration

```bash
#!/bin/bash
# Complete content workflow

# 1. Generate trend-based articles
python article_generator.py trends --count 5

# 2. Generate keyword-based articles  
python article_generator.py batch technology health

# 3. Run deduplication
python workflow_deduplication.py

# 4. Generate website
python generateSite.py
```

## 📈 Best Practices

### Keyword Selection
- **Be specific**: "machine learning in healthcare" vs "technology"
- **Target your audience**: Consider who will read your articles
- **Stay current**: Choose trending or newsworthy topics
- **Optimal length**: 1-4 words work best

### Batch Processing
- **Start small**: Try 3-5 keywords first
- **Quality over quantity**: Better fewer high-quality articles
- **Use custom prompts**: Tailor content to your brand voice
- **Monitor progress**: Use `stats` command to track growth

### Content Optimization
- **Regional relevance**: Specify target region for local content
- **Custom instructions**: Use prompts to guide content style
- **SEO keywords**: System automatically expands keywords
- **Internal linking**: Automatic links to related articles

## 🚨 Troubleshooting

### Common Issues

**"No trending keywords found"**
- Check your internet connection
- Verify API credentials
- Try `python getTrendInput.py` directly

**"API error 400/403"** 
- Verify GEMINI_API_KEY is set correctly
- Check API quota/billing
- Ensure API key has necessary permissions

**"No articles generated"**
- Check if keywords already exist (use `--no-skip`)
- Verify keyword_config.json format
- Try interactive mode first

**Image generation fails**
- Images will fallback to placeholders
- Check generateImage.py functionality
- Ensure image directory permissions

### Getting Help

1. **Check stats**: `python article_generator.py stats`
2. **Try interactive mode**: `python article_generator.py interactive`
3. **Review logs**: Look for specific error messages
4. **Test components**: Try individual functions

## 📚 Examples

### Example 1: Tech Blog Content
```bash
# Generate tech articles
python article_generator.py keywords --region "India" \
  "artificial intelligence" "machine learning" "blockchain technology"

# Process and publish
python workflow_deduplication.py
python generateSite.py
```

### Example 2: News Site Content
```bash
# Use trending keywords
python article_generator.py trends --count 10

# Add custom content
python article_generator.py keywords --prompt "Focus on breaking news style" \
  "current events" "policy changes"
```

### Example 3: Niche Content
```bash
# Create custom batch
python article_generator.py batch --config "niche_config.json" specialty

# Interactive refinement
python article_generator.py interactive
```

## 🎉 What's New

### Consolidated Benefits
- ✅ **Single entry point** - One script for all generation
- ✅ **Consistent interface** - Unified command structure  
- ✅ **Better error handling** - Improved messages and recovery
- ✅ **Enhanced features** - Best features from all old scripts
- ✅ **Easier maintenance** - One codebase instead of five

### New Features
- 🆕 **Statistics dashboard** - Track your content generation
- 🆕 **Enhanced batch processing** - More flexible batch management
- 🆕 **Improved error recovery** - Better handling of API failures
- 🆕 **Unified configuration** - Single config for all methods
- 🆕 **Migration support** - Smooth transition from old system

---

**Ready to start generating amazing content? Try:**
```bash
python article_generator.py interactive
```

For questions or issues, check the code in `article_generator.py` or run with `--help` for detailed options.
