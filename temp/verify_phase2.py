#!/usr/bin/env python3
import ast, json
from collections import Counter

for f in ['super_article_manager.py','generateSite_advanced.py','webapp_main.py','generate_eeat_pages.py']:
    ast.parse(open(f).read())
    print(f'Syntax OK: {f}')

with open('perplexityArticles_eeat_enhanced.json') as f:
    arts = json.load(f)

PILLARS = {'AI Infrastructure','Enterprise Transformation','Smart Mobility','India Digital Transformation'}
cats = Counter(a['category'] for a in arts)
off = {k:v for k,v in cats.items() if k not in PILLARS}
wc_all = [a.get('wordCount',0) or len(a.get('content','').split()) for a in arts]
no_thumb = sum(1 for a in arts if not a.get('thumbnailImageUrl','').strip())
no_og = sum(1 for a in arts if not a.get('ogImage','').strip())
slug_counts = Counter(a.get('slug','') for a in arts)
dupes = {s:n for s,n in slug_counts.items() if n>1 and s}
authors = Counter(a.get('author','') for a in arts)

print(f'\nTotal articles: {len(arts)}')
print(f'Off-pillar:     {off if off else "NONE - clean"}')
print(f'Min word count: {min(wc_all)} | Avg: {int(sum(wc_all)/len(wc_all))}')
print(f'Under 800w:     {sum(1 for w in wc_all if w < 800)}')
print(f'Missing ogImage:      {no_og}')
print(f'Missing thumbnail:    {no_thumb}')
print(f'Duplicate slugs:      {len(dupes)}')
print(f'\nAuthor distribution:')
for a, n in authors.most_common():
    print(f'  {n:5d}  {a}')
print(f'\nCategory distribution:')
for c, n in cats.most_common():
    print(f'  {n:5d}  {c}')

# Check EEAT pages exist
import os
eeat_pages = ['about','editorial-policy','fact-checking-policy','corrections-policy','privacy-policy','terms','contact']
print('\nEEAT pages:')
for p in eeat_pages:
    exists = os.path.exists(f'dist/{p}/index.html')
    print(f'  {"OK" if exists else "MISSING"} dist/{p}/index.html')
