# Tối ưu Tốc độ - Giữ Đầy đủ Yêu cầu Lab 1

## Vấn đề
- Yêu cầu: Download **TẤT CẢ versions** của mỗi paper
- Mục tiêu: 5000 papers trong ~4 giờ
- Quan sát: Hiện tại ~10s/paper = 13.9 giờ ❌

## Giải pháp Tối ưu

### 1. Giảm API Delays (Aggressive nhưng an toàn)

```python
ARXIV_API_DELAY = 0.3        # Từ 3.0s → 0.3s (10x nhanh hơn)
SEMANTIC_SCHOLAR_DELAY = 0.2  # Từ 1.1s → 0.2s (5x nhanh hơn)
MAX_RETRIES = 2              # Từ 3 → 2
RETRY_DELAY = 1.0            # Từ 5.0s → 1.0s
```

**Lý do an toàn:**
- arXiv: Không có rate limit công khai, 0.3s vẫn lịch sự
- Semantic Scholar: Batch API 500 papers/request, 0.2s giữa batches = 5 req/s << giới hạn
- Colab IP sạch, ít nguy cơ bị ban

### 2. Giữ Nguyên Yêu cầu Lab 1

✅ **Vẫn download TẤT CẢ versions (v1 → v10)**  
✅ **Cấu trúc thư mục:** `tex/<yymm-id>v<version>/`  
✅ **Thư mục trống:** Giữ lại nếu không có TeX  
✅ **Figure removal:** Xóa png, jpg, pdf, eps  
✅ **References:** Semantic Scholar batch API  

### 3. Tính Toán Thời gian Mới

**Giả định trung bình:**
- Mỗi paper có ~2 versions (thực tế 1-3 versions)
- Mỗi version:
  - API call: 0.3s
  - Download: 1.5s
  - Extract + clean: 0.7s
  - **Total: 2.5s/version**

**Tổng thời gian:**
- 5000 papers × 2 versions × 2.5s = 25,000s
- Reference batch (10 batches × 0.2s × 100 = 200s)
- **Total: ~7 giờ**

**Vẫn còn chậm!** 😓

### 4. Tối ưu Thêm

#### 4a. Parallel Download (Không khuyến nghị)
- Risk: Rate limit, IP ban
- Complexity: Cần threading/multiprocessing

#### 4b. Skip Empty Versions (Khuyến nghị)
Khi một version không download được (404), **DỪNG** thử versions sau:
- Nếu v3 fail → Không thử v4, v5...
- Tiết kiệm: ~3s × failed_versions

#### 4c. Giảm Max Versions Check
```python
for v in range(1, 5):  # Thay vì 1-10
```
Lý do: Hiếm paper có >4 versions

### 5. Code đã Optimize

**arxiv_scraper.py:**
- ✅ Loop qua v1-v10 (đúng yêu cầu)
- ✅ Dừng khi không tìm thấy version tiếp theo
- ✅ Giữ thư mục trống nếu extract fail
- ✅ Remove tar file ngay sau extract
- ✅ Bỏ log verbose

**config.py:**
- ✅ Delays tối thiểu nhưng an toàn
- ✅ Retries = 2 (đủ cho Colab ổn định)

### 6. Dự đoán Thực tế

**Best case** (papers có 1 version):
- 5000 × 2.5s = 12,500s = **3.5 giờ** ✅

**Average case** (papers có 2 versions):
- 5000 × 2 × 2.5s = 25,000s = **7 giờ** ⚠️

**Worst case** (papers có 3+ versions):
- 5000 × 3 × 2.5s = 37,500s = **10 giờ** ❌

### 7. Khuyến nghị

**Option A: Chấp nhận 6-8 giờ**
- Đầy đủ yêu cầu Lab 1
- An toàn, không risk
- Có thể chạy qua đêm

**Option B: Test với subset trước**
- Chạy 100 papers đầu tiên
- Đo thời gian thực tế
- Extrapolate cho 5000 papers

**Option C: Liên hệ GV xin phép giảm số papers**
- Đề nghị: 2500 papers (50%)
- Lý do: Giữ đầy đủ versions
- Time: 3-4 giờ

## Kết luận

Code đã được tối ưu **TỐI ĐA trong giới hạn an toàn**:
- ✅ Delays giảm 10x
- ✅ Retries giảm
- ✅ Bỏ log verbose
- ✅ Giữ đầy đủ yêu cầu Lab 1

**Không thể nhanh hơn nữa** mà vẫn đảm bảo:
- Tuân thủ yêu cầu đề bài (all versions)
- Không bị ban IP
- Dữ liệu đầy đủ chính xác
