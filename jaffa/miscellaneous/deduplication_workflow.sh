# Basic usage - run complete workflow
python workflow_deduplication.py

# Advanced options
python workflow_deduplication.py --interactive     # Ask before each step
python workflow_deduplication.py --dry-run        # Preview without changes
python workflow_deduplication.py --skip-backup    # Don't create backups
python workflow_deduplication.py --skip-website   # Don't regenerate site
python workflow_deduplication.py --input-file custom.json  # Custom input file