"""
Data models for multimodal content (PDFs with diagrams).

Structures for:
- Extracted images from PDFs
- Text-image pairs
- Multimodal question metadata
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from pathlib import Path
import base64


@dataclass
class ExtractedImage:
    """
    An image extracted from a PDF.

    Attributes:
        image_data: Raw image bytes
        page_number: Page number (1-indexed)
        image_index: Index of image on page (0-indexed)
        bbox: Bounding box (x0, y0, x1, y1) in PDF coordinates
        format: Image format (png, jpeg, etc.)
        caption: Extracted caption text (if found)
        nearby_text: Text near the image (paragraph above/below)
    """
    image_data: bytes
    page_number: int
    image_index: int = 0
    bbox: Optional[Tuple[float, float, float, float]] = None
    format: str = "png"
    caption: Optional[str] = None
    nearby_text: Optional[str] = None

    def to_base64(self) -> str:
        """Convert image data to base64 string for API calls."""
        return base64.b64encode(self.image_data).decode('utf-8')

    def save(self, output_path: str) -> None:
        """Save image to file."""
        Path(output_path).write_bytes(self.image_data)

    @property
    def size(self) -> int:
        """Image size in bytes."""
        return len(self.image_data)

    def __str__(self) -> str:
        caption_str = f" - {self.caption[:50]}..." if self.caption else ""
        return f"Image(page={self.page_number}, idx={self.image_index}, {self.size} bytes{caption_str})"


@dataclass
class PDFPage:
    """
    Content extracted from a single PDF page.

    Attributes:
        page_number: Page number (1-indexed)
        text: Full text content of the page
        images: List of images on this page
        has_formulas: Whether page contains mathematical formulas
        has_diagrams: Whether page contains diagrams/figures
    """
    page_number: int
    text: str = ""
    images: List[ExtractedImage] = field(default_factory=list)
    has_formulas: bool = False
    has_diagrams: bool = False

    def __str__(self) -> str:
        return f"Page {self.page_number}: {len(self.text)} chars, {len(self.images)} image(s)"


@dataclass
class TextImagePair:
    """
    A pairing of text context with one or more images.

    This represents a logical unit (e.g., a diagram with its explanation)
    that can be used to generate multimodal questions.

    Attributes:
        text: Contextual text (caption + nearby paragraphs)
        images: One or more related images
        page_number: Source page number
        topic_hint: Extracted topic/section hint (if available)
        source_pdf: Source PDF filename
    """
    text: str
    images: List[ExtractedImage]
    page_number: int
    topic_hint: Optional[str] = None
    source_pdf: Optional[str] = None

    @property
    def has_multiple_images(self) -> bool:
        """Check if pair contains multiple images."""
        return len(self.images) > 1

    @property
    def total_image_size(self) -> int:
        """Total size of all images in bytes."""
        return sum(img.size for img in self.images)

    def get_image_base64_list(self) -> List[str]:
        """Get all images as base64 strings."""
        return [img.to_base64() for img in self.images]

    def __str__(self) -> str:
        return f"TextImagePair(page={self.page_number}, text={len(self.text)} chars, images={len(self.images)})"


@dataclass
class PDFDocument:
    """
    Complete PDF document with extracted content.

    Attributes:
        filepath: Path to source PDF
        pages: List of extracted pages
        title: Document title (if available)
        subject: Subject/topic of document
    """
    filepath: str
    pages: List[PDFPage] = field(default_factory=list)
    title: Optional[str] = None
    subject: Optional[str] = None

    @property
    def total_pages(self) -> int:
        """Total number of pages."""
        return len(self.pages)

    @property
    def total_images(self) -> int:
        """Total number of images across all pages."""
        return sum(len(page.images) for page in self.pages)

    def get_pages_with_images(self) -> List[PDFPage]:
        """Get only pages that contain images."""
        return [page for page in self.pages if page.images]

    def get_all_images(self) -> List[ExtractedImage]:
        """Get all images from all pages."""
        all_images = []
        for page in self.pages:
            all_images.extend(page.images)
        return all_images

    def __str__(self) -> str:
        return f"PDFDocument({self.filepath}, {self.total_pages} pages, {self.total_images} images)"


# Extend the Question model to track multimodal source
@dataclass
class MultimodalQuestionMetadata:
    """
    Additional metadata for questions generated from diagrams.

    Can be stored alongside the Question object.
    """
    source_pdf: str
    source_page: int
    num_images_used: int
    image_captions: List[str] = field(default_factory=list)
    requires_diagram: bool = True  # Question requires seeing the diagram
    diagram_type: Optional[str] = None  # e.g., "graph", "circuit", "phase_diagram"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "source_pdf": self.source_pdf,
            "source_page": self.source_page,
            "num_images_used": self.num_images_used,
            "image_captions": self.image_captions,
            "requires_diagram": self.requires_diagram,
            "diagram_type": self.diagram_type
        }
