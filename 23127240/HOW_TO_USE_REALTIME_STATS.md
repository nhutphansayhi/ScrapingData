# 🚀 HƯỚNG DẪN SỬ DỤNG THỐNG KÊ REALTIME

## 📊 Để theo dõi scraper trong khi đang chạy:

### Bước 1: Khởi chạy scraper (Cell 21)
```python
# Cell này sẽ bắt đầu chạy scraper và in logs
# BẠN SẼ THẤY:
# 🔥 Progress: 50/5000...
# 🔥 Progress: 100/5000...
```

### Bước 2: Mở tab mới và chạy Cell thống kê realtime
**QUAN TRỌNG:** Mở Google Colab trong TAB MỚI (Ctrl/Cmd + Click vào notebook)

**Trong tab mới:**
1. Cuộn xuống tìm cell "📊 Thống kê REALTIME"
2. Chạy cell đó
3. Sẽ thấy output:

```
📊 THEO DÕI SCRAPER REALTIME
======================================================================
⏰ Bắt đầu theo dõi: 2025-11-14 14:00:00
📈 Target: 5000 papers
🔄 Check mỗi 10 giây, tổng 20 lần

🔥 [14:00:10] Papers:   50/5000 ( 1.0%) | Speed:  6.00 p/min | ETA: 15:23:45 | Remaining: 825 min
🔥 [14:00:20] Papers:   57/5000 ( 1.1%) | Speed:  7.00 p/min | ETA: 15:18:32 | Remaining: 706 min
🔥 [14:00:30] Papers:   64/5000 ( 1.3%) | Speed:  7.20 p/min | ETA: 15:15:22 | Remaining: 685 min
...
```

### Bước 3: Sau 20 lần check (200 giây), cell sẽ tạo file CSV
```
💾 Đã lưu thống kê vào: scraping_realtime_stats.csv

📊 TỔNG KẾT
======================================================================
📄 Papers đã xử lý: 140 papers
⏱️  Thời gian theo dõi: 3.3 minutes
⚡ Tốc độ trung bình: 7.07 papers/minute
📊 Tốc độ trung bình: 8.5 seconds/paper
⏳ Ước tính thời gian còn lại: 11.5 giờ
======================================================================
```

---

## 📈 CÁCH ĐÁNH GIÁ TỐC ĐỘ

### ✅ TỐT (7-8 papers/minute = 8-9s/paper):
```
🔥 [14:00:10] Papers:   50/5000 | Speed:  7.20 p/min ✅
🔥 [14:00:20] Papers:   62/5000 | Speed:  7.20 p/min ✅
```
→ Scraper đang chạy song song tốt!

### ⚠️ CHẬM (2-3 papers/minute = 20-30s/paper):
```
🔥 [14:00:10] Papers:   50/5000 | Speed:  2.40 p/min ⚠️
🔥 [14:00:20] Papers:   54/5000 | Speed:  2.40 p/min ⚠️
```
→ Có thể đang chạy tuần tự hoặc bị lỗi!

### ❌ RẤT CHẬM (0-1 papers/minute):
```
🔥 [14:00:10] Papers:   50/5000 | Speed:  0.60 p/min ❌
```
→ Có lỗi nghiêm trọng, kiểm tra logs!

---

## 🔧 XỬ LÝ KHI CHẬM

### Nếu speed < 3 papers/minute:

1. **Check Cell 21 (tab đầu tiên)** - xem có lỗi không?
2. **Xem logs** - có nhiều "ERROR" hoặc "HTTP 429"?
3. **Chạy debug cell (Cell 21.5)**:
   ```python
   # Sẽ in ra:
   # ⏰ 14:00:00 - Đã có 50 papers
   # ⏰ 14:00:02 - Đã có 51 papers  ← Chỉ tăng 1 = CHẬM!
   # ⏰ 14:00:04 - Đã có 58 papers  ← Tăng 7 = TỐT!
   ```

### Nếu HTTP 429 (Too Many Requests):
```
arxiv_scraper - ERROR - ❌ Lỗi scraping 2311.14711: HTTP 429
```
→ BÌNH THƯỜNG! arXiv đang rate limit, scraper sẽ tự động retry.

### Nếu "Không extract được":
```
utils - ERROR - Không extract được: .../2311.14689v1.tar.gz
```
→ BÌNH THƯỜNG! Paper đó chỉ có PDF, không có TeX source.

---

## 📊 FILE CSV CHỨA GÌ?

`scraping_realtime_stats.csv`:
```csv
timestamp,count,progress_percent,speed_per_minute,remaining_minutes,eta
2025-11-14 14:00:00,50,1.0,0.0,0.0,N/A
2025-11-14 14:00:10,57,1.14,7.2,687.5,15:27:32
2025-11-14 14:00:20,64,1.28,7.2,685.5,15:25:45
...
```

**Cột quan trọng:**
- `count`: Số papers đã hoàn thành
- `speed_per_minute`: Tốc độ (papers/phút)
- `remaining_minutes`: Thời gian còn lại (phút)
- `eta`: Giờ dự kiến hoàn thành

---

## 💡 MẸO

1. **Chạy cell thống kê nhiều lần** để có nhiều data points
2. **So sánh ETA giữa các lần chạy** để thấy tốc độ có ổn định không
3. **Lưu file CSV** để đưa vào báo cáo
4. **Screenshot output** cho demo video

---

## 🎯 KỲ VỌNG THỰC TẾ

**Với 6 workers:**
- Tốc độ: **7-8 papers/minute** (8-9 seconds/paper)
- Thời gian: **~11-12 giờ** cho 5000 papers
- ETA thường dao động ±1 giờ (do papers có version khác nhau)

**ĐÂY LÀ TỐC ĐỘ TỐI ƯU!** Không thể nhanh hơn nhiều vì API rate limits.

---

## ❓ FAQ

**Q: Tại sao ETA cứ thay đổi?**
A: Vì papers có số version khác nhau. Paper 3 versions chậm gấp 3 lần paper 1 version.

**Q: Có thể dừng cell thống kê không?**
A: Có! Nhấn nút ⬛ Stop. Scraper vẫn chạy bình thường ở tab kia.

**Q: Cell thống kê có làm chậm scraper không?**
A: KHÔNG! Cell chỉ đọc folder, không ảnh hưởng scraper.

**Q: Nên chạy cell này bao lâu một lần?**
A: Mỗi 30-60 phút, hoặc khi muốn check tốc độ hiện tại.

---

## 📁 FILES KHÁC

Ngoài realtime stats, còn có:
- `performance_metrics.json` (Cell 21 - cuối cùng)
- `paper_details.csv` (Cell 24 - sau khi hoàn thành)

**TẤT CẢ files này dùng cho báo cáo!**
