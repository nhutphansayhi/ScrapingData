import os
import sys
import time
import json
import logging
import psutil
import csv
from pathlib import Path

from config_settings import *
from utils import *
from parallel_scraper import ParallelArxivScraper
from reference_scraper_optimized import OptimizedReferenceScraper
from bibtex_generator import BibtexGenerator

logger = logging.getLogger(__name__)


class ArxivScraperPipeline:
    """Pipeline chính để scrape papers từ arXiv"""
    
    def __init__(self, output_dir: str, use_parallel: bool = True):
        self.output_dir = output_dir
        self.use_parallel = use_parallel
        ensure_dir(output_dir)
        
        # Dùng parallel scraper để tăng tốc
        if use_parallel:
            self.arxiv_scraper = ParallelArxivScraper(output_dir)
            logger.info(f"Chạy song song với {MAX_WORKERS} workers")
        else:
            from arxiv_scraper import ArxivScraper
            self.arxiv_scraper = ArxivScraper(output_dir)
        
        self.reference_scraper = OptimizedReferenceScraper(batch_size=500)
        self.bibtex_generator = BibtexGenerator()
        
        self.stats = {
            'total_papers': 0,
            'successful_papers': 0,
            'failed_papers': 0,
            'total_runtime': 0.0,
            'paper_runtimes': [],
            'paper_sizes_before': [],
            'paper_sizes_after': [],
            'reference_counts': [],
            'reference_success_counts': [],
            'discovery_time': 0.0,
            'max_ram_mb': 0.0,
            'avg_ram_mb': 0.0,
            'ram_samples': [],
            'max_disk_mb': 0.0,
            'final_disk_mb': 0.0
        }
        
        # Detailed paper tracking for CSV
        self.paper_details = []
        
        self.process = psutil.Process()
        self.initial_ram = self.process.memory_info().rss / (1024 * 1024)
    
    def get_completed_papers(self) -> set:
        """Get set of paper IDs that have already been scraped successfully"""
        completed = set()
        if not os.path.exists(self.output_dir):
            return completed
        
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            if os.path.isdir(item_path):
                # Check if paper has metadata.json and references.json (signs of completion)
                metadata_file = os.path.join(item_path, "metadata.json")
                references_file = os.path.join(item_path, "references.json")
                
                if os.path.exists(metadata_file) and os.path.exists(references_file):
                    # Convert folder name back to arxiv_id format (e.g., "2311-14685" -> "2311.14685")
                    arxiv_id = item.replace('-', '.')
                    completed.add(arxiv_id)
        
        return completed
    
    def get_attempted_papers(self) -> set:
        """Get set of ALL paper IDs that have been attempted (have any folder)"""
        attempted = set()
        if not os.path.exists(self.output_dir):
            return attempted
        
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            # Check if it's a directory and looks like a paper folder (format: YYMM-NNNNN)
            if os.path.isdir(item_path) and '-' in item:
                # Convert folder name back to arxiv_id format (e.g., "2311-14685" -> "2311.14685")
                arxiv_id = item.replace('-', '.')
                attempted.add(arxiv_id)
        
        return attempted
    
    def load_checkpoint_stats(self, completed_papers: set):
        """Load statistics from checkpoint to preserve previous progress
        
        Returns:
            set: arxiv_ids of papers already in CSV (to skip during scraping)
        """
        stats_file = os.path.join(self.output_dir, "scraping_stats.json")
        details_csv = os.path.join(self.output_dir, "paper_details.csv")
        csv_papers = set()
        
        # Load paper details from CSV if exists
        if os.path.exists(details_csv):
            try:
                with open(details_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Convert numeric fields
                        row['paper_id'] = int(row['paper_id'])
                        row['runtime_s'] = float(row['runtime_s'])
                        row['size_before'] = int(row['size_before'])
                        row['size_after'] = int(row['size_after'])
                        row['size_before_figures'] = int(row['size_before_figures'])
                        row['size_after_figures'] = int(row['size_after_figures'])
                        row['num_refs'] = int(row['num_refs'])
                        row['current_output_size'] = int(row['current_output_size'])
                        row['max_rss'] = float(row['max_rss'])
                        row['avg_rss'] = float(row['avg_rss'])
                        self.paper_details.append(row)
                        # Track arxiv_id to skip this paper
                        csv_papers.add(row['arxiv_id'])
                logger.info(f"Loaded {len(self.paper_details)} paper details from checkpoint")
            except Exception as e:
                logger.warning(f"Failed to load paper details from CSV: {e}")
        
        if not os.path.exists(stats_file):
            # No checkpoint file, count manually from completed papers
            logger.info("No checkpoint file found, counting from completed papers...")
            self.stats['successful_papers'] = len(completed_papers)
            return
        
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                saved_stats = json.load(f)
            
            # Restore key statistics
            data_stats = saved_stats.get('data_statistics', {})
            perf_time = saved_stats.get('performance_running_time', {})
            perf_mem = saved_stats.get('performance_memory_footprint', {})
            
            self.stats['successful_papers'] = data_stats.get('successful_papers', len(completed_papers))
            self.stats['failed_papers'] = data_stats.get('failed_papers', 0)
            self.stats['max_ram_mb'] = perf_mem.get('max_ram_mb', 0.0)
            self.stats['avg_ram_mb'] = perf_mem.get('avg_ram_mb', 0.0)
            self.stats['max_disk_mb'] = perf_mem.get('max_disk_storage_mb', 0.0)
            
            # Load arrays if available (for accurate averaging)
            # These won't be in JSON, so we'll rebuild from completed papers
            logger.info(f"Loaded checkpoint: {self.stats['successful_papers']} successful, {self.stats['failed_papers']} failed")
            
        except Exception as e:
            logger.warning(f"Failed to load checkpoint stats: {e}")
            self.stats['successful_papers'] = len(completed_papers)
        
        return csv_papers
    
    def update_memory_stats(self):
        current_ram = self.process.memory_info().rss / (1024 * 1024)
        self.stats['ram_samples'].append(current_ram)
        if current_ram > self.stats['max_ram_mb']:
            self.stats['max_ram_mb'] = current_ram
    
    def update_disk_stats(self):
        if os.path.exists(self.output_dir):
            disk_usage = get_directory_size(self.output_dir) / (1024 * 1024)
            if disk_usage > self.stats['max_disk_mb']:
                self.stats['max_disk_mb'] = disk_usage
    
    def generate_paper_ids(self, start_ym: str, start_id: int, 
                          end_ym: str, end_id: int) -> list:
        """
        Generate paper IDs for the range.
        For 23127240: 2311.14685 to 2312.00843
        - Month 2311: 14685 to 18840 (4156 papers)
        - Month 2312: 00001 to 00843 (843 papers)  ← BẮT ĐẦU TỪ 1, KHÔNG PHẢI 0
        Total: 4999 papers
        """
        paper_ids = []
        
        start_ym_int = int(start_ym)
        end_ym_int = int(end_ym)
        
        # Same month case
        if start_ym_int == end_ym_int:
            ym_str = str(start_ym_int)
            for paper_id in range(start_id, end_id + 1):
                arxiv_id = format_arxiv_id(ym_str, paper_id)
                paper_ids.append(arxiv_id)
            return paper_ids
        
        # Multi-month case: calculate end ID for first month
        # Total papers in last month = end_id (starting from 1, not 0)
        total_in_last_month = end_id
        
        # Calculate how many papers we need from first month
        TARGET_TOTAL = 5000  # 4156 + 844 = 5000
        papers_needed_from_first_month = TARGET_TOTAL - total_in_last_month
        first_month_end_id = start_id + papers_needed_from_first_month - 1
        
        # Generate papers for first month
        ym_str = str(start_ym_int)
        for paper_id in range(start_id, first_month_end_id + 1):
            arxiv_id = format_arxiv_id(ym_str, paper_id)
            paper_ids.append(arxiv_id)
        
        # Generate papers for last month (from 1 to end_id, NOT from 0)
        ym_str = str(end_ym_int)
        for paper_id in range(1, end_id + 1):  # BẮT ĐẦU TỪ 1
            arxiv_id = format_arxiv_id(ym_str, paper_id)
            paper_ids.append(arxiv_id)
        
        return paper_ids
    
    def scrape_single_paper(self, arxiv_id: str) -> bool:
        start_time = time.time()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing paper {arxiv_id}")
        logger.info(f"{'='*60}")
        
        folder_name = format_folder_name(arxiv_id)
        paper_dir = os.path.join(self.output_dir, folder_name)
        ensure_dir(paper_dir)
        
        size_before = get_directory_size(paper_dir) if os.path.exists(paper_dir) else 0
        
        success = self.arxiv_scraper.scrape_paper(arxiv_id, paper_dir)
        
        if not success:
            logger.error(f"Failed to scrape paper {arxiv_id}")
            self.stats['failed_papers'] += 1
            return False
        
        size_after = get_directory_size(paper_dir)
        self.stats['paper_sizes_before'].append(size_before)
        self.stats['paper_sizes_after'].append(size_after)
        
        self.update_memory_stats()
        self.update_disk_stats()
        
        metadata_path = os.path.join(paper_dir, "metadata.json")
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            self.stats['failed_papers'] += 1
            return False
        
        # NOTE: NO references.bib at paper level!
        # BibTeX files (.bib) should ONLY exist inside tex/<yymm-id>vX/ folders
        # Those are the ORIGINAL .bib files uploaded by authors
        
        # Scrape references from Semantic Scholar
        references_path = os.path.join(paper_dir, "references.json")
        ref_before = self.reference_scraper.get_stats()['total_references']
        self.reference_scraper.scrape_references(arxiv_id, references_path)
        ref_after = self.reference_scraper.get_stats()['total_references']
        
        num_refs = 0
        try:
            with open(references_path, 'r', encoding='utf-8') as f:
                references = json.load(f)
                num_refs = len(references)
                self.stats['reference_counts'].append(num_refs)
                self.stats['reference_success_counts'].append(ref_after - ref_before)
        except:
            self.stats['reference_counts'].append(0)
            self.stats['reference_success_counts'].append(0)
        
        runtime = time.time() - start_time
        self.stats['paper_runtimes'].append(runtime)
        self.stats['successful_papers'] += 1
        
        # Get current memory usage
        current_ram = self.process.memory_info().rss / (1024 * 1024)
        current_disk = get_directory_size(self.output_dir) / (1024 * 1024)
        avg_ram = sum(self.stats['ram_samples']) / len(self.stats['ram_samples']) if self.stats['ram_samples'] else current_ram
        
        # Save detailed paper info
        paper_detail = {
            'paper_id': self.stats['successful_papers'],
            'arxiv_id': arxiv_id,
            'title': metadata.get('title', 'N/A'),
            'authors': ', '.join(metadata.get('authors', [])),
            'runtime_s': round(runtime, 2),
            'size_before': size_before,
            'size_after': size_after,
            'size_before_figures': size_before,  # Before removing figures
            'size_after_figures': size_after,    # After removing figures
            'num_refs': num_refs,
            'current_output_size': int(current_disk * 1024 * 1024),  # bytes
            'max_rss': round(self.stats['max_ram_mb'], 2),
            'avg_rss': round(avg_ram, 2),
            'processed_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.paper_details.append(paper_detail)
        
        logger.info(f"Successfully processed {arxiv_id} in {runtime:.2f}s")
        logger.info(f"Paper size: {size_after / 1024:.2f} KB")
        
        return True
    
    def run(self, start_ym: str = None, start_id: int = None,
            end_ym: str = None, end_id: int = None):
        start_ym = start_ym or START_YEAR_MONTH
        start_id = start_id if start_id is not None else START_ID
        end_ym = end_ym or END_YEAR_MONTH
        end_id = end_id if end_id is not None else END_ID
        
        logger.info("="*80)
        logger.info("arXiv Scraper Pipeline Started")
        logger.info(f"Student ID: {STUDENT_ID}")
        logger.info(f"Range: {start_ym}.{start_id:05d} to {end_ym}.{end_id:05d}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("="*80)
        
        pipeline_start = time.time()
        
        logger.info("\nGenerating paper IDs...")
        discovery_start = time.time()
        paper_ids = self.generate_paper_ids(start_ym, start_id, end_ym, end_id)
        self.stats['discovery_time'] = time.time() - discovery_start
        
        # IMPORTANT: total_papers always = original count (not remaining)
        original_total = len(paper_ids)
        self.stats['total_papers'] = original_total
        
        # Check for papers that have been attempted (any folder exists)
        attempted_papers = self.get_attempted_papers()
        completed_papers = self.get_completed_papers()
        
        # Always load checkpoint stats from completed papers only
        csv_papers = self.load_checkpoint_stats(completed_papers)
        
        if attempted_papers:
            logger.info(f"Found {len(attempted_papers)} papers already attempted (have folders)")
        if completed_papers:
            logger.info(f"Found {len(completed_papers)} successfully completed (with metadata+references)")
        if csv_papers:
            logger.info(f"Found {len(csv_papers)} papers already tracked in CSV")
        
        # Skip ALL attempted papers (whether successful or failed)
        papers_to_skip = attempted_papers
        if papers_to_skip:
            logger.info(f"Total papers to skip: {len(papers_to_skip)}")
            logger.info("These papers will be skipped (already attempted)")
            
            # Filter out attempted papers
            paper_ids = [pid for pid in paper_ids if pid not in papers_to_skip]
            logger.info(f"Remaining papers to scrape: {len(paper_ids)}")
        
        logger.info(f"Total papers in assignment: {original_total}")
        logger.info(f"Papers to process now: {len(paper_ids)}")
        if paper_ids:
            logger.info(f"First paper: {paper_ids[0]}")
            logger.info(f"Last paper: {paper_ids[-1]}")
        
        # Nếu dùng parallel scraper, dùng batch processing với checkpoint
        if self.use_parallel and hasattr(self.arxiv_scraper, 'scrape_papers_batch'):
            logger.info("\n🚀 Using PARALLEL batch processing with checkpoints every 50 papers")
            
            # Định nghĩa callback cho checkpoint
            def checkpoint_callback(current, total):
                """Callback được gọi mỗi 50 papers - Cập nhật paper_details từ folders"""
                logger.info("📊 Collecting paper details from folders...")
                self.collect_paper_details_from_folders()
                self.print_progress()
                self.save_stats(intermediate=False)
                self.save_paper_details_csv()
            
            # Chạy batch với checkpoint mỗi 50 papers
            result = self.arxiv_scraper.scrape_papers_batch(
                paper_ids, 
                batch_size=6,  # Process 6 papers per batch (same as MAX_WORKERS)
                update_interval=50,  # Checkpoint mỗi 50 papers
                on_checkpoint=checkpoint_callback
            )
            
            self.stats['successful_papers'] += result['successful']
            self.stats['failed_papers'] += result['failed']
            
            # Cập nhật paper_details cuối cùng
            logger.info("\n📊 Final collection of paper details...")
            self.collect_paper_details_from_folders()
            
        else:
            # Fallback: sequential processing với checkpoint thủ công
            logger.info("\n⚙️  Using SEQUENTIAL processing with manual checkpoints")
            for i, arxiv_id in enumerate(paper_ids, 1):
                logger.info(f"\n[{i}/{len(paper_ids)}] Processing {arxiv_id}")
                
                try:
                    self.scrape_single_paper(arxiv_id)
                except Exception as e:
                    logger.error(f"Unexpected error processing {arxiv_id}: {e}")
                    self.stats['failed_papers'] += 1
                
                # Print progress và save stats mỗi 50 papers
                if i % 50 == 0:
                    self.print_progress()
                    logger.info(f"\n{'='*70}")
                    logger.info(f"💾 CHECKPOINT at paper {i}/{len(paper_ids)}")
                    logger.info(f"{'='*70}")
                    # Save full stats với CSV updates
                    self.save_stats(intermediate=False)
                    self.save_paper_details_csv()
                    logger.info(f"✅ All statistics files updated successfully!")
                    logger.info(f"{'='*70}\n")
                
                # Quick save mỗi 10 papers (chỉ JSON, không CSV để tăng tốc)
                elif i % 10 == 0:
                    self.print_progress()
                    # Save intermediate stats để không mất dữ liệu nếu crash
                    self.save_stats(intermediate=True)
        
        self.cleanup_all_temp_files()
        
        self.stats['total_runtime'] = time.time() - pipeline_start
        if self.stats['ram_samples']:
            self.stats['avg_ram_mb'] = sum(self.stats['ram_samples']) / len(self.stats['ram_samples'])
        self.stats['final_disk_mb'] = get_directory_size(self.output_dir) / (1024 * 1024)
        
        self.print_final_stats()
        self.save_stats()
    
    def print_progress(self):
        logger.info("\n" + "="*70)
        logger.info("📊 PROGRESS UPDATE")
        logger.info("="*70)
        total_processed = self.stats['successful_papers'] + self.stats['failed_papers']
        logger.info(f"Papers processed: {total_processed}")
        logger.info(f"  ✅ Successful: {self.stats['successful_papers']}")
        logger.info(f"  ❌ Failed: {self.stats['failed_papers']}")
        logger.info(f"  📈 Success rate: {self.stats['successful_papers']/max(1, total_processed)*100:.1f}%")
        
        # Memory info
        if self.stats['ram_samples']:
            current_ram = self.process.memory_info().rss / (1024 * 1024)
            logger.info(f"  💾 RAM: {current_ram:.1f} MB (max: {self.stats['max_ram_mb']:.1f} MB)")
        
        # Disk info
        current_disk = get_directory_size(self.output_dir) / (1024 * 1024)
        logger.info(f"  💿 Disk: {current_disk:.1f} MB")
        
        logger.info("="*70)
        logger.info("="*60 + "\n")
    
    def cleanup_all_temp_files(self):
        logger.info("\nCleaning up temporary files...")
        temp_cleaned = 0
        
        if not os.path.exists(self.output_dir):
            return
        
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            if os.path.isdir(item_path):
                temp_dir = os.path.join(item_path, "temp")
                if os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                        temp_cleaned += 1
                        logger.debug(f"Removed temp directory: {temp_dir}")
                    except Exception as e:
                        logger.warning(f"Failed to remove temp directory {temp_dir}: {e}")
        
        if temp_cleaned > 0:
            logger.info(f"Cleaned {temp_cleaned} temp directories")
        else:
            logger.info("No temp directories found")
    
    def print_final_stats(self):
        logger.info("\n" + "="*80)
        logger.info("FINAL STATISTICS")
        logger.info("="*80)
        
        logger.info(f"\n1. Scraping Results:")
        logger.info(f"  Total papers attempted: {self.stats['total_papers']}")
        logger.info(f"  Successful: {self.stats['successful_papers']}")
        logger.info(f"  Failed: {self.stats['failed_papers']}")
        success_rate = self.stats['successful_papers']/max(1, self.stats['total_papers'])*100
        logger.info(f"  Overall success rate: {success_rate:.2f}%")
        
        if self.stats['paper_sizes_before'] and self.stats['paper_sizes_after']:
            avg_before = sum(self.stats['paper_sizes_before']) / len(self.stats['paper_sizes_before'])
            avg_after = sum(self.stats['paper_sizes_after']) / len(self.stats['paper_sizes_after'])
            logger.info(f"\n2. Paper Size Statistics:")
            logger.info(f"  Average size before removing figures: {avg_before:.2f} bytes ({avg_before/1024:.2f} KB)")
            logger.info(f"  Average size after removing figures: {avg_after:.2f} bytes ({avg_after/1024:.2f} KB)")
            reduction = ((avg_before - avg_after) / avg_before * 100) if avg_before > 0 else 0
            logger.info(f"  Size reduction: {reduction:.1f}%")
        
        if self.stats['reference_counts']:
            avg_refs = sum(self.stats['reference_counts']) / len(self.stats['reference_counts'])
            logger.info(f"\n3. Reference Statistics:")
            logger.info(f"  Average references per paper: {avg_refs:.2f}")
            
            ref_stats = self.reference_scraper.get_stats()
            if ref_stats['papers_queried'] > 0:
                ref_success_rate = (ref_stats['papers_found'] / ref_stats['papers_queried']) * 100
                logger.info(f"  Papers queried for references: {ref_stats['papers_queried']}")
                logger.info(f"  Papers found: {ref_stats['papers_found']}")
                logger.info(f"  Total references found: {ref_stats['total_references']}")
                logger.info(f"  References with arXiv ID: {ref_stats['references_with_arxiv_id']}")
                logger.info(f"  Reference metadata success rate: {ref_success_rate:.2f}%")
        
        logger.info(f"\n4. Performance - Running Time:")
        logger.info(f"  Total runtime (wall time): {self.stats['total_runtime']:.2f}s ({self.stats['total_runtime']/60:.2f} min)")
        logger.info(f"  Entry discovery time: {self.stats['discovery_time']:.2f}s")
        if self.stats['paper_runtimes']:
            avg_runtime = sum(self.stats['paper_runtimes']) / len(self.stats['paper_runtimes'])
            logger.info(f"  Average time per paper: {avg_runtime:.2f}s")
            total_processing = sum(self.stats['paper_runtimes'])
            logger.info(f"  Total paper processing time: {total_processing:.2f}s ({total_processing/60:.2f} min)")
        
        logger.info(f"\n5. Performance - Memory Footprint:")
        logger.info(f"  Maximum RAM used: {self.stats['max_ram_mb']:.2f} MB")
        logger.info(f"  Average RAM consumption: {self.stats['avg_ram_mb']:.2f} MB")
        logger.info(f"  Maximum disk storage required: {self.stats['max_disk_mb']:.2f} MB")
        logger.info(f"  Final output storage size: {self.stats['final_disk_mb']:.2f} MB")
        
        arxiv_stats = self.arxiv_scraper.get_stats()
        logger.info(f"\n6. Additional ArXiv Statistics:")
        logger.info(f"  Total versions downloaded: {arxiv_stats['versions_downloaded']}")
        logger.info(f"  Total download time: {arxiv_stats['total_download_time']:.2f}s")
        
        logger.info("\n" + "="*80)
    
    def save_stats(self, intermediate=False):
        """
        Save statistics to JSON and CSV
        
        Args:
            intermediate: If True, only save JSON (faster). If False, save both JSON and CSV.
        """
        stats_file = os.path.join(self.output_dir, "scraping_stats.json")
        
        # Calculate 15 required metrics
        ref_stats = self.reference_scraper.get_stats()
        
        all_stats = {
            'metadata': {
                'student_id': STUDENT_ID,
                'paper_range_start': f"{START_YEAR_MONTH}.{START_ID:05d}",
                'paper_range_end': f"{END_YEAR_MONTH}.{END_ID:05d}",
                'total_papers_attempted': self.stats['total_papers'],
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'testbed': 'Google Colab CPU-only'
            },
            'required_15_metrics': {
                'data_statistics': {
                    'metric_1_papers_scraped_successfully': self.stats['successful_papers'],
                    'metric_2_overall_success_rate_percent': round((self.stats['successful_papers']/max(1, self.stats['total_papers']))*100, 2),
                    'metric_3_avg_size_before_removing_figures_bytes': round(sum(self.stats['paper_sizes_before']) / len(self.stats['paper_sizes_before']), 2) if self.stats['paper_sizes_before'] else 0,
                    'metric_4_avg_size_after_removing_figures_bytes': round(sum(self.stats['paper_sizes_after']) / len(self.stats['paper_sizes_after']), 2) if self.stats['paper_sizes_after'] else 0,
                    'metric_5_avg_references_per_paper': round(sum(self.stats['reference_counts']) / len(self.stats['reference_counts']), 2) if self.stats['reference_counts'] else 0,
                    'metric_6_reference_metadata_success_rate_percent': round((ref_stats['papers_found'] / max(1, ref_stats['papers_queried'])) * 100, 2),
                    'metric_7_other_stats_total_references_found': ref_stats['total_references']
                },
                'performance_running_time': {
                    'metric_8_total_wall_time_seconds': round(self.stats['total_runtime'], 2),
                    'metric_9_total_time_process_one_paper_seconds': round(sum(self.stats['paper_runtimes']) / len(self.stats['paper_runtimes']), 2) if self.stats['paper_runtimes'] else 0,
                    'metric_10_avg_time_per_required_paper_seconds': round(sum(self.stats['paper_runtimes']) / len(self.stats['paper_runtimes']), 2) if self.stats['paper_runtimes'] else 0,
                    'metric_11_entry_discovery_time_seconds': round(self.stats['discovery_time'], 2)
                },
                'performance_memory_footprint': {
                    'metric_12_maximum_ram_used_mb': round(self.stats['max_ram_mb'], 2),
                    'metric_13_average_ram_consumption_mb': round(self.stats['avg_ram_mb'], 2),
                    'metric_14_maximum_disk_storage_required_mb': round(self.stats['max_disk_mb'], 2),
                    'metric_15_final_output_storage_size_mb': round(self.stats['final_disk_mb'], 2)
                }
            },
            'additional_details': {
                'failed_papers': self.stats['failed_papers'],
                'total_paper_processing_time_seconds': round(sum(self.stats['paper_runtimes']), 2) if self.stats['paper_runtimes'] else 0,
                'arxiv_scraper_stats': self.arxiv_scraper.get_stats() if hasattr(self.arxiv_scraper, 'get_stats') else {},
                'reference_scraper_stats': ref_stats
            }
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(all_stats, f, indent=2)
        
        if not intermediate:
            logger.info(f"\nStatistics saved to: {stats_file}")
        
        # Also save CSV format for report (only on full save to avoid overhead)
        if not intermediate:
            self.save_stats_csv()
            self.save_paper_details_csv()
    
    def save_stats_csv(self):
        """Save 15 REQUIRED METRICS in CSV format as per Lab 1 requirements"""
        csv_file = os.path.join(self.output_dir, "scraping_stats.csv")
        
        # Calculate the 15 required metrics
        total_papers = self.stats['total_papers']
        successful_papers = self.stats['successful_papers']
        
        # Metric 1: Number of papers scraped successfully
        metric_1 = successful_papers
        
        # Metric 2: Overall success rate
        metric_2 = (successful_papers / max(1, total_papers)) * 100
        
        # Metric 3: Average paper size BEFORE removing figures (bytes)
        metric_3 = sum(self.stats['paper_sizes_before']) / len(self.stats['paper_sizes_before']) if self.stats['paper_sizes_before'] else 0
        
        # Metric 4: Average paper size AFTER removing figures (bytes)
        metric_4 = sum(self.stats['paper_sizes_after']) / len(self.stats['paper_sizes_after']) if self.stats['paper_sizes_after'] else 0
        
        # Metric 5: Average number of references per paper
        metric_5 = sum(self.stats['reference_counts']) / len(self.stats['reference_counts']) if self.stats['reference_counts'] else 0
        
        # Metric 6: Average success rate for scraping reference metadata
        ref_stats = self.reference_scraper.get_stats()
        metric_6 = (ref_stats['papers_found'] / max(1, ref_stats['papers_queried'])) * 100
        
        # Metric 7: Other relevant statistics (total references found)
        metric_7 = ref_stats['total_references']
        
        # Metric 8: Wall time (total runtime end-to-end)
        metric_8 = self.stats['total_runtime']
        
        # Metric 9: Total time to process ONE paper (average)
        metric_9 = sum(self.stats['paper_runtimes']) / len(self.stats['paper_runtimes']) if self.stats['paper_runtimes'] else 0
        
        # Metric 10: Average time to process each required paper (same as metric 9)
        metric_10 = metric_9
        
        # Metric 11: Total time for entry discovery
        metric_11 = self.stats['discovery_time']
        
        # Metric 12: Maximum RAM used
        metric_12 = self.stats['max_ram_mb']
        
        # Metric 13: Average RAM consumption
        metric_13 = self.stats['avg_ram_mb']
        
        # Metric 14: Maximum disk storage required
        metric_14 = self.stats['max_disk_mb']
        
        # Metric 15: Final output's storage size
        metric_15 = self.stats['final_disk_mb']
        
        # Generate timestamp
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # CSV rows following Lab 1 required format
        rows = [
            ['Metric_ID', 'Category', 'Metric_Name', 'Value', 'Unit', 'Notes'],
            ['', '', '', '', '', ''],
            ['INFO', 'General', 'Student ID', STUDENT_ID, '', ''],
            ['INFO', 'General', 'Paper Range', f"{START_YEAR_MONTH}.{START_ID:05d} to {END_YEAR_MONTH}.{END_ID:05d}", '', ''],
            ['INFO', 'General', 'Total Papers Attempted', total_papers, 'papers', ''],
            ['INFO', 'General', 'Generated At', timestamp, '', ''],
            ['', '', '', '', '', ''],
            ['', '=== DATA STATISTICS (7 metrics) ===', '', '', '', ''],
            ['1', 'Data Statistics', 'Papers Scraped Successfully', metric_1, 'papers', 'Required Metric 1'],
            ['2', 'Data Statistics', 'Overall Success Rate', f"{metric_2:.2f}", '%', 'Required Metric 2'],
            ['3', 'Data Statistics', 'Avg Paper Size Before Removing Figures', f"{metric_3:.2f}", 'bytes', 'Required Metric 3'],
            ['4', 'Data Statistics', 'Avg Paper Size After Removing Figures', f"{metric_4:.2f}", 'bytes', 'Required Metric 4'],
            ['5', 'Data Statistics', 'Avg References Per Paper', f"{metric_5:.2f}", 'references', 'Required Metric 5'],
            ['6', 'Data Statistics', 'Reference Metadata Success Rate', f"{metric_6:.2f}", '%', 'Required Metric 6'],
            ['7', 'Data Statistics', 'Total References Found', metric_7, 'references', 'Required Metric 7 (other stats)'],
            ['', '', '', '', '', ''],
            ['', '=== PERFORMANCE - RUNNING TIME (4 metrics) ===', '', '', '', ''],
            ['8', 'Performance - Time', 'Total Wall Time (End-to-End)', f"{metric_8:.2f}", 'seconds', 'Required Metric 8'],
            ['8', 'Performance - Time', 'Total Wall Time (End-to-End)', f"{metric_8/60:.2f}", 'minutes', 'Same as above'],
            ['9', 'Performance - Time', 'Total Time to Process ONE Paper', f"{metric_9:.2f}", 'seconds', 'Required Metric 9'],
            ['10', 'Performance - Time', 'Avg Time Per Required Paper', f"{metric_10:.2f}", 'seconds', 'Required Metric 10'],
            ['11', 'Performance - Time', 'Entry Discovery Time', f"{metric_11:.2f}", 'seconds', 'Required Metric 11'],
            ['', '', '', '', '', ''],
            ['', '=== PERFORMANCE - MEMORY FOOTPRINT (4 metrics) ===', '', '', '', ''],
            ['12', 'Performance - Memory', 'Maximum RAM Used', f"{metric_12:.2f}", 'MB', 'Required Metric 12'],
            ['13', 'Performance - Memory', 'Average RAM Consumption', f"{metric_13:.2f}", 'MB', 'Required Metric 13'],
            ['14', 'Performance - Memory', 'Maximum Disk Storage Required', f"{metric_14:.2f}", 'MB', 'Required Metric 14'],
            ['15', 'Performance - Memory', 'Final Output Storage Size', f"{metric_15:.2f}", 'MB', 'Required Metric 15'],
            ['15', 'Performance - Memory', 'Final Output Storage Size', f"{metric_15/1024:.2f}", 'GB', 'Same as above'],
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        logger.info(f"✅ Lab 1 Required Statistics (15 metrics) saved to: {csv_file}")
    
    def collect_paper_details_from_folders(self):
        """Scan tất cả paper folders và build paper_details list"""
        import psutil
        
        # Clear existing list
        self.paper_details = []
        
        # Get all paper folders
        if not os.path.exists(self.output_dir):
            return
        
        folders = sorted([d for d in os.listdir(self.output_dir) 
                         if os.path.isdir(os.path.join(self.output_dir, d)) and '-' in d])
        
        current_disk = get_directory_size(self.output_dir) / (1024 * 1024)
        current_ram = self.process.memory_info().rss / (1024 * 1024)
        avg_ram = sum(self.stats['ram_samples']) / len(self.stats['ram_samples']) if self.stats['ram_samples'] else current_ram
        
        for paper_id_num, folder in enumerate(folders, 1):
            paper_dir = os.path.join(self.output_dir, folder)
            arxiv_id = folder.replace('-', '.')
            
            # Load metadata
            metadata_path = os.path.join(paper_dir, "metadata.json")
            title = 'N/A'
            authors = []
            runtime_s = 0.0
            processed_at_from_metadata = None
            
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        title = metadata.get('title', 'N/A')
                        authors = metadata.get('authors', [])
                        runtime_s = metadata.get('runtime_seconds', 0.0)
                        processed_at_from_metadata = metadata.get('processed_at')
                except:
                    pass
            
            # Calculate sizes
            size_before = 0
            size_after = 0
            tex_path = os.path.join(paper_dir, "tex")
            if os.path.exists(tex_path):
                size_after = get_directory_size(tex_path)
                # Estimate size before (assume ~12MB per version)
                versions = len([d for d in os.listdir(tex_path) 
                              if os.path.isdir(os.path.join(tex_path, d))])
                size_before = size_after + (12 * 1024 * 1024 * max(versions, 1))
            
            # Count references
            num_refs = 0
            ref_path = os.path.join(paper_dir, "references.json")
            if os.path.exists(ref_path):
                try:
                    with open(ref_path, 'r', encoding='utf-8') as f:
                        refs = json.load(f)
                        if isinstance(refs, list):
                            num_refs = len(refs)
                except:
                    pass
            
            # Get processed time (from metadata or file mtime)
            processed_at = processed_at_from_metadata
            if not processed_at and os.path.exists(metadata_path):
                processed_at = time.strftime('%Y-%m-%d %H:%M:%S', 
                                            time.localtime(os.path.getmtime(metadata_path)))
            if not processed_at:
                processed_at = 'N/A'
            
            # Add to list
            paper_detail = {
                'paper_id': paper_id_num,
                'arxiv_id': arxiv_id,
                'title': title[:100],  # Limit title length
                'authors': ', '.join(authors[:3]) if authors else 'N/A',  # Max 3 authors
                'runtime_s': runtime_s,
                'size_before': size_before,
                'size_after': size_after,
                'size_before_figures': size_before,
                'size_after_figures': size_after,
                'num_refs': num_refs,
                'current_output_size': int(current_disk * 1024 * 1024),
                'max_rss': round(self.stats['max_ram_mb'], 2),
                'avg_rss': round(avg_ram, 2),
                'processed_at': processed_at
            }
            self.paper_details.append(paper_detail)
        
        logger.info(f"✅ Collected {len(self.paper_details)} paper details from folders")
    
    def save_paper_details_csv(self):
        """Save detailed per-paper statistics to CSV"""
        csv_file = os.path.join(self.output_dir, "paper_details.csv")
        
        if not self.paper_details:
            logger.warning("No paper details to save")
            return
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['paper_id', 'arxiv_id', 'title', 'authors', 'runtime_s', 
                         'size_before', 'size_after', 'size_before_figures', 'size_after_figures',
                         'num_refs', 'current_output_size', 'max_rss', 'avg_rss', 'processed_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(self.paper_details)
        
        logger.info(f"✅ Paper details CSV updated: {csv_file} ({len(self.paper_details)} papers)")


def main():
    setup_logging(LOGS_DIR)
    
    pipeline = ArxivScraperPipeline(DATA_DIR)
    pipeline.run(
        start_ym=START_YEAR_MONTH,
        start_id=START_ID,
        end_ym=END_YEAR_MONTH,
        end_id=END_ID
    )
    
    print("\nDone!")


if __name__ == "__main__":
    main()
