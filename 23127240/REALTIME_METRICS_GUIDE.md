# 📊 Hướng dẫn Realtime Metrics

## Tính năng mới: Tự động cập nhật metrics mỗi 100 papers

Giờ scraper sẽ **tự động** tính và lưu 15 metrics theo yêu cầu Lab 1 mỗi khi xử lý được 100 papers!

---

## ✅ Lợi ích

### 1. Theo dõi Tiến độ Realtime
- Không cần đợi đến cuối mới có metrics
- Xem được kết quả trong khi đang chạy
- Biết ngay nếu có vấn đề

### 2. An toàn hơn
- Nếu scraper **crash giữa chừng** → vẫn có metrics của papers đã hoàn thành
- Không mất hết dữ liệu nếu Colab timeout
- Có thể resume và metrics vẫn chính xác

### 3. Đúng Format Đề bài
Tự động tạo **3 files** theo yêu cầu Lab 1:
- `23127240_full_metrics.json` - JSON đầy đủ (tất cả 15 metrics)
- `23127240_metrics_summary.csv` - CSV tóm tắt (bảng 15 metrics)
- `23127240_paper_details.csv` - CSV chi tiết từng paper

---

## 📋 15 Metrics theo Lab 1

### I. DATA STATISTICS (7 metrics)

1. **Papers Scraped Successfully** - Số papers thành công
2. **Overall Success Rate** - Tỷ lệ thành công tổng thể (%)
3. **Avg Paper Size Before** - Kích thước TB trước xóa hình (bytes)
4. **Avg Paper Size After** - Kích thước TB sau xóa hình (bytes)
5. **Avg References Per Paper** - Số references trung bình
6. **Ref Metadata Success Rate** - Tỷ lệ lấy refs thành công (%)
7. **Other Stats** - Thống kê khác (dict)

### II. PERFORMANCE (8 metrics)

#### A. Running Time (4 metrics)

8. **Total Wall Time** - Tổng thời gian (seconds)
9. **Avg Time Per Paper** - Thời gian TB/paper (seconds)
10. **Total Time One Paper** - Thời gian xử lý 1 paper (seconds)
11. **Entry Discovery Time** - Thời gian tìm entries (seconds)

#### B. Memory Footprint (4 metrics)

12. **Max RAM Used** - RAM tối đa (MB)
13. **Max Disk Storage** - Disk tối đa (MB)
14. **Final Output Size** - Kích thước output (MB)
15. **Avg RAM Consumption** - RAM trung bình (MB)

---

## 🚀 Cách sử dụng

### Trong Notebook (Google Colab)

**Scraper tự động update!** Không cần làm gì thêm:

```python
# Cell này chạy scraper
# Metrics sẽ tự động update mỗi 100 papers
!python src/run_parallel.py
```

### Xem Metrics Realtime

Chạy cell này **trong khi scraper đang chạy**:

```python
# Xem metrics hiện tại
import json

with open('23127240_full_metrics.json', 'r') as f:
    metrics = json.load(f)

print(f"Papers hoàn thành: {metrics['1_papers_scraped_successfully']}")
print(f"Thời gian: {metrics['8_total_wall_time_seconds']:.2f}s")
print(f"TB/paper: {metrics['9_avg_time_per_paper_seconds']:.2f}s")
```

---

## 📁 Output Files

### 1. `23127240_full_metrics.json`

JSON đầy đủ với tất cả metrics:

```json
{
  "1_papers_scraped_successfully": 150,
  "2_overall_success_rate_percent": 98.67,
  "3_avg_paper_size_before_bytes": 12582912,
  "4_avg_paper_size_after_bytes": 153600,
  "5_avg_references_per_paper": 23.45,
  "6_ref_metadata_success_rate_percent": 95.33,
  "7_other_stats": {
    "total_papers": 152,
    "papers_with_refs": 150,
    "total_references": 3518
  },
  "8_total_wall_time_seconds": 1350.23,
  "9_avg_time_per_paper_seconds": 8.88,
  ...
}
```

### 2. `23127240_metrics_summary.csv`

Bảng tóm tắt 15 metrics:

| Metric_ID | Category | Name | Value | Unit |
|-----------|----------|------|-------|------|
| 1 | Data Statistics | Papers Scraped Successfully | 150 | papers |
| 2 | Data Statistics | Overall Success Rate | 98.67 | % |
| 3 | Data Statistics | Avg Paper Size Before | 12582912 | bytes |
| ... | ... | ... | ... | ... |

**Copy trực tiếp vào Report.docx!**

### 3. `23127240_paper_details.csv`

Chi tiết từng paper:

| paper_id | success | versions | tex_files | bib_files | num_references | size_before_bytes | size_after_bytes |
|----------|---------|----------|-----------|-----------|----------------|-------------------|------------------|
| 2311-14685 | True | 2 | 5 | 1 | 25 | 25165824 | 204800 |
| ... | ... | ... | ... | ... | ... | ... | ... |

---

## ⚙️ Cấu hình

### Thay đổi tần suất update

Mặc định: **mỗi 100 papers**

Muốn thay đổi? Edit `src/run_parallel.py`:

```python
# Update mỗi 50 papers
results = scraper.scrape_papers_batch(
    paper_ids, 
    batch_size=50,
    update_interval=50  # <-- Thay đổi ở đây
)
```

Các tùy chọn:
- `update_interval=50` - Cập nhật mỗi 50 papers (frequent)
- `update_interval=100` - Mỗi 100 papers (khuyến nghị)
- `update_interval=200` - Mỗi 200 papers (ít hơn)

---

## 🔍 Debug / Troubleshooting

### Check metrics có đúng không?

```python
import json

with open('23127240_full_metrics.json', 'r') as f:
    metrics = json.load(f)

# Check timestamp
print(f"Last update: {metrics['timestamp']}")

# Check số papers
print(f"Papers: {metrics['1_papers_scraped_successfully']}")

# Check thời gian
print(f"Running time: {metrics['total_wall_time_hours']:.2f}h")
```

### File không tồn tại?

- Chưa chạy đến 100 papers đầu tiên
- Hoặc scraper chưa bắt đầu
- Check log: `logs/scraper.log`

### Metrics không update?

Check xem có lỗi không:

```bash
# Xem log
!tail -50 logs/scraper.log

# Check số papers hiện tại
!ls -1 23127240_data | wc -l
```

---

## 📊 So sánh với Cách Cũ

| Aspect | Cách Cũ | Cách Mới (Realtime) |
|--------|---------|---------------------|
| **Khi nào có metrics?** | Sau khi chạy xong HẾT | Mỗi 100 papers |
| **Nếu crash?** | Mất hết | Vẫn có metrics đến lúc crash |
| **Theo dõi progress?** | Không | Có! Xem realtime |
| **Format output** | Phải tính thủ công | Tự động 3 files |
| **Đúng 15 metrics Lab?** | Phải check lại | Tự động đúng format |

---

## ✅ Checklist Report.docx

Với metrics tự động, bạn có:

- [x] 15 metrics đầy đủ theo Lab 1
- [x] JSON format (cho thầy check detail)
- [x] CSV format (copy vào Word)
- [x] Realtime progress tracking
- [x] An toàn nếu crash
- [x] Timestamp để track thời gian

**Chỉ cần:**
1. Chạy scraper
2. Đợi xong (hoặc theo dõi realtime)
3. Copy từ CSV vào Report.docx
4. Done! ✨

---

## 🎯 Tips

### Ước tính thời gian còn lại

```python
import json

with open('23127240_full_metrics.json', 'r') as f:
    m = json.load(f)

papers_done = m['1_papers_scraped_successfully']
avg_time = m['9_avg_time_per_paper_seconds']
papers_remaining = 5000 - papers_done

time_remaining_hours = (papers_remaining * avg_time) / 3600

print(f"Papers xong: {papers_done}/5000")
print(f"Thời gian TB: {avg_time:.2f}s/paper")
print(f"Ước tính còn: {time_remaining_hours:.2f} giờ")
```

### Monitor RAM/Disk

```python
# Check xem có nguy cơ hết RAM không
if m['12_max_ram_mb'] > 10000:  # >10GB
    print("⚠️ RAM cao! Có thể cần cleanup")
```

---

## 📚 Reference

- Lab 1 Requirements: Tất cả 15 metrics bắt buộc
- Update frequency: Mỗi 100 papers (có thể thay đổi)
- Files location: Root của repo (cùng cấp với `src/`)
- Naming: `{STUDENT_ID}_*.{json,csv}`

---

**Chúc bạn scraping thành công! 🚀**
