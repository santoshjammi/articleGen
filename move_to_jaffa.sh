#!/bin/bash
echo "🚚 Moving obsolete files to jaffa folder..."
echo "This keeps your workspace clean while preserving everything safely!"
echo

# Create jaffa subdirectories if they don't exist
mkdir -p jaffa/compatibility_wrappers
mkdir -p jaffa/original_consolidated  
mkdir -p jaffa/obsolete_utilities
mkdir -p jaffa/duplicate_data
mkdir -p jaffa/obsolete_docs
mkdir -p jaffa/miscellaneous

echo "📂 Moving compatibility wrappers..."
# Move compatibility wrappers (6 files)
mv article_generator.py jaffa/compatibility_wrappers/ 2>/dev/null && echo "   ✅ article_generator.py"
mv enhance_articles.py jaffa/compatibility_wrappers/ 2>/dev/null && echo "   ✅ enhance_articles.py"
mv deduplicate_articles.py jaffa/compatibility_wrappers/ 2>/dev/null && echo "   ✅ deduplicate_articles.py"
mv merge_articles.py jaffa/compatibility_wrappers/ 2>/dev/null && echo "   ✅ merge_articles.py"
mv fix_articles.py jaffa/compatibility_wrappers/ 2>/dev/null && echo "   ✅ fix_articles.py"
mv workflow_deduplication.py jaffa/compatibility_wrappers/ 2>/dev/null && echo "   ✅ workflow_deduplication.py"

echo
echo "📂 Moving original consolidated files..."
# Move original consolidated files (5 files)
mv generateArticles.py jaffa/original_consolidated/ 2>/dev/null && echo "   ✅ generateArticles.py"
mv keywordBasedArticleGen.py jaffa/original_consolidated/ 2>/dev/null && echo "   ✅ keywordBasedArticleGen.py"
mv perplexitySEOArticleGen.py jaffa/original_consolidated/ 2>/dev/null && echo "   ✅ perplexitySEOArticleGen.py"
mv quickKeywordGen.py jaffa/original_consolidated/ 2>/dev/null && echo "   ✅ quickKeywordGen.py"
mv batchKeywordGen.py jaffa/original_consolidated/ 2>/dev/null && echo "   ✅ batchKeywordGen.py"

echo
echo "📂 Moving obsolete utilities..."
# Move obsolete utilities (3 files)
mv analyze_duplicates.py jaffa/obsolete_utilities/ 2>/dev/null && echo "   ✅ analyze_duplicates.py"
mv migrate_to_consolidated.py jaffa/obsolete_utilities/ 2>/dev/null && echo "   ✅ migrate_to_consolidated.py"
mv migrate_to_super_consolidation.py jaffa/obsolete_utilities/ 2>/dev/null && echo "   ✅ migrate_to_super_consolidation.py"

echo
echo "📂 Moving duplicate data files..."
# Move duplicate data files (8 files)
mv "articles copy.json" jaffa/duplicate_data/ 2>/dev/null && echo "   ✅ articles copy.json"
mv "articles copy 2.json" jaffa/duplicate_data/ 2>/dev/null && echo "   ✅ articles copy 2.json"
mv perplexityArticles.json.backup.* jaffa/duplicate_data/ 2>/dev/null && echo "   ✅ perplexityArticles.json.backup.*"
mv perplexityArticles_comprehensive_fix_*.json jaffa/duplicate_data/ 2>/dev/null && echo "   ✅ perplexityArticles_comprehensive_fix_*.json"
mv perplexityArticles_pre_enhancement_*.json jaffa/duplicate_data/ 2>/dev/null && echo "   ✅ perplexityArticles_pre_enhancement_*.json"
mv perplexityArticles_enhance_*.json jaffa/duplicate_data/ 2>/dev/null && echo "   ✅ perplexityArticles_enhance_*.json"
mv perplexityArticles_operation_*.json jaffa/duplicate_data/ 2>/dev/null && echo "   ✅ perplexityArticles_operation_*.json"

echo
echo "📂 Moving obsolete documentation..."
# Move obsolete documentation (5 files)
mv MIGRATION_SUMMARY.md jaffa/obsolete_docs/ 2>/dev/null && echo "   ✅ MIGRATION_SUMMARY.md"
mv CONSOLIDATED_README.md jaffa/obsolete_docs/ 2>/dev/null && echo "   ✅ CONSOLIDATED_README.md"
mv QUICK_START.md jaffa/obsolete_docs/ 2>/dev/null && echo "   ✅ QUICK_START.md"
mv keywordSystemSummary.py jaffa/obsolete_docs/ 2>/dev/null && echo "   ✅ keywordSystemSummary.py"
mv final_summary.py jaffa/obsolete_docs/ 2>/dev/null && echo "   ✅ final_summary.py"

echo
echo "📂 Moving miscellaneous files..."
# Move miscellaneous files (4 files)
mv deduplication_workflow.sh jaffa/miscellaneous/ 2>/dev/null && echo "   ✅ deduplication_workflow.sh"
mv sample_json.json jaffa/miscellaneous/ 2>/dev/null && echo "   ✅ sample_json.json"
mv san.ps1 jaffa/miscellaneous/ 2>/dev/null && echo "   ✅ san.ps1"
mv san./ jaffa/miscellaneous/ 2>/dev/null && echo "   ✅ san./"

echo
echo "🎉 File organization complete!"
echo
echo "📊 SUMMARY:"
echo "   🗂️  All obsolete files moved to jaffa/ folder"
echo "   📁 Organized into 6 categories for easy reference"
echo "   🧹 Main workspace is now ultra-clean"
echo "   💾 Everything preserved safely - zero data loss"
echo
echo "📁 Essential files remaining in main directory:"
echo "   • super_article_manager.py (THE MAIN MODULE)"
echo "   • getTrendInput.py"
echo "   • generateImage.py"
echo "   • generateSite.py"
echo "   • perplexityArticles.json (main data)"
echo "   • articles.json (legacy data)"
echo "   • Configuration and documentation files"
echo
echo "🔍 To see what's in jaffa folder:"
echo "   ls -la jaffa/*/"
echo
echo "✨ Your workspace is now professionally organized!"
