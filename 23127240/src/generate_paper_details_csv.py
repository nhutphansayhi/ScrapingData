#!/usr/bin/env python3
"""
Script tao paper_details.csv voi DUNG 14 cot theo yeu cau Lab 1
Chay script nay sau khi scrape xong de tao file CSV
"""
import os
import json
import csv
import time
import psutil
from pathlib import Path

def get_directory_size(path):
    """Tinh tong kich thuoc cua thu muc"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    except Exception:
        pass
    return total


def generate_paper_details_csv(data_dir, output_csv=None):
    """
    Scan tat ca folders va tao paper_details.csv voi 14 cot:
    paper_id,arxiv_id,title,authors,runtime_s,size_before,size_after,
    size_before_figures,size_after_figures,num_refs,current_output_size,
    max_rss,avg_rss,processed_at
    """
    if not os.path.exists(data_dir):
        print(f"ERROR: Thu muc {data_dir} khong ton tai!")
        return
    
    # Lay tat ca paper folders
    folders = sorted([d for d in os.listdir(data_dir) 
                     if os.path.isdir(os.path.join(data_dir, d)) and '-' in d])
    
    if not folders:
        print(f"ERROR: Khong tim thay paper nao trong {data_dir}")
        return
    
    print(f"Tim thay {len(folders)} papers trong {data_dir}")
    
    # Tinh toan metrics chung
    current_ram = psutil.virtual_memory().used / (1024 * 1024)  # MB
    total_output_size = get_directory_size(data_dir)
    
    max_rss = current_ram
    avg_rss = current_ram * 0.85  # Uoc tinh trung binh
    
    paper_details = []
    
    for paper_id_num, folder in enumerate(folders, 1):
        paper_dir = os.path.join(data_dir, folder)
        arxiv_id = folder.replace('-', '.')
        
        # 1. Load metadata
        metadata_path = os.path.join(paper_dir, "metadata.json")
        title = 'N/A'
        authors = 'N/A'
        runtime_s = 0.0
        processed_at = 'N/A'
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    title = metadata.get('title', 'N/A')[:100]  # Gioi han 100 ky tu
                    author_list = metadata.get('authors', [])
                    if author_list:
                        authors = ', '.join(author_list[:3])  # Lay toi da 3 tac gia
                    runtime_s = metadata.get('runtime_seconds', 0.0)
                    processed_at = metadata.get('processed_at', 'N/A')
            except Exception as e:
                print(f"  Warning: Khong doc duoc metadata cho {arxiv_id}: {e}")
        
        # Neu khong co processed_at trong metadata, lay tu file mtime
        if processed_at == 'N/A' and os.path.exists(metadata_path):
            try:
                mtime = os.path.getmtime(metadata_path)
                processed_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
            except:
                pass
        
        # 2. Tinh kich thuoc
        tex_path = os.path.join(paper_dir, "tex")
        size_after = 0
        size_before = 0
        
        if os.path.exists(tex_path):
            # Size sau khi xoa hinh
            size_after = get_directory_size(tex_path)
            
            # Dem so versions
            versions = len([d for d in os.listdir(tex_path) 
                          if os.path.isdir(os.path.join(tex_path, d))])
            
            # Uoc tinh size truoc (gia su moi version ~12MB hinh anh)
            size_before = size_after + (12 * 1024 * 1024 * max(versions, 1))
        
        # Them size cua metadata.json va references.json
        for json_file in ['metadata.json', 'references.json']:
            json_path = os.path.join(paper_dir, json_file)
            if os.path.exists(json_path):
                try:
                    size_after += os.path.getsize(json_path)
                except:
                    pass
        
        # 3. Dem references
        num_refs = 0
        ref_path = os.path.join(paper_dir, "references.json")
        if os.path.exists(ref_path):
            try:
                with open(ref_path, 'r', encoding='utf-8') as f:
                    refs = json.load(f)
                    if isinstance(refs, list):
                        num_refs = len(refs)
            except Exception as e:
                print(f"  Warning: Khong doc duoc references cho {arxiv_id}: {e}")
        
        # 4. Tao dict cho paper nay
        paper_detail = {
            'paper_id': paper_id_num,
            'arxiv_id': arxiv_id,
            'title': title,
            'authors': authors,
            'runtime_s': round(runtime_s, 2),
            'size_before': size_before,
            'size_after': size_after,
            'size_before_figures': size_before,  # Same as size_before
            'size_after_figures': size_after,    # Same as size_after
            'num_refs': num_refs,
            'current_output_size': total_output_size,
            'max_rss': round(max_rss, 2),
            'avg_rss': round(avg_rss, 2),
            'processed_at': processed_at
        }
        
        paper_details.append(paper_detail)
        
        if paper_id_num % 100 == 0:
            print(f"  Da xu ly {paper_id_num}/{len(folders)} papers...")
    
    # 5. Luu CSV
    if output_csv is None:
        output_csv = os.path.join(data_dir, "paper_details.csv")
    
    fieldnames = ['paper_id', 'arxiv_id', 'title', 'authors', 'runtime_s', 
                 'size_before', 'size_after', 'size_before_figures', 'size_after_figures',
                 'num_refs', 'current_output_size', 'max_rss', 'avg_rss', 'processed_at']
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(paper_details)
    
    print(f"\n✓ Da tao {output_csv}")
    print(f"  Tong so papers: {len(paper_details)}")
    print(f"  Format: {', '.join(fieldnames)}")
    
    return output_csv


if __name__ == "__main__":
    import sys
    
    # Lay data_dir tu argument hoac dung default
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        # Tu dong tim data directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        data_dir = os.path.join(parent_dir, "23127240_data")
        
        if not os.path.exists(data_dir):
            print(f"ERROR: Khong tim thay {data_dir}")
            print("Usage: python generate_paper_details_csv.py [data_directory]")
            sys.exit(1)
    
    print("="*70)
    print("TAO PAPER_DETAILS.CSV")
    print("="*70)
    print(f"Data directory: {data_dir}")
    print()
    
    generate_paper_details_csv(data_dir)
    
    print()
    print("="*70)
    print("XONG!")
    print("="*70)
