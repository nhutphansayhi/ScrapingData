#!/usr/bin/env python3
"""
Main script to run parallel arXiv scraper
Designed for Google Colab execution
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    print("Starting ArXiv Parallel Scraper...")
    print("="*80)
    print("Features:")
    print("   - Parallel processing with 6 workers")
    print("   - Auto checkpoint every 50 papers")
    print("   - Realtime CSV updates")
    print("   - Memory & performance tracking")
    print("="*80)
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print("Progress has been saved at last checkpoint")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
