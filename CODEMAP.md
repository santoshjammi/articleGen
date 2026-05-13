# Codebase Map — Country's News Article Generator

## Entry Points

| Script | Purpose |
|--------|---------|
| `super_article_manager.py` | **Main CLI** — article generation, enhancement, categorisation |
| `webapp_main.py` | FastAPI web UI (runs on port 8000 via uvicorn) |
| `generateSite_advanced.py` | Static site builder → writes `dist/` |
| `auto_publish.sh` | Full pipeline shell script (generate → build → FTP deploy) |

---

## CLI Structure (`super_article_manager.py`)

```
python super_article_manager.py <command> [subcommand] [options]

COMMANDS
├── generate
│   ├── keywords <kw1> <kw2> ...      Generate from explicit keywords
│   │     --count/-c  INT             Articles per keyword  [default: 1]
│   │     --region/-r STR             Target region         [default: India]
│   │     --no-skip                   Regenerate even if keyword was processed before
│   │     --prompt/-p STR             Extra instructions appended to the prompt
│   │
│   ├── trends                        Generate from Google Trends
│   │     --count/-c  INT             # of trending keywords to process [default: 3]
│   │     --regions   STR...          Override regions (e.g. India USA)
│   │     --per-region                Top N per region, not global top N
│   │
│   ├── batch [batch_names]           Process JSON-defined keyword batches
│   │     --config    FILE            keyword_config.json [default]
│   │
│   └── interactive                   REPL-style keyword input
│
├── enhance
│   ├── --headers-only                Validate & clean article headers (editorial rules)
│   ├── --deduplicate                 Remove duplicate articles
│   ├── --fix-issues                  Fix missing IDs, broken slugs, etc.
│   ├── --merge-legacy                Merge articles.json → perplexityArticles_eeat_enhanced.json
│   └── --all                         Run all of the above
│
├── categorize
│   ├── test   --count N              Test keyword-pillar categorisation on N articles
│   ├── all    --force --max-ai N     Re-categorise everything
│   └── stats                         Print pillar distribution
│
├── images
│   ├── --missing-only                Generate only where image is absent
│   ├── --regenerate                  Force-regenerate all images
│   ├── --articles slug1 slug2        Target specific articles
│   └── --type main|thumbnail|inline  Which image types to generate
│
├── stats                             Print article counts, category breakdown, recent items
├── workflow --complete               Enhance → deduplicate → fix → save in one pass
└── backup --images                   Copy all images to images_backup/
```

---

## Data Flow (article generation pipeline)

```
CLI args
  │
  └─► generate_articles_from_keywords()
        │
        ├─ expand_keywords(kw, region)
        │     Returns 5 variants:
        │       "{kw} India"
        │       "{kw} industry impact"
        │       "{kw} enterprise"
        │       "{kw} 2025 2026"
        │       "{kw} analysis"
        │
        └─► ArticleGenerator.generate_article_from_keyword()  [async, one per variant]
              │
              ├─ Builds intelligence prompt (7-part mandatory structure)
              ├─ Calls LLM (OpenRouter if LLM_MODEL set, else Gemini)
              ├─ Parses JSON response → article fields
              ├─ generateImage() × N  (main + thumb + inline images)
              ├─ categorize_with_ai()  → assigns to editorial pillar
              ├─ backup_images()
              └─ Returns article dict
                   │
                   └─► Appended to perplexityArticles_eeat_enhanced.json
                              │
                              └─► python generateSite_advanced.py
                                    └─► dist/  (index.html, articles/*.html, categories/*.html)
```

---

## Key Files

| File | Role |
|------|------|
| `perplexityArticles_eeat_enhanced.json` | **Master articles store** — read & written by every script |
| `custom_keywords.txt` | Keywords processed by cron/auto_publish.sh |
| `keyword_config.json` | Named keyword batches for `generate batch` |
| `dist/` | Generated static site output |
| `dist/images/<slug>/` | Generated images per article |
| `images_backup/` | Backup copy of images outside dist/ |
| `.env` | API keys, FTP credentials, LLM model selection |
| `enhance_existing_headers.py` | Post-generation editorial validator |
| `generateSite_advanced.py` | Static site renderer (homepage, article pages, category pages) |

---

## LLM Selection (from .env)

| Variable | Effect |
|----------|--------|
| `LLM_MODEL` + `OPENROUTER_API_KEY` | Uses OpenRouter (e.g. `google/gemma-4-26b-a4b-it`) |
| `GEM_API_KEY` (fallback) | Uses Gemini 2.0 Flash directly |
| Temperature | 0.5 (both providers) |

---

## Generate 5 Articles Per Keyword — Commands

### Option A — Specific keywords (recommended)
```bash
cd /Users/kgt/Desktop/Projects/articleGen
source venv/bin/activate

python super_article_manager.py generate keywords \
  "AI inference" \
  "large language models" \
  "generative ai" \
  "ai agents" \
  "llm inference" \
  --count 5 \
  --region India \
  --no-skip
```
This generates **5 × 5 = 25 articles** (each keyword × 5 semantic variants).

### Option B — All keywords from custom_keywords.txt at once
```bash
cd /Users/kgt/Desktop/Projects/articleGen
source venv/bin/activate

grep -v '^#' custom_keywords.txt | grep -v '^$' | \
  xargs python super_article_manager.py generate keywords \
  --count 5 --region India --no-skip
```

### Option C — After generating, build the site
```bash
python generateSite_advanced.py
```

### Option D — Full pipeline (generate → build → FTP deploy)
```bash
bash auto_publish.sh
```

---

## Editorial Pillars (4)

| Pillar | Covers |
|--------|--------|
| AI Infrastructure | LLMs, inference, GPU, agents, AI tooling, MLOps |
| Enterprise Transformation | ERP, SaaS, automation, AI copilots, productivity |
| Smart Mobility | EV, charging, fleets, robotics, smart logistics |
| India Digital Transformation | UPI, ONDC, smart cities, India startups, gov AI |

## Mandatory 7-Part Article Structure

1. Context
2. Why This Matters
3. Operational Implications
4. Economic Implications
5. Winners and Losers
6. Future Outlook
7. Strategic Takeaway
