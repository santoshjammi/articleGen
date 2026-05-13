#!/usr/bin/env python3
"""
Editorial Structure Enforcer
Country's News — Phase 1 Transformation

Replaces the old keyword-stuffing header enhancer.
This script:
  1. Validates the 7-part mandatory article structure
  2. Strips prohibited heading patterns (keyword stuffing, generic SEO openers)
  3. Normalises categories to the 4 editorial pillars
  4. Reports article-level editorial quality scores
  5. Marks articles as structure-validated for tracking

Does NOT call any external API. Text processing only.
"""

import json
import re
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import shutil

# ── Constants ────────────────────────────────────────────────────────────────

ARTICLES_FILE = "perplexityArticles_eeat_enhanced.json"

# The 7-part mandatory structure (order matters for scoring)
MANDATORY_SECTIONS = [
    "context",
    "why this matters",
    "operational implications",
    "economic implications",
    "winners and losers",
    "future outlook",
    "strategic takeaway",
]

# Heading patterns that are explicitly prohibited by editorial rules
PROHIBITED_HEADING_PATTERNS = [
    r"^what is .{2,50}\?$",                    # "What is X?" openers
    r"^.{2,40} - complete guide$",             # "X - Complete Guide"
    r"^.{2,40} - (ultimate|comprehensive) guide$",
    r"^how .{2,40} works$",                    # "How X Works"
    r"^best .{2,40} practices$",               # "Best X Practices"
    r"^.{2,40} best practices( in .+)?$",
    r"^.{2,40} tips( and tricks)?$",           # "X Tips and Tricks"
    r"^.{2,40} for beginners$",                # "X for Beginners"
    r"^(top|best) \d+ .{2,40}$",              # "Top 10 X"
    r"^.{2,40}: complete guide$",
    r"^.{2,40}: ultimate guide$",
    r"^introduction to .{2,40}$",              # "Introduction to X"
    r"^overview of .{2,40}$",                  # "Overview of X"
    r"^everything you need to know about .+$", # "Everything you need to know..."
]

# Prohibited body text patterns (fake statistics, filler)
PROHIBITED_BODY_PATTERNS = [
    (r"recent studies show", "vague fabricated statistic"),
    (r"industry surveys indicate", "vague fabricated statistic"),
    (r"according to experts", "vague unattributed claim"),
    (r"studies have shown", "vague fabricated statistic"),
    (r"research shows", "vague unattributed claim"),
    (r"revolutionary", "hype language"),
    (r"game.changing", "hype language"),
    (r"groundbreaking", "hype language"),
    (r"unprecedented", "hype language"),
    (r"in today's (fast.paced|ever.changing|rapidly evolving) world", "generic filler opener"),
    (r"in the (fast.paced|ever.changing|rapidly evolving) (world|landscape)", "generic filler opener"),
]

EDITORIAL_PILLARS = [
    'AI Infrastructure',
    'Enterprise Transformation',
    'Smart Mobility',
    'India Digital Transformation',
]


# ── Core Class ────────────────────────────────────────────────────────────────

class ExistingArticleHeaderEnhancer:
    """Validate and enforce editorial standards on existing articles.

    The class name is intentionally kept the same so that the import in
    super_article_manager.py continues to work without changes.
    """

    def __init__(self, articles_file: str = ARTICLES_FILE):
        self.articles_file = articles_file
        self.backup_file = (
            f"{articles_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

    def create_backup(self) -> None:
        shutil.copy2(self.articles_file, self.backup_file)
        print(f"📁 Backup: {self.backup_file}")

    # ── Structure validation ──────────────────────────────────────────────

    def detect_present_sections(self, content: str) -> List[str]:
        """Return which of the 7 mandatory sections are present in the article."""
        headings = re.findall(r'<h2[^>]*>(.*?)</h2>', content, re.IGNORECASE | re.DOTALL)
        headings += re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        heading_text = ' '.join(re.sub(r'<[^>]+>', '', h).lower() for h in headings)

        found = []
        for section in MANDATORY_SECTIONS:
            key_words = section.replace(" and ", " ").split()
            if all(w in heading_text for w in key_words[:2]):
                found.append(section)
        return found

    def structure_score(self, content: str) -> Tuple[int, List[str], List[str]]:
        """Returns (score 0–100, present_sections, missing_sections)."""
        present = self.detect_present_sections(content)
        missing = [s for s in MANDATORY_SECTIONS if s not in present]
        score = round(len(present) / len(MANDATORY_SECTIONS) * 100)
        return score, present, missing

    # ── Prohibited pattern detection ─────────────────────────────────────

    def find_prohibited_headings(self, content: str) -> List[str]:
        """Return list of headings that match prohibited patterns."""
        headings = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', content, re.IGNORECASE | re.DOTALL)
        headings += re.findall(r'^#{2,3}\s+(.+)$', content, re.MULTILINE)
        headings = [re.sub(r'<[^>]+>', '', h).strip().lower() for h in headings]

        bad = []
        for heading in headings:
            for pattern in PROHIBITED_HEADING_PATTERNS:
                if re.fullmatch(pattern, heading):
                    bad.append(heading)
                    break
        return bad

    def find_prohibited_body_patterns(self, content: str) -> List[Tuple[str, str]]:
        """Return list of (matched_text, reason) for body-level prohibited patterns."""
        clean = re.sub(r'<[^>]+>', '', content).lower()
        findings = []
        for pattern, reason in PROHIBITED_BODY_PATTERNS:
            for match in re.finditer(pattern, clean):
                findings.append((match.group(0), reason))
        return findings

    # ── Heading cleanup ───────────────────────────────────────────────────

    def _strip_keyword_stuffing(self, heading_text: str) -> str:
        """Remove mechanical keyword additions injected by the old enhancer."""
        text = re.sub(r'^[^:]{3,40}:\s+', '', heading_text)
        text = re.sub(r'\s+with\s+[^:]{3,40}$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+for\s+[^:]{3,40}$', '', text, flags=re.IGNORECASE)
        return text.strip()

    def clean_stuffed_headings(self, content: str) -> Tuple[str, int]:
        """Remove keyword-stuffing patterns from headings. Returns (content, n_cleaned)."""
        cleaned = 0

        def clean_html(m):
            nonlocal cleaned
            tag, inner = m.group(1), m.group(2)
            inner_text = re.sub(r'<[^>]+>', '', inner).strip()
            new_text = self._strip_keyword_stuffing(inner_text)
            if new_text != inner_text:
                cleaned += 1
                return f"<{tag}>{new_text}</{tag}>"
            return m.group(0)

        def clean_md(m):
            nonlocal cleaned
            hashes, text = m.group(1), m.group(2).strip()
            new_text = self._strip_keyword_stuffing(text)
            if new_text != text:
                cleaned += 1
                return f"{hashes} {new_text}"
            return m.group(0)

        content = re.sub(r'<(h[23])[^>]*>(.*?)</h[23]>', clean_html,
                         content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'^(#{2,3})\s+(.+)$', clean_md, content, flags=re.MULTILINE)
        return content, cleaned

    # ── Category normalisation ────────────────────────────────────────────

    def normalise_category(self, category: str) -> str:
        """Map any category string to the nearest editorial pillar."""
        if category in EDITORIAL_PILLARS:
            return category
        cat = category.lower()
        if any(k in cat for k in ['ai', 'llm', 'inference', 'gpu', 'model', 'agent', 'coding', 'compute']):
            return 'AI Infrastructure'
        if any(k in cat for k in ['enterprise', 'saas', 'erp', 'automation', 'workflow', 'business', 'finance']):
            return 'Enterprise Transformation'
        if any(k in cat for k in ['ev', 'electric', 'mobility', 'vehicle', 'battery', 'logistics', 'robotics', 'environment']):
            return 'Smart Mobility'
        return 'India Digital Transformation'

    # ── Per-article processing ────────────────────────────────────────────

    def enhance_article(self, article: Dict) -> Dict:
        """Validate and clean a single article. Returns a result dict."""
        content = article.get('content', '')
        if not content:
            return {'enhanced': False, 'reason': 'no_content'}

        result: Dict = {
            'enhanced': False,
            'title': article.get('title', '')[:60],
            'changes': [],
            'warnings': [],
        }

        # 1. Structure score
        score, present, missing = self.structure_score(content)
        result['structure_score'] = score
        result['sections_present'] = present
        result['sections_missing'] = missing
        if missing:
            result['warnings'].append(f"Missing sections: {', '.join(missing)}")

        # 2. Strip keyword-stuffed headings (old enhancer artefacts)
        if article.get('enhanced_headers'):
            cleaned_content, n_cleaned = self.clean_stuffed_headings(content)
            if n_cleaned > 0:
                article['content'] = cleaned_content
                result['changes'].append(f"Cleaned {n_cleaned} keyword-stuffed headings")
                article.pop('enhanced_headers', None)
                article.pop('main_keyword_enhanced', None)
                article.pop('enhanced_headers_count', None)
                content = cleaned_content

        # 3. Prohibited heading check (informational)
        bad_headings = self.find_prohibited_headings(content)
        if bad_headings:
            result['warnings'].append(
                f"Prohibited headings ({len(bad_headings)}): " +
                "; ".join(bad_headings[:3])
            )

        # 4. Prohibited body patterns (informational)
        bad_body = self.find_prohibited_body_patterns(content)
        if bad_body:
            result['warnings'].append(
                f"Prohibited body patterns ({len(bad_body)}): " +
                ", ".join(set(r for _, r in bad_body))
            )

        # 5. Category normalisation
        original_cat = article.get('category', '')
        normalised_cat = self.normalise_category(original_cat)
        if normalised_cat != original_cat:
            article['category'] = normalised_cat
            result['changes'].append(f"Category: '{original_cat}' → '{normalised_cat}'")

        # 6. Stamp editorial validation metadata
        article['editorial_validated'] = True
        article['editorial_validation_date'] = datetime.now().isoformat()
        article['structure_score'] = score

        if result['changes']:
            result['enhanced'] = True

        return result

    # ── Batch processing ──────────────────────────────────────────────────

    def enhance_all_articles(self, max_articles: Optional[int] = None, backup: bool = True) -> Dict:
        """Process all articles: validate structure, clean headings, normalise categories."""
        print("🔍 Editorial Structure Enforcer — Country's News Phase 1")
        print("=" * 60)

        if backup:
            self.create_backup()

        try:
            with open(self.articles_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        except Exception as e:
            return {'error': str(e), 'success': False}

        if max_articles:
            articles = articles[:max_articles]

        total = len(articles)
        print(f"📊 Processing {total} articles...\n")

        changed_count = 0
        warning_count = 0
        structure_scores = []
        category_fixes = 0

        for i, article in enumerate(articles, 1):
            result = self.enhance_article(article)
            if not result.get('enhanced') and not result.get('warnings'):
                pass  # silently skip unchanged articles

            if result.get('changes'):
                changed_count += 1
                if any('Category' in c for c in result['changes']):
                    category_fixes += 1

            if result.get('warnings'):
                warning_count += 1

            score = result.get('structure_score', 0)
            if isinstance(score, int):
                structure_scores.append(score)

            # Verbose output for first 5 and every 100
            if i <= 5 or i % 100 == 0:
                status = "✅" if score >= 70 else ("⚠️ " if score >= 40 else "❌")
                print(f"{status} [{i}/{total}] {result.get('title', '')}")
                print(f"   Structure: {score}% | Sections: {len(result.get('sections_present', []))}/7")
                if result.get('changes'):
                    print(f"   Changes:  {'; '.join(result['changes'])}")
                if result.get('warnings'):
                    print(f"   Warnings: {result['warnings'][0][:80]}")
                print()

        # Save
        try:
            with open(self.articles_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            return {'error': f'Save failed: {str(e)}', 'success': False}

        avg_score = round(sum(structure_scores) / len(structure_scores)) if structure_scores else 0
        fully_structured = sum(1 for s in structure_scores if s == 100)
        needs_work = sum(1 for s in structure_scores if s < 40)

        print("=" * 60)
        print("📋 Editorial Validation Complete")
        print(f"   Articles processed:       {total}")
        print(f"   Articles changed:         {changed_count}")
        print(f"   Category fixes:           {category_fixes}")
        print(f"   Articles with warnings:   {warning_count}")
        print(f"   Avg structure score:      {avg_score}%")
        print(f"   Fully structured (100%):  {fully_structured}")
        print(f"   Needs rewrite (<40%):     {needs_work}")
        print()
        print("💡 Articles scoring <40% should be regenerated with the updated prompt.")

        return {
            'success': True,
            'total_articles': total,
            'enhanced_count': changed_count,
            'category_fixes': category_fixes,
            'warning_count': warning_count,
            'avg_structure_score': avg_score,
            'fully_structured': fully_structured,
            'needs_rewrite': needs_work,
            'backup_file': self.backup_file,
        }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Validate and enforce editorial structure on existing articles"
    )
    parser.add_argument('--max-articles', type=int,
                        help='Limit to N articles (for testing)')
    parser.add_argument('--file', default=ARTICLES_FILE,
                        help='Articles JSON file to process')
    parser.add_argument('--no-backup', action='store_true',
                        help='Skip creating a backup before processing')
    args = parser.parse_args()

    enforcer = ExistingArticleHeaderEnhancer(args.file)
    results = enforcer.enhance_all_articles(
        max_articles=args.max_articles,
        backup=not args.no_backup,
    )

    if results.get('success'):
        print("\n✅ Editorial enforcement completed.")
        return True
    else:
        print(f"\n❌ Failed: {results.get('error', 'Unknown error')}")
        return False


if __name__ == "__main__":
    exit(0 if main() else 1)
