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

## 10. External Dependencies & APIs

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

## 7. SEO & AEO Strategy

### 7.1 Search Engine Optimisation (SEO)

SEO is baked into every layer — from how trends are selected through to what lands in the HTML `<head>`.

#### Trend-to-Keyword SEO Filter

The very first gate is the trend filter in `trends.py`:
- Global trends must have **>100,000 searches** to qualify (noise removal)
- India's **top 15** trends are always included regardless of volume (local authority)
- Output is written to SEO-labelled CSVs (`all_seo_filtered_trends.csv`)

This ensures only high-demand keywords enter the pipeline, which is the foundation of traffic-driven SEO.

#### Keyword Density in Content (LLM Prompt Engineering)

The LLM prompt in `super_article_manager.py` (`generate_article_from_keyword()`) directly encodes SEO rules:

| Rule | Detail |
|---|---|
| **Keyword in every H2/H3** | Prompt mandates exact keyword phrase in every major heading |
| **Keyword density 15–20×** | "Achieve HIGH DENSITY: Mention '{keyword}' at least 15-20 times" |
| **Minimum 1,500 words** | Long-form content signals depth to search crawlers |
| **Question-based headings** | "What is X?", "How Does X Work?", "X vs Alternatives" — matches natural search queries |
| **Bold in first paragraph** | Keyword bolded on first use for on-page prominence |
| **Comparison tables** | Added where relevant for featured snippet candidacy |
| **Logical content architecture** | Foundation → Application → Optimization → Strategy layers |
| **Year in content** | Prompts include "current 2025 trends" for freshness signals |

Keyword expansion also happens at the article object level (`expand_keywords()`), generating variants like `"{keyword} in {region}"`, `"{keyword} news"`, `"{keyword} trends 2025"`, and these are stored in the article's `keywords` array.

#### On-Page HTML SEO (per article page)

Every generated `dist/articles/{slug}.html` contains:

```html
<title>{Article Title} | Country's News</title>
<meta name="description" content="{excerpt, 160 chars max}">
<meta name="keywords" content="{comma-separated keywords array}">
<meta name="author" content="...">
<meta name="article:published_time" content="YYYY-MM-DD">
<meta name="article:modified_time" content="YYYY-MM-DD">
<meta name="article:section" content="{category}">
<link rel="canonical" href="https://countrysnews.com/articles/{slug}.html">
```

#### Open Graph & Twitter Cards

Every page (homepage, article, category) includes full OG and Twitter card tags:

```html
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:type" content="article">  <!-- or "website" for homepage -->
<meta property="og:url" content="...">
<meta property="og:image" content="{absolute public image URL}">
<meta property="og:site_name" content="Country's News">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="...">
<meta name="twitter:description" content="...">
<meta name="twitter:image" content="...">
```

Image URLs in OG/Twitter tags are always converted to absolute public URLs (`https://countrysnews.com/...`) even if the local path starts with `dist/` or a relative prefix.

#### Structured Data / Schema.org (JSON-LD)

Three different structured data blocks are generated depending on page type:

| Page | Schema Type | Key Fields |
|---|---|---|
| **Homepage** | `NewsMediaOrganization` + `ItemList` of `NewsArticle` | name, url, logo, sameAs (Twitter), top-10 recent articles |
| **Article** | `NewsArticle` | headline, description, datePublished, dateModified, author (Person), publisher (Organization + logo), mainEntityOfPage, image (ImageObject with absolute URL) |
| **Category** | `CollectionPage` + `ItemList` of `NewsArticle` | name, description, url, itemListElement (top-10 articles in category) |

All are embedded as `<script type="application/ld+json">` in the `<head>`.

#### E-E-A-T Signals (Experience, Expertise, Authoritativeness, Trustworthiness)

Google's E-E-A-T guidelines are addressed at multiple levels:

| Signal | Implementation |
|---|---|
| **Author** | Every article has a named author field; rendered on-page with bio and placeholder avatar |
| **Fact-checked by** | `factCheckedBy: "AI Content Review"` stored in article JSON, displayed in article meta |
| **Editor reviewed by** | `editorReviewedBy: "AI Editor"` stored in JSON |
| **Publisher schema** | Organisation + logo in every `NewsArticle` structured data block |
| **E-E-A-T meta tags** | `<meta name="author">`, `<meta name="publisher">`, `<meta name="copyright">` on every page |
| **Schema type** | `NewsArticle` (not just `Article`) signals news authority to Google |
| **Tagline** | "Trusted. Verified. Expert." in site header |
| **Footer copy** | "Verified Journalism | Expert Analysis | Fact-Checked Content" |

#### Technical SEO

- **Sitemap** (`dist/sitemap.xml`): Generated for all article and category URLs. Date format is validated post-generation — invalid dates abort the build to prevent Google Search Console errors.
- **Robots.txt** (`dist/robots.txt`): Generated to allow all crawlers.
- **RSS feed** (`dist/rss.xml`): Top 20 articles with full metadata. Auto-linked from every page `<head>`.
- **Canonical URLs**: Every page declares its canonical to prevent duplicate content issues.
- **Breadcrumbs**: Rendered on every article page (`Home > Category > Article Title`) for crawl path clarity.
- **Slug generation**: Clean URL slugs (`re.sub` to strip non-word characters, lowercase, hyphen-join).
- **Date sanitisation**: `sanitize_date_format()` ensures dates are always `YYYY-MM-DD` — malformed dates are replaced with today's date before sitemap inclusion.
- **Differential sync**: Only changed files are uploaded, so crawlers see incremental updates, not full re-serves, which preserves crawl budget.

#### Performance (Core Web Vitals)

- `<link rel="preconnect">` for Google Fonts and `fonts.gstatic.com`
- Images use `loading="lazy"` on cards; `IntersectionObserver`-based lazy loading for below-fold images
- Images saved as **WebP** (quality 85) — typically 25–35% smaller than JPEG at equivalent quality
- Tailwind CSS from CDN (no unused CSS problem at current scale)
- `onerror` fallback on every image to prevent layout shifts from broken images

---

### 7.2 Answer Engine Optimisation (AEO)

AEO targets AI-powered answer surfaces: Google AI Overviews, Perplexity, ChatGPT browsing, Bing Copilot, etc. The system explicitly names Perplexity as a target in its LLM prompts.

#### AEO-Oriented Content Structure

The LLM prompt enforces a **question-based article structure** which is the primary AEO technique:

```
Foundational Questions:
  "What is {keyword}?"         ← Direct definitional answer → triggers knowledge panel / AI overview
  "Why Do You Need {keyword}?" ← Intent clarification
  "How Does {keyword} Work?"   ← Process answer → answer box candidate

Practical Questions:
  "Best {keyword} Examples"    ← List-based answer → ordered list AI response
  "How to Create/Use {keyword}" ← Numbered steps → step-by-step AI answer
  "Common {keyword} Mistakes"  ← Negative framing for contrast answers

Advanced Questions:
  "Advanced {keyword} Techniques"
  "Tools for {keyword}"        ← Comparison → tool comparison AI answer
  "{keyword} Best Practices in {region}" ← Localised answer

Future Questions:
  "Future of {keyword}"
  "{keyword} vs Alternatives"  ← Versus framing → comparative AI answer
```

This mirrors the structure that answer engines decompose a topic into, making the articles directly citable.

#### Explicit AEO Prompt Instruction

The LLM prompt literally states:

> *"This article must be strategically structured with high keyword density and optimized to be easily summarized and cited by AI answer engines like Perplexity."*

This affects how the model writes the content — shorter definitive sentences for each section opener, clear topic sentences, structured lists — all of which are patterns answer engines extract from.

#### Formatting for Extractability

The prompt also mandates:
- **Bold text** for key concepts (AI crawlers weight bolded text as summaries)
- **Bullet points** for benefits/features (extracted as list answers)
- **Numbered steps** for processes (extracted as step-by-step answers)
- **Comparison tables** where relevant (extracted as structured data by some engines)
- **Hypothetical statistics** framed as `"Recent studies show..."`, `"Industry surveys indicate..."` — mimics the citation-heavy style that answer engines prefer

#### Table of Contents with Anchor IDs

Every article page auto-generates a Table of Contents from H2/H3 headings, with `id` attributes injected into each heading. The TOC is:
- Shown in a sticky sidebar on desktop
- Shown inline above content on mobile

This creates fragment-addressable sections (`#what-is-ai-healthcare`) which answer engines can link to directly, and improves dwell time by making navigation fast.

#### Markdown → HTML conversion

Article content from the LLM sometimes arrives as Markdown, sometimes HTML. The site generator detects which and converts Markdown using the `markdown` library with extensions: `extra`, `sane_lists`, `smarty`, `tables`, `fenced_code`. This ensures lists, tables, and code blocks survive the conversion with proper HTML semantics, which are more parseable by answer engines than raw text.

#### Internal Linking

`add_internal_links()` scans article content and adds `<a href="...">` links when other article titles appear as text (up to 3 links per article). This builds a topical cluster structure — a strong AEO and SEO signal that the site has deep coverage of related topics.

#### Related Articles (Topical Authority)

`compute_related_articles_map()` scores article similarity using:
- Shared keywords (weighted 3.0 per shared keyword)
- Shared social hashtags (1.0 per shared tag)
- Title word overlap (1.5 per shared significant word)
- Recency boost (up to +2.0 for articles published within 30 days)

Up to 5 related articles are shown in a sticky sidebar on every article page with thumbnail, title, and relative time (`"2 hours ago"`). This reduces bounce rate and signals topical depth.

---

## 8. UI / UX Design

### 8.1 Design Language

The site uses a consistent **navy/blue editorial** aesthetic throughout.

| Token | Value |
|---|---|
| Primary blue | `#2563eb` (Tailwind `blue-600`) |
| Header gradient | `from-blue-900 via-blue-700 to-blue-800` |
| Heading colour | `#1e3a8a` (Tailwind `blue-900`) — article content headings |
| Page background | `#f3f4f6` (Tailwind `gray-100`) |
| Card background | `#ffffff` |
| Footer background | `#111827` (Tailwind `gray-900`) |
| Body font | Inter (Google Fonts), weights 400/500/600/700 |
| Border radius (cards) | `rounded-xl` (12px) |
| Card shadow | `shadow-lg` + `border border-gray-100` |

### 8.2 Page Layouts

#### Homepage (`dist/index.html`)

```
┌─────────────────────────────────────────────────┐
│  STICKY HEADER (logo + nav + mobile hamburger)  │
├─────────────────────────────────────────────────┤
│  TOP BANNER AD SLOT                             │
├─────────────────────────────────────────────────┤
│  HERO SECTION                                   │
│  ┌──────────────────────────┐  ┌─────────────┐ │
│  │  Featured articles grid  │  │ Sidebar ad  │ │
│  │  (3 cards, top articles) │  │             │ │
│  │                          │  │ Categories  │ │
│  │                          │  │ list        │ │
│  └──────────────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────┤
│  RECENT ARTICLES                                │
│  3-column responsive card grid                  │
│  [card][card][card]                             │
│  [card][card][card]                             │
│            [Load More Articles]                 │
├─────────────────────────────────────────────────┤
│  FOOTER (4-column: logo/desc, cats, links, RSS) │
├─────────────────────────────────────────────────┤
│  MOBILE BOTTOM STICKY AD (hidden on desktop)    │
└─────────────────────────────────────────────────┘
```

- First N articles rendered server-side (static HTML)
- Remaining articles injected client-side via "Load More" button (vanilla JS, 6 per page)
- Loading state: spinner animation + "Loading..." text on button
- Load More button disappears when all articles exhausted

#### Article Page (`dist/articles/{slug}.html`)

```
┌─────────────────────────────────────────────────┐
│  STICKY HEADER                                  │
├─────────────────────────────────────────────────┤
│  ARTICLE BODY (max-w-4xl)                       │
│  ┌───────────────────────────┐  ┌─────────────┐│
│  │  Breadcrumb nav           │  │             ││
│  │  Category badge           │  │ Sidebar ad  ││
│  │  H1 Title                 │  │             ││
│  │  Author / Date / Mins     │  │ Table of    ││
│  │  Featured image           │  │ Contents    ││
│  │  Twitter + Facebook share │  │ (sticky)    ││
│  │  ─────────────────────    │  │             ││
│  │  [Mobile TOC on small]    │  │ Related     ││
│  │  Article HTML content     │  │ Articles    ││
│  │  In-content ad slot       │  │ (5 max)     ││
│  │  Social hashtags          │  │             ││
│  │  Author bio card          │  │ Sidebar     ││
│  │  Second in-content ad     │  │ ad          ││
│  └───────────────────────────┘  └─────────────┘│
├─────────────────────────────────────────────────┤
│  FOOTER                                         │
└─────────────────────────────────────────────────┘
```

#### Category Page (`dist/categories/{slug}.html`)

Header + banner ad, then a 3-column article card grid filtered to that category, then footer.

### 8.3 Components

#### Article Card

```
┌────────────────────────────────┐
│  [Thumbnail 16:9, h-48]        │
│  [Category badge top-left]     │
├────────────────────────────────┤
│  Title (2-line clamp, bold)    │
│  Excerpt (3-line clamp, gray)  │
│                                │
│  [Author] [Reading time]  Date │
└────────────────────────────────┘
```

- `onerror` image fallback to `images/placeholder.webp`
- Card hover: `translateY(-5px)` + deeper shadow (CSS transition 200ms)
- Category badge: `bg-blue-600 text-white rounded-full text-xs`

#### Navigation Header

- **Desktop**: Sticky, gradient background. Logo left. Nav links right with "More" dropdown (categories 6+). Glassmorphism dropdown (`backdrop-filter: blur(10px)`).
- **Mobile**: Hamburger button. Slide-down menu with all categories + About/Contact links.

#### Author Profile Card

Blue-left-border card (`border-left: 4px solid #0ea5e9`), gradient background (`#f0f9ff → #e0f2fe`), author avatar (placeholder SVG), name, bio paragraph.

#### Social Sharing Bar

Inline row above article content: "Share:" label + Twitter (blue-500) + Facebook (blue-600) icon buttons. URLs use native share intents.

#### Hashtag Chips

Pill-shaped tags with blue gradient background, hover `scale(1.05)`. Shown below article content. Maximum 5 per article.

#### Table of Contents

- **Desktop**: Sticky right sidebar `<nav>`, anchored links to H2/H3 headings (auto-generated `id` attributes).
- **Mobile**: Collapsed block above article content with blue border styling.
- H3 headings indented with `ml-4` vs H2's `ml-0`.

#### Load More Button

```css
background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.4);
/* hover: translateY(-2px) + larger shadow */
```

#### Ad Containers

5 ad zones per article page, all using empty `data-ad-slot` divs (populated by AdSense JS at runtime):
- `banner-top` — below header on every page
- `article-sidebar-1` / `article-sidebar-2` — in sticky sidebar
- `article-content-1` / `article-content-2` — inline within article body
- `banner-footer` — above footer on every page
- `mobile-bottom` — fixed bottom bar, hidden on desktop (`lg:hidden`)

#### Lazy Loading Image Skeleton

```css
.lazy-image {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite; /* shimmer */
  min-height: 200px;
}
```

Images with `data-src` are observed via `IntersectionObserver`; the real `src` is swapped in when the image enters the viewport.

### 8.4 Web App Dashboard (Admin UI)

The operator-facing dashboard (`webapp_templates/dashboard.html`) uses a different visual language from the public site:

| Token | Value |
|---|---|
| App background | `bg-gray-50` |
| Nav background | `gradient-bg` = `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` (purple/blue) |
| Stat cards | white, `shadow`, `rounded-lg` |
| Accent colours | blue-500 (generate), green-500 (register), yellow (pending), purple (deployed) |
| Icons | Font Awesome 6 (CDN) |

#### Sections (single-page, tab-switched)

1. **Login / Register modals** — centred modal overlays with JWT auth
2. **Quick Stats row** — 4 metric cards: Articles Generated, Deployed, Active Jobs, Last Run
3. **Generate** — keyword textarea, settings accordion, progress bar (0-100%), live status messages
4. **Trends** — reads cached CSV, shows current trending keywords with search volumes, Refresh button
5. **Scheduler** — shows last cron run time + exit status from `logs/scheduler_status.json`, manual trigger button
6. **History** — table of past jobs from SQLite `generation_history`

Progress bar updates via polling the `/api/jobs/{job_id}` endpoint every 2 seconds during active generation.

### 8.5 Responsive Breakpoints

Tailwind's standard breakpoints are used throughout:

| Breakpoint | Width | Key changes |
|---|---|---|
| Default (mobile) | < 640px | Single column, hamburger nav, mobile TOC inline |
| `sm` | 640px | Logo text visible in header |
| `lg` | 1024px | Desktop nav shown, sidebar shown, mobile menu hidden |

Article body max-width: `max-w-4xl` (~56rem). Homepage article grid: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`.

---

## 9. Known Weaknesses / Areas for Improvement

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

## 11. Environment Variables Reference

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
