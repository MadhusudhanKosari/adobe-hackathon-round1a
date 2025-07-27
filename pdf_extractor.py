import pdfplumber
from pypdf import PdfReader
from statistics import median
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    """Enhanced PDF outline extractor with robust error handling."""
    
    def __init__(self):
        self.outline_data = {"title": "", "outline": []}

    def extract_outline(self, pdf_path: str) -> Dict:
        """Extract document outline with comprehensive error handling."""
        logger.debug(f"Starting extraction for: {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if not pdf.pages:
                    logger.warning(f"PDF has no pages: {pdf_path}")
                    return {"title": "Empty Document", "outline": []}
                
                # Extract title
                self.outline_data["title"] = self._extract_title(pdf_path, pdf)
                
                # Extract headings
                headings = self._extract_headings(pdf)
                self.outline_data["outline"] = headings
                
                logger.debug(f"Extracted {len(headings)} headings from {pdf_path}")
                return self.outline_data.copy()
                
        except Exception as e:
            logger.error(f"Failed to process PDF {pdf_path}: {e}")
            raise

    def _extract_title(self, pdf_path: str, pdf) -> str:
        """Extract title with multiple fallback methods."""
        # Try metadata first
        try:
            reader = PdfReader(pdf_path)
            if (reader.metadata and 
                hasattr(reader.metadata, 'title') and 
                reader.metadata.title and 
                reader.metadata.title.strip()):
                title = reader.metadata.title.strip()
                logger.debug(f"Title from metadata: {title}")
                return title
        except Exception as e:
            logger.debug(f"Metadata extraction failed: {e}")
        
        # Fallback to first page analysis
        try:
            title = self._guess_title_from_content(pdf)
            logger.debug(f"Title from content: {title}")
            return title
        except Exception as e:
            logger.debug(f"Content title extraction failed: {e}")
            return "Document"

    def _guess_title_from_content(self, pdf) -> str:
        """Guess title from first page content."""
        try:
            first_page = pdf.pages[0]
            words = first_page.extract_words(extra_attrs=["size"])
            
            if not words:
                return "Document"
            
            # Find largest font size
            max_size = max(w["size"] for w in words)
            candidates = [w for w in words if w["size"] >= max_size * 0.95]
            
            if candidates:
                candidates.sort(key=lambda x: (-x["size"], -len(x["text"])))
                title = self._clean_text(candidates[0]["text"])
                return title[:100]  # Limit title length
            
        except Exception as e:
            logger.debug(f"Title guessing failed: {e}")
        
        return "Document"

    def _extract_headings(self, pdf) -> List[Dict]:
        """Extract headings using statistical font analysis."""
        try:
            # Collect font sizes for statistical analysis
            all_sizes = []
            for page_num, page in enumerate(pdf.pages):
                try:
                    for char in page.chars:
                        if isinstance(char.get("size"), (int, float)):
                            all_sizes.append(round(char["size"], 1))
                except Exception as e:
                    logger.debug(f"Error processing page {page_num + 1}: {e}")
                    continue
            
            if not all_sizes:
                logger.warning("No font size data found")
                return []
            
            median_size = median(all_sizes)
            logger.debug(f"Median font size: {median_size}")
            
            # Extract headings
            headings = []
            for page_no, page in enumerate(pdf.pages, 1):
                try:
                    page_headings = self._extract_page_headings(page, page_no, median_size)
                    headings.extend(page_headings)
                except Exception as e:
                    logger.debug(f"Error processing headings on page {page_no}: {e}")
                    continue
            
            # Remove duplicates and limit results
            unique_headings = self._deduplicate_headings(headings)
            return unique_headings[:50]  # Limit to 50 headings
            
        except Exception as e:
            logger.error(f"Heading extraction failed: {e}")
            return []

    def _extract_page_headings(self, page, page_no: int, median_size: float) -> List[Dict]:
        """Extract headings from a single page."""
        headings = []
        
        try:
            words = page.extract_words(
                extra_attrs=["size", "fontname"], 
                keep_blank_chars=False
            )
            
            for word in words:
                try:
                    text = self._clean_text(word.get("text", ""))
                    if len(text) < 3 or text.isdigit() or not text.strip():
                        continue

                    size = round(word.get("size", 0), 1)
                    font = word.get("fontname", "").lower()
                    is_bold = "bold" in font

                    # Classify heading level
                    level = self._classify_heading_level(size, median_size, is_bold, text)
                    
                    if level:
                        headings.append({
                            "level": level,
                            "text": text,
                            "page": page_no,
                            "font_size": size,
                            "is_bold": is_bold
                        })
                        
                except Exception as e:
                    logger.debug(f"Error processing word: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"Error extracting words from page {page_no}: {e}")
        
        return headings

    def _classify_heading_level(self, size: float, median_size: float, is_bold: bool, text: str) -> str:
        """Classify heading level based on size and formatting."""
        try:
            if size >= median_size * 1.6:
                return "H1"
            elif size >= median_size * 1.3:
                return "H2"
            elif size >= median_size * 1.1 or is_bold:
                return "H3"
            elif self._is_heading_pattern(text):
                return "H3"
            return None
        except Exception:
            return None

    def _is_heading_pattern(self, text: str) -> bool:
        """Detect common heading patterns."""
        try:
            patterns = [
                r'^(chapter|section|part)\s+\d+',
                r'^(introduction|conclusion|summary|abstract)',
                r'^\d+\.\s+\w+',
                r'^[A-Z][A-Z\s]{3,}$'  # ALL CAPS (minimum 4 chars)
            ]
            
            text_lower = text.lower()
            for pattern in patterns:
                if re.match(pattern, text_lower):
                    return True
            return False
        except Exception:
            return False

    def _deduplicate_headings(self, headings: List[Dict]) -> List[Dict]:
        """Remove duplicate headings."""
        try:
            unique_headings = []
            seen = set()
            
            for heading in headings:
                key = f"{heading['text']}_{heading['page']}"
                if key not in seen and len(heading['text'].strip()) > 0:
                    seen.add(key)
                    unique_headings.append(heading)
            
            return unique_headings
        except Exception as e:
            logger.debug(f"Deduplication failed: {e}")
            return headings

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        try:
            if not text:
                return ""
            # Remove excessive whitespace and clean up
            cleaned = re.sub(r'\s+', ' ', str(text)).strip()
            # Remove control characters
            cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
            return cleaned
        except Exception:
            return str(text) if text else ""
