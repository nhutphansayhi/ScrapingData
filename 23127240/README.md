# arXiv Paper Scraper - Student ID: 23127240

This project scrapes arXiv papers including full TeX sources, metadata, BibTeX references, and citation information using Semantic Scholar API.

## Assignment Details

**Student ID:** 23127240  
**Paper Range:** 2023-11/14685 to 2023-12/00843  
**Course:** Introduction to Data Science - Milestone 1

## Features

- **Parallel Processing:** 4-8 worker threads for optimal speed (tuân thủ API rate limits)
- **All Versions:** Downloads v1 → v10 của mỗi paper (Lab 1 requirement)
- **Figure Removal:** Automatic removal để giảm 95% kích thước
- **Batch API:** Semantic Scholar batch endpoint (500 papers/request)
- **Complete Metadata:** JSON format với submission/revision dates
- **BibTeX Generation:** Automatic .bib files
- **Resume Support:** Skip completed papers khi re-run

## Environment Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for API access

### Installation

1. **Clone or extract the project**
   ```bash
   cd 23127240
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

## Running the Scraper

### On Google Colab (Lab 1 Testbed)

**Recommended:** Use Colab notebook for benchmarking:

```python
# Open: https://colab.research.google.com/github/nhutphansayhi/ScrapingDataNew/blob/main/23127240/ArXiv_Scraper_Colab.ipynb

# Runtime > Change runtime type > Hardware accelerator > None (CPU-only)
# Run all cells
```

### Local Usage

```bash
cd src
python main.py
```

Scrapes papers **2311.14685 → 2312.00843** (5000 papers)

## Performance Optimization

### Parallel Strategy (Lab 1 Compliant)

- **Workers:** 4-8 threads (configurable in `config.py`)
- **Speedup:** 6x faster than sequential
- **Rate Limits:** Tuân thủ arXiv & Semantic Scholar
- **Target:** ~4-6 hours for 5000 papers

### Configuration

Edit `src/config.py`:

```python
MAX_WORKERS = 6              # Parallel threads (4-8 recommended)
ARXIV_API_DELAY = 1.0        # Delay between arXiv requests
SEMANTIC_SCHOLAR_DELAY = 1.1  # Delay between S2 requests
```

## Output Structure

The scraper creates the following directory structure:

```
23127240_data/
├── 2311-14685/
│   ├── tex/
│   │   ├── v1/
│   │   ├── v2/
│   │   └── ...
│   ├── metadata.json
│   ├── references.bib
│   └── references.json
├── 2311-14686/
│   └── ...
└── scraping_stats.json   # Overall scraping statistics
```

### File Descriptions

1. **tex/** - Contains all versions of the paper's TeX source files with figures removed
2. **metadata.json** - Paper metadata including title, authors, submission date, revised dates, abstract, categories, DOI, journal reference
3. **references.bib** - BibTeX entry for the paper
4. **references.json** - Dictionary of references that have arXiv IDs with metadata

## Processing Details

### Figure Removal

The scraper automatically removes figures from TeX files to reduce storage size by removing `\includegraphics` commands, `\begin{figure}...\end{figure}` environments, and deleting image files.

### API Rate Limits

The scraper respects API rate limits with 3 seconds delay between arXiv requests and 1.1 seconds delay between Semantic Scholar requests.

### Error Handling

Automatic retry up to 3 attempts for failed requests, graceful handling of missing papers, and detailed logging of all operations.

## Logging

Logs are saved to `logs/scraper.log` with progress updates, download status, error messages, and performance statistics.

## Statistics Tracking

The scraper tracks comprehensive statistics as required:

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

All statistics are saved to `scraping_stats.json` in the output directory.

## Performance Notes

- **Runtime**: Approximately 10-15 seconds per paper
- **Storage**: Each paper typically uses 50-500 KB after figure removal
- **Memory**: Peak usage around 200-300 MB

## Troubleshooting

### Common Issues

1. **"Paper not found" errors** - Some arXiv IDs may not exist, scraper continues with other papers
2. **Rate limit errors** - Automatically handled with delays
3. **Connection timeouts** - Automatic retry for failed requests
4. **Import errors** - Ensure all packages installed: `pip install -r requirements.txt`

### Testing on Google Colab

To run the scraper on Google Colab:

```python
!pip install arxiv requests sickle pandas psutil

!python main.py
```

## System Requirements

- **Python**: 3.8 or higher
- **Disk Space**: At least 1 GB free
- **RAM**: Minimum 2 GB recommended
- **Network**: Stable internet connection

## License

This project is created for educational purposes as part of the Introduction to Data Science course.

## Contact

**Student ID:** 23127240

