#!/usr/bin/env python3
"""One-shot script: remap remaining legacy categories to PRD pillars."""
import json
from collections import Counter

CATEGORY_MAPPING = {
    'AI Infrastructure': 'AI Infrastructure',
    'Enterprise Transformation': 'Enterprise Transformation',
    'Smart Mobility': 'Smart Mobility',
    'India Digital Transformation': 'India Digital Transformation',
    'Technology': 'AI Infrastructure',
    'Artificial Intelligence': 'AI Infrastructure',
    'Web Development': 'AI Infrastructure',
    'Databases': 'AI Infrastructure',
    'Analysis': 'AI Infrastructure',
    'Business': 'Enterprise Transformation',
    'Business and Finance': 'Enterprise Transformation',
    'Career Development': 'Enterprise Transformation',
    'Health': 'Enterprise Transformation',
    'Marketing': 'Enterprise Transformation',
    'Environment': 'Smart Mobility',
    'Education': 'India Digital Transformation',
    'Politics': 'India Digital Transformation',
}

EDITORIAL_PILLARS = {
    'AI Infrastructure', 'Enterprise Transformation',
    'Smart Mobility', 'India Digital Transformation',
}

with open('perplexityArticles_eeat_enhanced.json') as f:
    articles = json.load(f)

remapped = 0
for a in articles:
    cat = a.get('category', '')
    if cat not in EDITORIAL_PILLARS:
        a['category'] = CATEGORY_MAPPING.get(cat, 'AI Infrastructure')
        remapped += 1

print(f'Remapped {remapped} articles to pillars')
dist = Counter(a['category'] for a in articles)
for pillar, n in dist.most_common():
    print(f'  {n:5d}  {pillar}')

with open('perplexityArticles_eeat_enhanced.json', 'w') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)
print('Saved.')
