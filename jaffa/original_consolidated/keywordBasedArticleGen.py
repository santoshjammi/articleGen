#!/usr/bin/env python3
"""
Legacy wrapper for keywordBasedArticleGen.py
Redirects to the new consolidated article_generator.py
"""
import subprocess
import sys

print("⚠️  This script has been replaced by article_generator.py")
print("🔄 Use: python article_generator.py keywords [keywords...]")
print("    or: python article_generator.py interactive")
print()

# Note: This was primarily used as a module, so we just show help
subprocess.run([sys.executable, "article_generator.py", "--help"])
