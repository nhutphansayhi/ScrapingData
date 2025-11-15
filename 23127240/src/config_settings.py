# Configuration file for my arXiv scraper
# Student ID: 23127240

# My info
STUDENT_ID = "23127240"

# Paper range from the assignment
START_YEAR_MONTH = "2311"
START_ID = 14685
END_YEAR_MONTH = "2312"
END_ID = 844

# API delays - learned this the hard way, got blocked a few times lol
ARXIV_API_DELAY = 1.0  # wait 1 sec between arXiv calls
SEMANTIC_SCHOLAR_DELAY = 1.1  # Semantic Scholar is stricter, need to wait longer

# Retry settings for when API calls fail
MAX_RETRIES = 3
RETRY_DELAY = 3.0  # wait 3 sec before trying again

# Parallel processing - tested different values, 6 seems optimal
MAX_WORKERS = 6  # tried 3, 6, and 12. 12 was too much, 3 was slow

# Folders
DATA_DIR = f"../{STUDENT_ID}_data"
LOGS_DIR = "./logs"

# Skip really big files
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB max

# Semantic Scholar API settings
SEMANTIC_SCHOLAR_API_BASE = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_FIELDS = "references,references.paperId,references.externalIds,references.title,references.authors,references.publicationDate,references.year"
