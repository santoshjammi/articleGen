# countrysnews-web — Design Spec
**Date:** 2026-06-03  
**Author:** Design session with GitHub Copilot  
**Status:** Approved — ready for implementation planning  

---

## 1. Overview

Migrate countrysnews.com from the Python static site generator (`generateSite_advanced.py`) to a Next.js 16 App Router application (`countrysnews-web`). The Python pipeline is **unchanged** — it continues to generate and own the articles JSON. Next.js replaces only the HTML generation step.

### Goals
- Client-side navigation between pages (no full-page reloads after first visit)
- Revenue: AdSense slots, newsletter capture, affiliate link boxes
- Search with trending topics
- Tech team `/docs/` portal (release notes, how-to, FAQ)
- Maintainable codebase separate from the legacy `articleGen` repo

### Non-goals
- Rewriting the Python article pipeline
- Moving images off FTP
- Adding a CMS or database
- Authentication / user accounts (Phase 1)

---

## 2. Repositories

| Repo | Path | Purpose |
|---|---|---|
| `articleGen` | `~/Desktop/Projects/articleGen` | Legacy pipeline — trends → articles → JSON. No changes to core logic. Gains `sync_to_web_repo.py`. |
| `countrysnews-web` | `~/Desktop/Projects/countrysnews-web` | New Next.js app. Independent git repo. |

The two repos are **never nested**. `countrysnews-web` is not a subfolder of `articleGen`.

---

## 3. Tech Stack

| Concern | Choice | Notes |
|---|---|---|
| Framework | Next.js 16, App Router | `output: 'export'` |
| Styling | Tailwind CSS v4 | Same as CommandCenter |
| Search | Fuse.js | Client-side, searches `data/index.json` |
| Markdown rendering | `marked` | Docs page only |
| Language | TypeScript | Strict mode |
| Fonts | Inter + Inter Tight | Same as CommandCenter |
| Runtime server | Express.js | Replaces `npx serve`; adds `/api/subscribe` |
| Email | nodemailer + Hostinger SMTP | Optional — disabled if SMTP env vars absent |
| Hosting | Hostinger Node.js managed | `npm start` = `node server.js` |
| Deploy trigger | Git push to `main` | Hostinger auto-redeploys on push |

---

## 4. Project Structure

```
countrysnews-web/
├── app/
│   ├── layout.tsx                  Root layout: Header + Footer, global meta
│   ├── page.tsx                    Homepage
│   ├── articles/
│   │   └── [slug]/
│   │       └── page.tsx            Article pages
│   ├── ai-infrastructure/
│   │   ├── page.tsx                Category page (page 1)
│   │   └── page/[page]/
│   │       └── page.tsx            Paginated category pages
│   ├── enterprise-transformation/
│   │   ├── page.tsx
│   │   └── page/[page]/page.tsx
│   ├── smart-mobility/
│   │   ├── page.tsx
│   │   └── page/[page]/page.tsx
│   ├── india-digital-transformation/
│   │   ├── page.tsx
│   │   └── page/[page]/page.tsx
│   ├── search/
│   │   └── page.tsx                Search page (client component)
│   ├── newsletter/
│   │   └── page.tsx                Newsletter landing page
│   ├── docs/
│   │   └── page.tsx                Tech team docs portal
│   ├── about/page.tsx
│   ├── contact/page.tsx
│   ├── privacy-policy/page.tsx
│   ├── disclaimer/page.tsx
│   ├── editorial-policy/page.tsx
│   ├── fact-checking-policy/page.tsx
│   ├── corrections-policy/page.tsx
│   ├── sitemap.ts                  Auto-generated sitemap.xml
│   ├── robots.ts
│   └── rss.xml/
│       └── route.ts                RSS feed
├── components/
│   ├── Header.tsx                  Logo, 4 category nav links, search icon
│   ├── Footer.tsx                  Links, newsletter mini-form, legal links
│   ├── ArticleCard.tsx             Used on homepage, category, related, search
│   ├── ArticleContent.tsx          Renders article HTML safely
│   ├── AuthorBox.tsx               Author avatar, name, title, bio
│   ├── RelatedArticles.tsx         3-card row
│   ├── AdSlot.tsx                  CLS-safe ad placeholder wrapper
│   ├── NewsletterBanner.tsx        Inline in-article capture
│   ├── NewsletterStickyBar.tsx     Mobile sticky bottom bar
│   ├── SearchBar.tsx               Fuse.js search, trending pills below
│   ├── KeyTakeaways.tsx            Highlighted box at top of article
│   ├── DocsPortal.tsx              Tabbed docs component (client)
│   └── Pagination.tsx              Page 1 / 2 / ... / N controls
├── lib/
│   ├── articles.ts                 Data access — reads data/index.json and data/articles/*.json
│   ├── types.ts                    ArticleMeta, ArticleFull, Subscriber, DocsEntry TypeScript types
│   ├── constants.ts                SITE_URL, CATEGORIES, PILLAR_SLUGS, AUTHORS, PAGE_SIZE
│   └── search-index.ts             Build-time script: writes data/search-index.json
├── data/                           Written by Python pipeline daily (committed to git)
│   ├── index.json                  All articles, slim (no content field), image URLs absolute
│   ├── meta.json                   Site metadata, category counts, generated timestamp
│   ├── featured.json               Featured article slugs/metadata for homepage hero
│   ├── search-index.json           Pre-built Fuse.js index (generated at build time)
│   ├── articles/
│   │   └── {slug}.json             Full article data including content
│   └── docs/
│       ├── release-notes.json      [ { version, date, changes[] } ]
│       ├── howto.json              [ { question, answer (markdown) } ]
│       └── faq.json                [ { question, answer (markdown) } ]
├── public/
│   ├── favicon.ico
│   ├── logo.svg
│   ├── og-default.png              Default OpenGraph image (1200×630)
│   └── author-placeholder.svg     Author avatar fallback
├── server.js                       Express server — serves out/, handles /api/subscribe
├── subscribers.json                Created on first subscription, NEVER committed (.gitignore)
├── .gitignore
├── next.config.ts
├── package.json
├── postcss.config.mjs
└── tsconfig.json
```

---

## 5. Routing & URL Structure

| URL Pattern | Page | Static Params Source |
|---|---|---|
| `/` | Homepage | — |
| `/articles/{slug}/` | Article | All slugs from `data/index.json` |
| `/ai-infrastructure/` | Category p.1 | Static |
| `/ai-infrastructure/page/{n}/` | Category p.N | Article count ÷ 24 |
| `/enterprise-transformation/` | Category p.1 | Static |
| `/enterprise-transformation/page/{n}/` | Category p.N | Article count ÷ 24 |
| `/smart-mobility/` | Category p.1 | Static |
| `/smart-mobility/page/{n}/` | Category p.N | Article count ÷ 24 |
| `/india-digital-transformation/` | Category p.1 | Static |
| `/india-digital-transformation/page/{n}/` | Category p.N | Article count ÷ 24 |
| `/search/` | Search | — (client-side) |
| `/newsletter/` | Newsletter landing | — |
| `/docs/` | Tech team portal | — |
| `/about/` | About (EEAT) | — |
| `/contact/` | Contact (EEAT) | — |
| `/privacy-policy/` | Privacy Policy | — |
| `/disclaimer/` | Disclaimer | — |
| `/editorial-policy/` | Editorial Policy | — |
| `/fact-checking-policy/` | Fact-Checking | — |
| `/corrections-policy/` | Corrections | — |
| `/sitemap.xml` | Sitemap | — |
| `/robots.txt` | Robots | — |
| `/rss.xml` | RSS Feed | — |

**Pagination:** 24 articles per page (`PAGE_SIZE = 24`). Category page 1 is accessible at both `/ai-infrastructure/` and `/ai-infrastructure/page/1/` — canonical is the short form.

**Legacy redirect map:** `sync_to_web_repo.py` writes `public/_redirects` (Hostinger-compatible) mapping old flat URLs:
```
/{slug}.html  →  /articles/{slug}/  301
/about-us.html  →  /about/  301
/contact.html  →  /contact/  301
```

---

## 6. Data Model

### `ArticleMeta` (used in `data/index.json`)
```typescript
interface ArticleMeta {
  id: string
  slug: string
  title: string
  author: string
  publishDate: string          // ISO date
  dateModified: string
  category: string             // "AI Infrastructure" | "Enterprise Transformation" | "Smart Mobility" | "India Digital Transformation"
  subCategory?: string
  tags: string[]
  excerpt: string
  thumbnailImageUrl: string    // absolute: https://countrysnews.com/images/...
  ogImage?: string             // absolute
  readingTimeMinutes: number
  featured: boolean
  wordCount?: number
}
```

### `ArticleFull` (used in `data/articles/{slug}.json`)
Extends `ArticleMeta` plus:
```typescript
interface ArticleFull extends ArticleMeta {
  content: string              // HTML string, already sanitised by Python pipeline
  metaDescription: string
  keywords: string[]
  keyTakeaways: string[]
  authorTitle: string
  authorBio: string
  relatedArticleIds: string[]
  structuredData?: object      // pre-built JSON-LD if present
  affiliateLinks?: Array<{ label: string; url: string; rel: string }>
}
```

### `data/docs/release-notes.json`
```json
[
  {
    "version": "1.0.0",
    "date": "2026-06-03",
    "changes": [
      "Initial Next.js launch — replaced Python static generator",
      "Client-side navigation, search, newsletter capture"
    ]
  }
]
```

---

## 7. Page Designs

### 7.1 Homepage

```
┌──────────────────────────────────────────────────────┐
│ Header: [Logo]  AI Infra  Enterprise  Mobility  India │  🔍
├──────────────────────────────────────────────────────┤
│ ┌───────────────────────┐  ┌────────┐ ┌────────┐     │
│ │  HERO ARTICLE         │  │ Card 2 │ │ Card 3 │     │
│ │  (large, left 60%)    │  └────────┘ ┌────────┐     │
│ │  title, excerpt,      │            │ Card 4 │     │
│ │  author, date, cat    │            └────────┘     │
│ └───────────────────────┘                            │
├──────────────────────────────────────────────────────┤
│ AI Infrastructure ─────────────────── View all →     │
│ [Card][Card][Card][Card][Card][Card]                  │
├──────────────────────────────────────────────────────┤
│ Enterprise Transformation ─────────── View all →     │
│ [Card][Card][Card][Card][Card][Card]                  │
├──────────────────────────────────────────────────────┤
│ Smart Mobility ────────────────────── View all →     │
│ [Card][Card][Card][Card][Card][Card]                  │
├──────────────────────────────────────────────────────┤
│ India Digital Transformation ──────── View all →     │
│ [Card][Card][Card][Card][Card][Card]                  │
├──────────────────────────────────────────────────────┤
│ Footer                                               │
└──────────────────────────────────────────────────────┘
```

- Hero: most recent `featured: true` article from `data/featured.json`
- 6 cards per pillar strip, sorted by `publishDate` descending
- AdSense slot rendered as a fixed-height placeholder between pillar strips (every other strip)

### 7.2 Category Page

```
┌──────────────────────────────────────────────────────┐
│ Header                                               │
├──────────────────────────────────────────────────────┤
│ AI Infrastructure                                    │
│ 1,506 articles                                       │
├──────────────────────────────────────────────────────┤
│ [Card][Card][Card]  ← 3 per row desktop              │
│ [Card][Card][Card]                                   │
│ [AdSlot — fixed 90px height]                         │
│ [Card][Card][Card]                                   │
│ ... (24 cards total)                                 │
├──────────────────────────────────────────────────────┤
│ ← Prev  1  2  3  ...  63  Next →                    │
├──────────────────────────────────────────────────────┤
│ Footer                                               │
└──────────────────────────────────────────────────────┘
```

### 7.3 Article Page

```
┌──────────────────────────────────────────────────────┐
│ Header                                               │
├──────────────────────────────────────────────────────┤
│ Home > AI Infrastructure > Article Title             │  ← Breadcrumb
├───────────────────────────────────┬──────────────────┤
│ TITLE (h1)                        │                  │
│ Aryan Mehta · Jun 1 2026 · 8 min  │  [AdSlot 300×250]│
│ [AI Infrastructure] [tag] [tag]   │                  │
├───────────────────────────────────┴──────────────────┤
│ ┌─────────────────────────────────────────────────┐  │
│ │ Key Takeaways                                   │  │
│ │ • Point 1  • Point 2  • Point 3                 │  │
│ └─────────────────────────────────────────────────┘  │
│ [Thumbnail image — absolute URL from FTP CDN]        │
│                                                      │
│ Article HTML content...                              │
│                                                      │
│ [AdSlot — after paragraph 3]                         │
│                                                      │
│ ...rest of content...                                │
│                                                      │
│ [NewsletterBanner — "Get the AI Intelligence Brief"] │
│                                                      │
│ ...rest of content...                                │
│                                                      │
│ [AdSlot — end of content]                            │
├──────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────┐ │
│ │ [Avatar] Aryan Mehta                             │ │
│ │ AI Infrastructure & Enterprise Reporter          │ │
│ │ Bio text...                                      │ │
│ └──────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────┤
│ Related Articles                                     │
│ [Card]  [Card]  [Card]                               │
├──────────────────────────────────────────────────────┤
│ Footer                                               │
└──────────────────────────────────────────────────────┘
```

**Ad injection strategy (CLS-safe):**
- `ArticleContent.tsx` splits the HTML string into paragraphs server-side
- Slots inserted at paragraph index 3 and 60% mark
- Each `<AdSlot />` renders `<div style={{minHeight: '250px'}} />` before the ad script loads — prevents layout shift

### 7.4 Search Page (`/search/`)

```
┌──────────────────────────────────────────────────────┐
│ Header                                               │
├──────────────────────────────────────────────────────┤
│       Search CountrysNews                            │
│  ┌──────────────────────────────────────────────┐    │
│  │ 🔍  Type to search articles...               │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  Trending Topics                                     │
│  [AI Agents] [LLM Infrastructure] [India EV Policy] │
│  [ONDC] [DevOps CI/CD] [Quantum Computing]          │
│  [Enterprise AI] [Smart Cities] [UPI 2.0]           │
│  [Cloud Native] [Edge AI] [Digital India]           │
├──────────────────────────────────────────────────────┤
│  Results (shown once user types ≥2 chars)            │
│  [ArticleCard] [ArticleCard] [ArticleCard]           │
│  [ArticleCard] [ArticleCard] [ArticleCard]           │
│  ... up to 20 results                                │
├──────────────────────────────────────────────────────┤
│ Footer                                               │
└──────────────────────────────────────────────────────┘
```

**Trending tags:** computed at build time in `lib/search-index.ts` — counts all tags across `data/index.json`, returns top 12 by frequency. Written into the page as static props, zero runtime cost.

**Fuse.js config:**
- Keys: `title` (weight 2), `excerpt` (weight 1), `tags` (weight 1.5)
- Threshold: 0.35 (reasonably fuzzy)
- Index loaded once from `data/search-index.json` on page mount

### 7.5 Newsletter Page (`/newsletter/`)

- Headline + value proposition ("Weekly AI intelligence digest — free")
- Single form: Name (optional) + Email (required)
- Posts to `POST /api/subscribe` on Express server
- On success: inline "You're subscribed!" — no page reload
- Interests checkboxes (optional): AI Infrastructure / Enterprise Transformation / Smart Mobility / India Digital

### 7.6 Docs Portal (`/docs/`)

Three tabs rendered client-side — no separate routes:

**Release Notes tab** — reads `data/docs/release-notes.json`:
```
v1.0.0 — 2026-06-03
  • Initial Next.js launch
  • Client-side navigation
  • ...

v0.9.0 — 2026-05-01  (legacy Python site)
  • ...
```

**How-To tab** — reads `data/docs/howto.json`:
- Accordion-style Q&A
- Content rendered from markdown via `marked`
- Covers: adding keywords, triggering a rebuild, archiving articles, adding a category, checking cron logs

**FAQ tab** — reads `data/docs/faq.json`:
- Same accordion style
- Covers: "Where do images go?", "What if a build fails?", "How do subscribers get stored?", "How do I export subscriber emails?", "How do I add an affiliate link?"

---

## 8. Server (`server.js`)

```
Hostinger runs: npm start → node server.js
```

### Routes

| Method | Path | Handler |
|---|---|---|
| `GET *` | All paths | `express.static('out')` — serves pre-built Next.js output |
| `POST /api/subscribe` | Subscribe form | Validates email, appends to `subscribers.json`, sends confirmation email if SMTP configured |
| `GET *` (fallback) | 404 | Serves `out/404.html` |

### `/api/subscribe` logic

1. Parse `{ name, email, interests }` from JSON body
2. Validate: email must match RFC 5322 pattern; reject if missing
3. Check for duplicate email in `subscribers.json` — return `{ ok: true, existing: true }` silently (no error shown to user — prevents email enumeration)
4. Append entry: `{ id: uuid, name, email, interests, subscribedAt: ISO timestamp, source: "web" }`
5. If `SMTP_HOST` + `SMTP_USER` + `SMTP_PASS` env vars are set: send confirmation email via nodemailer
6. Return `{ ok: true }`

### `subscribers.json` schema

```json
{
  "subscribers": [
    {
      "id": "uuid-v4",
      "name": "Ravi Kumar",
      "email": "ravi@example.com",
      "interests": ["AI Infrastructure", "Enterprise Transformation"],
      "subscribedAt": "2026-06-03T14:22:00.000Z",
      "source": "web"
    }
  ]
}
```

**Security:** `subscribers.json` is at server root, never inside `out/` — not publicly accessible. Listed in `.gitignore` — never committed to Git.

**Rate limiting:** `express-rate-limit` on `POST /api/subscribe` — max 5 requests per IP per 15 minutes. Prevents abuse without requiring a CAPTCHA.

---

## 9. `next.config.ts`

```typescript
import type { NextConfig } from 'next'

const config: NextConfig = {
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },   // required for static export; images served from FTP CDN anyway
  eslint: { ignoreDuringBuilds: false },
}

export default config
```

---

## 10. `package.json` (key scripts)

```json
{
  "name": "countrysnews-web",
  "scripts": {
    "dev": "next dev -p 3010",
    "build": "tsx lib/search-index.ts && next build",
    "start": "node server.js",
    "lint": "eslint"
  },
  "dependencies": {
    "express": "^4.18.2",
    "express-rate-limit": "^7.2.0",
    "fuse.js": "^7.3.0",
    "marked": "^12.0.0",
    "next": "16.x",
    "nodemailer": "^6.9.13",
    "react": "19.x",
    "react-dom": "19.x",
    "uuid": "^9.0.0"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/express": "^4",
    "@types/nodemailer": "^6",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "@types/uuid": "^9",
    "tailwindcss": "^4",
    "tsx": "^4.21.0",
    "typescript": "^5"
  }
}
```

---

## 11. Python Pipeline Integration (`sync_to_web_repo.py`)

New script in `articleGen/`. Added as the last step in `auto_publish.sh`.

### What it does

1. **Reads** `perplexityArticles_eeat_enhanced.json`
2. **Writes** `~/Desktop/Projects/countrysnews-web/data/index.json`
   - All articles, slim fields only (no `content`)
   - Rewrites `thumbnailImageUrl` / `ogImage`: `dist/images/...` → `https://countrysnews.com/images/...`
3. **Copies** `dist/api/v1/articles/*.json` → `data/articles/` (image URLs rewritten in each file)
4. **Copies** `dist/api/v1/meta.json` → `data/meta.json`
5. **Copies** `dist/api/v1/featured.json` → `data/featured.json`
6. **Writes** `public/_redirects` (slug redirect map: old `.html` URLs → new `/articles/{slug}/`)

### Updated `auto_publish.sh` tail

```bash
# ... existing steps unchanged ...

echo "=== Syncing data to countrysnews-web ==="
python3 sync_to_web_repo.py

echo "=== Building Next.js site ==="
cd ~/Desktop/Projects/countrysnews-web
npm run build

echo "=== Deploying to Hostinger via Git ==="
git add -A
git commit -m "deploy: $(date +%Y-%m-%d)"
git push origin main

cd ~/Desktop/Projects/articleGen
echo "=== Deploy complete ==="
```

---

## 12. Hostinger Setup (one-time)

1. Create Node.js app in Hostinger panel pointing to `countrysnews-web` git repo
2. Set start command: `node server.js`
3. Set env vars in Hostinger dashboard:
   - `NODE_ENV=production`
   - `NEXT_PUBLIC_SITE_URL=https://countrysnews.com`
   - `SMTP_HOST=smtp.hostinger.com` (optional)
   - `SMTP_USER=noreply@countrysnews.com` (optional)
   - `SMTP_PASS=<password>` (optional)
4. `subscribers.json` will be auto-created on first subscription — persists across redeploys

---

## 13. AdSense Integration

- `AdSlot.tsx` accepts `slot` (AdSense slot ID) and `format` props
- Renders a fixed-height `<div>` containing the `<ins class="adsbygoogle">` tag
- The outer `div` has a hardcoded `minHeight` matching the slot size — prevents CLS
- Slot IDs stored in `lib/constants.ts` (`AD_SLOT_ARTICLE_TOP`, `AD_SLOT_ARTICLE_MID`, `AD_SLOT_ARTICLE_BOTTOM`, `AD_SLOT_CATEGORY`)
- AdSense script loaded once in `app/layout.tsx` via `<Script strategy="lazyOnload">`
- AdSense publisher ID stored in `NEXT_PUBLIC_ADSENSE_PUB_ID` env var

---

## 14. SEO & Structured Data

Every article page generates:

```json
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "...",
  "datePublished": "...",
  "dateModified": "...",
  "author": {
    "@type": "Person",
    "name": "Aryan Mehta",
    "jobTitle": "AI Infrastructure Reporter",
    "url": "https://countrysnews.com/about/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "CountrysNews Intelligence Platform",
    "url": "https://countrysnews.com",
    "logo": { "@type": "ImageObject", "url": "https://countrysnews.com/logo.svg" }
  },
  "image": "...",
  "description": "...",
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://countrysnews.com/articles/..." }
}
```

Also generated per page: `BreadcrumbList` JSON-LD, `og:*` meta tags, `twitter:card` meta tags, canonical `<link>`.

---

## 15. Open Items (post-launch)

| Item | Priority | Phase |
|---|---|---|
| Affiliate link `affiliateLinks` field in pipeline | Medium | Phase 1 |
| AdSense approval (requires live site with content) | High | Phase 1 |
| Newsletter confirmation email template | Low | Phase 1 |
| Subscriber export script (JSON → CSV) | Low | Phase 1 |
| Premium content gate / paywall | Low | Phase 2 |
| Analytics (Plausible or GA4) | Medium | Phase 2 |

---

## 16. Build Time Estimate

| Step | Time |
|---|---|
| `sync_to_web_repo.py` (copy + rewrite 3,801 JSON files) | ~30 sec |
| `tsx lib/search-index.ts` (build Fuse.js index) | ~5 sec |
| `next build` (3,801 article pages + ~100 other pages) | ~5–8 min |
| `git add -A && git push` | ~1–2 min |
| **Total daily cron addition** | **~10 min** |

Total cron window becomes ~25 min (was ~15 min). Well within the 6 PM IST daily slot.
