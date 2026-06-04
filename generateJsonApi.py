#!/usr/bin/env python3
"""
generateJsonApi.py
Exports article data as static JSON API files into dist/api/v1/

Run after generateSite_advanced.py and before customRSync.py.

Output structure:
  dist/api/v1/meta.json                          — site metadata + category index
  dist/api/v1/articles/index.json                — paginated article list (no body)
  dist/api/v1/articles/[slug].json               — full individual article
  dist/api/v1/categories/index.json              — category list with counts
  dist/api/v1/categories/[category-slug].json    — article list per category
  dist/api/v1/featured.json                      — featured articles
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from collections import defaultdict

ARTICLES_FILE = "perplexityArticles_eeat_enhanced.json"
API_DIR = os.path.join("dist", "api", "v1")
BASE_URL = "https://countrysnews.com"
PAGE_SIZE = 20                 # articles per index page
EXCERPT_LEN = 200              # chars for excerpt in list views

# ── Category slug map ────────────────────────────────────────────────────────
CATEGORY_SLUGS = {
    "AI Infrastructure":              "ai-infrastructure",
    "Enterprise Transformation":      "enterprise-transformation",
    "Smart Mobility":                 "smart-mobility",
    "India Digital Transformation":   "india-digital-transformation",
    # legacy categories — kept for backwards compat
    "Technology":                     "technology",
    "Business":                       "business",
    "Sports":                         "sports",
    "World":                          "world",
    "Entertainment":                  "entertainment",
    "Lifestyle":                      "lifestyle",
}

# PRD primary pillars — used for featured/priority ordering
PRIMARY_PILLARS = {
    "AI Infrastructure",
    "Enterprise Transformation",
    "Smart Mobility",
    "India Digital Transformation",
}


def _write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def _normalise_image(url) -> str | None:
    """Strip 'dist/' prefix and ensure absolute URL.
    Accepts either a plain URL string or an inlineImages dict with a 'url' key.
    """
    if isinstance(url, dict):
        # inlineImages entries are {"url": "...", "alt": "...", ...}
        url = url.get("url") or ""
    if not url:
        return None
    if url.startswith("dist/"):
        url = "/" + url[len("dist/"):]
    if url.startswith("/"):
        return BASE_URL + url
    return url


def _safe_excerpt(article: dict) -> str:
    excerpt = article.get("excerpt") or article.get("metaDescription") or ""
    if not excerpt:
        content = article.get("content") or ""
        # strip markdown/HTML tags for a plain-text excerpt
        content = re.sub(r"<[^>]+>", "", content)
        content = re.sub(r"[#*`_\[\]()]", "", content)
        excerpt = content.strip()
    return excerpt[:EXCERPT_LEN].rsplit(" ", 1)[0] + "…" if len(excerpt) > EXCERPT_LEN else excerpt


def _card(article: dict) -> dict:
    """Lightweight card — used in list endpoints (no full body)."""
    return {
        "id":               article.get("id", ""),
        "slug":             article.get("slug", ""),
        "title":            article.get("title", ""),
        "excerpt":          _safe_excerpt(article),
        "category":         article.get("category", ""),
        "categorySlug":     CATEGORY_SLUGS.get(article.get("category", ""), ""),
        "tags":             article.get("tags", []),
        "publishDate":      article.get("publishDate") or article.get("datePublished", ""),
        "dateModified":     article.get("dateModified", ""),
        "readingTime":      article.get("readingTimeMinutes", 0),
        "wordCount":        article.get("wordCount", 0),
        "featured":         bool(article.get("featured")),
        "contentType":      article.get("contentType", "article"),
        "thumbnailUrl":     _normalise_image(article.get("thumbnailImageUrl")),
        "ogImage":          _normalise_image(article.get("ogImage")),
        "canonicalUrl":     article.get("canonicalUrl") or f"{BASE_URL}/articles/{article.get('slug', '')}",
        "author":           article.get("author", ""),
        "language":         article.get("language", "en-IN"),
    }


def _full_article(article: dict) -> dict:
    """Full article payload — used in individual article endpoints."""
    card = _card(article)
    card.update({
        "content":              article.get("content", ""),
        "metaDescription":      article.get("metaDescription", ""),
        "keywords":             article.get("keywords", []),
        "ogTitle":              article.get("ogTitle", ""),
        "ogUrl":                article.get("ogUrl", ""),
        "schemaType":           article.get("schemaType", "NewsArticle"),
        "inlineImages": [
            {**img, "url": _normalise_image(img)} if isinstance(img, dict)
            else _normalise_image(img)
            for img in (article.get("inlineImages") or [])
            if img
        ],
        "keyTakeaways":         article.get("keyTakeaways", []),
        "relatedArticleIds":    article.get("relatedArticleIds", []),
        "structuredData":       article.get("structuredData"),
        "socialShareText":      article.get("socialShareText", ""),
        "socialMediaHashtags":  article.get("socialMediaHashtags", []),
        "callToActionText":     article.get("callToActionText", ""),
        "targetAudience":       article.get("targetAudience", []),
        "difficultyLevel":      article.get("difficultyLevel", ""),
        "factCheckedBy":        article.get("factCheckedBy", ""),
        "editorReviewedBy":     article.get("editorReviewedBy", ""),
        "adPlacementKeywords":  article.get("adPlacementKeywords", []),
        "adDensity":            article.get("adDensity", "medium"),
    })
    return card


def _sort_key(article: dict):
    date_str = article.get("publishDate") or article.get("datePublished") or ""
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def generate_api(articles_file: str = ARTICLES_FILE) -> None:
    print(f"📡 Generating JSON API from {articles_file}…")

    with open(articles_file, encoding="utf-8") as f:
        raw = json.load(f)

    # Filter: must have slug + title
    articles = [a for a in raw if a.get("slug") and a.get("title")]
    print(f"   {len(articles)} valid articles (of {len(raw)} total)")

    # Sort newest-first
    articles.sort(key=_sort_key, reverse=True)

    # ── 1. Individual article files ──────────────────────────────────────────
    articles_dir = os.path.join(API_DIR, "articles")
    written = 0
    for article in articles:
        slug = article["slug"]
        path = os.path.join(articles_dir, f"{slug}.json")
        _write_json(path, _full_article(article))
        written += 1
    print(f"   ✅ {written} individual article files → {articles_dir}/")

    # ── 2. Paginated article index ───────────────────────────────────────────
    cards = [_card(a) for a in articles]
    total_pages = max(1, (len(cards) + PAGE_SIZE - 1) // PAGE_SIZE)
    for page in range(total_pages):
        chunk = cards[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]
        payload = {
            "page":       page + 1,
            "totalPages": total_pages,
            "total":      len(cards),
            "pageSize":   PAGE_SIZE,
            "articles":   chunk,
        }
        suffix = "" if page == 0 else f"-page-{page + 1}"
        _write_json(os.path.join(articles_dir, f"index{suffix}.json"), payload)
    print(f"   ✅ Article index ({total_pages} pages) → {articles_dir}/index*.json")

    # ── 3. Category indexes ──────────────────────────────────────────────────
    by_category: dict[str, list] = defaultdict(list)
    for card in cards:
        cat = card["category"]
        if cat:
            by_category[cat].append(card)

    categories_dir = os.path.join(API_DIR, "categories")
    category_meta = []
    for cat_name, cat_cards in sorted(by_category.items(), key=lambda x: -len(x[1])):
        cat_slug = CATEGORY_SLUGS.get(cat_name, re.sub(r"[^a-z0-9]+", "-", cat_name.lower()))
        total_cat_pages = max(1, (len(cat_cards) + PAGE_SIZE - 1) // PAGE_SIZE)
        for page in range(total_cat_pages):
            chunk = cat_cards[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]
            payload = {
                "category":   cat_name,
                "slug":       cat_slug,
                "page":       page + 1,
                "totalPages": total_cat_pages,
                "total":      len(cat_cards),
                "pageSize":   PAGE_SIZE,
                "articles":   chunk,
            }
            suffix = "" if page == 0 else f"-page-{page + 1}"
            _write_json(os.path.join(categories_dir, f"{cat_slug}{suffix}.json"), payload)
        category_meta.append({
            "name":        cat_name,
            "slug":        cat_slug,
            "count":       len(cat_cards),
            "isPrimary":   cat_name in PRIMARY_PILLARS,
            "latestDate":  cat_cards[0]["publishDate"] if cat_cards else "",
        })
    _write_json(os.path.join(categories_dir, "index.json"), {"categories": category_meta})
    print(f"   ✅ Category indexes → {categories_dir}/")

    # ── 4. Featured articles ─────────────────────────────────────────────────
    featured = [c for c in cards if c["featured"]]
    if not featured:
        # fall back to top 3 from each primary pillar
        seen: set[str] = set()
        for pillar in PRIMARY_PILLARS:
            for c in cards:
                if c["category"] == pillar and c["slug"] not in seen:
                    featured.append(c)
                    seen.add(c["slug"])
                    if len([f for f in featured if f["category"] == pillar]) >= 3:
                        break
    featured = featured[:12]
    _write_json(os.path.join(API_DIR, "featured.json"), {"articles": featured})
    print(f"   ✅ {len(featured)} featured articles → {API_DIR}/featured.json")

    # ── 5. Site meta ─────────────────────────────────────────────────────────
    meta = {
        "site":        "CountrysNews Intelligence Platform",
        "domain":      BASE_URL,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "totalArticles": len(articles),
        "categories":  category_meta,
        "primaryPillars": sorted(PRIMARY_PILLARS),
        "apiVersion":  "1",
        "endpoints": {
            "articles":        f"{BASE_URL}/api/v1/articles/index.json",
            "articleBySlug":   f"{BASE_URL}/api/v1/articles/{{slug}}.json",
            "categories":      f"{BASE_URL}/api/v1/categories/index.json",
            "categoryBySlug":  f"{BASE_URL}/api/v1/categories/{{slug}}.json",
            "featured":        f"{BASE_URL}/api/v1/featured.json",
            "meta":            f"{BASE_URL}/api/v1/meta.json",
        },
    }
    _write_json(os.path.join(API_DIR, "meta.json"), meta)
    print(f"   ✅ Site meta → {API_DIR}/meta.json")

    # ── 6. .htaccess for CORS (Apache on FTP host) ───────────────────────────
    htaccess_path = os.path.join("dist", "api", ".htaccess")
    htaccess = (
        "# Allow cross-origin reads so the Next.js app can fetch these JSON files\n"
        '<IfModule mod_headers.c>\n'
        '    Header set Access-Control-Allow-Origin "*"\n'
        '    Header set Access-Control-Allow-Methods "GET, OPTIONS"\n'
        '    Header set Cache-Control "public, max-age=300, stale-while-revalidate=60"\n'
        '</IfModule>\n'
        '\n'
        'AddType application/json .json\n'
    )
    os.makedirs(os.path.dirname(htaccess_path), exist_ok=True)
    with open(htaccess_path, "w") as f:
        f.write(htaccess)
    print(f"   ✅ CORS .htaccess → {htaccess_path}")

    print(f"\n🎉 JSON API complete — {len(articles)} articles exported to {API_DIR}/")
    print(f"   Live URL: {BASE_URL}/api/v1/meta.json")


if __name__ == "__main__":
    if not os.path.exists(ARTICLES_FILE):
        print(f"❌ Articles file not found: {ARTICLES_FILE}")
        sys.exit(1)
    if not os.path.isdir("dist"):
        print("❌ dist/ directory not found — run generateSite_advanced.py first")
        sys.exit(1)
    generate_api()
