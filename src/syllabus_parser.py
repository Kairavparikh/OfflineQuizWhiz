"""
Syllabus parser for extracting structured hierarchy from DOCX files.

Parses syllabus documents with headings and lists into Subject → Section → Topic → SubTopic hierarchy.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from docx import Document
from docx.text.paragraph import Paragraph
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from src.models.models import Subject, Section, Topic, SubTopic


class SyllabusParser:
    """
    Parse DOCX syllabus files into structured Subject objects.

    Assumptions about document structure:
    - Heading 1: Subject name (e.g., "Metallurgical Engineering")
    - Heading 2: Section name (e.g., "Engineering Mathematics", "Physics")
    - Heading 3: Topic name (e.g., "Linear Algebra", "Calculus")
    - Bullet/numbered lists under topics: SubTopics
    - Normal text: descriptions/details
    """

    def __init__(
        self,
        subject_heading_level: int = 1,
        section_heading_level: int = 2,
        topic_heading_level: int = 3,
        extract_keywords: bool = True
    ):
        """
        Initialize parser with configurable heading levels.

        Args:
            subject_heading_level: Heading level for subjects (default: 1)
            section_heading_level: Heading level for sections (default: 2)
            topic_heading_level: Heading level for topics (default: 3)
            extract_keywords: Whether to extract keywords from subtopic text
        """
        self.subject_level = subject_heading_level
        self.section_level = section_heading_level
        self.topic_level = topic_heading_level
        self.extract_keywords = extract_keywords

    def parse_docx(self, docx_path: str) -> List[Subject]:
        """
        Parse DOCX file and return list of Subject objects.

        Args:
            docx_path: Path to the DOCX file

        Returns:
            List of Subject objects with full hierarchy
        """
        doc = Document(docx_path)
        subjects = []
        current_subject = None
        current_section = None
        current_topic = None
        description_buffer = []

        for para in doc.paragraphs:
            heading_level = self._get_heading_level(para)
            text = para.text.strip()

            if not text:
                continue

            # Subject level (e.g., Heading 1)
            if heading_level == self.subject_level:
                # Save previous subject
                if current_subject:
                    subjects.append(current_subject)

                # Start new subject
                current_subject = Subject(name=text)
                current_section = None
                current_topic = None
                description_buffer = []
                print(f"📚 Found Subject: {text}")

            # Section level (e.g., Heading 2)
            elif heading_level == self.section_level:
                if current_subject:
                    # Attach buffered description to previous section
                    if current_section and description_buffer:
                        current_section.description = " ".join(description_buffer)
                        description_buffer = []

                    # Create new section
                    current_section = Section(name=text)
                    current_subject.add_section(current_section)
                    current_topic = None
                    print(f"  📂 Found Section: {text}")

            # Topic level (e.g., Heading 3)
            elif heading_level == self.topic_level:
                if current_section:
                    # Attach buffered description to previous topic
                    if current_topic and description_buffer:
                        current_topic.description = " ".join(description_buffer)
                        description_buffer = []

                    # Create new topic
                    current_topic = Topic(name=text)
                    current_section.add_topic(current_topic)
                    print(f"    📖 Found Topic: {text}")

            # List item (subtopic)
            elif self._is_list_item(para):
                if current_topic:
                    subtopic_text = self._clean_list_text(text)
                    if subtopic_text:
                        keywords = self._extract_keywords(subtopic_text) if self.extract_keywords else []
                        subtopic = SubTopic(
                            name=subtopic_text,
                            keywords=keywords
                        )
                        current_topic.add_subtopic(subtopic)
                        print(f"      • Found SubTopic: {subtopic_text}")

            # Normal text (descriptions)
            else:
                # Accumulate description text
                if text and not text.startswith("Page ") and len(text) > 10:
                    description_buffer.append(text)

        # Save last subject
        if current_subject:
            subjects.append(current_subject)

        print(f"\n✅ Parsed {len(subjects)} subject(s)")
        return subjects

    def _get_heading_level(self, para: Paragraph) -> Optional[int]:
        """
        Extract heading level from paragraph style.

        Args:
            para: Paragraph object

        Returns:
            Heading level (1, 2, 3, ...) or None if not a heading
        """
        style_name = para.style.name.lower()

        # Check for "Heading 1", "Heading 2", etc.
        if style_name.startswith('heading'):
            match = re.search(r'heading\s*(\d+)', style_name)
            if match:
                return int(match.group(1))

        # Check for custom heading styles (e.g., "Title", "Subtitle")
        if style_name == 'title':
            return 1
        elif style_name == 'subtitle':
            return 2

        return None

    def _is_list_item(self, para: Paragraph) -> bool:
        """
        Check if paragraph is a list item (bullet or numbered).

        Args:
            para: Paragraph object

        Returns:
            True if paragraph is a list item
        """
        # Check paragraph format for list numbering
        if para._element.pPr is not None:
            numPr = para._element.pPr.numPr
            if numPr is not None:
                return True

        # Check text patterns for manual bullets/numbers
        text = para.text.strip()
        patterns = [
            r'^\d+\.',  # 1., 2., 3.
            r'^\d+\)',  # 1), 2), 3)
            r'^[a-z]\.',  # a., b., c.
            r'^[a-z]\)',  # a), b), c)
            r'^\([a-z]\)',  # (a), (b), (c)
            r'^•',  # bullet
            r'^-\s',  # dash
            r'^\*\s',  # asterisk
            r'^[ivx]+\.',  # Roman numerals: i., ii., iii.
        ]

        for pattern in patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True

        return False

    def _clean_list_text(self, text: str) -> str:
        """
        Remove list markers (bullets, numbers) from text.

        Args:
            text: Raw list item text

        Returns:
            Cleaned text without markers
        """
        # Remove common list markers
        text = re.sub(r'^\d+\.?\s*', '', text)  # 1. or 1
        text = re.sub(r'^\d+\)\s*', '', text)  # 1)
        text = re.sub(r'^[a-z]\.?\s*', '', text, flags=re.IGNORECASE)  # a. or a
        text = re.sub(r'^[a-z]\)\s*', '', text, flags=re.IGNORECASE)  # a)
        text = re.sub(r'^\([a-z]\)\s*', '', text, flags=re.IGNORECASE)  # (a)
        text = re.sub(r'^[•\-\*]\s*', '', text)  # bullets
        text = re.sub(r'^[ivx]+\.?\s*', '', text, flags=re.IGNORECASE)  # Roman numerals

        return text.strip()

    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract potential keywords from subtopic text.

        Simple heuristic: extract capitalized words and technical terms.

        Args:
            text: Subtopic text
            max_keywords: Maximum number of keywords to extract

        Returns:
            List of keywords
        """
        keywords = []

        # Split into words
        words = re.findall(r'\b[A-Z][a-z]*\b|\b[a-z]{4,}\b', text)

        # Filter and deduplicate
        seen = set()
        for word in words:
            word_lower = word.lower()
            if word_lower not in seen and len(word_lower) >= 3:
                # Skip common words
                if word_lower not in ['the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'been', 'will']:
                    keywords.append(word_lower)
                    seen.add(word_lower)

            if len(keywords) >= max_keywords:
                break

        return keywords

    def subjects_to_json(self, subjects: List[Subject], output_path: Optional[str] = None) -> str:
        """
        Convert list of Subject objects to JSON.

        Args:
            subjects: List of Subject objects
            output_path: Optional path to save JSON file

        Returns:
            JSON string
        """
        data = {"subjects": []}

        for subject in subjects:
            subject_dict = {
                "name": subject.name,
                "code": subject.code,
                "description": subject.description,
                "sections": []
            }

            for section in subject.sections:
                section_dict = {
                    "name": section.name,
                    "description": section.description,
                    "topics": []
                }

                for topic in section.topics:
                    topic_dict = {
                        "name": topic.name,
                        "description": topic.description,
                        "subtopics": []
                    }

                    for subtopic in topic.subtopics:
                        subtopic_dict = {
                            "name": subtopic.name,
                            "description": subtopic.description,
                            "keywords": subtopic.keywords
                        }
                        topic_dict["subtopics"].append(subtopic_dict)

                    section_dict["topics"].append(topic_dict)

                subject_dict["sections"].append(section_dict)

            data["subjects"].append(subject_dict)

        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        if output_path:
            Path(output_path).write_text(json_str, encoding='utf-8')
            print(f"\n💾 Saved JSON to: {output_path}")

        return json_str

    def json_to_subjects(self, json_path: str) -> List[Subject]:
        """
        Load Subject objects from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            List of Subject objects
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        subjects = []

        for subject_data in data.get("subjects", []):
            subject = Subject(
                name=subject_data["name"],
                code=subject_data.get("code"),
                description=subject_data.get("description")
            )

            for section_data in subject_data.get("sections", []):
                section = Section(
                    name=section_data["name"],
                    description=section_data.get("description")
                )

                for topic_data in section_data.get("topics", []):
                    topic = Topic(
                        name=topic_data["name"],
                        description=topic_data.get("description")
                    )

                    for subtopic_data in topic_data.get("subtopics", []):
                        subtopic = SubTopic(
                            name=subtopic_data["name"],
                            description=subtopic_data.get("description"),
                            keywords=subtopic_data.get("keywords", [])
                        )
                        topic.add_subtopic(subtopic)

                    section.add_topic(topic)

                subject.add_section(section)

            subjects.append(subject)

        return subjects


def print_syllabus_summary(subjects: List[Subject]) -> None:
    """
    Print a summary of the parsed syllabus structure.

    Args:
        subjects: List of Subject objects
    """
    print("\n" + "=" * 80)
    print("SYLLABUS STRUCTURE SUMMARY")
    print("=" * 80)

    for subject in subjects:
        print(f"\n📚 SUBJECT: {subject.name}")
        if subject.description:
            print(f"   Description: {subject.description[:100]}...")

        for section in subject.sections:
            print(f"\n  📂 Section: {section.name}")
            if section.description:
                print(f"     Description: {section.description[:80]}...")

            for topic in section.topics:
                print(f"\n    📖 Topic: {topic.name}")
                if topic.description:
                    print(f"       Description: {topic.description[:70]}...")

                if topic.subtopics:
                    print(f"       SubTopics ({len(topic.subtopics)}):")
                    for i, subtopic in enumerate(topic.subtopics, 1):
                        keywords_str = f" [Keywords: {', '.join(subtopic.keywords[:3])}]" if subtopic.keywords else ""
                        print(f"         {i}. {subtopic.name}{keywords_str}")

    print("\n" + "=" * 80)
    total_sections = sum(len(s.sections) for s in subjects)
    total_topics = sum(len(sec.topics) for s in subjects for sec in s.sections)
    total_subtopics = sum(
        len(topic.subtopics)
        for s in subjects
        for sec in s.sections
        for topic in sec.topics
    )
    print(f"TOTALS: {len(subjects)} Subject(s), {total_sections} Section(s), "
          f"{total_topics} Topic(s), {total_subtopics} SubTopic(s)")
    print("=" * 80)
