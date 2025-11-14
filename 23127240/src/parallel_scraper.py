import concurrent.futures
import threading
import logging
from typing import List
import os

from arxiv_scraper import ArxivScraper
from utils import format_folder_name
from config import MAX_WORKERS

logger = logging.getLogger(__name__)


class ParallelArxivScraper:
    """
    Parallel scraper: 4-8 workers (tuân thủ rate limit)
    Lab 1 requirement: Tối ưu wall time
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.lock = threading.Lock()
    
    def scrape_single_paper_wrapper(self, arxiv_id: str):
        """Thread-safe wrapper"""
        scraper = ArxivScraper(self.output_dir)
        folder_name = format_folder_name(arxiv_id)
        paper_dir = os.path.join(self.output_dir, folder_name)
        
        try:
            success = scraper.scrape_paper(arxiv_id, paper_dir)
            return arxiv_id, success
        except Exception as e:
            logger.error(f"Error {arxiv_id}: {e}")
            return arxiv_id, False
    
    def scrape_papers_batch(self, paper_ids: List[str], batch_size: int = 50):
        """
        Scrape papers in batches
        batch_size = 50 → progress updates every 50 papers
        """
        total = len(paper_ids)
        successful = 0
        failed = 0
        
        for i in range(0, total, batch_size):
            batch = paper_ids[i:i+batch_size]
            logger.info(f"\nBatch {i//batch_size + 1}: Processing {len(batch)} papers...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {executor.submit(self.scrape_single_paper_wrapper, pid): pid for pid in batch}
                
                for future in concurrent.futures.as_completed(futures):
                    pid, success = future.result()
                    if success:
                        successful += 1
                    else:
                        failed += 1
            
            logger.info(f"Progress: {i+len(batch)}/{total} | Success: {successful} | Failed: {failed}")
        
        return {'successful': successful, 'failed': failed, 'total': total}
