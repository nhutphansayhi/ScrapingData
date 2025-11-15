# Helper functions for the scraper

import os
import re
import tarfile
import gzip
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def setup_logging(log_dir: str = "./logs"):
    """Set up logging so we can see what's happening"""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "scraper.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def format_arxiv_id(year_month: str, paper_id: int) -> str:
    """Convert year-month and ID to proper arXiv format
    Example: "2208" and 11941 -> "2208.11941"
    """
    return f"{year_month}.{paper_id:05d}"


def format_folder_name(arxiv_id: str) -> str:
    """Convert arXiv ID to folder name (replace dot with dash)
    Example: "2208.11941" -> "2208-11941"
    """
    return arxiv_id.replace(".", "-")


def extract_tar_gz(tar_path: str, extract_dir: str) -> bool:
    """Extract tar.gz file or handle gzip compressed files
    This was tricky - some papers are tar archives, some are just gzipped tex files!
    """
    if not os.path.exists(tar_path):
        logger.error(f"File doesn't exist: {tar_path}")
        return False
    
    # Try as tar.gz first
    try:
        with tarfile.open(tar_path, 'r:*') as tar:
            tar.extractall(path=extract_dir)
        logger.info(f"Extracted tar archive {tar_path}")
        return True
    except (tarfile.TarError, tarfile.ReadError):
        # Not a tar file, maybe it's just gzipped?
        try:
            with gzip.open(tar_path, 'rb') as gz_file:
                content = gz_file.read()
            
            # Check if it looks like a LaTeX file
            if content.startswith(b'\\') or b'\\documentclass' in content[:1000]:
                base_name = os.path.splitext(os.path.splitext(os.path.basename(tar_path))[0])[0]
                tex_filename = f"{base_name}.tex"
                tex_path = os.path.join(extract_dir, tex_filename)
                
                with open(tex_path, 'wb') as f:
                    f.write(content)
                
                logger.info(f"Extracted gzipped tex file {tar_path}")
                return True
            else:
                logger.error(f"Can't extract {tar_path}: not a valid file")
                return False
        except (gzip.BadGzipFile, OSError):
            # Not gzipped either, maybe it's just a plain tex file?
            try:
                with open(tar_path, 'rb') as f:
                    content = f.read()
                
                # Check if it's a tex file
                if content.startswith(b'\\') or b'\\documentclass' in content[:1000] or b'%' in content[:100]:
                    base_name = os.path.splitext(os.path.splitext(os.path.basename(tar_path))[0])[0]
                    tex_filename = f"{base_name}.tex"
                    tex_path = os.path.join(extract_dir, tex_filename)
                    
                    with open(tex_path, 'wb') as f:
                        f.write(content)
                    
                    logger.info(f"Extracted plain tex file {tar_path}")
                    return True
                else:
                    logger.error(f"Can't figure out what {tar_path} is")
                    return False
            except Exception as e:
                logger.error(f"Failed to extract {tar_path}: {e}")
                return False
        except Exception as e:
            logger.error(f"Failed to extract {tar_path}: {e}")
            return False
    except Exception as e:
        logger.error(f"Failed to extract {tar_path}: {e}")
        return False


def remove_figures_from_tex(tex_content: str) -> str:
    """Remove figure commands from tex files
    Originally tried to be fancy with this but simpler is better
    """
    # Remove \includegraphics commands
    tex_content = re.sub(
        r'\\includegraphics(\[.*?\])?\{.*?\}',
        r'% Figure removed',
        tex_content
    )
    
    # Remove figure environments
    tex_content = re.sub(
        r'\\begin\{figure\}.*?\\end\{figure\}',
        r'% Figure environment removed',
        tex_content,
        flags=re.DOTALL
    )
    
    # Remove figure* environments
    tex_content = re.sub(
        r'\\begin\{figure\*\}.*?\\end\{figure\*\}',
        r'% Figure environment removed',
        tex_content,
        flags=re.DOTALL
    )
    
    return tex_content


def remove_image_files(directory: str) -> int:
    """
    Remove common image file types from directory
    
    Args:
        directory: Directory to clean
    
    Returns:
        Number of files removed
    """
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.eps', '.svg', '.bmp', '.tiff']
    removed_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    removed_count += 1
                    logger.debug(f"Removed image file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove {file_path}: {e}")
    
    return removed_count


def find_main_tex_file(tex_dir: str) -> Optional[str]:
    """
    Find the main .tex file (contains \\documentclass)
    
    Args:
        tex_dir: Directory containing .tex files
    
    Returns:
        Path to main .tex file, or None if not found
    """
    for root, dirs, files in os.walk(tex_dir):
        for file in files:
            if file.endswith('.tex'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(2000)  # Read first 2000 chars
                        if '\\documentclass' in content:
                            return file_path
                except Exception as e:
                    logger.debug(f"Error reading {file_path}: {e}")
    return None


def find_bib_file(tex_dir: str) -> Optional[str]:
    """
    Find the .bib file (bibliography)
    
    Args:
        tex_dir: Directory containing .bib files
    
    Returns:
        Path to .bib file, or None if not found
    """
    for root, dirs, files in os.walk(tex_dir):
        for file in files:
            if file.endswith('.bib'):
                return os.path.join(root, file)
    return None


def clean_version_folder(version_dir: str) -> Dict[str, int]:
    """
    Clean version folder to keep ONLY:
    - 1 main .tex file (renamed to paper.tex)
    - 1 .bib file (renamed to references.bib)
    Remove ALL other files and subfolders
    
    Args:
        version_dir: Version directory path
    
    Returns:
        Dictionary with statistics
    """
    stats = {
        'kept_tex': 0,
        'kept_bib': 0,
        'removed': 0
    }
    
    # Find main .tex and .bib files
    main_tex = find_main_tex_file(version_dir)
    main_bib = find_bib_file(version_dir)
    
    # Create temp copies
    tex_content = None
    bib_content = None
    
    if main_tex and os.path.exists(main_tex):
        with open(main_tex, 'r', encoding='utf-8', errors='ignore') as f:
            tex_content = f.read()
        stats['kept_tex'] = 1
    
    if main_bib and os.path.exists(main_bib):
        with open(main_bib, 'r', encoding='utf-8', errors='ignore') as f:
            bib_content = f.read()
        stats['kept_bib'] = 1
    
    # Remove ALL files and subdirectories
    for item in os.listdir(version_dir):
        item_path = os.path.join(version_dir, item)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                stats['removed'] += 1
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                stats['removed'] += 1
        except Exception as e:
            logger.warning(f"Failed to remove {item_path}: {e}")
    
    # Write back ONLY the 2 required files
    if tex_content:
        paper_tex_path = os.path.join(version_dir, 'paper.tex')
        with open(paper_tex_path, 'w', encoding='utf-8') as f:
            f.write(tex_content)
        logger.debug(f"Created paper.tex in {version_dir}")
    
    if bib_content:
        ref_bib_path = os.path.join(version_dir, 'references.bib')
        with open(ref_bib_path, 'w', encoding='utf-8') as f:
            f.write(bib_content)
        logger.debug(f"Created references.bib in {version_dir}")
    
    return stats


def process_tex_files(tex_dir: str) -> Dict[str, int]:
    """
    Process all .tex files in directory to remove figures
    
    Args:
        tex_dir: Directory containing .tex files
    
    Returns:
        Dictionary with processing statistics
    """
    stats = {
        'processed': 0,
        'failed': 0,
        'images_removed': 0
    }
    
    # Remove image files first
    stats['images_removed'] = remove_image_files(tex_dir)
    
    # Process .tex files
    for root, dirs, files in os.walk(tex_dir):
        for file in files:
            if file.endswith('.tex'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Remove figures
                    cleaned_content = remove_figures_from_tex(content)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    
                    stats['processed'] += 1
                    logger.debug(f"Processed TeX file: {file_path}")
                except Exception as e:
                    stats['failed'] += 1
                    logger.warning(f"Failed to process {file_path}: {e}")
    
    return stats


def get_directory_size(directory: str) -> int:
    """
    Calculate total size of directory in bytes
    
    Args:
        directory: Directory path
    
    Returns:
        Total size in bytes
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def clean_temp_files(temp_dir: str):
    """
    Remove temporary files and directories
    
    Args:
        temp_dir: Temporary directory to clean
    """
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean {temp_dir}: {e}")


def ensure_dir(directory: str):
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Directory path
    """
    os.makedirs(directory, exist_ok=True)

