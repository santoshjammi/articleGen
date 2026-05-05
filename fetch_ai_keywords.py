#!/usr/bin/env python3
"""
fetch_ai_keywords.py
Fetches trending AI-related topics from free public sources and appends
new ones to custom_keywords.txt for article generation.

Sources used (all no-auth, no API key required):
  1. Hacker News Algolia API  — top AI stories
  2. Google News RSS          — AI / machine learning news
  3. Reddit RSS               — r/artificial, r/MachineLearning
"""

import os
import re
import sys
import json
import time
import html
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# ── Config ─────────────────────────────────────────────────────────────────
KEYWORDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_keywords.txt")
MAX_KEYWORDS   = 10        # max new keywords to add per run
MIN_WORD_LEN   = 4         # discard tokens shorter than this
MAX_KW_WORDS   = 7         # discard keyphrases longer than this many words
REQUEST_TIMEOUT = 15       # seconds per HTTP request

# Noise words to strip from extracted titles
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "this", "that", "are", "was",
    "be", "been", "has", "have", "had", "will", "would", "can", "could",
    "should", "do", "does", "did", "new", "how", "what", "why", "when",
    "who", "show", "hn", "ask", "tell", "using", "via", "into", "as",
    "its", "your", "our", "their", "my", "we", "you", "he", "she", "they",
    "i", "us", "about", "up", "out", "if", "not", "no", "so", "than",
    "more", "just", "also", "use", "get", "make", "his", "her", "which",
}

# Core AI terms — at least one must appear in a title for it to qualify
AI_TERMS = {
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "llm", "large language model", "gpt", "chatgpt", "claude", "gemini",
    "openai", "anthropic", "mistral", "llama", "transformer", "neural",
    "diffusion", "generative", "rag", "agent", "inference", "fine-tun",
    "reinforcement learning", "computer vision", "nlp", "natural language",
    "stable diffusion", "hugging face", "huggingface", "copilot", "midjourney",
    "sora", "gemma", "flux", "bert", "embedding", "vector database",
    "multimodal", "foundation model", "alignment", "agi", "robotics",
}

HEADERS = {
    "User-Agent": "articleGen/1.0 (keyword fetcher; +https://countrysnews.com)",
    "Accept": "application/json, application/xml, text/html, */*",
}

# ── Helpers ─────────────────────────────────────────────────────────────────

def _fetch(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return resp.read()
    except Exception as e:
        print(f"  ⚠️  Could not fetch {url}: {e}")
        return None


def _is_ai_related(text: str) -> bool:
    t = text.lower()
    return any(term in t for term in AI_TERMS)


def _clean_title(title: str) -> str:
    """Strip HTML entities and common noise, return lowercase cleaned title."""
    title = html.unescape(title)
    # Remove parenthetical year suffixes like (2025)
    title = re.sub(r'\s*\(\d{4}\)\s*', ' ', title)
    # Remove leading dashes/bullets (common in arXiv feed titles)
    title = re.sub(r'^\s*[-–—•]+\s*', '', title)
    # Remove markdown/special chars except apostrophes
    title = re.sub(r'[^\w\s\']', ' ', title)
    return re.sub(r'\s+', ' ', title).strip()


def _extract_keyphrases(title: str, max_words: int = MAX_KW_WORDS) -> list[str]:
    """
    Extract candidate keyphrases from a title.
    Strategy: try the full cleaned title first, then noun-phrase windows.
    """
    title = _clean_title(title)
    candidates = set()

    # Full title as-is (if short enough)
    words = title.split()
    if 2 <= len(words) <= max_words:
        candidates.add(title.lower())

    # Sliding windows 2..max_words
    for size in range(2, min(len(words) + 1, max_words + 1)):
        for i in range(len(words) - size + 1):
            phrase = " ".join(words[i:i+size]).lower()
            # Must not start/end with a stop word
            phrase_words = phrase.split()
            if phrase_words[0] in STOP_WORDS or phrase_words[-1] in STOP_WORDS:
                continue
            # Must contain at least one non-stop word ≥ MIN_WORD_LEN
            if not any(len(w) >= MIN_WORD_LEN and w not in STOP_WORDS for w in phrase_words):
                continue
            candidates.add(phrase)

    return list(candidates)


def _score_phrases(phrases: list[str], source_titles: list[str]) -> dict[str, int]:
    """Score each phrase by frequency, with a length bonus for more specific phrases."""
    scores: dict[str, int] = {}
    lowered_titles = [t.lower() for t in source_titles]
    for phrase in phrases:
        count = sum(1 for t in lowered_titles if phrase in t)
        if count > 0:
            # Bonus for longer (more specific) phrases, penalty for very generic 2-word phrases
            word_count = len(phrase.split())
            specificity_bonus = word_count - 1  # 3-word = +2, 4-word = +3, etc.
            scores[phrase] = scores.get(phrase, 0) + count + specificity_bonus
    return scores


def _load_existing_keywords() -> set[str]:
    """Return the set of non-comment lines already in custom_keywords.txt."""
    existing = set()
    if not os.path.exists(KEYWORDS_FILE):
        return existing
    with open(KEYWORDS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                existing.add(line.lower())
    return existing


# ── Source fetchers ─────────────────────────────────────────────────────────

def fetch_hackernews_ai(limit: int = 100) -> list[str]:
    """Top HN stories that mention AI terms."""
    print("  📡 Hacker News…", end=" ", flush=True)
    url = (
        "https://hn.algolia.com/api/v1/search?"
        "query=AI+artificial+intelligence+LLM&"
        "tags=story&"
        f"hitsPerPage={limit}&"
        "numericFilters=points%3E20"
    )
    data = _fetch(url)
    if not data:
        return []
    try:
        hits = json.loads(data).get("hits", [])
        titles = [h.get("title", "") for h in hits if _is_ai_related(h.get("title", ""))]
        print(f"{len(titles)} AI stories")
        return titles
    except Exception as e:
        print(f"parse error: {e}")
        return []


def _parse_rss_titles(data: bytes) -> list[str]:
    """Parse RSS/Atom XML and return item titles."""
    try:
        root = ET.fromstring(data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        titles = []
        # RSS 2.0
        for item in root.findall(".//item"):
            t = item.findtext("title", "")
            if t:
                titles.append(t)
        # Atom
        for entry in root.findall(".//atom:entry", ns):
            t = entry.findtext("atom:title", "", ns)
            if t:
                titles.append(t)
        return titles
    except Exception as e:
        print(f"XML parse error: {e}")
        return []


def fetch_google_news_ai() -> list[str]:
    """Google News RSS for AI topics."""
    print("  📡 Google News RSS…", end=" ", flush=True)
    queries = ["artificial+intelligence", "machine+learning+LLM", "AI+tools+2025"]
    all_titles: list[str] = []
    for q in queries:
        url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
        data = _fetch(url)
        if data:
            titles = [t for t in _parse_rss_titles(data) if _is_ai_related(t)]
            all_titles.extend(titles)
        time.sleep(0.5)
    print(f"{len(all_titles)} headlines")
    return all_titles


def fetch_reddit_ai() -> list[str]:
    """Top posts from AI-focused subreddits via JSON API."""
    print("  📡 Reddit AI subreddits…", end=" ", flush=True)
    subreddits = ["artificial", "MachineLearning", "LocalLLaMA", "ChatGPT"]
    titles: list[str] = []
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/top.json?limit=25&t=week"
        data = _fetch(url)
        if not data:
            continue
        try:
            posts = json.loads(data).get("data", {}).get("children", [])
            for p in posts:
                title = p.get("data", {}).get("title", "")
                if _is_ai_related(title):
                    titles.append(title)
        except Exception:
            pass
        time.sleep(0.5)
    print(f"{len(titles)} posts")
    return titles


def fetch_arxiv_ai() -> list[str]:
    """Recent AI/ML paper titles from arXiv Atom feed (no auth needed)."""
    print("  📡 arXiv cs.AI / cs.LG…", end=" ", flush=True)
    url = (
        "https://export.arxiv.org/rss/cs.AI+cs.LG"
    )
    data = _fetch(url)
    if not data:
        return []
    titles = [t for t in _parse_rss_titles(data) if _is_ai_related(t)]
    # Paper titles are often too technical; take only short ones
    titles = [t for t in titles if len(t.split()) <= 10]
    print(f"{len(titles)} papers")
    return titles


# ── Main ────────────────────────────────────────────────────────────────────

def fetch_ai_keywords(max_keywords: int = MAX_KEYWORDS, dry_run: bool = False) -> list[str]:
    """
    Fetch trending AI keywords from multiple sources, rank them,
    and append new ones to custom_keywords.txt.
    Returns the list of newly added keywords.
    """
    print("\n🤖 Fetching trending AI keywords…")
    print("─" * 50)

    existing = _load_existing_keywords()
    print(f"ℹ️  {len(existing)} keyword(s) already in {os.path.basename(KEYWORDS_FILE)}")

    # Collect all titles from all sources
    all_titles: list[str] = []
    all_titles.extend(fetch_hackernews_ai())
    all_titles.extend(fetch_google_news_ai())
    all_titles.extend(fetch_reddit_ai())
    all_titles.extend(fetch_arxiv_ai())

    print(f"\n📊 Total raw titles collected: {len(all_titles)}")

    if not all_titles:
        print("❌ No titles fetched — check network connectivity")
        return []

    # Build candidate phrases from all titles
    all_phrases: list[str] = []
    for title in all_titles:
        if _is_ai_related(title):
            all_phrases.extend(_extract_keyphrases(title))

    # Score each phrase
    scores = _score_phrases(all_phrases, all_titles)

    # Rank and filter
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Must be AI-related, not already stored, not all stop-words
    # Also skip phrases that are substrings of a phrase we already picked
    new_keywords: list[str] = []
    picked_set: list[str] = []
    for phrase, score in ranked:
        if len(new_keywords) >= max_keywords:
            break
        phrase_lower = phrase.lower().strip()
        if phrase_lower in existing:
            continue
        if not _is_ai_related(phrase_lower):
            continue
        phrase_words = phrase_lower.split()
        if all(w in STOP_WORDS for w in phrase_words):
            continue
        # Skip if this phrase is a strict substring of an already-picked phrase
        if any(phrase_lower in p for p in picked_set):
            continue
        # Skip if an already-picked phrase is a strict substring of this one (keep the longer)
        picked_set = [p for p in picked_set if p not in phrase_lower]
        new_keywords.append(phrase)
        picked_set.append(phrase_lower)
        existing.add(phrase_lower)   # prevent duplicates within this run

    if not new_keywords:
        print("\nℹ️  No new AI keywords found (all already present or filtered out)")
        return []

    print(f"\n✅ {len(new_keywords)} new keyword(s) to add:")
    for kw in new_keywords:
        print(f"   • {kw}")

    if dry_run:
        print("\n(dry-run — not writing to file)")
        return new_keywords

    # Append to custom_keywords.txt
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open(KEYWORDS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n# Auto-fetched AI keywords — {timestamp}\n")
        for kw in new_keywords:
            f.write(f"{kw}\n")

    print(f"\n💾 Appended to {KEYWORDS_FILE}")
    return new_keywords


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    max_kw = MAX_KEYWORDS
    for arg in sys.argv[1:]:
        if arg.startswith("--max="):
            try:
                max_kw = int(arg.split("=")[1])
            except ValueError:
                pass

    added = fetch_ai_keywords(max_keywords=max_kw, dry_run=dry_run)
    sys.exit(0 if added is not None else 1)
