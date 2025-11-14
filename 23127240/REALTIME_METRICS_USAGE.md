# 🚀 Realtime Metrics Update - Hướng dẫn sử dụng

## Tính năng mới

Script đã được cập nhật để **tự động tạo và cập nhật file thống kê mỗi 50 papers**!

## 📊 Files được tạo tự động

### 1. `paper_details.csv`
**Cập nhật:** Mỗi 50 papers  
**Nội dung:** Chi tiết từng paper đã scrape

Format:
```csv
paper_id,arxiv_id,title,authors,runtime_s,size_before,size_after,size_before_figures,size_after_figures,num_refs,current_output_size,max_rss,avg_rss,processed_at
1,2311.14859,Paper Title,Authors,10.16,18979,18979,18979,18979,28,20789632,623.17,27.48,2025-11-14 09:41:14
```

### 2. `scraping_stats.csv`
**Cập nhật:** Mỗi 50 papers  
**Nội dung:** Tổng quan 15 metrics theo Lab 1

Sections:
- General Info (Student ID, range)
- Data Statistics (7 metrics)
- Performance - Running Time (4 metrics)
- Performance - Memory Footprint (4 metrics)

### 3. `scraping_stats.json`
**Cập nhật:** Mỗi 50 papers  
**Nội dung:** Dữ liệu đầy đủ dạng JSON

Structure:
```json
{
  "general_info": {...},
  "data_statistics": {...},
  "performance_running_time": {...},
  "performance_memory_footprint": {...}
}
```

## 🎯 Sử dụng trên Google Colab

### Bước 1: Chạy scraper
```python
# Cell "Chạy Scraper"
# Scraper sẽ tự động cập nhật metrics mỗi 50 papers
```

### Bước 2: Xem metrics realtime
```python
# Cell "Xem Metrics Realtime"
# Chạy cell này mỗi vài phút để xem tiến độ
import pandas as pd

df = pd.read_csv('23127240_data/paper_details.csv')
print(f"Papers processed: {len(df)}")
print(f"Last update: {df.iloc[-1]['processed_at']}")
```

### Bước 3: Download files (optional)
```python
# Cell "Download Files"
from google.colab import files
files.download('23127240_data/paper_details.csv')
files.download('23127240_data/scraping_stats.csv')
```

## 🔍 Xem metrics từ terminal (local)

Nếu chạy local, có thể dùng script helper:

```bash
cd src
python view_metrics.py
```

Script này sẽ:
- Hiển thị metrics realtime
- Tự động refresh mỗi 30 giây
- Show last 5 papers processed
- Show performance stats

## ⚙️ Cách hoạt động

### Timeline cập nhật:

```
Papers 1-9:   ⏱️  Progress log only
Paper 10:     📝 Quick save (JSON only)
Papers 11-19: ⏱️  Progress log only
Paper 20:     📝 Quick save (JSON only)
...
Paper 50:     💾 FULL CHECKPOINT
               ✅ paper_details.csv updated
               ✅ scraping_stats.csv updated
               ✅ scraping_stats.json updated
Papers 51-59: ⏱️  Progress log only
Paper 60:     📝 Quick save (JSON only)
...
Paper 100:    💾 FULL CHECKPOINT
               (files updated again)
```

### Log messages bạn sẽ thấy:

```
📊 PROGRESS UPDATE
==================================================================
Papers processed: 50
  ✅ Successful: 48
  ❌ Failed: 2
  📈 Success rate: 96.0%
  💾 RAM: 1234.5 MB (max: 1500.0 MB)
  💿 Disk: 2345.6 MB
==================================================================

💾 CHECKPOINT: Saving full statistics at paper 50/5000
📄 Paper details CSV updated: 23127240_data/paper_details.csv
   Total papers tracked: 48
✅ CSV files updated: paper_details.csv & scraping_stats.csv
```

## 📈 Ví dụ sử dụng CSV

### Python/Pandas
```python
import pandas as pd

# Load chi tiết papers
df = pd.read_csv('23127240_data/paper_details.csv')

# Tính các metrics
print(f"Total papers: {len(df)}")
print(f"Avg runtime: {df['runtime_s'].mean():.2f}s")
print(f"Avg references: {df['num_refs'].mean():.2f}")

# Filter papers có nhiều references
high_ref_papers = df[df['num_refs'] > 30]
print(f"Papers with >30 refs: {len(high_ref_papers)}")

# Plot distribution
import matplotlib.pyplot as plt
df['runtime_s'].hist(bins=50)
plt.title('Runtime Distribution')
plt.xlabel('Runtime (seconds)')
plt.show()
```

### Excel/Google Sheets
1. Download `paper_details.csv`
2. Mở bằng Excel/Sheets
3. Tạo pivot tables, charts
4. Phân tích data cho report

## 🎓 Đáp ứng yêu cầu Lab 1

Files này chứa đầy đủ 15 metrics yêu cầu:

### I. Data Statistics (7 metrics)
✅ 1. Papers scraped successfully  
✅ 2. Overall success rate (%)  
✅ 3. Avg paper size before (bytes)  
✅ 4. Avg paper size after (bytes)  
✅ 5. Avg references per paper  
✅ 6. Reference metadata success rate (%)  
✅ 7. Other statistics (total refs, versions, etc.)  

### II. Performance (8 metrics)

#### A. Running Time (4 metrics)
✅ 8. Total wall time (seconds)  
✅ 9. Avg time per paper (seconds)  
✅ 10. Total time one paper (seconds)  
✅ 11. Entry discovery time (seconds)  

#### B. Memory Footprint (4 metrics)
✅ 12. Maximum RAM used (MB)  
✅ 13. Maximum disk storage required (MB)  
✅ 14. Final output storage size (MB)  
✅ 15. Average RAM consumption (MB)  

## 💡 Tips

1. **Theo dõi tiến độ:** Chạy cell "Xem Metrics Realtime" mỗi 5-10 phút
2. **Backup thường xuyên:** Download CSV sau mỗi 100-200 papers
3. **Monitor RAM:** Nếu RAM gần đầy, restart Colab runtime
4. **Kiểm tra logs:** Scroll logs để xem papers nào failed

## 🐛 Troubleshooting

### File chưa được tạo
**Nguyên nhân:** Chưa đủ 50 papers  
**Giải pháp:** Đợi scraper xử lý đủ 50 papers

### CSV không update
**Nguyên nhân:** Scraper bị crash trước checkpoint  
**Giải pháp:** Chạy lại, progress được lưu từ checkpoint trước

### RAM overflow trên Colab
**Nguyên nhân:** Quá nhiều papers trong memory  
**Giải pháp:** 
- Runtime > Restart runtime
- Chạy lại, script sẽ skip papers đã scrape
- Checkpoint đã được lưu mỗi 50 papers

## 📞 Support

Nếu có vấn đề:
1. Check logs trong Colab
2. Xem file `logs/scraper.log`
3. Kiểm tra file README_METRICS.md trong thư mục data

---

**Happy Scraping! 🎉**
