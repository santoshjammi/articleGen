#!/usr/bin/env python3
"""
Legacy wrapper for quickKeywordGen.py
Redirects to the new consolidated article_generator.py
"""
import subprocess
import sys

print("⚠️  This script has been replaced by article_generator.py")
print("🔄 Redirecting to: python article_generator.py keywords")
print()

if len(sys.argv) > 1:
    subprocess.run([sys.executable, "article_generator.py", "keywords"] + sys.argv[1:])
else:
    subprocess.run([sys.executable, "article_generator.py", "interactive"])
