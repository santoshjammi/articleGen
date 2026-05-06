import os, json

before_slugs = set(open('/tmp/pipeline_before_slugs.txt').read().splitlines())

with open('perplexityArticles_eeat_enhanced.json') as f:
    arts = json.load(f)

new_arts = [a for a in arts if a.get('slug') and a['slug'] not in before_slugs]

print("=== SESSION TRACKING REPORT ===\n")
print(f"ARTICLES: {len(before_slugs)} -> {len(arts)} (+{len(new_arts)} new)\n")
print("NEW ARTICLES:")
total_imgs = 0
for a in new_arts:
    slug = a['slug']
    d = 'dist/images/' + slug
    imgs = [f for f in os.listdir(d) if f.endswith('.webp') and os.path.getsize(d+'/'+f)>1000] if os.path.isdir(d) else []
    total_imgs += len(imgs)
    words = a.get('wordCount', a.get('word_count', '?'))
    cat = a.get('category', '?')
    status = "OK" if len(imgs) >= 4 else "PARTIAL"
    print(f"  [{len(imgs)}/4 imgs | {words} words | {cat}] [{status}]")
    print(f"    {a['title'][:70]}")

current_imgs = sum(1 for r, d, fs in os.walk('dist/images') for f in fs if f.endswith('.webp'))
print(f"\nIMAGES: 6948 -> {current_imgs} (+{current_imgs - 6948})")
print(f"  New article images: {total_imgs}/36")

print("\nFTP SYNC:")
print("  Run 1: 6072/6078 files, 223 MB, 27 min  (6 failures: 3 images + 3 HTML)")
print("  Run 2:   35/35 files,  new images, 21s   (0 failures)")
print("  TOTAL:  6107 files successfully synced to 212.1.209.3/public_html")

print("\nFAILED KEYWORDS (LLM JSON parse errors - can be retried):")
for kw in ['machine learning', 'ai agents', 'deep learning', 'AI INferences', 'sagemaker ai', 'ai models']:
    print(f"  - {kw}")
