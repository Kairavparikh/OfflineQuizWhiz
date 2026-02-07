"""
Paper builder for assembling complete exam papers from generated questions.

Features:
- Builds papers matching section/difficulty distributions
- Avoids duplicate questions across papers
- Supports both text-only and multimodal questions
- Tracks question usage to prevent reuse
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from pathlib import Path
import json
from models import Question, PaperConfig, DifficultyLevel
from mcq_generator import generate_mcqs
from multimodal_generator import MultimodalMCQGenerator
from multimodal_models import TextImagePair


@dataclass
class PaperSection:
    """Configuration for a single section within a paper."""
    name: str  # e.g., "Main Subject", "Aptitude", "General Knowledge"
    question_count: int  # Total questions for this section
    difficulty_distribution: Dict[str, int]  # {difficulty: count}
    topics: List[Dict[str, str]] = field(default_factory=list)  # [{main_topic, subtopic}]


@dataclass
class Paper:
    """A complete assembled exam paper."""
    paper_id: str
    paper_name: str
    subject: str
    questions: List[Question]
    created_at: str

    def validate(self) -> List[str]:
        """Validate the complete paper."""
        errors = []

        # Check total count
        if len(self.questions) == 0:
            errors.append("Paper has no questions")

        # Check for duplicate question IDs
        question_ids = [q.question_id for q in self.questions]
        if len(question_ids) != len(set(question_ids)):
            errors.append("Paper contains duplicate question IDs")

        # Validate each question
        for i, q in enumerate(self.questions, 1):
            q_errors = q.validate()
            if q_errors:
                errors.append(f"Question {i} invalid: {', '.join(q_errors)}")

        return errors

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "paper_id": self.paper_id,
            "paper_name": self.paper_name,
            "subject": self.subject,
            "created_at": self.created_at,
            "total_questions": len(self.questions),
            "questions": [q.to_dict() for q in self.questions]
        }


class QuestionBank:
    """
    Manages generated questions and prevents duplicates.

    Tracks used question IDs across papers to ensure uniqueness.
    """

    def __init__(self, state_file: str = "question_bank_state.json"):
        self.state_file = Path(state_file)
        self.used_question_ids: Set[str] = set()
        self.all_questions: List[Question] = []
        self._load_state()

    def _load_state(self):
        """Load previously used question IDs from disk."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                self.used_question_ids = set(data.get('used_question_ids', []))

    def _save_state(self):
        """Save used question IDs to disk."""
        with open(self.state_file, 'w') as f:
            json.dump({
                'used_question_ids': list(self.used_question_ids)
            }, f, indent=2)

    def add_questions(self, questions: List[Question]):
        """Add questions to the bank and mark as used."""
        for q in questions:
            if q.question_id not in self.used_question_ids:
                self.used_question_ids.add(q.question_id)
                self.all_questions.append(q)

        self._save_state()

    def is_used(self, question_id: str) -> bool:
        """Check if a question ID has been used."""
        return question_id in self.used_question_ids

    def clear(self):
        """Clear all used questions (use with caution!)."""
        self.used_question_ids.clear()
        self.all_questions.clear()
        self._save_state()


class PaperBuilder:
    """
    Builds complete exam papers from configuration.

    Supports:
    - Text-only questions from syllabus topics
    - Multimodal questions from PDF diagrams
    - Section-based distribution
    - Difficulty-based distribution
    - Duplicate prevention
    """

    def __init__(self, question_bank: Optional[QuestionBank] = None, use_real_vlm: bool = False):
        self.question_bank = question_bank or QuestionBank()

        # Use real VLM if requested, otherwise use mock for testing
        if use_real_vlm:
            from vlm_client import VLMConfig, VLMClient
            vlm_config = VLMConfig(
                base_url="http://localhost:11434",
                model_name="llava",
                timeout_seconds=180
            )
            vlm_client = VLMClient(vlm_config)
            self.multimodal_generator = MultimodalMCQGenerator(vlm_client=vlm_client)
            print("⚡ Using REAL VLM (LLaVA) for diagram-based questions")
        else:
            self.multimodal_generator = MultimodalMCQGenerator(use_mock=True)
            print("⚠️  Using MockVLMClient - responses will be dummy data")

    def build_paper(
        self,
        config: PaperConfig,
        sections: List[PaperSection],
        diagram_pairs: Optional[List[TextImagePair]] = None
    ) -> Paper:
        """
        Build a complete exam paper from configuration.

        Args:
            config: Paper configuration
            sections: List of section configurations
            diagram_pairs: Optional text-image pairs for multimodal questions

        Returns:
            Complete Paper object

        Example:
            >>> config = PaperConfig(
            ...     paper_name="Sample Exam 2026",
            ...     subject="Metallurgical Engineering",
            ...     total_questions=100
            ... )
            >>>
            >>> sections = [
            ...     PaperSection(
            ...         name="Main Subject",
            ...         question_count=60,
            ...         difficulty_distribution={"Easy": 40, "Medium": 15, "Hard": 5},
            ...         topics=[
            ...             {"main_topic": "Material Science", "subtopic": "Crystal Structure"},
            ...             {"main_topic": "Thermodynamics", "subtopic": "Phase Diagrams"}
            ...         ]
            ...     ),
            ...     PaperSection(
            ...         name="Aptitude",
            ...         question_count=20,
            ...         difficulty_distribution={"Easy": 15, "Medium": 5, "Hard": 0},
            ...         topics=[
            ...             {"main_topic": "Quantitative Aptitude", "subtopic": "Number Systems"}
            ...         ]
            ...     )
            ... ]
            >>>
            >>> paper = builder.build_paper(config, sections)
        """
        import uuid
        from datetime import datetime

        all_questions = []

        print(f"\n{'='*80}")
        print(f"BUILDING PAPER: {config.paper_name}")
        print(f"{'='*80}")
        print(f"Subject: {config.subject}")
        print(f"Total questions: {config.total_questions}")
        print(f"Sections: {len(sections)}")

        # Build each section
        for section in sections:
            print(f"\n{'─'*80}")
            print(f"SECTION: {section.name} ({section.question_count} questions)")
            print(f"{'─'*80}")

            section_questions = self._build_section(
                section=section,
                subject=config.subject,
                diagram_pairs=diagram_pairs
            )

            all_questions.extend(section_questions)

            print(f"✅ Generated {len(section_questions)} questions for {section.name}")

        # Create paper
        paper = Paper(
            paper_id=str(uuid.uuid4()),
            paper_name=config.paper_name,
            subject=config.subject,
            questions=all_questions,
            created_at=datetime.now().isoformat()
        )

        # Validate
        errors = paper.validate()
        if errors:
            print(f"\n⚠️  Paper validation errors:")
            for error in errors:
                print(f"   - {error}")
        else:
            print(f"\n✅ Paper validated successfully!")

        # Add to question bank
        self.question_bank.add_questions(all_questions)

        print(f"\n{'='*80}")
        print(f"✅ PAPER COMPLETE!")
        print(f"{'='*80}")
        print(f"Paper ID: {paper.paper_id}")
        print(f"Total questions: {len(paper.questions)}")
        print(f"Used questions tracked: {len(self.question_bank.used_question_ids)}")

        return paper

    def _build_section(
        self,
        section: PaperSection,
        subject: str,
        diagram_pairs: Optional[List[TextImagePair]] = None
    ) -> List[Question]:
        """Build all questions for a single section."""
        questions = []

        # Generate questions for each difficulty level
        for difficulty_str, count in section.difficulty_distribution.items():
            if count == 0:
                continue

            difficulty = DifficultyLevel[difficulty_str.upper()]

            print(f"\n  Generating {count} {difficulty_str} questions...")

            # Determine how many questions per topic
            if not section.topics:
                print(f"  ⚠️  No topics specified for {section.name}, skipping...")
                continue

            questions_per_topic = count // len(section.topics)
            remainder = count % len(section.topics)

            # Generate from each topic
            for i, topic_spec in enumerate(section.topics):
                topic_count = questions_per_topic + (1 if i < remainder else 0)

                if topic_count == 0:
                    continue

                main_topic = topic_spec.get("main_topic", "General")
                subtopic = topic_spec.get("subtopic", "General")

                print(f"    - {main_topic} → {subtopic}: {topic_count} questions")

                # Try to use multimodal generation if pairs available
                if diagram_pairs and len(diagram_pairs) > 0:
                    # Use first available pair (in production, match by topic)
                    pair = diagram_pairs[0]

                    try:
                        topic_questions = self.multimodal_generator.generate_from_pair(
                            pair=pair,
                            subject=subject,
                            main_topic=main_topic,
                            subtopic=subtopic,
                            difficulty=difficulty,
                            n=topic_count
                        )

                        # Update test_section
                        for q in topic_questions:
                            q.test_section = section.name

                        questions.extend(topic_questions)

                    except Exception as e:
                        print(f"      ⚠️  Multimodal generation failed: {e}")
                        print(f"      Falling back to text-only generation...")

                        # Fallback to text-only
                        topic_questions = generate_mcqs(
                            subject=subject,
                            main_topic=main_topic,
                            subtopic=subtopic,
                            difficulty=difficulty,
                            n=topic_count
                        )
                        # Update test_section
                        for q in topic_questions:
                            q.test_section = section.name
                        questions.extend(topic_questions)

                else:
                    # Text-only generation
                    topic_questions = generate_mcqs(
                        subject=subject,
                        main_topic=main_topic,
                        subtopic=subtopic,
                        difficulty=difficulty,
                        n=topic_count
                    )
                    # Update test_section
                    for q in topic_questions:
                        q.test_section = section.name
                    questions.extend(topic_questions)

        return questions


def build_paper(config: PaperConfig, sections: List[PaperSection]) -> Paper:
    """
    Convenience function to build a paper with default settings.

    Args:
        config: Paper configuration
        sections: List of section configurations

    Returns:
        Complete Paper object
    """
    builder = PaperBuilder()
    return builder.build_paper(config, sections)
