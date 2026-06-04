#!/usr/bin/env python3
"""
Smoke-test all pipeline components without actually calling any external API
or writing new articles. Validates imports, config, and file structure.
"""
import sys, os, json
sys.path.insert(0, '.')

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
WARN = "\033[33mWARN\033[0m"

def check(label, fn):
    try:
        result = fn()
        if result is True or result is None:
            print(f"  {PASS}  {label}")
            return True
        elif isinstance(result, str) and result.startswith("WARN"):
            print(f"  {WARN}  {label}: {result[5:]}")
            return True
        else:
            print(f"  {FAIL}  {label}: {result}")
            return False
    except Exception as e:
        print(f"  {FAIL}  {label}: {e}")
        return False

failures = 0

print("\n=== 1. Module imports ===")
for mod in ['super_article_manager', 'generateSite_advanced', 'getTrendInput',
            'generate_eeat_pages', 'generateJsonApi', 'daily_trend_filter',
            'webapp_main']:
    if not check(f"import {mod}", lambda m=mod: __import__(m) and True):
        failures += 1

print("\n=== 2. Environment variables ===")
import check_env as _ce  # noqa — just validate import
required_env = ['OPENROUTER_API_KEY', 'FTP_HOST', 'FTP_USER', 'FTP_PASS']
for var in required_env:
    def _chk(v=var):
        val = os.environ.get(v, '')
        if not val:
            return f"WARN not set (pipeline will degrade gracefully)"
        return True
    check(f"env {var}", _chk)

print("\n=== 3. Data file integrity ===")
def _articles():
    with open('perplexityArticles_eeat_enhanced.json') as f:
        arts = json.load(f)
    assert len(arts) >= 3500, f"Only {len(arts)} articles"
    offpillar = [a for a in arts if a.get('category') not in (
        'AI Infrastructure','Enterprise Transformation',
        'Smart Mobility','India Digital Transformation')]
    assert offpillar == [], f"{len(offpillar)} off-pillar articles"
    no_author = [a for a in arts if not a.get('author') or
                 a['author'] in ('', 'JAMSA - Country\'s News', 'Editorial Team')]
    assert no_author == [], f"{len(no_author)} articles with bad author"
    return True

for label, fn in [
    ("perplexityArticles_eeat_enhanced.json readable + clean", _articles),
    ("dist/ directory exists", lambda: os.path.isdir('dist') or "WARN dist/ missing — run generateSite_advanced.py"),
    ("dist/index.html present", lambda: os.path.isfile('dist/index.html') or "WARN missing homepage"),
    ("dist/sitemap.xml present", lambda: os.path.isfile('dist/sitemap.xml') or "WARN missing sitemap"),
    ("dist/rss.xml present", lambda: os.path.isfile('dist/rss.xml') or "WARN missing RSS"),
]:
    if not check(label, fn):
        failures += 1

print("\n=== 4. EEAT pages ===")
for slug in ['about','editorial-policy','fact-checking-policy',
             'corrections-policy','privacy-policy','terms','contact']:
    path = f'dist/{slug}/index.html'
    if not check(path, lambda p=path: os.path.isfile(p) or f"missing {p}"):
        failures += 1

print("\n=== 5. Pillar-alignment filter (getTrendInput) ===")
from getTrendInput import _is_pillar_aligned
cases = [
    ('NVIDIA GPU cluster 2026', True),
    ('IPL 2026 winner', False),
    ('RCB vs CSK scorecard', False),
    ('AI in cricket analytics', True),
    ('UPI digital payments India', True),
    ('Shah Rukh Khan movie review', False),
    ('electric vehicle subsidy India', True),
    ('Bigg Boss winner 2026', False),
]
for kw, expected in cases:
    actual = _is_pillar_aligned(kw)
    if not check(f"filter({kw!r}) == {expected}", lambda a=actual, e=expected: a == e or f"got {a}"):
        failures += 1

print("\n=== 6. auto_publish.sh structure ===")
def _autopublish():
    with open('auto_publish.sh') as f:
        content = f.read()
    for step in ['generateSite_advanced.py', 'generateJsonApi.py', 'generate_eeat_pages.py']:
        assert step in content, f"{step} not wired into auto_publish.sh"
    return True
if not check("auto_publish.sh has all pipeline steps", _autopublish):
    failures += 1

print("\n=== 7. Quality gate constants ===")
import super_article_manager as sam
def _qgate():
    assert hasattr(sam, 'QUALITY_MIN_SCORE'), "QUALITY_MIN_SCORE missing"
    assert sam.QUALITY_MIN_SCORE == 60, f"Expected 60, got {sam.QUALITY_MIN_SCORE}"
    assert hasattr(sam, 'QUALITY_MIN_WORDS'), "QUALITY_MIN_WORDS missing"
    assert sam.QUALITY_MIN_WORDS == 800, f"Expected 800, got {sam.QUALITY_MIN_WORDS}"
    assert hasattr(sam, '_AUTHOR_PERSONAS'), "_AUTHOR_PERSONAS missing"
    assert len(sam._AUTHOR_PERSONAS) == 3, f"Expected 3 personas, got {len(sam._AUTHOR_PERSONAS)}"
    return True
if not check("Quality gate + personas configured correctly", _qgate):
    failures += 1

print()
if failures:
    print(f"{'='*50}")
    print(f"RESULT: {failures} check(s) FAILED")
    sys.exit(1)
else:
    print(f"{'='*50}")
    print("RESULT: All checks passed ✅")
    sys.exit(0)
