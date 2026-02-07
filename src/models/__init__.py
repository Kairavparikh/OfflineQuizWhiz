"""Data models for MCQ system."""

from .models import (
    Question,
    Subject,
    Section,
    Topic,
    SubTopic,
    DifficultyLevel,
    PaperConfig
)
from .multimodal_models import (
    ExtractedImage,
    PDFPage,
    TextImagePair,
    PDFDocument,
    MultimodalQuestionMetadata
)

__all__ = [
    "Question",
    "Subject",
    "Section",
    "Topic",
    "SubTopic",
    "DifficultyLevel",
    "PaperConfig",
    "ExtractedImage",
    "PDFPage",
    "TextImagePair",
    "PDFDocument",
    "MultimodalQuestionMetadata"
]
