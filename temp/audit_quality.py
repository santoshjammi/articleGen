#!/usr/bin/env python3
import json
from collections import Counter

with open('perplexityArticles_eeat_enhanced.json') as f:
    arts = json.load(f)

authors = Counter(a.get('author','') for a in arts)
print('Authors:', dict(authors.most_common(5)))

no_og = sum(1 for a in arts if not a.get('ogImage','').strip())
no_thumb = sum(1 for a in arts if not a.get('thumbnailImageUrl','').strip())
print(f'Missing ogImage: {no_og}')
print(f'Missing thumbnailImageUrl: {no_thumb}')

slugs = [a.get('slug','') for a in arts]
slug_counts = Counter(slugs)
dupes = {s:n for s,n in slug_counts.items() if n>1 and s}
print(f'Duplicate slugs: {len(dupes)} ({sum(dupes.values())-len(dupes)} extra articles)')

no_excerpt = sum(1 for a in arts if not a.get('excerpt','').strip())
print(f'Missing excerpts: {no_excerpt}')

wc = [a.get('wordCount',0) for a in arts if a.get('wordCount',0)]
if wc:
    print(f'WordCount - min: {min(wc)}, avg: {int(sum(wc)/len(wc))}, max: {max(wc)}')
    print(f'Articles < 800 words: {sum(1 for w in wc if w<800)}')

no_tags = sum(1 for a in arts if not a.get('tags'))
print(f'Missing tags: {no_tags}')
no_meta = sum(1 for a in arts if not a.get('metaDescription','').strip())
print(f'Missing metaDescription: {no_meta}')
