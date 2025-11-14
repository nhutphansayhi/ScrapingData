# ✅ FORMAT FILE THỐNG KÊ THEO LAB 1

## 🎯 3 FILES THỐNG KÊ ĐƯỢC TẠO MỖI 50 PAPERS:

### 1. **scraping_stats.csv** - 15 METRICS BẮT BUỘC

Format CSV rõ ràng để import vào Report:

```csv
Metric_ID,Category,Metric_Name,Value,Unit,Notes
INFO,General,Student ID,23127240,,
INFO,General,Generated At,2025-11-15 10:30:00,,

=== DATA STATISTICS (7 metrics) ===
1,Data Statistics,Papers Scraped Successfully,1313,papers,Required Metric 1
2,Data Statistics,Overall Success Rate,26.26,%,Required Metric 2
3,Data Statistics,Avg Paper Size Before Removing Figures,31048.08,bytes,Required Metric 3
4,Data Statistics,Avg Paper Size After Removing Figures,654767.22,bytes,Required Metric 4
5,Data Statistics,Avg References Per Paper,19.29,references,Required Metric 5
6,Data Statistics,Reference Metadata Success Rate,100.00,%,Required Metric 6
7,Data Statistics,Total References Found,43805,references,Required Metric 7

=== PERFORMANCE - RUNNING TIME (4 metrics) ===
8,Performance - Time,Total Wall Time (End-to-End),27761.04,seconds,Required Metric 8
9,Performance - Time,Total Time to Process ONE Paper,25.40,seconds,Required Metric 9
10,Performance - Time,Avg Time Per Required Paper,25.40,seconds,Required Metric 10
11,Performance - Time,Entry Discovery Time,0.00,seconds,Required Metric 11

=== PERFORMANCE - MEMORY FOOTPRINT (4 metrics) ===
12,Performance - Memory,Maximum RAM Used,766.38,MB,Required Metric 12
13,Performance - Memory,Average RAM Consumption,0.00,MB,Required Metric 13
14,Performance - Memory,Maximum Disk Storage Required,854.28,MB,Required Metric 14
15,Performance - Memory,Final Output Storage Size,0.00,MB,Required Metric 15
```

### 2. **scraping_stats.json** - FULL DETAILS

Cấu trúc JSON rõ ràng theo 15 metrics:

```json
{
  "metadata": {
    "student_id": "23127240",
    "paper_range_start": "2311.14685",
    "paper_range_end": "2312.00844",
    "total_papers_attempted": 5000,
    "generated_at": "2025-11-15 10:30:00",
    "testbed": "Google Colab CPU-only"
  },
  "required_15_metrics": {
    "data_statistics": {
      "metric_1_papers_scraped_successfully": 1313,
      "metric_2_overall_success_rate_percent": 26.26,
      "metric_3_avg_size_before_removing_figures_bytes": 31048.08,
      "metric_4_avg_size_after_removing_figures_bytes": 654767.22,
      "metric_5_avg_references_per_paper": 19.29,
      "metric_6_reference_metadata_success_rate_percent": 100.00,
      "metric_7_other_stats_total_references_found": 43805
    },
    "performance_running_time": {
      "metric_8_total_wall_time_seconds": 27761.04,
      "metric_9_total_time_process_one_paper_seconds": 25.40,
      "metric_10_avg_time_per_required_paper_seconds": 25.40,
      "metric_11_entry_discovery_time_seconds": 0.00
    },
    "performance_memory_footprint": {
      "metric_12_maximum_ram_used_mb": 766.38,
      "metric_13_average_ram_consumption_mb": 0.00,
      "metric_14_maximum_disk_storage_required_mb": 854.28,
      "metric_15_final_output_storage_size_mb": 0.00
    }
  },
  "additional_details": {
    "failed_papers": 377,
    "total_paper_processing_time_seconds": 27761.04
  }
}
```

### 3. **paper_details.csv** - CHI TIẾT TỪNG PAPER

```csv
paper_id,arxiv_id,title,authors,runtime_s,size_before,size_after,size_before_figures,size_after_figures,num_refs,current_output_size,max_rss,avg_rss,processed_at
1,2311.14859,An Empirical Investigation...,Prakhar Ganesh,10.16,18979,18979,18979,18979,28,20789632,623.17,27.48,2025-11-14 09:41:14
2,2311.14860,Anomalous Josephson diode effect...,"A. S. Osin, Alex Levchenko",20.88,0,470530,0,470530,26,21505158,623.17,30.91,2025-11-14 09:41:34
...
```

---

## 📊 MAPPING VỚI 15 METRICS BẮT BUỘC LAB 1:

### A. DATA STATISTICS (7 metrics):

| Metric | Tên trong Lab 1 | Field trong JSON | CSV Row |
|--------|----------------|------------------|---------|
| 1 | Papers scraped successfully | `metric_1_papers_scraped_successfully` | ID=1 |
| 2 | Overall success rate | `metric_2_overall_success_rate_percent` | ID=2 |
| 3 | Avg size BEFORE removing figures | `metric_3_avg_size_before_removing_figures_bytes` | ID=3 |
| 4 | Avg size AFTER removing figures | `metric_4_avg_size_after_removing_figures_bytes` | ID=4 |
| 5 | Avg references per paper | `metric_5_avg_references_per_paper` | ID=5 |
| 6 | Reference metadata success rate | `metric_6_reference_metadata_success_rate_percent` | ID=6 |
| 7 | Other relevant statistics | `metric_7_other_stats_total_references_found` | ID=7 |

### B. PERFORMANCE - RUNNING TIME (4 metrics):

| Metric | Tên trong Lab 1 | Field trong JSON | CSV Row |
|--------|----------------|------------------|---------|
| 8 | Wall time (end-to-end) | `metric_8_total_wall_time_seconds` | ID=8 |
| 9 | Total time to process ONE paper | `metric_9_total_time_process_one_paper_seconds` | ID=9 |
| 10 | Avg time per required paper | `metric_10_avg_time_per_required_paper_seconds` | ID=10 |
| 11 | Entry discovery time | `metric_11_entry_discovery_time_seconds` | ID=11 |

### C. PERFORMANCE - MEMORY FOOTPRINT (4 metrics):

| Metric | Tên trong Lab 1 | Field trong JSON | CSV Row |
|--------|----------------|------------------|---------|
| 12 | Maximum RAM used | `metric_12_maximum_ram_used_mb` | ID=12 |
| 13 | Average RAM consumption | `metric_13_average_ram_consumption_mb` | ID=13 |
| 14 | Maximum disk storage required | `metric_14_maximum_disk_storage_required_mb` | ID=14 |
| 15 | Final output storage size | `metric_15_final_output_storage_size_mb` | ID=15 |

---

## 🎯 THÀNH PHẦN BỔ SUNG (BEST PRACTICE):

### Timestamp & Metadata:
- ✅ `generated_at`: Thời gian tạo file stats
- ✅ `testbed`: "Google Colab CPU-only"
- ✅ `student_id`: Mã số sinh viên
- ✅ `paper_range_start` & `paper_range_end`: Phạm vi papers

### Lợi ích:
1. **Tính minh bạch**: Chứng minh thời điểm chạy
2. **Tái tạo được**: Dễ verify wall time
3. **Quản lý phiên bản**: Phân biệt các lần chạy

---

## 📂 VỊ TRÍ FILE:

```
23127240_data/
├── scraping_stats.csv      ← 15 metrics dạng table
├── scraping_stats.json     ← 15 metrics + chi tiết
├── paper_details.csv       ← Chi tiết từng paper
└── 2311-14685/, ...        ← Paper folders
```

---

## 🚀 SỬ DỤNG CHO REPORT:

### Từ CSV (dễ nhất):
1. Mở `scraping_stats.csv` trong Excel/Google Sheets
2. Copy rows có ID 1-15
3. Paste vào Report dưới dạng table
4. Thêm mô tả và phân tích

### Từ JSON (nếu cần script):
```python
import json

with open('scraping_stats.json', 'r') as f:
    data = json.load(f)
    
metrics = data['required_15_metrics']
print(f"Metric 1: {metrics['data_statistics']['metric_1_papers_scraped_successfully']}")
print(f"Metric 8: {metrics['performance_running_time']['metric_8_total_wall_time_seconds']}")
```

---

## ✅ ĐÃ TUÂN THỦ LAB 1:

- ✅ 15 metrics bắt buộc
- ✅ Phân loại rõ ràng (Data Stats, Running Time, Memory)
- ✅ Đơn vị chính xác (papers, bytes, seconds, MB, %)
- ✅ Timestamp để minh bạch
- ✅ Format CSV dễ import vào Report
- ✅ Format JSON cho automation

**→ SẴN SÀNG CHO REPORT!** 🎉
