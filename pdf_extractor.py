"""
PDF extraction pipeline for multimodal MCQ generation.

Extracts:
- Text content per page
- Images (diagrams, formulas) with bounding boxes
- Image captions and nearby text

Uses PyMuPDF (fitz) for robust extraction.
"""

import re
from typing import List, Optional, Tuple
from pathlib import Path
import io

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️  PyMuPDF not installed. Install with: pip install PyMuPDF")

from multimodal_models import ExtractedImage, PDFPage, PDFDocument, TextImagePair


class PDFExtractor:
    """
    Extract text and images from PDF documents.

    Uses PyMuPDF for high-quality extraction of:
    - Text blocks with positioning
    - Images with metadata
    - Captions and nearby text
    """

    def __init__(
        self,
        min_image_size: int = 10000,  # Minimum image size in bytes
        min_image_dimension: int = 100,  # Minimum width/height in pixels
        extract_vector_graphics: bool = True
    ):
        """
        Initialize PDF extractor.

        Args:
            min_image_size: Skip images smaller than this (bytes)
            min_image_dimension: Skip images smaller than this (pixels)
            extract_vector_graphics: Whether to extract vector graphics as images
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF is required. Install with: pip install PyMuPDF")

        self.min_image_size = min_image_size
        self.min_image_dimension = min_image_dimension
        self.extract_vector_graphics = extract_vector_graphics

    def extract_pdf(self, pdf_path: str, pages: Optional[List[int]] = None) -> PDFDocument:
        """
        Extract complete PDF document.

        Args:
            pdf_path: Path to PDF file
            pages: Specific pages to extract (1-indexed), or None for all

        Returns:
            PDFDocument with all extracted content
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        print(f"\n📄 Extracting PDF: {pdf_path.name}")

        doc = fitz.open(str(pdf_path))
        pdf_doc = PDFDocument(filepath=str(pdf_path))

        # Extract metadata
        metadata = doc.metadata
        pdf_doc.title = metadata.get('title', '')
        pdf_doc.subject = metadata.get('subject', '')

        # Determine which pages to process
        if pages:
            page_numbers = [p - 1 for p in pages]  # Convert to 0-indexed
        else:
            page_numbers = range(len(doc))

        print(f"📊 Total pages: {len(doc)}, Processing: {len(page_numbers)}")

        for page_idx in page_numbers:
            page_num = page_idx + 1  # 1-indexed for display
            print(f"\n  Processing page {page_num}...")

            page = doc[page_idx]
            pdf_page = self._extract_page(page, page_num)
            pdf_doc.pages.append(pdf_page)

        doc.close()

        print(f"\n✅ Extracted {pdf_doc.total_pages} pages, {pdf_doc.total_images} images")
        return pdf_doc

    def _extract_page(self, page: fitz.Page, page_number: int) -> PDFPage:
        """Extract content from a single page."""
        pdf_page = PDFPage(page_number=page_number)

        # Extract text
        pdf_page.text = page.get_text()
        print(f"    Text: {len(pdf_page.text)} chars")

        # Check for formulas (heuristic: look for math symbols)
        pdf_page.has_formulas = self._has_formulas(pdf_page.text)

        # Extract images
        images = self._extract_images(page, page_number)
        pdf_page.images = images
        pdf_page.has_diagrams = len(images) > 0

        # Try to find captions for each image
        for img in images:
            img.caption = self._find_caption(page, img)
            img.nearby_text = self._find_nearby_text(page, img)

        print(f"    Images: {len(images)}")
        for img in images:
            if img.caption:
                print(f"      - {img} (caption: {img.caption[:30]}...)")
            else:
                print(f"      - {img}")

        return pdf_page

    def _extract_images(self, page: fitz.Page, page_number: int) -> List[ExtractedImage]:
        """Extract all images from a page."""
        images = []
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]  # Image reference number

            # Extract image
            try:
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Get image dimensions
                width = base_image.get("width", 0)
                height = base_image.get("height", 0)

                # Filter small images
                if len(image_bytes) < self.min_image_size:
                    continue
                if width < self.min_image_dimension or height < self.min_image_dimension:
                    continue

                # Get bounding box
                bbox = self._get_image_bbox(page, xref)

                extracted_img = ExtractedImage(
                    image_data=image_bytes,
                    page_number=page_number,
                    image_index=img_index,
                    bbox=bbox,
                    format=image_ext
                )

                images.append(extracted_img)

            except Exception as e:
                print(f"      ⚠️  Failed to extract image {img_index}: {e}")
                continue

        return images

    def _get_image_bbox(self, page: fitz.Page, xref: int) -> Optional[Tuple[float, float, float, float]]:
        """Get bounding box for an image."""
        try:
            for img in page.get_images():
                if img[0] == xref:
                    # Get image position from page
                    rects = page.get_image_rects(xref)
                    if rects:
                        rect = rects[0]
                        return (rect.x0, rect.y0, rect.x1, rect.y1)
        except:
            pass
        return None

    def _find_caption(self, page: fitz.Page, image: ExtractedImage) -> Optional[str]:
        """
        Find caption for an image using heuristics.

        Looks for:
        - "Figure N:", "Fig. N:", "Diagram N:" near the image
        - Text immediately below the image
        """
        if not image.bbox:
            return None

        x0, y0, x1, y1 = image.bbox
        page_height = page.rect.height

        # Search area: slightly below the image
        search_rect = fitz.Rect(x0, y1, x1, min(y1 + 100, page_height))

        # Extract text in search area
        nearby_text = page.get_text("text", clip=search_rect).strip()

        # Look for caption patterns
        caption_patterns = [
            r'(Fig(?:ure)?\.?\s*\d+[:.]\s*.+?)(?:\n|$)',
            r'(Diagram\s*\d+[:.]\s*.+?)(?:\n|$)',
            r'(Table\s*\d+[:.]\s*.+?)(?:\n|$)',
            r'(Graph\s*\d+[:.]\s*.+?)(?:\n|$)',
        ]

        for pattern in caption_patterns:
            match = re.search(pattern, nearby_text, re.IGNORECASE)
            if match:
                caption = match.group(1).strip()
                # Limit caption length
                if len(caption) > 200:
                    caption = caption[:200] + "..."
                return caption

        # Fallback: return first line if it's reasonably short
        lines = nearby_text.split('\n')
        if lines and 10 < len(lines[0]) < 150:
            return lines[0]

        return None

    def _find_nearby_text(self, page: fitz.Page, image: ExtractedImage, context_lines: int = 3) -> Optional[str]:
        """
        Find text near the image for context.

        Extracts a few lines above and below the image.
        """
        if not image.bbox:
            return None

        x0, y0, x1, y1 = image.bbox
        page_height = page.rect.height

        # Search area: above and below image
        margin = 150  # pixels
        search_rect = fitz.Rect(
            0,  # Full width
            max(0, y0 - margin),
            page.rect.width,
            min(page_height, y1 + margin)
        )

        # Extract text
        text = page.get_text("text", clip=search_rect).strip()

        # Clean and limit
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) > context_lines * 2:
            # Take first N and last N lines
            lines = lines[:context_lines] + ['...'] + lines[-context_lines:]

        nearby_text = '\n'.join(lines)

        # Limit total length
        if len(nearby_text) > 1000:
            nearby_text = nearby_text[:1000] + "..."

        return nearby_text if nearby_text else None

    def _has_formulas(self, text: str) -> bool:
        """
        Heuristic check for mathematical formulas.

        Looks for common math symbols and patterns.
        """
        math_indicators = [
            r'[∫∑∏√∂∇]',  # Integral, sum, product, sqrt, partial, nabla
            r'[αβγδεζηθλμπρσφψω]',  # Greek letters
            r'[≤≥≠≈∞]',  # Math relations
            r'\b(?:sin|cos|tan|log|ln|exp)\b',  # Functions
            r'[a-z]_\{[a-z0-9]+\}',  # Subscripts (LaTeX-style)
            r'\^[0-9]',  # Superscripts
            r'\\frac|\\int|\\sum',  # LaTeX commands
        ]

        for pattern in math_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False


class TextImagePairer:
    """
    Pair extracted images with relevant text to create multimodal units.

    Strategies:
    - Same-page pairing: image + caption + nearby text
    - Topic-based pairing: group images by section/topic
    """

    def __init__(self, min_text_length: int = 50):
        """
        Initialize pairer.

        Args:
            min_text_length: Minimum text length for a valid pair
        """
        self.min_text_length = min_text_length

    def create_pairs(self, pdf_doc: PDFDocument) -> List[TextImagePair]:
        """
        Create text-image pairs from extracted PDF.

        Args:
            pdf_doc: Extracted PDF document

        Returns:
            List of text-image pairs
        """
        pairs = []

        print(f"\n🔗 Creating text-image pairs...")

        for page in pdf_doc.pages:
            if not page.images:
                continue

            # Strategy 1: One pair per image (with caption + nearby text)
            for img in page.images:
                pair = self._create_single_image_pair(img, page, pdf_doc.filepath)
                if pair:
                    pairs.append(pair)

        print(f"✅ Created {len(pairs)} text-image pair(s)")

        return pairs

    def _create_single_image_pair(
        self,
        image: ExtractedImage,
        page: PDFPage,
        source_pdf: str
    ) -> Optional[TextImagePair]:
        """Create a pair for a single image."""
        # Combine caption and nearby text
        text_parts = []

        if image.caption:
            text_parts.append(f"Caption: {image.caption}")

        if image.nearby_text:
            text_parts.append(f"Context: {image.nearby_text}")

        # Fallback: use full page text if nothing better
        if not text_parts:
            text_parts.append(page.text[:500])  # First 500 chars

        combined_text = "\n\n".join(text_parts)

        # Filter pairs with too little text
        if len(combined_text) < self.min_text_length:
            return None

        return TextImagePair(
            text=combined_text,
            images=[image],
            page_number=page.page_number,
            source_pdf=Path(source_pdf).name
        )


# Convenience functions

def extract_pdf(pdf_path: str, pages: Optional[List[int]] = None) -> PDFDocument:
    """
    Extract PDF with default settings.

    Args:
        pdf_path: Path to PDF file
        pages: Specific pages to extract (1-indexed), or None for all

    Returns:
        PDFDocument with extracted content
    """
    extractor = PDFExtractor()
    return extractor.extract_pdf(pdf_path, pages)


def create_text_image_pairs(pdf_doc: PDFDocument) -> List[TextImagePair]:
    """
    Create text-image pairs from extracted PDF.

    Args:
        pdf_doc: Extracted PDF document

    Returns:
        List of text-image pairs ready for multimodal generation
    """
    pairer = TextImagePairer()
    return pairer.create_pairs(pdf_doc)
