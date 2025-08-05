#!/usr/bin/env python3
"""
Legacy wrapper for generateArticles.py
Redirects to the new consolidated article_generator.py
"""
import subprocess
import sys

print("⚠️  This script has been replaced by article_generator.py")
print("🔄 Redirecting to: python article_generator.py trends --count 3")
print()

subprocess.run([sys.executable, "article_generator.py", "trends", "--count", "3"] + sys.argv[1:])
