#!/usr/bin/env python3
"""
Archive articles under 800 words and fix 3 missing thumbnailImageUrl entries.
Run once: python3 temp/fix_thin_and_thumbs.py
"""
import json, os
from datetime import datetime

ARTICLES_FILE = "perplexityArticles_eeat_enhanced.json"
ARCHIVE_FILE = f"backups/archived_thin_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
MIN_WORDS = 800

with open(ARTICLES_FILE) as f:
    arts = json.load(f)

thin = [a for a in arts if (a.get('wordCount') or len(a.get('content','').split())) < MIN_WORDS]
keep = [a for a in arts if a not in thin]

print(f"Thin articles (< {MIN_WORDS} words): {len(thin)}")
for a in thin[:5]:
    print(f"  - [{a.get('wordCount',0)}w] {a.get('title','')[:70]}")
if len(thin) > 5:
    print(f"  ... and {len(thin)-5} more")

# Archive thin articles
os.makedirs("backups", exist_ok=True)
with open(ARCHIVE_FILE, 'w') as f:
    json.dump(thin, f, ensure_ascii=False, indent=2)
print(f"\nArchived {len(thin)} thin articles → {ARCHIVE_FILE}")

# Fix missing thumbnailImageUrl — derive from ogImage
fixed = 0
for a in keep:
    if not a.get('thumbnailImageUrl', '').strip():
        og = a.get('ogImage', '')
        if og:
            # Replace /main.webp with /thumb.webp
            thumb = og.replace('/main.webp', '/thumb.webp')
            a['thumbnailImageUrl'] = thumb
            fixed += 1
            print(f"Fixed thumbnail for: {a.get('slug','')}")

print(f"\nFixed {fixed} missing thumbnailImageUrl entries")
print(f"Saving {len(keep)} articles...")

with open(ARTICLES_FILE, 'w') as f:
    json.dump(keep, f, ensure_ascii=False, indent=2)
print("Done.")
