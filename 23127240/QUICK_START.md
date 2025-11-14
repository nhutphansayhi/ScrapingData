# 🚀 Quick Start - Realtime Metrics

## ✨ Tính năng mới

Script tự động tạo và cập nhật file thống kê **MỖI 50 PAPERS**!

## 📁 Files tự động tạo

```
23127240_data/
├── paper_details.csv      ← Chi tiết từng paper
├── scraping_stats.csv     ← Tổng quan 15 metrics
├── scraping_stats.json    ← Dữ liệu đầy đủ
└── README_METRICS.md      ← Hướng dẫn
```

## 🎯 Sử dụng trên Colab

### 1. Chạy scraper (cell "Chạy Scraper")
```python
# Scraper tự động update metrics mỗi 50 papers
# Bạn sẽ thấy log:
# 💾 CHECKPOINT: Saving full statistics at paper 50/5000
# ✅ CSV files updated
```

### 2. Xem tiến độ (cell "Xem Metrics Realtime")
```python
# Chạy cell này mỗi vài phút để xem progress
# Hiển thị:
# - Số papers đã xử lý
# - Stats trung bình
# - 5 papers gần nhất
```

### 3. Download files (cell "Download Files")
```python
# Download về máy local để phân tích
from google.colab import files
files.download('23127240_data/paper_details.csv')
```

## 📊 Format CSV

### paper_details.csv
```csv
paper_id,arxiv_id,title,authors,runtime_s,size_before,size_after,num_refs,...
1,2311.14859,Paper Title,Authors,10.16,18979,18979,28,...
```

### scraping_stats.csv
```csv
Metric Category,Metric Name,Value,Unit
Data Statistics,Successful Papers,1313,papers
Performance - Time,Total Wall Time,27761.04,seconds
Performance - Memory,Max RAM Used,766.38,MB
```

## ⚡ Tần suất cập nhật

- **Mỗi 10 papers:** Progress log + Quick save (JSON)
- **Mỗi 50 papers:** FULL CHECKPOINT (CSV + JSON)

## 💡 Tips

✅ **DO:**
- Chạy "Xem Metrics" cell mỗi 5-10 phút
- Download CSV backup mỗi 100-200 papers
- Để Colab chạy liên tục (đừng tắt tab)

❌ **DON'T:**
- Interrupt scraper giữa chừng (mất progress)
- Tắt Colab trong khi đang chạy
- Lo lắng nếu crash - checkpoint đã lưu!

## 📖 Đọc thêm

- `REALTIME_METRICS_USAGE.md` - Hướng dẫn chi tiết
- `README_METRICS.md` - Format file & metrics
- Notebook có cell instructions đầy đủ

---

**Chúc bạn scraping thành công! 🎉**
