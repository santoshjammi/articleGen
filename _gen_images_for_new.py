import json, os, sys, time, urllib.parse, requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
load_dotenv('./.env')

def pollinations_get(prompt, filepath, retries=8):
    """Download one image from Pollinations, retry on 429 with 30s wait."""
    encoded = urllib.parse.quote(prompt[:300])
    url = (f"https://image.pollinations.ai/prompt/{encoded}"
           "?width=1024&height=1024&model=flux&nologo=true&enhance=true")
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=180)
            if r.status_code == 429:
                wait = 30 + attempt * 10
                print(f"  429 rate-limit, waiting {wait}s (attempt {attempt+1}/{retries})...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            img = Image.open(BytesIO(r.content))
            if img.mode in ('RGBA','LA','P'):
                bg = Image.new('RGB', img.size, (255,255,255))
                if img.mode == 'P': img = img.convert('RGBA')
                bg.paste(img, mask=img.split()[-1])
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(filepath, 'WEBP', quality=85)
            return True
        except Exception as e:
            print(f"  Error attempt {attempt+1}: {e}")
            time.sleep(10)
    return False

with open('perplexityArticles_eeat_enhanced.json') as f:
    arts = json.load(f)

before_slugs = set(open('/tmp/pipeline_before_slugs.txt').read().splitlines())
new_arts = [a for a in arts if a.get('slug') and a['slug'] not in before_slugs]

print(f"Generating images for {len(new_arts)} new articles via Pollinations.ai (sequential, rate-limited)...")
total_ok = 0
total_fail = 0

for a in new_arts:
    slug = a['slug']
    img_dir = f'dist/images/{slug}'
    os.makedirs(img_dir, exist_ok=True)
    title = a.get('title', slug)
    print(f"\n>> {title[:60]}")

    tasks = [
        (f"{img_dir}/main.webp", f"High quality professional photo about: {title}"),
        (f"{img_dir}/thumb.webp", f"Thumbnail image for article about: {title}"),
        (f"{img_dir}/inline_1.webp", f"Illustration for: {title}"),
        (f"{img_dir}/inline_2.webp", f"Technology diagram about: {title}"),
    ]
    for fp, prompt in tasks:
        if os.path.exists(fp) and os.path.getsize(fp) > 1000:
            print(f"  SKIP {os.path.basename(fp)} (exists {os.path.getsize(fp)//1024}KB)")
            continue
        print(f"  Generating {os.path.basename(fp)}...")
        ok = pollinations_get(prompt, fp)
        if ok and os.path.exists(fp) and os.path.getsize(fp) > 1000:
            print(f"  OK   {os.path.basename(fp)} ({os.path.getsize(fp)//1024}KB)")
            total_ok += 1
        else:
            print(f"  FAIL {os.path.basename(fp)}")
            total_fail += 1
        time.sleep(5)  # pause between images

print(f"\nDone — Images: {total_ok} created, {total_fail} failed")
