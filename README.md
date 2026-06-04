# Country's News — Article Generation & Publishing System

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

An automated Python system that generates SEO-optimised news articles using LLMs, builds a static website, and syncs it to a production FTP server — all from a single daily script.

---

## 📁 Project Structure

```
articleGen/
├── super_article_manager.py    # Core CLI — article generation, enhancement, categorisation
├── generateSite_advanced.py    # Static site generator (differential mode)
├── customRSync.py              # FTP sync (differential, fast)
├── auto_publish.sh             # Daily automation script (runs everything)
├── generateDifferentialManifest.py  # Computes files changed since last sync
├── generateImage.py            # Image generation (Pollinations → Gemini fallback)
├── fetch_ai_keywords.py        # Auto-fetches trending AI keywords from the web
├── fetch_fresh_trends.py       # Refreshes Google Trends data for next run
├── custom_keywords.txt         # Your custom keywords (edit this!)
├── perplexityArticles_eeat_enhanced.json  # Master article store
├── requirements.txt
├── .env                        # API keys and FTP credentials
│
├── dist/                       # Generated static site (deployed to server)
│   ├── index.html
│   ├── articles/
│   ├── categories/
│   ├── images/
│   ├── sitemap.xml
│   ├── robots.txt
│   └── rss.xml
│
├── images/                     # Article images (WebP, generated locally)
├── backups/                    # Automatic article JSON backups
└── logs/                       # Daily run logs
```

---

## ⚙️ Setup

### Prerequisites

- Python 3.13+
- FTP-accessible web host (e.g. Hostinger)

### Installation

```bash
git clone https://github.com/santoshjammi/articleGen.git
cd articleGen
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root with:

```env
# LLM (required)
OPENROUTER_API_KEY=your_key
LLM_MODEL=google/gemma-4-26b-a4b-it

# Image generation (optional — falls back to Pollinations.ai for free)
GEM_API_KEY=your_gemini_key
GEMINI_API_KEY=your_gemini_key

# FTP deployment (required for auto_publish)
FTP_HOST=your.ftp.host
FTP_USER=your_ftp_user
FTP_PASS=your_ftp_password
FTP_PORT=21
REMOTE_DIRECTORY=/public_html
LOCAL_DIRECTORY=/path/to/articleGen/dist
```

---

## 🚀 Automated Publishing: `auto_publish.sh`

This is the main production script. Run it daily (or via cron) to generate articles, build the site, and push everything to your server.

```bash
bash auto_publish.sh
```

### What It Does (in order)

| Step | Action |
|------|--------|
| 1 | Generates 10 trend-based articles from today's top Google Trends |
| 1.5a | Auto-fetches new AI keywords from the internet → `custom_keywords.txt` |
| 1.5b | Generates 5 articles per keyword in `custom_keywords.txt` (with images) |
| 1.6 | Fills any missing images (retries up to 3×) |
| 2 | Refreshes trend data for tomorrow's run |
| 2.4 | Rebuilds the static site (differential — only changed pages) |
| 2.5 | Computes the differential sync manifest (which files changed) |
| 3 | Uploads only changed files to the FTP server |

Logs are written to `logs/auto_publish_YYYYMMDD.log`.

### How to Provide Your Own Keywords

Edit `custom_keywords.txt` in the project root. One keyword per line. Lines starting with `#` are ignored.

```
# custom_keywords.txt
AI inference
India digital transformation
Battery Tech Evolution
electric vehicles india 2026
```

These are picked up automatically on the next `auto_publish.sh` run. To run immediately:

```bash
python super_article_manager.py generate keywords "AI inference" "Battery Tech" \
  --region India --count 5 --no-skip
```

### Configuration

| Variable | Location | Default | Effect |
|----------|----------|---------|--------|
| `DEFAULT_CUSTOM_REGION` | `auto_publish.sh` line 63 | `US` | Region for keyword articles |
| `--count 5` | `auto_publish.sh` line 105 | 5 | Articles generated per keyword |

---

## 🛠️ `super_article_manager.py` — CLI Reference

All article operations go through this script.

### Generate Articles

```bash
# From today's trending topics
python super_article_manager.py generate trends --count 10

# From specific keywords (5 distinct articles each, India focus, with images)
python super_article_manager.py generate keywords "AI inference" "Smart Mobility" \
  --region India --count 5 --no-skip

# From keyword batches defined in keyword_config.json
python super_article_manager.py generate batch technology health

# Interactive prompt
python super_article_manager.py generate interactive
```

**`generate keywords` flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--region` | `India` | Target region (India, USA, UK, Canada, Australia) |
| `--count` | `1` | Number of differentiated articles per keyword |
| `--no-skip` | off | Generate even if keyword was already processed |
| `--skip-images` | off | Use placeholder images instead of generating real ones (faster for testing) |

**`generate trends` flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--count` | `3` | Number of trending keywords to process |
| `--regions` | auto | Filter to specific regions |
| `--per-region` | off | Get top N from each region separately |

### Enhance Articles

```bash
python super_article_manager.py enhance --all            # All operations
python super_article_manager.py enhance --deduplicate    # Remove duplicates
python super_article_manager.py enhance --fix-issues     # Fix IDs, titles, metadata
python super_article_manager.py enhance --merge-legacy   # Import from legacy articles.json
python super_article_manager.py enhance --headers-only   # Re-enhance headers only (fast)
```

### Generate / Fix Images

```bash
# Generate missing images for all articles
python super_article_manager.py images

# Regenerate images for a specific article
python super_article_manager.py images --articles my-article-slug --regenerate

# Only generate main + thumbnail (skip inline)
python super_article_manager.py images --type main
```

### Statistics

```bash
python super_article_manager.py stats
```

### Backup Images

```bash
python super_article_manager.py backup --images
```

### Workflow Shortcuts

```bash
python super_article_manager.py workflow --complete        # Deduplicate + fix + enhance
python super_article_manager.py workflow --generate-first  # Generate then run complete workflow
```

### AI Categorisation

```bash
python super_article_manager.py categorize test --count 10   # Test on 10 articles
python super_article_manager.py categorize all               # Recategorise all
python super_article_manager.py categorize stats             # Show category breakdown
```

---

## 🌐 Site Generation

The static site is built by `generateSite_advanced.py`. It runs in differential mode by default: only pages that changed since the last run are regenerated.

```bash
python generateSite_advanced.py
```

Output goes to `dist/`. Includes:
- Article pages (`dist/articles/<slug>/index.html`)
- Category pages (`dist/categories/`)
- Tag pages (`dist/tags/`)
- Homepage with lazy-loading article grid
- `sitemap.xml`, `robots.txt`, `rss.xml`

---

## 📤 FTP Sync

`customRSync.py` uploads only the files listed in `dist/.differential_sync.json` (generated by the previous step), skipping unchanged content.

```bash
python customRSync.py
```

Typical sync time: ~12 seconds for a batch of 30 changed files.

---

## 🖼️ Image Generation

Images are generated in `generateImage.py` with this fallback chain:

1. **Pollinations.ai** — free, no API key required
2. **Gemini Imagen 4** — requires `GEM_API_KEY` (paid tier)
3. **Gemini 2.5 Flash** — multimodal fallback
4. **Placeholder URL** — if all fail, a placeholder is used and no article is blocked

Images are saved as `.webp` in `images/<article-slug>/`.

---

## 🔒 Backup System

Every operation that modifies articles automatically creates a timestamped backup:

```
backups/perplexityArticles_backup_YYYYMMDD_HHMMSS.json
```

Only the last 10 backups are kept. To restore, copy any backup file over `perplexityArticles_eeat_enhanced.json`.

---

## 🔐 Security

- API keys and FTP credentials live in `.env` only (never committed)
- Static site has no server-side execution surface
- XSS: all article content is sanitised before rendering

---

## 📊 Live Site

**[countrysnews.com](https://countrysnews.com)**

---

*Last updated: May 2026*
