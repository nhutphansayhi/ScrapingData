"""
Configuration settings for arXiv scraper
Student ID: 23127240
"""

# Student information
STUDENT_ID = "23127240"

# Paper range to scrape (as specified in assignment)
START_YEAR_MONTH = "2311"
START_ID = 14685
END_YEAR_MONTH = "2312"
END_ID = 844

# API rate limiting delays (in seconds)
ARXIV_API_DELAY = 1.0  # Delay between arXiv API calls
SEMANTIC_SCHOLAR_DELAY = 1.1  # Delay between Semantic Scholar API calls

# Retry settings for failed requests
MAX_RETRIES = 3
RETRY_DELAY = 3.0

# Parallel processing configuration
MAX_WORKERS = 6  # Number of parallel workers

# Directory paths
DATA_DIR = f"../{STUDENT_ID}_data"
LOGS_DIR = "./logs"

# File size limit
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Semantic Scholar API configuration
SEMANTIC_SCHOLAR_API_BASE = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_FIELDS = "references,references.paperId,references.externalIds,references.title,references.authors,references.publicationDate,references.year"
