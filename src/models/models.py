"""
Data models for MCQ generation system.

Defines the core data structures for:
- Syllabus hierarchy (Subject → Section → Topic → SubTopic)
- Questions with metadata and content
- Difficulty levels
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime
import uuid


class DifficultyLevel(Enum):
    """Question difficulty levels with their semantic meaning."""
    EASY = "Easy"  # Direct recall, definitions, simple formulas
    MEDIUM = "Medium"  # Application of concepts, 1-2 step problems
    HARD = "Hard"  # Multi-step reasoning, combined concepts


@dataclass
class SubTopic:
    """A specific sub-topic within a topic (e.g., 'Matrices and Determinants')."""
    name: str
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return self.name


@dataclass
class Topic:
    """A topic within a section (e.g., 'Linear Algebra')."""
    name: str
    subtopics: List[SubTopic] = field(default_factory=list)
    description: Optional[str] = None

    def __str__(self) -> str:
        return self.name

    def add_subtopic(self, subtopic: SubTopic) -> None:
        """Add a subtopic to this topic."""
        self.subtopics.append(subtopic)


@dataclass
class Section:
    """A section within a subject (e.g., 'Engineering Mathematics', 'Physics')."""
    name: str
    topics: List[Topic] = field(default_factory=list)
    description: Optional[str] = None

    def __str__(self) -> str:
        return self.name

    def add_topic(self, topic: Topic) -> None:
        """Add a topic to this section."""
        self.topics.append(topic)


@dataclass
class Subject:
    """A complete subject/exam area (e.g., 'Metallurgical Engineering')."""
    name: str
    sections: List[Section] = field(default_factory=list)
    code: Optional[str] = None  # e.g., "SME", "ME101"
    description: Optional[str] = None

    def __str__(self) -> str:
        return self.name

    def add_section(self, section: Section) -> None:
        """Add a section to this subject."""
        self.sections.append(section)


@dataclass
class Question:
    """
    A complete MCQ with metadata and content.

    Matches the client's required format:
    - Metadata: test_section, main_topic, subtopic, difficulty
    - Content: question, options, correct_answer, explanation, references
    """
    # Metadata
    question_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_section: str = ""  # Subject/Section name
    main_topic: str = ""  # Topic name
    subtopic: str = ""  # SubTopic name
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM

    # Content
    question_text_en: str = ""  # Question in English
    option_a_en: str = ""
    option_b_en: str = ""
    option_c_en: str = ""
    option_d_en: str = ""
    correct_answer: str = ""  # Must be "A", "B", "C", or "D"
    explanation: str = ""  # Solution/explanation
    references: List[str] = field(default_factory=list)  # URLs or book citations

    # Optional metadata
    created_at: datetime = field(default_factory=datetime.now)
    source_pdf: Optional[str] = None  # If generated from a specific PDF
    has_diagram: bool = False  # Whether question references a diagram
    image_reference: Optional[str] = None  # Image filename or ID (e.g., "diagram_page2_img1.jpg")
    image_description: Optional[str] = None  # Description of the image for test creators
    tags: List[str] = field(default_factory=list)  # For filtering/search

    def validate(self) -> List[str]:
        """
        Validate question fields and return list of errors.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Check required fields
        if not self.question_text_en.strip():
            errors.append("Question text is empty")

        if not self.option_a_en.strip():
            errors.append("Option A is empty")
        if not self.option_b_en.strip():
            errors.append("Option B is empty")
        if not self.option_c_en.strip():
            errors.append("Option C is empty")
        if not self.option_d_en.strip():
            errors.append("Option D is empty")

        # Check correct answer
        if self.correct_answer not in ["A", "B", "C", "D"]:
            errors.append(f"Correct answer must be A, B, C, or D (got '{self.correct_answer}')")

        # Check explanation
        if not self.explanation.strip():
            errors.append("Explanation is empty")
        elif len(self.explanation.strip()) < 20:
            errors.append("Explanation is too short (< 20 characters)")

        # Check for duplicate options
        options = [
            self.option_a_en.strip().lower(),
            self.option_b_en.strip().lower(),
            self.option_c_en.strip().lower(),
            self.option_d_en.strip().lower()
        ]
        if len(options) != len(set(options)):
            errors.append("Options contain duplicates")

        # Check metadata
        if not self.test_section.strip():
            errors.append("Test section is empty")
        if not self.main_topic.strip():
            errors.append("Main topic is empty")

        return errors

    def is_valid(self) -> bool:
        """Check if question is valid."""
        return len(self.validate()) == 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "question_id": self.question_id,
            "test_section": self.test_section,
            "main_topic": self.main_topic,
            "subtopic": self.subtopic,
            "difficulty": self.difficulty.value,
            "question_text_en": self.question_text_en,
            "option_a_en": self.option_a_en,
            "option_b_en": self.option_b_en,
            "option_c_en": self.option_c_en,
            "option_d_en": self.option_d_en,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "references": self.references,
            "created_at": self.created_at.isoformat(),
            "source_pdf": self.source_pdf,
            "has_diagram": self.has_diagram,
            "tags": self.tags
        }

    def get_options_dict(self) -> dict:
        """Get options as a dictionary for easier iteration."""
        return {
            "A": self.option_a_en,
            "B": self.option_b_en,
            "C": self.option_c_en,
            "D": self.option_d_en
        }


@dataclass
class PaperConfig:
    """
    Configuration for generating a complete exam paper.

    Example:
        100 questions total
        - Main Subject: 60 questions (40 Easy, 15 Medium, 5 Hard)
        - Aptitude: 20 questions (15 Easy, 5 Medium)
        - General Knowledge: 10 questions (8 Easy, 2 Medium)
        - Language: 10 questions (10 Easy)
    """
    paper_name: str
    subject: str
    total_questions: int

    # Section distributions
    section_distribution: dict = field(default_factory=dict)  # {section_name: count}

    # Difficulty distribution (as percentages)
    difficulty_distribution: dict = field(default_factory=lambda: {
        "Easy": 0.60,
        "Medium": 0.30,
        "Hard": 0.10
    })

    def get_difficulty_counts(self, section_count: int) -> dict:
        """
        Calculate number of questions per difficulty for a section.

        Args:
            section_count: Total questions for this section

        Returns:
            Dict with counts per difficulty level
        """
        counts = {}
        remaining = section_count

        for difficulty, percentage in self.difficulty_distribution.items():
            if difficulty == list(self.difficulty_distribution.keys())[-1]:
                # Last difficulty gets remaining questions
                counts[difficulty] = remaining
            else:
                count = int(section_count * percentage)
                counts[difficulty] = count
                remaining -= count

        return counts
