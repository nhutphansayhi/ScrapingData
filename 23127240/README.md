# arXiv Paper Scraper - Lab 1

Project scrape paper từ arXiv, lấy source code TeX, metadata, references và info từ Semantic Scholar.

## Thông tin Lab

**MSSV:** 23127240  
**Khoảng paper:** 2311.14685 đến 2312.00843 (khoảng 5000 papers)
**Môn:** Nhập môn khoa học dữ liệu - Lab 1

## Tính năng chính

- **Chạy song song:** Dùng 6 threads để tăng tốc (vẫn tuân thủ rate limit của API)
- **Lấy tất cả version:** Download từ v1 đến v10 của mỗi paper (theo yêu cầu đề bài)
- **Xóa hình ảnh:** Tự động remove figures để giảm dung lượng (~95%)
- **Batch API:** Dùng Semantic Scholar batch API (500 papers mỗi lần)
- **Metadata đầy đủ:** Lưu dạng JSON với ngày submit và update
- **Tạo BibTeX:** Tự động gen file .bib 
- **Resume được:** Nếu chạy lại thì skip papers đã xong

## Cài đặt môi trường

### Yêu cầu

- Python 3.8 trở lên
- pip để cài thư viện
- Kết nối internet

### Cách cài

1. **Vào thư mục project**
   ```bash
   cd 23127240
   ```

2. **Tạo virtual env (nên làm)**
   ```bash
   python -m venv venv
   
   # Windows:
   venv\Scripts\activate
   
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Cài thư viện**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

## Chạy scraper

### Trên Google Colab (theo yêu cầu Lab)

Dùng notebook này để test trên Colab:

```
Link: https://colab.research.google.com/github/nhutphansayhi/ScrapingDataNew/blob/main/23127240/ArXiv_Scraper_Colab.ipynb

Nhớ chỉnh Runtime > Change runtime type > None (CPU-only như đề yêu cầu)
Rồi Run all cells
```

### Chạy local

```bash
cd src
python main.py
```

Sẽ scrape papers từ **2311.14685 đến 2312.00843** (khoảng 5000 cái)

## Tối ưu hiệu năng

### Song song hóa (theo Lab 1)

- **Số workers:** Mình dùng 6 threads (có thể đổi trong `config.py`)
- **Tăng tốc:** Nhanh hơn chạy tuần tự khoảng 6 lần
- **Rate limit:** Vẫn tuân thủ quy định của arXiv & Semantic Scholar
- **Mục tiêu:** Chạy xong 5000 papers trong ~4 tiếng

### Cấu hình

Sửa trong file `src/config.py`:

```python
MAX_WORKERS = 6              # Số thread song song
ARXIV_API_DELAY = 1.0        # Delay giữa các request arXiv
SEMANTIC_SCHOLAR_DELAY = 1.1  # Delay giữa các request S2
```

## Cấu trúc output

Scraper sẽ tạo thư mục như này:

```
23127240_data/
├── 2311-14685/
│   ├── tex/
│   │   ├── v1/          # version 1
│   │   ├── v2/          # version 2
│   │   └── ...
│   ├── metadata.json    # thông tin paper
│   ├── references.bib   # file bibtex
│   └── references.json  # danh sách references
├── 2311-14686/
│   └── ...
└── scraping_stats.json   # thống kê tổng quan
```

### Giải thích các file

1. **tex/** - Chứa source TeX của tất cả versions, đã xoá hình
2. **metadata.json** - Metadata của paper (title, authors, ngày submit, abstract, categories, DOI, v.v.)
3. **references.bib** - BibTeX entry
4. **references.json** - Dict các references có arXiv ID kèm metadata

## Chi tiết xử lý

### Xóa hình ảnh

Scraper tự động remove figures để giảm dung lượng bằng cách xoá `\includegraphics` commands, xoá `\begin{figure}...\end{figure}` environments, và xoá các file ảnh.

### Rate limits

Code có delay giữa các requests: 1s cho arXiv và 1.1s cho Semantic Scholar (tuân thủ quy định API).

### Xử lý lỗi

- Tự retry tối đa 3 lần nếu request fail
- Handle được trường hợp paper không tồn tại
- Log chi tiết các operations

## Logs

Logs được lưu vào `logs/scraper.log` với các thông tin progress, download status, errors và performance stats.

## Thống kê

Scraper track các số liệu như đề yêu cầu:

### Data Statistics
- Number of papers scraped successfully
- Overall success rate
- Average paper size before and after removing figures
- Average number of references per paper
- Average success rate for scraping reference metadata

### Performance Metrics

#### Running Time
- Total runtime (wall time)
- Entry discovery time
- Average time to process each paper
- Total paper processing time

#### Memory Footprint
- Maximum RAM used during scraping
- Average RAM consumption
- Maximum disk storage required
- Final output storage size

Tất cả stats được lưu vào `scraping_stats.json`.

## Performance

- **Runtime**: Mỗi paper mất khoảng 10-15s
- **Dung lượng**: Mỗi paper sau khi xoá hình khoảng 50-500 KB
- **Memory**: Dùng peak khoảng 200-300 MB

## Xử lý lỗi thường gặp

### Các vấn đề hay gặp

1. **"Paper not found"** - Một số arXiv ID không tồn tại, scraper sẽ skip qua
2. **Rate limit errors** - Đã handle tự động với delays
3. **Connection timeout** - Tự retry nếu fail
4. **Import error** - Nhớ cài đủ packages: `pip install -r requirements.txt`

### Test trên Colab

Để chạy trên Colab:

```python
!pip install arxiv requests beautifulsoup4 bibtexparser psutil

!python main.py
```

## Yêu cầu hệ thống

- **Python**: 3.8 trở lên
- **Ổ cứng**: Tầm 1-2 GB trống
- **RAM**: Tối thiểu 2 GB
- **Mạng**: Internet ổn định

## Ghi chú

Project này làm cho môn Nhập môn khoa học dữ liệu, Lab 1.

**MSSV:** 23127240

