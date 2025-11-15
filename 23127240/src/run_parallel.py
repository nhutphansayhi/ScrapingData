#!/usr/bin/env python3
"""
Main script to run parallel arXiv scraper
Designed for Google Colab execution
"""

import sys
import os
import time
import logging

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_settings import *
from utils import setup_logging, ensure_dir, format_arxiv_id
from parallel_scraper import ParallelArxivScraper

def main():
    """Main execution function"""
    # Setup logging
    setup_logging(LOGS_DIR)
    logger = logging.getLogger(__name__)
    
    logger.info("="*80)
    logger.info("STARTING ARXIV SCRAPER")
    logger.info(f"Student ID: {STUDENT_ID}")
    logger.info(f"Paper range: {START_YEAR_MONTH}.{START_ID:05d} to {END_YEAR_MONTH}.{END_ID:05d}")
    logger.info(f"Workers: {MAX_WORKERS}")
    logger.info("="*80)
    
    # Calculate paper IDs to scrape
    paper_ids = []
    
    # Calculate how many papers needed from first month
    TARGET_TOTAL = 5000
    total_in_last_month = END_ID
    papers_from_first_month = TARGET_TOTAL - total_in_last_month
    first_month_end_id = START_ID + papers_from_first_month - 1
    
    # First month: from START_ID to calculated end
    for paper_id in range(START_ID, first_month_end_id + 1):
        arxiv_id = format_arxiv_id(START_YEAR_MONTH, paper_id)
        paper_ids.append(arxiv_id)
    
    # Second month: from 1 to END_ID
    for paper_id in range(1, END_ID + 1):
        arxiv_id = format_arxiv_id(END_YEAR_MONTH, paper_id)
        paper_ids.append(arxiv_id)
    
    logger.info(f"Total papers to scrape: {len(paper_ids)}")
    logger.info(f"First paper: {paper_ids[0]}")
    logger.info(f"Last paper: {paper_ids[-1]}")
    
    # Setup output directory
    output_dir = DATA_DIR
    ensure_dir(output_dir)
    
    # Create scraper
    scraper = ParallelArxivScraper(output_dir)
    
    # Check for already completed papers (for resume capability)
    completed = set()
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isdir(item_path) and '-' in item:
                # Check if paper is complete
                metadata_file = os.path.join(item_path, "metadata.json")
                references_file = os.path.join(item_path, "references.json")
                if os.path.exists(metadata_file) and os.path.exists(references_file):
                    arxiv_id = item.replace('-', '.')
                    completed.add(arxiv_id)
    
    if completed:
        logger.info(f"Found {len(completed)} completed papers, skipping them")
        paper_ids = [pid for pid in paper_ids if pid not in completed]
        logger.info(f"Remaining papers to scrape: {len(paper_ids)}")
    
    # START SCRAPING!
    logger.info(f"\nSTARTING scraping with {MAX_WORKERS} workers!")
    start_time = time.time()
    
    results = scraper.scrape_papers_batch(paper_ids, batch_size=50)
    
    elapsed = time.time() - start_time
    
    # Print results
    logger.info("\n" + "="*80)
    logger.info("COMPLETED!")
    logger.info("="*80)
    logger.info(f"Time: {elapsed:.2f}s ({elapsed/60:.2f} minutes)")
    logger.info(f"Successful: {results['successful']}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Total: {results['total']}")
    logger.info("="*80)

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
