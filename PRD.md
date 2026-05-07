# Product Requirements Document — articleGen
**"Country's News" — Automated News Site Generation System**

---

## 1. What This Product Is

articleGen is a fully automated news website factory. Given a set of trending keywords or topic batches, it:

1. Pulls live trends from Google
2. Uses an LLM (Gemini / OpenRouter) to write SEO-optimised articles
3. Generates matching images (Gemini, OpenRouter, or Pollinations.ai as fallback)
4. Assembles a static HTML website in `dist/`
5. Syncs the `dist/` folder to a shared-hosting FTP server (Hostinger)
6. Runs the whole pipeline automatically every day at 6 PM IST via cron

There is also a browser-based dashboard (`webapp_main.py`) that lets you trigger ad-hoc article generation and monitor jobs.

The live website is **countrysnews.com**.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       ENTRY POINTS                          │
│                                                             │
│  auto_publish.sh  ←─── cron_wrapper.sh ←─── crontab        │
│  (daily 6 PM IST)                                           │
│                                                             │
│  webapp_main.py (FastAPI, port 8000)  ←─── browser         │
│  workflow_noninteractive.py / workflow.py  ←─── CLI         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PIPELINE ORCHESTRATION LAYER                   │
│                                                             │
│  auto_publish.sh calls these steps in order:               │
│  1. fetch_fresh_trends.py  →  trends.py (Google Trends)     │
│  2. super_article_manager.py generate trends --count 10     │
│  3. (optional) custom_keywords.txt articles                 │
│  4. generateSite_advanced.py                                │
│  5. generateLocalManifest.py  →  generateDifferentialManifest│
│  6. ultraFastSync.py  (FTP upload)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│  TREND DATA  │ │  ARTICLE    │ │  SITE GEN    │
│  output/*.csv│ │  DATA       │ │  dist/       │
│              │ │  perplexity │ │              │
│  trends.py   │ │  Articles_  │ │  generateSite│
│  daily_trend │ │  eeat_      │ │  _advanced.py│
│  _filter.py  │ │  enhanced   │ │              │
│  getTrendIn  │ │  .json      │ │              │
│  put.py      │ │             │ │              │
└──────────────┘ └─────────────┘ └──────────────┘
```

---

## 3. Layer-by-Layer Breakdown

### 3.1 Trend Collection Layer

| File | Role |
|---|---|
| `trends.py` | Calls `trendspy-lite` to pull trending searches for US, IN, AU, CA, GB. Applies SEO filters: global trends must have >100K searches; India's top 15 are always included regardless of volume. Writes `output/*.csv`. |
| `daily_trend_filter.py` | Post-processes raw trend CSVs into `output/daily_filtered_trends.csv` and `output/all_seo_filtered_trends.csv`. |
| `getTrendInput.py` | `get_top_region_keywords()` — reads the filtered CSVs and returns the top-N `(region, keyword, search_volume)` tuples. This is the interface that `super_article_manager.py` calls to get its keyword list. |
| `fetch_fresh_trends.py` | Thin wrapper: just calls `trends.py` as a subprocess and reports which CSVs were updated. Used in the `auto_publish.sh` pipeline and the webapp. |
| `fetch_ai_keywords.py` | Supplementary: fetches AI-specific keyword ideas. |
| `check_trends.py` | CLI debug tool: `python check_trends.py IN 15` prints top 15 India trends. |

**Key design decision:** Trends are cached in CSVs. Article generation reads the cache rather than hitting Google Trends on every run. `fetch_fresh_trends.py` is the explicit "refresh the cache" step.

---

### 3.2 Article Generation & Management Layer (`super_article_manager.py`)

This is the largest file (~2,700+ lines) and the heart of the system. It is a self-contained CLI tool and importable library.

#### 3.2.1 Core data structure

Every article is a JSON object with these key fields:

```json
{
  "id": 42,
  "slug": "ai-in-healthcare-2025",
  "title": "...",
  "content": "<html...>",
  "excerpt": "...",
  "metaDescription": "...",
  "category": "Technology",
  "subcategory": "Artificial Intelligence",
  "tags": ["AI", "healthcare", ...],
  "keywords": ["AI in healthcare", ...],
  "sourceKeyword": "AI healthcare trends",
  "author": "JAMSA - Country's News",
  "publishDate": "2026-05-07",
  "ogImage": "/images/ai-in-healthcare-2025/main.webp",
  "thumbnailImageUrl": "/images/ai-in-healthcare-2025/thumb.webp",
  "readingTime": 5,
  "wordCount": 1020,
  "schemaType": "NewsArticle",
  "factCheckedBy": "AI Content Review",
  "editorReviewedBy": "AI Editor",
  "language": "en-IN"
}
```

All articles live in **`perplexityArticles_eeat_enhanced.json`** — a single JSON array. This is the master data file.

#### 3.2.2 CLI commands

```
python super_article_manager.py generate trends --count 10
python super_article_manager.py generate keywords "AI" "blockchain"
python super_article_manager.py generate batch technology
python super_article_manager.py enhance --all
python super_article_manager.py dedupe
python super_article_manager.py stats
python super_article_manager.py backup
```

#### 3.2.3 Article generation pipeline (per keyword)

```
keyword  ──▶  expand_keywords()  ──▶  LLM prompt (Gemini or OpenRouter)
                                            │
                                            ▼
                                   raw content (Markdown/HTML)
                                            │
                                            ▼
                              build_article_object()
                              - generate slug
                              - extract/generate excerpt
                              - estimate reading time
                              - normalize category
                              - add E-E-A-T fields
                              - embed inline images
                              - add internal links
                                            │
                                            ▼
                              generateImage()  ──▶  images/slug/main.webp
                                                    images/slug/thumb.webp
                                            │
                                            ▼
                              deduplication check (slug + title similarity)
                                            │
                                            ▼
                              append to perplexityArticles_eeat_enhanced.json
                              backup  ──▶  perplexityArticles/perplexityArticles_operation_YYYYMMDD_HHMMSS.json
```

#### 3.2.4 Categorisation system

8 canonical categories: **Technology, Business, Health, Sports, Entertainment, Lifestyle, Environment, World**

Three-tier resolution:
1. **Subcategory mapping** (explicit lookup table, ~80 subcategories mapped) — most accurate
2. **Category normalisation** (explicit mapping for 30+ aliases like "Finance" → "Business")
3. **AI keyword scoring** (counts keyword-pattern matches, confidence threshold 0.8)

#### 3.2.5 Deduplication

Articles are considered duplicates when:
- Same slug, OR
- Title similarity > configurable threshold (string distance), OR
- Same `sourceKeyword` already processed

When a duplicate is detected, a quality score decides which to keep:
- Content length (up to 50 pts)
- Presence of key fields (title, excerpt, ogImage, etc.)
- Penalty for missing slug or id

#### 3.2.6 Backup strategy

Every `create_backup("operation")` call writes a timestamped snapshot of the master JSON into `perplexityArticles/`. The `auto_publish.sh` also maintains up to 10 daily backups in `backups/`.

---

### 3.3 Image Generation Layer (`generateImage.py`)

Three providers in priority order:

| Provider | Trigger | Cost |
|---|---|---|
| **Gemini** (`google/generativeai`) | `GEM_API_KEY` set | Paid (Google) |
| **OpenRouter** | `OPENROUTER_API_KEY` + `IMAGE_MODEL` set | Paid (varies) |
| **Pollinations.ai** | Fallback — always available | Free |

All images are saved as **WebP** (quality 85, optimised). RGBA/palette images are flattened to RGB before saving.

The infographic sub-system (`InfographicAnalyzer` class in `super_article_manager.py`) analyses each article section heading and content to pick an infographic type (flowchart, comparison chart, data viz, case study, etc.) and generates a tailored AI prompt for that type.

---

### 3.4 Site Generation Layer (`generateSite_advanced.py`)

Input: `perplexityArticles_eeat_enhanced.json`  
Output: `dist/` — a fully self-contained static website

#### Pages generated

| Page | Notes |
|---|---|
| `dist/index.html` | Homepage. Shows latest N articles with "Load More" (AJAX/lazy). Category filter tabs. |
| `dist/articles/{slug}.html` | Individual article page per article |
| `dist/categories/{category-slug}.html` | One page per category |
| `dist/contact.html` | Static contact form |
| `dist/privacy-policy.html` | GDPR-ready |
| `dist/disclaimer.html` | Legal disclaimer |
| `dist/about-us.html` | About page |
| `dist/sitemap.xml` | Sitemap with validated date formats |
| `dist/robots.txt` | Search engine directives |
| `dist/rss.xml` | RSS feed |

#### Generation modes

- **Differential** (default): `generateDifferentialManifest.py` compares the current `dist/` manifest against the last sync manifest and flags only changed/new files. `ultraFastSync.py` uploads only those files.
- **Full**: Regenerates every file. Used when layout changes.

#### Pre-flight & post-flight validation

Before and after generation, the script validates:
- All articles have non-empty, unique slugs and titles
- Sitemap XML dates are in valid `YYYY-MM-DD` format (invalid dates cause Google Search Console errors)
- Required static files exist

#### Styling

- **Tailwind CSS** (CDN)
- **Google Fonts** — Inter (400, 500, 600, 700)
- **Font Awesome** icons in the webapp dashboard
- Article content headings: `color: #1e3a8a` (dark blue)
- Card hover: `translateY(-5px)` + shadow
- Light gray page background: `#f3f4f6`

#### Ad integration

Google AdSense (`ca-pub-7451593482486400`) is loaded in every page head. Ad zones are placed at strategic positions within article pages.

---

### 3.5 FTP Sync Layer

| File | Role |
|---|---|
| `ultraFastSync.py` | Primary sync: parallel FTP upload using `concurrent.futures`, up to 20 workers by default. Loads differential manifest to only upload changed files. No console output for speed — logs to file only. |
| `customRSync.py` | Alternative sync. More explicit control. |
| `generateLocalManifest.py` | Walks `dist/` and writes a JSON manifest (`{filepath: md5_hash}`) for differential comparisons. |
| `generateDifferentialManifest.py` | Compares current manifest with previous to produce a list of files to upload/delete. |

FTP credentials come from `.env`: `FTP_HOST`, `FTP_USER`, `FTP_PASS`, `REMOTE_DIRECTORY`, `MAX_WORKERS`.

---

### 3.6 Automation Layer

#### `auto_publish.sh` — the daily driver

Runs in this order:

```
1. backup_articles()              — snapshot master JSON to backups/
2. generate_custom_keyword_articles()  — reads custom_keywords.txt
3. generate_trend_articles()      — runs super_article_manager.py generate trends --count 10
4. generateSite_advanced.py       — builds dist/
5. generate_local_manifest()      — generateLocalManifest.py
6. generateDifferentialManifest.py
7. generate_missing_images()      — retries up to 3× for any articles with no image
8. ultraFastSync.py               — FTP upload
9. refresh_trends_data()          — fetch_fresh_trends.py (for next day's run)
10. cleanup_logs()                — removes logs older than 7 days
```

#### Cron setup

`setup_daily_cron.sh` installs: `0 18 * * * /path/to/cron_wrapper.sh`

`cron_wrapper.sh` sets PATH, cd's to the project dir, runs `auto_publish.sh`, writes `logs/scheduler_status.json` with `{ last_run, exit_code, status }` — consumed by the webapp's Scheduler tab.

#### Custom keywords

Drop keywords into `custom_keywords.txt` (one per line, `#` for comments). `auto_publish.sh` picks them up and generates articles before the trend run. File is not consumed/deleted — edit it to change the standing keyword list.

---

### 3.7 Web Application Layer (`webapp_main.py`)

A **FastAPI** app that provides a browser GUI over the same pipeline.

#### Stack

- **FastAPI** + **Uvicorn** (dev) / **Gunicorn + UvicornWorker** (prod)
- **Jinja2** templates (`webapp_templates/dashboard.html`)
- **Tailwind CSS** + **Font Awesome** (CDN)
- **SQLite** (`webapp_users.db`) for users, configs, generation history
- **JWT** (PyJWT, HS256, 24-hour expiry) for auth
- **bcrypt** for password hashing

#### Routes / Features

| Section | What it does |
|---|---|
| **Login / Register** | Modal-based auth. Default admin: `admin` / `admin123`. |
| **Generate** | Enter keywords → POSTs to `/api/generate` → background task runs `generate_articles_from_keywords()` → SSE or polling for progress (0–100%). Optional immediate FTP deploy. |
| **Trends** | Calls `/api/trends` which reads the cached CSV files and returns current trending keywords. Refresh button triggers `fetch_fresh_trends.py` as a subprocess. |
| **Scheduler** | Reads `logs/scheduler_status.json` to show last cron run time and status. Can manually trigger `auto_publish.sh`. |
| **History** | Reads `generation_history` table — lists past jobs with keyword, status, articles generated. |
| **Stats cards** | Total articles, deployed count, pending jobs, last run time. |

#### Background job tracking

Jobs are tracked in-memory in `active_jobs: Dict[str, Dict]` (UUID → `{status, progress, message, ...}`). On completion, written to `generation_history` SQLite table.

#### Key config models (Pydantic)

- `WebsiteConfig` — URL, name, author, social handles
- `FTPConfig` — host, user, password, remote dir, max workers
- `ContentConfig` — articles per keyword (1–10), target regions, generate images, min length, SEO focus
- `ArticleGenerationRequest` — combines the above + `deploy_immediately` flag

---

## 4. Data Flow: Full Daily Run

```
6 PM IST (cron)
     │
     ▼
cron_wrapper.sh
     │
     ▼
auto_publish.sh
     │
     ├─▶ [1] Backup: perplexityArticles_eeat_enhanced.json → backups/
     │
     ├─▶ [2] Custom keywords from custom_keywords.txt
     │         └─▶ super_article_manager.py generate keywords ...
     │                └─▶ Gemini/OpenRouter LLM API
     │                └─▶ Image gen → images/
     │                └─▶ Appends to perplexityArticles_eeat_enhanced.json
     │                └─▶ Backup → perplexityArticles/
     │
     ├─▶ [3] Trend articles
     │         └─▶ getTrendInput.py reads output/all_seo_filtered_trends.csv
     │         └─▶ super_article_manager.py generate trends --count 10
     │                └─▶ (same as above ×10 articles)
     │
     ├─▶ [4] generateSite_advanced.py
     │         └─▶ reads perplexityArticles_eeat_enhanced.json
     │         └─▶ validates slugs, dates
     │         └─▶ generates dist/ (HTML, sitemap, RSS, robots.txt)
     │
     ├─▶ [5+6] generateLocalManifest.py + generateDifferentialManifest.py
     │         └─▶ identifies changed files
     │
     ├─▶ [7] Image retry for articles still missing images
     │
     ├─▶ [8] ultraFastSync.py
     │         └─▶ parallel FTP upload of changed files to Hostinger
     │
     ├─▶ [9] fetch_fresh_trends.py → trends.py → refreshes output/*.csv
     │
     └─▶ [10] Cleanup old logs + write logs/scheduler_status.json
```

---

## 5. File & Directory Map

```
articleGen/
├── .env                        # API keys, FTP creds (never committed)
├── custom_keywords.txt         # Standing custom keyword list
├── keyword_config.json         # Keyword categories for batch generation
├── intelligent_categories.json # Category config
│
├── ── CORE PIPELINE ──
├── trends.py                   # Google Trends fetcher
├── daily_trend_filter.py       # Trend CSV post-processor
├── getTrendInput.py            # Trend CSV reader / keyword selector
├── fetch_fresh_trends.py       # Wrapper to refresh trends
├── super_article_manager.py    # Article generation, enhancement, deduplication
├── generateImage.py            # Image generation (Gemini/OpenRouter/Pollinations)
├── imgGen.py                   # Lower-level image helpers
├── generateSite_advanced.py    # Static site generator (primary)
├── generateSite.py             # Static site generator (simpler, legacy)
├── generateSite_clean.py       # Static site generator (no E-E-A-T display)
├── generateLocalManifest.py    # dist/ manifest builder
├── generateDifferentialManifest.py  # Diff between manifests
├── ultraFastSync.py            # Parallel FTP uploader
├── customRSync.py              # Alternative FTP sync
│
├── ── AUTOMATION ──
├── auto_publish.sh             # Daily pipeline script
├── cron_wrapper.sh             # Cron-safe wrapper for auto_publish.sh
├── setup_daily_cron.sh         # Installs the crontab entry
├── setup_cron.sh               # Alternative cron setup
│
├── ── WEB APP ──
├── webapp_main.py              # FastAPI application
├── webapp_config.py            # Config constants for the webapp
├── webapp_requirements.txt     # Webapp-specific pip deps
├── webapp_users.db             # SQLite: users, configs, history
├── webapp_templates/
│   └── dashboard.html          # Single-page dashboard
├── webapp_static/              # Static assets for the webapp
├── gunicorn.conf.py            # Production WSGI config
├── start_webapp.sh             # Starts uvicorn/gunicorn
│
├── ── DATA ──
├── perplexityArticles_eeat_enhanced.json  # MASTER article store
├── perplexityArticles/         # Operation-level JSON backups
├── output/                     # Trend CSVs from trends.py
├── input/                      # Supplementary input data
├── images/                     # Generated article images (local)
├── images_backup/              # Extra image backup outside dist/
├── backups/                    # Daily article JSON backups (last 10)
│
├── ── GENERATED SITE ──
├── dist/
│   ├── index.html
│   ├── articles/{slug}.html    # One file per article
│   ├── categories/{cat}.html   # One file per category
│   ├── contact.html
│   ├── privacy-policy.html
│   ├── disclaimer.html
│   ├── about-us.html
│   ├── sitemap.xml
│   ├── robots.txt
│   ├── rss.xml
│   └── images/                 # Copied from images/ at build time
│
├── ── UTILITIES / MAINTENANCE ──
├── enhance_existing_headers.py # Keyword-optimise H2/H3 in existing articles
├── audit_categorization.py     # Detects + fixes miscategorised articles
├── consolidate_categories.py   # Merges variant category names
├── ai_categorization.py        # Standalone AI categoriser
├── intelligent_categories.py   # Category config management
├── workflow.py                 # Interactive 8-option CLI menu
├── workflow_noninteractive.py  # Non-interactive equivalent (for scripts)
├── migrate_tools_data.py       # Data migration helper
├── remove_ads.py               # Strips ad blocks from HTML
├── _gen_images_for_new.py      # Batch image gen for new articles
├── _report.py                  # Article stats report
│
├── ── DIAGNOSTICS ──
├── check_env.py
├── check_static_pages.py
├── check_trends.py
├── comprehensive_static_diagnostic.py
├── browser_test_static_pages.py
├── verify_static_paths.py
├── final_static_fix.py
├── fix_static_pages.py
│
└── logs/
    ├── auto_publish_YYYYMMDD.log
    ├── scheduler_status.json   # Read by webapp Scheduler tab
    └── ultraFastSync_*.log
```

---

## 6. External Dependencies & APIs

| Dependency | Purpose | Key Env Var |
|---|---|---|
| Google Gemini (`google-generativeai`) | Article text + image generation | `GEM_API_KEY` |
| OpenRouter | Alternative LLM + image generation | `OPENROUTER_API_KEY`, `LLM_MODEL`, `IMAGE_MODEL` |
| Pollinations.ai | Free image generation fallback | None (public) |
| trendspy-lite | Google Trends data | None (scraping) |
| FTP server (Hostinger) | Website hosting | `FTP_HOST`, `FTP_USER`, `FTP_PASS` |
| Google AdSense | Monetisation | Hardcoded publisher ID `ca-pub-7451593482486400` |
| Tailwind CSS | Styling (CDN) | None |
| Google Fonts | Typography (CDN) | None |

Python libraries (core): `pandas`, `aiohttp`, `asyncio`, `Pillow`, `markdown`, `python-dotenv`, `PyYAML`, `requests`, `tqdm`

Python libraries (webapp only): `fastapi`, `uvicorn`, `pydantic`, `jinja2`, `PyJWT`, `passlib[bcrypt]`, `gunicorn`

---

## 7. Known Weaknesses / Areas for Improvement

| Area | Current State | Gap |
|---|---|---|
| **Single master JSON file** | All articles in one flat file | No proper DB; concurrent writes are unsafe; file grows unbounded |
| **No dedup between keywords** | Same trend can produce near-identical articles on different runs | Similarity threshold dedup is post-hoc, not pre-emptive |
| **In-memory job tracking** | `active_jobs` dict in webapp process | Lost on app restart; no persistent job queue |
| **Default admin credentials** | `admin` / `admin123` shipped in code | Must be changed manually |
| **Category AI confidence** | Keyword counting, not a real LLM call | Low precision for ambiguous topics |
| **Blocking LLM calls** | Article generation is `async` but image gen may block | Pipeline can stall on slow API responses |
| **No article editing UI** | Can only generate, not edit in browser | Content corrections require file edits |
| **Differential sync reliability** | Manifest comparison relies on MD5 of local files | Remote deletions (e.g. server-side changes) are not detected |
| **No scheduling UI** | Cron is managed via shell script, visible in webapp read-only | Cannot change schedule from browser |
| **Trend data freshness** | Fetched once per day, cached in CSV | Intra-day trend spikes are missed |
| **Image quality control** | No review step; Pollinations fallback quality varies | Published images may be low quality |

---

## 8. Environment Variables Reference

```
# Required
GEM_API_KEY=               # Gemini API key
FTP_HOST=                  # e.g. 212.1.209.3
FTP_USER=                  # FTP username
FTP_PASS=                  # FTP password
REMOTE_DIRECTORY=          # e.g. /public_html
LOCAL_DIRECTORY=           # Local dist/ path for sync

# Optional
OPENROUTER_API_KEY=        # OpenRouter for LLM / images
LLM_MODEL=                 # e.g. google/gemma-4-26b-a4b-it
IMAGE_MODEL=               # OpenRouter image model
MAX_WORKERS=20             # FTP parallel workers
SECRET_KEY=                # JWT secret for webapp
WEBSITE_URL=               # Published site URL
WEBSITE_NAME=              # Site display name
AUTHOR_NAME=               # Default author byline
AUTHOR_EMAIL=              # Contact email
```

---

*Last updated: 7 May 2026*
