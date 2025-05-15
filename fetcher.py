import requests
from bs4 import BeautifulSoup
import re
import html2text
import trafilatura
from newspaper import Article
import os
import paramiko
from urllib.parse import urlparse
import tempfile
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'  # Define explicit date format
)
logger = logging.getLogger("fetcher")

def fetch_page(url):
    """Fetch content from a web page, local file, or FTP server.
    
    Args:
        url (str): URL, file path, or FTP URL to fetch
        
    Returns:
        str: HTML content or None if failed
    """
    # Parse the URL to determine the protocol
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme.lower() if parsed_url.scheme else ""
    
    # Handle URLs in the specified order: no scheme, http, https, ftp, ftps, file
    
    # 1. No scheme - try to determine if it's a local file or assume http
    if not scheme:
        logger.info(f"No scheme specified for {url}, attempting to determine source type")
        if os.path.exists(url):
            logger.info(f"URL {url} exists as a local file, treating as file")
            return fetch_local_file(url)
        else:
            # Try to prepend http:// and fetch
            logger.info(f"URL {url} doesn't exist locally, treating as http URL")
            return fetch_http(f"http://{url}")
    
    # 2. HTTP
    if scheme == "http":
        return fetch_http(url)
    
    # 3. HTTPS
    if scheme == "https":
        return fetch_http(url)
    
    # 4. FTP
    if scheme == "ftp":
        return fetch_sftp(parsed_url)
    
    # 5. FTPS (Secure FTP)
    if scheme == "ftps":
        return fetch_sftp(parsed_url)
    
    # 6. File
    if scheme == "file":
        return fetch_local_file(parsed_url.path)
    
    # Handle unknown schemes
    logger.warning(f"Unsupported URL scheme: {scheme} for {url}")
    return None

def fetch_local_file(path):
    """Fetch content from a local file.
    
    Args:
        path (str): Path to local file
        
    Returns:
        str: File content or None if failed
    """
    try:
        # Handle 'file://' prefix if present
        if path.startswith("file://"):
            path = path[7:]
        
        # Check if file exists
        if not os.path.isfile(path):
            logger.error(f"Local file not found: {path}")
            return None
        
        # Read file content
        with open(path, 'rb') as f:
            content = f.read()
        logger.info(f"Successfully fetched local file: {path}")
        return content
    except Exception as e:
        logger.error(f"Error fetching local file {path}: {str(e)}")
        return None

def fetch_sftp(parsed_url):
    """Fetch content from an SFTP server.
    
    Args:
        parsed_url (ParseResult): Parsed URL from urlparse
        
    Returns:
        str: File content or None if failed
    """
    try:
        # Extract SFTP connection info
        hostname = parsed_url.netloc
        port = 22  # Default SFTP port
        
        # Handle username/password if provided
        username = parsed_url.username if parsed_url.username else "anonymous"
        password = parsed_url.password if parsed_url.password else ""
        
        # Create SFTP connection
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Get the remote file path
        remote_path = parsed_url.path
        
        # Create a temporary file to store the content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            
            # Download the file
            sftp.get(remote_path, temp_path)
            
        # Close SFTP connection
        sftp.close()
        transport.close()
        
        # Read content from temporary file
        # Download the file
        try:
            with open(temp_path, 'wb') as f:
                ftp.retrbinary(f'RETR {filename}', f.write)
            logger.info(f"Downloaded file: {filename}")
        except Exception as e:
            logger.error(f"Error downloading file {filename}: {str(e)}")
            ftp.quit()
            os.unlink(temp_path)
            return None
        
        ftp.quit()
        
        # Read the downloaded file
        with open(temp_path, 'rb') as f:
            content = f.read()
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        protocol = "FTPS" if secure else "FTP"
        logger.info(f"Successfully fetched {protocol} file: {parsed_url.geturl()}")
        return content
    except Exception as e:
        protocol = "FTPS" if secure else "FTP"
        logger.error(f"Error fetching {protocol} file {parsed_url.geturl()}: {str(e)}")
        return None

def fetch_http(url):
    """Fetch content from an HTTP/HTTPS URL.
    
    Args:
        url (str): URL to fetch
        
    Returns:
        str: HTML content or None if failed
    """
    try:
        headers = {
            "User-Agent": "FedLoad Monitor/1.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully fetched HTTP URL: {url}")
        return response.content
    except Exception as e:
        logger.error(f"Error fetching HTTP URL {url}: {str(e)}")
        return None

def extract_text(html, method="trafilatura"):
    """Extract main text content from HTML.
    
    Args:
        html (str): HTML content
        method (str): Method to use for extraction ('trafilatura', 'newspaper', 'bs4', or 'html2text')
        
    Returns:
        str: Extracted text content
    """
    if html is None:
        return ""
    
    # Method 1: Trafilatura (best for articles, blog posts)
    if method == "trafilatura":
        text = trafilatura.extract(html, include_comments=False, include_tables=True, 
                                   include_links=False, include_images=False)
        if text:
            return text
        # Fall back to other methods if trafilatura fails
    
    # Method 2: Newspaper3k (specialized for news articles)
    if method == "newspaper" or method == "trafilatura":
        try:
            article = Article(url="")
            article.set_html(html)
            article.parse()
            return article.text
        except Exception:
            # Fall back to other methods
            pass
    
    # Method 3: html2text (works well for most pages)
    if method == "html2text" or method in ["trafilatura", "newspaper"]:
        try:
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            h.ignore_tables = False
            h.skip_internal_links = True
            h.single_line_break = True
            h.ignore_emphasis = True
            return h.handle(html.decode('utf-8') if isinstance(html, bytes) else html)
        except Exception:
            # Fall back to BeautifulSoup
            pass
    
    # Method 4: BeautifulSoup (fallback method)
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove scripts, styles, and navigation elements
    for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
        element.extract()
    
    # Get text and normalize whitespace
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def extract_main_content(url, method="trafilatura"):
    """Fetch a page and extract its main content.
    
    Args:
        url (str): URL, file path, or FTP URL to fetch
        method (str): Method to use for extraction
        
    Returns:
        dict: Dictionary with 'title', 'text', and 'meta' data
    """
    html = fetch_page(url)
    if not html:
        return {"title": "", "text": "", "meta": {}}
    
    # Handle non-HTML files
    content_type = detect_content_type(html, url)
    if content_type != "html":
        return process_non_html_file(html, content_type, url)
    
    # Extract with newspaper for structured data
    try:
        article = Article(url)
        article.set_html(html)
        article.parse()
        
        # Get main text through specified method
        text = extract_text(html, method)
        
        return {
            "title": article.title,
            "text": text,
            "meta": {
                "authors": article.authors,
                "publish_date": article.publish_date,
                "keywords": article.keywords,
                "summary": article.summary if hasattr(article, 'summary') else ""
            }
        }
    except Exception as e:
        logger.error(f"Error extracting content: {str(e)}")
        # Fall back to basic extraction
        text = extract_text(html, "bs4")
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else ""
        
        return {
            "title": title,
            "text": text,
            "meta": {}
        }

def detect_content_type(content, url):
    """Detect if content is HTML or another file type.
    
    Args:
        content (bytes): File content
        url (str): URL or path to the file
        
    Returns:
        str: Content type ('html', 'pdf', 'doc', 'text', or 'unknown')
    """
    # Check based on URL extension
    if url:
        lower_url = url.lower()
        if lower_url.endswith('.pdf'):
            return "pdf"
        elif lower_url.endswith(('.doc', '.docx')):
            return "doc"
        elif lower_url.endswith(('.txt', '.csv', '.json')):
            return "text"
        elif lower_url.endswith(('.htm', '.html')):
            return "html"
    
    # Try to detect by content
    try:
        if content[:4] == b'%PDF':
            return "pdf"
        elif content[:2] in (b'\xD0\xCF', b'\x50\x4B'):  # DOC or DOCX/XLSX (zip) signatures
            return "doc"
        
        # Try to detect if it's HTML content
        text_start = content[:100].decode('utf-8', errors='ignore')
        if re.search(r'<!DOCTYPE\s+html|<html', text_start, re.IGNORECASE):
            return "html"
        
        # If primarily ASCII, probably text
        if all(c < 128 for c in content[:100] if c not in (9, 10, 13)):  # Ignore tab, LF, CR
            return "text"
        
    except Exception:
        pass
    
    # Default to HTML for web URLs
    if url and url.startswith(('http://', 'https://')):
        return "html"
    
    return "unknown"

def process_non_html_file(content, content_type, url):
    """Process non-HTML file content.
    
    Args:
        content (bytes): File content
        content_type (str): Content type from detect_content_type
        url (str): Original URL or path
        
    Returns:
        dict: Dictionary with extracted content
    """
    title = os.path.basename(url) if url else "Unknown File"
    
    if content_type == "text":
        # Simple text file handling
        try:
            text = content.decode('utf-8', errors='replace')
            return {
                "title": title,
                "text": text,
                "meta": {
                    "file_type": "text"
                }
            }
        except Exception as e:
            logger.error(f"Error processing text file: {str(e)}")
    
    elif content_type == "pdf":
        # Basic handling for PDF files
        try:
            import io
            from pdfminer.high_level import extract_text as pdf_extract_text
            
            text = pdf_extract_text(io.BytesIO(content))
            return {
                "title": title,
                "text": text,
                "meta": {
                    "file_type": "pdf"
                }
            }
        except ImportError:
            logger.warning("PDF extraction requires pdfminer.six package")
        except Exception as e:
            logger.error(f"Error processing PDF file: {str(e)}")
    
    # Return minimal information for unsupported types
    return {
        "title": title,
        "text": f"[Content of type {content_type} - extraction not supported]",
        "meta": {
            "file_type": content_type,
            "size": len(content)
        }
    }
