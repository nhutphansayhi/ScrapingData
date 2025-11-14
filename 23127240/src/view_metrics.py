#!/usr/bin/env python3
"""
Script hiển thị metrics realtime - chạy song song với scraper
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
import time

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def display_metrics(data_dir="23127240_data"):
    """Hiển thị metrics từ các file CSV/JSON"""
    
    details_csv = os.path.join(data_dir, "paper_details.csv")
    stats_csv = os.path.join(data_dir, "scraping_stats.csv")
    stats_json = os.path.join(data_dir, "scraping_stats.json")
    
    clear_screen()
    
    print("="*80)
    print(f"📊 ARXIV SCRAPER - REALTIME METRICS")
    print(f"⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    
    # Check paper details
    if os.path.exists(details_csv):
        try:
            df = pd.read_csv(details_csv)
            total_papers = len(df)
            
            print(f"✅ Papers Processed: {total_papers}")
            print()
            print("📈 Performance Metrics:")
            print(f"   Avg runtime: {df['runtime_s'].mean():.2f}s per paper")
            print(f"   Avg size after: {df['size_after'].mean()/1024:.2f} KB")
            print(f"   Avg references: {df['num_refs'].mean():.2f}")
            print(f"   Max RAM: {df['max_rss'].max():.2f} MB")
            print(f"   Current RAM: {df['avg_rss'].iloc[-1]:.2f} MB")
            print()
            
            print("📋 Last 5 Papers:")
            print("-"*80)
            last_5 = df[['paper_id', 'arxiv_id', 'runtime_s', 'num_refs']].tail(5)
            for _, row in last_5.iterrows():
                print(f"   [{row['paper_id']:4d}] {row['arxiv_id']:15s} | {row['runtime_s']:6.2f}s | {row['num_refs']:2.0f} refs")
            print("-"*80)
            print()
            
            print(f"⏱️  Last Update: {df.iloc[-1]['processed_at']}")
            
        except Exception as e:
            print(f"❌ Error reading paper_details.csv: {e}")
    else:
        print("⏳ Waiting for first checkpoint (50 papers)...")
        print("   paper_details.csv will be created after 50 papers")
    
    print()
    
    # Check stats JSON
    if os.path.exists(stats_json):
        try:
            with open(stats_json, 'r') as f:
                stats = json.load(f)
            
            data_stats = stats.get('data_statistics', {})
            perf_time = stats.get('performance_running_time', {})
            perf_mem = stats.get('performance_memory_footprint', {})
            
            print("📊 Summary Statistics:")
            print(f"   Success rate: {data_stats.get('success_rate', 0):.2f}%")
            print(f"   Total runtime: {perf_time.get('total_runtime_s', 0)/60:.2f} minutes")
            print(f"   Disk usage: {perf_mem.get('max_disk_mb', 0):.2f} MB")
            
        except Exception as e:
            print(f"❌ Error reading stats: {e}")
    
    print()
    print("="*80)
    print("💡 Press Ctrl+C to exit | Updates every 30s")
    print("="*80)

def main():
    """Main loop - cập nhật mỗi 30 giây"""
    
    # Kiểm tra thư mục data
    data_dir = "23127240_data"
    if not os.path.exists(data_dir):
        # Thử tìm trong parent directory
        data_dir = "../23127240_data"
        if not os.path.exists(data_dir):
            print(f"❌ Error: Không tìm thấy thư mục {data_dir}")
            print("   Chạy script này từ thư mục chứa '23127240_data' hoặc từ 'src/'")
            sys.exit(1)
    
    print("🚀 Starting metrics viewer...")
    print("   Monitoring:", os.path.abspath(data_dir))
    time.sleep(2)
    
    try:
        while True:
            display_metrics(data_dir)
            time.sleep(30)  # Cập nhật mỗi 30 giây
            
    except KeyboardInterrupt:
        print("\n\n👋 Exiting metrics viewer...")
        sys.exit(0)

if __name__ == "__main__":
    main()
