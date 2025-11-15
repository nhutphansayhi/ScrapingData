# Lab 1 - arXiv Paper Scraper

**Student:** Nhut Phan  
**Student ID:** 23127240

## About This Project

This is my Lab 1 assignment for Introduction to Data Science course. I had to build a program to scrape around 5,000 research papers from arXiv and collect their metadata.

### What I Need to Do:

- Download TeX source files from papers
- Get metadata like authors, titles, abstracts, dates
- Collect references using Semantic Scholar API
- Remove images/figures to save storage space
- Track performance metrics (time, RAM, disk space)
- Run everything on Google Colab with CPU only

### Papers I'm Scraping:

- Starting from: 2311.14685
- Ending at: 2312.00843  
- Total target: around 5,000 papers

---

## How I Built It

### 1. Setup

I'm using Google Colab as required by the assignment, running on CPU only (no GPU).

### 2. Code Structure

I split my code into several Python files to keep things organized:

- `config_settings.py` - stores all the settings like delays, number of workers, file paths
- `utils.py` - helper functions for extracting files, removing images, etc
- `arxiv_scraper.py` - main class that handles downloading papers
- `parallel_scraper.py` - handles running multiple downloads at once

### 3. Main Features

**Parallel Downloads:**
- I'm using ThreadPoolExecutor with 6 workers to download multiple papers at the same time
- This speeds things up a lot but I still need to respect the API rate limits
- Each worker downloads one paper independently

**Getting All Versions:**
- For each paper, I download all available versions (v1, v2, v3, etc up to v10)
- Each version gets saved in its own folder
- For example: `2311-14685v1`, `2311-14685v2`, and so on

**Removing Figures:**
- After extracting the tar.gz files, I only keep the `.tex` and `.bib` files
- I delete all image files (`.png`, `.jpg`, `.pdf`, `.eps`, etc)
- This saves about 95% of the disk space!

**Getting References:**
- I use the Semantic Scholar API to get paper references
- Only collecting references that have arXiv IDs (as the assignment asks)
- Everything gets saved as JSON files

**Performance Tracking:**
- I measure the total wall clock time
- Track maximum RAM usage during execution
- Monitor disk space used
- Save all metrics to CSV and JSON files for the report

### 4. Data Structure

Here's how the output data is organized:

```
23127240_data/
├── 2311-14685/
│   ├── tex/
│   │   ├── 2311-14685v1/
│   │   │   ├── main.tex
│   │   │   └── references.bib
│   │   └── 2311-14685v2/
│   │       └── main.tex
│   ├── metadata.json
│   └── references.json
├── 2311-14686/
│   └── ...
└── ...
```

Each paper folder contains:
- `tex/` - folder with all versions' TeX source files
- `metadata.json` - paper info (title, authors, abstract, dates)
- `references.json` - list of references from Semantic Scholar

Example metadata.json:
```json
{
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "submission_date": "2023-11-27T18:45:00",
  "revised_dates": ["2023-11-28T10:30:00"],
  "publication_venue": "Conference Name",
  "abstract": "Paper abstract...",
  "arxiv_id": "2311.14685"
}
```

---

## Running on Google Colab

### Step 1: Open the Notebook
- Upload `ArXiv_Scraper_Colab.ipynb` to Google Colab
- Or clone it from my GitHub repo

### Step 2: Check Runtime
- Make sure you're using CPU only (not GPU - assignment requirement)
- Run the first cell to verify

### Step 3: Clone Repository
```python
!git clone https://github.com/nhutphansayhi/ScrapingDataNew.git
%cd ScrapingDataNew/23127240
```

### Step 4: Install Libraries
```python
!pip install arxiv requests beautifulsoup4 bibtexparser psutil
```

### Step 5: Run the Scraper
- Run the main cell (the one with `monitor.start()`)
- Wait about 11-12 hours for all 5000 papers
- The monitor will print progress in real-time

### Step 6: Calculate Metrics
- After scraping is done, run the metrics cell
- This creates 3 files with all the required metrics

### Step 7: Download Results
- Zip the data folder
- Download or upload to Google Drive

---

## Expected Results

### Data Stats:
- Successfully scraped: around 4950/5000 papers (99%)
- Paper size before removing figures: ~12 MB each
- Paper size after removing figures: ~0.15 MB each  
- Storage reduction: about 98.75%
- Average references per paper: 20-25

### Performance:
- Total time: 11-12 hours (using 6 workers)
- Average time per paper: 8-9 seconds
- Max RAM usage: 2-3 GB
- Max disk usage: 15-20 GB (during processing)
- Final output size: 0.75-1 GB

---

## Challenges I Faced

1. **API Rate Limits:**
   - arXiv API has automatic 3 second delays
   - Semantic Scholar limits to 100 requests per 5 minutes
   - Had to add extra delays and retry logic when requests fail

2. **Extracting tar.gz Files:**
   - Some papers are just single gzip files, not tar archives
   - Had to write code to handle both cases
   - Took me a while to figure this out!

3. **Removing Figures:**
   - At first I tried using regex to find figures in .tex files then delete them
   - That was complicated so I changed to just deleting all files except .tex and .bib
   - Much simpler approach

4. **Memory Management:**
   - Processing 5000 papers means I need to clean up temp files constantly
   - Can't keep everything in RAM
   - Had to be careful about disk space on Colab

5. **Resume Capability:**
   - If Colab crashes in the middle, I lose everything
   - Added checks to skip papers that are already done
   - Still not perfect but helps a lot

---

## Performance Metrics

The assignment requires tracking 15 different metrics:

### I. Data Statistics (7 metrics)

1. Papers scraped successfully
2. Overall success rate (%)
3. Average paper size before removing figures (bytes)
4. Average paper size after removing figures (bytes)
5. Average references per paper
6. Reference metadata success rate (%)
7. Other statistics (total refs, tex files, bib files)

### II. Performance - Running Time (4 metrics)

8. Total wall time (seconds)
9. Average time per paper (seconds)
10. Total time for one paper (seconds)
11. Entry discovery time (seconds)

### III. Performance - Memory Footprint (4 metrics)

12. Maximum RAM usage (MB)
13. Maximum disk storage (MB)
14. Final output size (MB)
15. Average RAM consumption (MB)

All metrics get saved in these files:
- `paper_details.csv` - details for each paper
- `scraping_stats.csv` - summary of all 15 metrics
- `scraping_stats.json` - complete metrics in JSON format

---

## Technical Details

### Rate Limiting
- **arXiv API:** 1.0 second delay between requests
- **Semantic Scholar:** 1.1 second delay (they limit to 100 requests per 5 minutes)

### Error Handling
- If a request fails, I retry up to 3 times
- Wait 3 seconds between retries
- Most temporary failures get recovered automatically

### Parallel Processing
- 6 workers running at the same time
- Each worker processes one paper independently
- Thread-safe progress tracking so they don't interfere with each other

---

## Dependencies

I'm using these Python libraries:

```
arxiv==2.1.0
requests==2.31.0
pandas==2.0.3
psutil==5.9.5
```

---

## File Structure

```
23127240/
├── ArXiv_Scraper_Colab.ipynb    # Main notebook
├── README.md                     # This file
├── 23127240_data/               # Downloaded papers
│   ├── paper_details.csv
│   ├── scraping_stats.csv
│   └── scraping_stats.json
└── src/                         # Source code
    ├── arxiv_scraper.py         # Main scraper class
    ├── config_settings.py       # Settings
    ├── parallel_scraper.py      # Parallel processing
    ├── requirements.txt         # Dependencies
    ├── run_parallel.py          # Entry point
    └── utils.py                 # Helper functions
```

---

## Some Design Choices

**Why 6 workers?**
- I tested with 3, 6, and 12 workers
- 6 seems to be the sweet spot - fast but doesn't hit rate limits
- 12 was too aggressive and I kept getting blocked

**Why delete all figures?**
- Assignment says to reduce storage
- Images take up like 95% of the space
- For text analysis we only need the .tex and .bib files anyway

**Why use Semantic Scholar?**
- Their API is pretty reliable and gives structured data
- Has good arXiv ID mapping
- Easier than trying to parse BibTeX files (those are a mess)

---

## Known Issues

1. **Success rate isn't 100%:**
   - Some papers just don't have source code available (PDF only)
   - Sometimes the API fails temporarily
   - Network timeouts happen occasionally
   - Got about 99% success rate which I think is pretty good

2. **References only have arXiv IDs:**
   - Assignment specifically asks for this
   - Means I'm excluding conference papers, books, etc that aren't on arXiv
   - Kind of limits the data but that's what was required

3. **Takes forever to run:**
   - 10-12 hours for 5000 papers
   - Can't really speed it up more because of API rate limits
   - Just have to let it run overnight

---

## What Could Be Better

If I had more time, I would:
1. Add better resume capability if Colab crashes
2. Cache Semantic Scholar responses to avoid re-fetching
3. Maybe add progress bars to make it look nicer
4. Better error logging to debug issues faster

---

## Submission

**Student:** Nhut Phan  
**Student ID:** 23127240  
**Course:** Introduction to Data Science  
**Instructor:** hlhdang@fit.hcmus.edu.vn

---

**Note:** This code was written for educational purposes as part of Lab 1. I referenced the arXiv API and Semantic Scholar API documentation, and implemented the parallel processing and performance monitoring based on the assignment requirements.
