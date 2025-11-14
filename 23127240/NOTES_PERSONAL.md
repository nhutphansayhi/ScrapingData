# Ghi chú cá nhân - Lab 1

## TODO List

- [x] Setup project structure
- [x] Implement basic scraper
- [x] Add parallel processing
- [x] Test với 10 papers
- [x] Fix bug extract tar.gz
- [x] Add performance monitoring
- [x] Handle API rate limits
- [x] Implement resume capability
- [x] Calculate 15 metrics
- [x] Write documentation
- [ ] Chạy full 5000 papers
- [ ] Làm Report.docx
- [ ] Quay demo video
- [ ] Upload lên Drive
- [ ] Nộp bài

---

## Bugs đã fix

### 1. Extract tar.gz fail
**Vấn đề:** Một số papers không extract được  
**Nguyên nhân:** Có papers chỉ là single gzip file, không phải tar  
**Fix:** Thêm fallback handle cho gzip file

### 2. Rate limit S2
**Vấn đề:** Bị rate limit từ Semantic Scholar  
**Nguyên nhân:** Gọi API quá nhanh  
**Fix:** Thêm delay 1.1s giữa mỗi call

### 3. Memory leak
**Vấn đề:** RAM tăng dần khi chạy nhiều papers  
**Nguyên nhân:** Không cleanup temp files  
**Fix:** Xóa temp folder trong finally block

### 4. Parallel không work
**Vấn đề:** Vẫn chạy tuần tự dù có ThreadPoolExecutor  
**Nguyên nhân:** Logger có lock chung  
**Fix:** Mỗi thread tạo scraper riêng

---

## Notes về API

### arXiv API
- Endpoint: `https://arxiv.org/e-print/{arxiv_id}`
- Rate limit: Tự động delay 3s trong library
- Download: `.tar.gz` chứa toàn bộ source
- Versions: Append `v1`, `v2`... vào arxiv_id

### Semantic Scholar API
- Endpoint: `https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}`
- Rate limit: 100 req/5 min
- Fields: `references,references.paperId,references.externalIds,...`
- Note: Chỉ lấy refs có ArXiv ID

---

## Thời gian ước tính

### Với 6 workers:
- Mỗi paper: ~8-9 giây (do API delays)
- 5000 papers: ~44,000 giây = ~12 giờ
- Không thể nhanh hơn được vì API rate limit

### Các bước trong mỗi paper:
1. Get metadata: ~1-2s (arXiv API)
2. Download all versions: ~2-3s/version (arXiv)
3. Extract tar.gz: ~0.5s
4. Clean figures: ~0.1s
5. Get references: ~1-2s (S2 API)

Tổng: ~8-9s nếu 1 version, lâu hơn nếu nhiều version

---

## Optimization đã thử

### ✅ Làm được:
1. **Parallel processing** - chạy 6 papers cùng lúc
2. **Skip completed** - resume nếu crash
3. **Remove figures** - giảm 95% dung lượng
4. **Batch operations** - process theo batch 50 papers

### ❌ Không làm được:
1. **Giảm API delay** - không được, sẽ bị ban
2. **Tăng thêm workers** - không giúp gì vì bị limit bởi API
3. **Cache references** - không có API list toàn bộ

---

## Metrics cần tính

### I. Data Statistics (7)
1. Papers thành công - đếm papers có đủ metadata + tex
2. Success rate - % papers thành công
3. Size trước xóa hình - ước tính dựa vào versions
4. Size sau xóa hình - đo thực tế
5. Avg references - tổng refs / papers có refs
6. Ref success rate - % API calls thành công
7. Other stats - nested dict

### II. Performance (8)
**Time (4):**
8. Total wall time - từ monitor
9. Avg time per paper - từ monitor
10. Time one paper - same as #9
11. Entry discovery - ước tính 1s/paper

**Memory (4):**
12. Max RAM - từ monitor
13. Max disk - từ monitor
14. Final output size - đo folder
15. Avg RAM - estimate 70% của max

---

## Checklist Report.docx

### Phần 1: Giới thiệu
- [ ] Mô tả bài toán
- [ ] Phạm vi dữ liệu (5000 papers)
- [ ] Yêu cầu đề bài

### Phần 2: Phương pháp
- [ ] Kiến trúc hệ thống
- [ ] Các bước thực hiện
- [ ] Công nghệ sử dụng
- [ ] Parallel processing strategy

### Phần 3: Kết quả
- [ ] 15 metrics (đầy đủ)
- [ ] Bảng số liệu
- [ ] 3-4 biểu đồ:
  - Success rate (pie chart)
  - Size before/after (bar chart)
  - Time distribution
  - Memory usage

### Phần 4: Thảo luận
- [ ] Phân tích kết quả
- [ ] So sánh expected vs actual
- [ ] Khó khăn gặp phải
- [ ] Giải pháp đã áp dụng

### Phần 5: Kết luận
- [ ] Tóm tắt kết quả
- [ ] Đạt được mục tiêu chưa
- [ ] Hướng phát triển (nếu có)

---

## Demo video script

### Scene 1: Setup (15s)
- Mở Colab
- Show runtime type (CPU-only)
- Clone repo

### Scene 2: Running (45s)
- Chạy scraper
- Show progress logs
- Giải thích parallel processing
- Show debug cell (papers tăng)

### Scene 3: Results (45s)
- Show metrics output
- Highlight key numbers:
  - 99% success
  - 98% size reduction
  - 12 hours wall time
- Show data structure
- Preview CSV files

### Scene 4: Conclusion (15s)
- Show 3 output files
- Mention GitHub & Drive
- Cảm ơn

---

## Files cần nộp

1. **Report.docx**
   - Đầy đủ 15 metrics
   - Có biểu đồ
   - Phân tích kết quả
   
2. **Demo video**
   - ≤120 giây
   - YouTube public 1 tháng
   - Show đủ các bước

3. **Data**
   - Upload Google Drive
   - Share link trong Report
   - File `23127240_data.zip`

4. **Source code**
   - GitHub repo
   - Link trong Report
   - Có README

---

## Timeline

- **Week 1:** Setup + implement basic scraper
- **Week 2:** Add parallel + optimize
- **Week 3:** Test + fix bugs
- **Week 4:** Full run 5000 papers ← ĐÂY
- **Week 5:** Report + video + submit

**Deadline:** [Điền ngày deadline]

---

## References

- arXiv API Docs: https://info.arxiv.org/help/api/
- Semantic Scholar API: https://api.semanticscholar.org/
- Python multiprocessing: https://docs.python.org/3/library/concurrent.futures.html
- Lab 1 requirements: [Link đến đề bài]

---

## Notes thêm

- Test với 10-20 papers trước khi chạy full
- Backup code thường xuyên (git commit)
- Monitor RAM/disk trong khi chạy
- Colab timeout 12 giờ - cần check thường xuyên
- Nếu crash, chạy lại sẽ resume tự động

---

**Last updated:** [Ngày tháng hiện tại]
