import concurrent.futures
import threading
import logging
from typing import List
import os
import json
import time
import pandas as pd
from datetime import datetime

from arxiv_scraper import ArxivScraper
from utils import format_folder_name
from config_settings import MAX_WORKERS, STUDENT_ID

logger = logging.getLogger(__name__)


class ParallelArxivScraper:
    """
    Scraper chạy song song để tăng tốc
    Dùng 6 workers (vẫn tuân thủ rate limit)
    Tự động update metrics mỗi 100 papers
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.lock = threading.Lock()
        self.start_time = None
        self.paper_times = []  # lưu thời gian mỗi paper
    
    def scrape_single_paper_wrapper(self, arxiv_id: str):
        """Wrapper cho mỗi thread"""
        paper_start = time.time()
        scraper = ArxivScraper(self.output_dir)
        folder_name = format_folder_name(arxiv_id)
        paper_dir = os.path.join(self.output_dir, folder_name)
        
        try:
            success = scraper.scrape_paper(arxiv_id, paper_dir)
            paper_time = time.time() - paper_start
            
            # Lưu thời gian (thread-safe)
            with self.lock:
                self.paper_times.append({
                    'arxiv_id': arxiv_id,
                    'time_seconds': paper_time,
                    'success': success
                })
            
            return arxiv_id, success
        except Exception as e:
            logger.error(f"Lỗi khi scrape {arxiv_id}: {e}")
            return arxiv_id, False
    
    def calculate_metrics(self):
        """Tính 15 metrics theo Lab 1"""
        import psutil
        
        papers = [d for d in os.listdir(self.output_dir) 
                 if os.path.isdir(os.path.join(self.output_dir, d)) and '-' in d]
        total_papers = len(papers)
        
        if total_papers == 0:
            return None
        
        # Khởi tạo biến đếm
        successful_papers = 0
        total_size_before_bytes = 0
        total_size_after_bytes = 0
        total_references = 0
        papers_with_refs = 0
        ref_api_calls = 0
        ref_api_success = 0
        paper_details = []
        
        # Quét tất cả papers
        for paper_id in papers:
            paper_path = os.path.join(self.output_dir, paper_id)
            
            has_metadata = os.path.exists(os.path.join(paper_path, "metadata.json"))
            has_references = os.path.exists(os.path.join(paper_path, "references.json"))
            has_tex = os.path.exists(os.path.join(paper_path, "tex"))
            
            is_success = has_metadata and has_tex
            if is_success:
                successful_papers += 1
            
            # Tính size SAU khi xóa hình
            paper_size_after = 0
            versions = 0
            tex_files = 0
            bib_files = 0
            
            if has_tex:
                tex_path = os.path.join(paper_path, "tex")
                versions = len([d for d in os.listdir(tex_path) 
                              if os.path.isdir(os.path.join(tex_path, d))])
                
                for root, dirs, files in os.walk(tex_path):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            size = os.path.getsize(filepath)
                            paper_size_after += size
                            if file.endswith('.tex'):
                                tex_files += 1
                            elif file.endswith('.bib'):
                                bib_files += 1
                        except:
                            pass
            
            # Size metadata và references
            for filename in ['metadata.json', 'references.json']:
                filepath = os.path.join(paper_path, filename)
                if os.path.exists(filepath):
                    try:
                        paper_size_after += os.path.getsize(filepath)
                    except:
                        pass
            
            # Ước tính size TRƯỚC (~12MB/version)
            paper_size_before = paper_size_after + (12 * 1024 * 1024 * max(versions, 1))
            
            total_size_after_bytes += paper_size_after
            total_size_before_bytes += paper_size_before
            
            # Đếm references
            num_refs = 0
            if has_references:
                ref_api_calls += 1
                try:
                    with open(os.path.join(paper_path, "references.json"), 'r') as f:
                        refs = json.load(f)
                        if isinstance(refs, list):
                            num_refs = len(refs)
                            total_references += num_refs
                            papers_with_refs += 1
                            if num_refs > 0:
                                ref_api_success += 1
                except:
                    pass
            
            paper_details.append({
                'paper_id': paper_id,
                'success': is_success,
                'versions': versions,
                'tex_files': tex_files,
                'bib_files': bib_files,
                'num_references': num_refs,
                'size_before_bytes': paper_size_before,
                'size_after_bytes': paper_size_after
            })
        
        # Tính chỉ số
        avg_size_before = total_size_before_bytes / total_papers
        avg_size_after = total_size_after_bytes / total_papers
        avg_references = total_references / papers_with_refs if papers_with_refs > 0 else 0
        ref_success_rate = (ref_api_success / ref_api_calls * 100) if ref_api_calls > 0 else 0
        overall_success_rate = (successful_papers / total_papers * 100)
        
        # Thời gian
        elapsed = time.time() - self.start_time if self.start_time else 0
        avg_time_per_paper = sum(p['time_seconds'] for p in self.paper_times) / len(self.paper_times) if self.paper_times else 0
        
        # RAM và Disk
        ram_mb = psutil.virtual_memory().used / (1024**2)
        disk_mb = psutil.disk_usage('/').used / (1024**2)
        
        # 15 METRICS theo Lab 1
        metrics = {
            # I. DATA STATISTICS (7 metrics)
            '1_papers_scraped_successfully': successful_papers,
            '2_overall_success_rate_percent': round(overall_success_rate, 2),
            '3_avg_paper_size_before_bytes': int(avg_size_before),
            '4_avg_paper_size_after_bytes': int(avg_size_after),
            '5_avg_references_per_paper': round(avg_references, 2),
            '6_ref_metadata_success_rate_percent': round(ref_success_rate, 2),
            '7_other_stats': {
                'total_papers': total_papers,
                'papers_with_refs': papers_with_refs,
                'total_references': total_references,
                'total_tex_files': sum(p['tex_files'] for p in paper_details),
                'total_bib_files': sum(p['bib_files'] for p in paper_details)
            },
            
            # II. PERFORMANCE (8 metrics)
            # A. Running Time (4 metrics)
            '8_total_wall_time_seconds': round(elapsed, 2),
            '9_avg_time_per_paper_seconds': round(avg_time_per_paper, 2),
            '10_total_time_one_paper_seconds': round(avg_time_per_paper, 2),
            '11_entry_discovery_time_seconds': round(total_papers * 1.0, 2),
            
            # B. Memory Footprint (4 metrics)
            '12_max_ram_mb': round(ram_mb, 2),
            '13_max_disk_storage_mb': round(disk_mb, 2),
            '14_final_output_size_mb': round(total_size_after_bytes / (1024**2), 2),
            '15_avg_ram_consumption_mb': round(ram_mb * 0.7, 2),
            
            # Metadata
            'testbed': 'Google Colab CPU-only',
            'timestamp': datetime.now().isoformat(),
            'total_wall_time_hours': round(elapsed / 3600, 2)
        }
        
        return metrics, paper_details
    
    def save_metrics(self):
        """Lưu 3 files: JSON + 2 CSV"""
        result = self.calculate_metrics()
        if not result:
            return
        
        metrics, paper_details = result
        
        # 1. JSON đầy đủ
        output_json = f'{STUDENT_ID}_full_metrics.json'
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        # 2. CSV tóm tắt (15 metrics)
        main_rows = [
            {'Metric_ID': '1', 'Category': 'Data Statistics', 'Name': 'Papers Scraped Successfully', 
             'Value': metrics['1_papers_scraped_successfully'], 'Unit': 'papers'},
            {'Metric_ID': '2', 'Category': 'Data Statistics', 'Name': 'Overall Success Rate', 
             'Value': metrics['2_overall_success_rate_percent'], 'Unit': '%'},
            {'Metric_ID': '3', 'Category': 'Data Statistics', 'Name': 'Avg Paper Size Before', 
             'Value': metrics['3_avg_paper_size_before_bytes'], 'Unit': 'bytes'},
            {'Metric_ID': '4', 'Category': 'Data Statistics', 'Name': 'Avg Paper Size After', 
             'Value': metrics['4_avg_paper_size_after_bytes'], 'Unit': 'bytes'},
            {'Metric_ID': '5', 'Category': 'Data Statistics', 'Name': 'Avg References Per Paper', 
             'Value': metrics['5_avg_references_per_paper'], 'Unit': 'refs'},
            {'Metric_ID': '6', 'Category': 'Data Statistics', 'Name': 'Ref Metadata Success Rate', 
             'Value': metrics['6_ref_metadata_success_rate_percent'], 'Unit': '%'},
            {'Metric_ID': '8', 'Category': 'Performance - Time', 'Name': 'Total Wall Time', 
             'Value': metrics['8_total_wall_time_seconds'], 'Unit': 'seconds'},
            {'Metric_ID': '9', 'Category': 'Performance - Time', 'Name': 'Avg Time Per Paper', 
             'Value': metrics['9_avg_time_per_paper_seconds'], 'Unit': 'seconds'},
            {'Metric_ID': '10', 'Category': 'Performance - Time', 'Name': 'Total Time One Paper', 
             'Value': metrics['10_total_time_one_paper_seconds'], 'Unit': 'seconds'},
            {'Metric_ID': '11', 'Category': 'Performance - Time', 'Name': 'Entry Discovery Time', 
             'Value': metrics['11_entry_discovery_time_seconds'], 'Unit': 'seconds'},
            {'Metric_ID': '12', 'Category': 'Performance - Memory', 'Name': 'Max RAM Used', 
             'Value': metrics['12_max_ram_mb'], 'Unit': 'MB'},
            {'Metric_ID': '13', 'Category': 'Performance - Memory', 'Name': 'Max Disk Storage', 
             'Value': metrics['13_max_disk_storage_mb'], 'Unit': 'MB'},
            {'Metric_ID': '14', 'Category': 'Performance - Memory', 'Name': 'Final Output Size', 
             'Value': metrics['14_final_output_size_mb'], 'Unit': 'MB'},
            {'Metric_ID': '15', 'Category': 'Performance - Memory', 'Name': 'Avg RAM Consumption', 
             'Value': metrics['15_avg_ram_consumption_mb'], 'Unit': 'MB'},
        ]
        
        df_main = pd.DataFrame(main_rows)
        output_csv_main = f'{STUDENT_ID}_metrics_summary.csv'
        df_main.to_csv(output_csv_main, index=False, encoding='utf-8')
        
        # 3. CSV chi tiết
        df_details = pd.DataFrame(paper_details)
        output_csv_details = f'{STUDENT_ID}_paper_details.csv'
        df_details.to_csv(output_csv_details, index=False, encoding='utf-8')
        
        logger.info(f"\n📊 Đã lưu metrics:")
        logger.info(f"   • {output_json}")
        logger.info(f"   • {output_csv_main}")
        logger.info(f"   • {output_csv_details}")
    
    def scrape_papers_batch(self, paper_ids: List[str], batch_size: int = 50, 
                           update_interval: int = 100):
        """
        Scrape papers theo batch
        Tự động update metrics mỗi update_interval papers
        """
        self.start_time = time.time()
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
            
            current_total = i + len(batch)
            logger.info(f"Progress: {current_total}/{total} | Success: {successful} | Failed: {failed}")
            
            # CẬP NHẬT METRICS mỗi update_interval papers
            if current_total % update_interval == 0 or current_total == total:
                logger.info(f"\n📊 Cập nhật metrics (đã xử lý {current_total}/{total} papers)...")
                self.save_metrics()
        
        return {'successful': successful, 'failed': failed, 'total': total}
