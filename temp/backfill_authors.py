#!/usr/bin/env python3
"""Backfill named author personas onto all existing articles."""
import json, sys
sys.path.insert(0, '.')
from super_article_manager import _pick_author, _AUTHOR_PERSONAS

with open('perplexityArticles_eeat_enhanced.json') as f:
    arts = json.load(f)

updated = 0
for a in arts:
    if a.get('author','') in ('', 'JAMSA - Country\'s News', 'Editorial Team'):
        persona = _pick_author(a.get('sourceKeyword','') or a.get('slug',''), a.get('category','AI Infrastructure'))
        a['author'] = persona['name']
        a['authorTitle'] = persona['title']
        a['authorBio'] = persona['bio']
        updated += 1

print(f'Backfilled {updated} articles with named personas')

from collections import Counter
authors = Counter(a['author'] for a in arts)
for name, n in authors.most_common():
    print(f'  {n:5d}  {name}')

with open('perplexityArticles_eeat_enhanced.json', 'w') as f:
    json.dump(arts, f, ensure_ascii=False, indent=2)
print('Saved.')
