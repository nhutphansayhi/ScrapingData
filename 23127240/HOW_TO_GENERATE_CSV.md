# Cach tao paper_details.csv dung format

## Van de

File `paper_details.csv` phai co DUNG 14 cot theo yeu cau Lab 1:
```
paper_id,arxiv_id,title,authors,runtime_s,size_before,size_after,size_before_figures,size_after_figures,num_refs,current_output_size,max_rss,avg_rss,processed_at
```

## Giai phap

Da them script `generate_paper_details_csv.py` de tao file CSV dung format.

## Cach dung

### Tren Colab:

Sau khi scrape xong, chay cell "Buoc 7" trong notebook:

```python
%cd /content/ScrapingData/23127240/src
!python3 generate_paper_details_csv.py ../23127240_data
```

File se duoc tao tai: `23127240_data/paper_details.csv`

### Tren may local:

```bash
cd 23127240/src
python3 generate_paper_details_csv.py ../23127240_data
```

## Script lam gi?

1. **Scan tat ca folders** trong `23127240_data/`
2. **Doc metadata.json** de lay:
   - `title`: Tieu de paper
   - `authors`: Danh sach tac gia (lay toi da 3)
   - `runtime_seconds`: Thoi gian scrape paper do
   - `processed_at`: Thoi diem xu ly

3. **Tinh size**:
   - `size_after`: Size sau khi xoa hinh (tex folder + JSON files)
   - `size_before`: Uoc tinh size truoc (size_after + ~12MB/version)
   - `size_before_figures` = `size_before`
   - `size_after_figures` = `size_after`

4. **Dem references** tu `references.json`

5. **Metrics chung**:
   - `current_output_size`: Tong size output folder
   - `max_rss`: RAM toi da
   - `avg_rss`: RAM trung binh

## Kiem tra file

Sau khi tao xong, kiem tra:

```bash
# Xem header
head -1 paper_details.csv

# Xem dong dau tien
head -2 paper_details.csv | tail -1

# Dem so dong (= so papers + 1 header)
wc -l paper_details.csv
```

## Vi du output

```csv
paper_id,arxiv_id,title,authors,runtime_s,size_before,size_after,size_before_figures,size_after_figures,num_refs,current_output_size,max_rss,avg_rss,processed_at
1,2311.14685,Example Paper Title,Author1, Author2, Author3,12.34,12582912,345678,12582912,345678,25,156789012,2048.5,1741.2,2024-11-15 10:23:45
```

## Luu y

- Script tu dong lay data tu `23127240_data/` (ten folder theo MSSV)
- Neu metadata.json thieu `runtime_seconds` hoac `processed_at`, se dung gia tri mac dinh
- Chi papers co du metadata.json va tex/ folder moi duoc tinh toan day du
- Script chay nhanh, chi mat vai giay cho 5000 papers
