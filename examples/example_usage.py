"""
Example usage of the syllabus parser and data models.

Demonstrates:
1. Parsing a DOCX syllabus file
2. Saving/loading to/from JSON
3. Creating sample questions
4. Validating questions
"""

import sys
from pathlib import Path

from src.models.models import (
    Subject, Section, Topic, SubTopic, Question, DifficultyLevel, PaperConfig
)
from src.syllabus_parser import SyllabusParser, print_syllabus_summary


def example_parse_docx():
    """Example: Parse a DOCX syllabus file."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Parse DOCX Syllabus")
    print("="*80)

    # Initialize parser
    parser = SyllabusParser(
        subject_heading_level=1,
        section_heading_level=2,
        topic_heading_level=3,
        extract_keywords=True
    )

    # Parse DOCX (replace with your actual file path)
    docx_path = "Syllabus-for-SME.docx"

    if not Path(docx_path).exists():
        print(f"\n⚠️  File not found: {docx_path}")
        print("📝 To use this example, place your syllabus DOCX file in the current directory.")
        print("   Or modify the path in example_usage.py")
        return None

    # Parse
    subjects = parser.parse_docx(docx_path)

    # Print summary
    print_syllabus_summary(subjects)

    # Save to JSON
    output_json = "parsed_syllabus.json"
    parser.subjects_to_json(subjects, output_json)

    return subjects


def example_load_from_json():
    """Example: Load syllabus from JSON."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Load from JSON")
    print("="*80)

    parser = SyllabusParser()
    json_path = "sample_syllabus.json"

    if not Path(json_path).exists():
        print(f"\n⚠️  File not found: {json_path}")
        return None

    # Load from JSON
    subjects = parser.json_to_subjects(json_path)

    print(f"\n✅ Loaded {len(subjects)} subject(s) from JSON")

    # Access the hierarchy
    for subject in subjects:
        print(f"\n📚 Subject: {subject.name}")
        for section in subject.sections[:2]:  # Show first 2 sections
            print(f"  📂 Section: {section.name}")
            for topic in section.topics[:2]:  # Show first 2 topics
                print(f"    📖 Topic: {topic.name}")
                for subtopic in topic.subtopics[:3]:  # Show first 3 subtopics
                    print(f"      • {subtopic.name}")

    return subjects


def example_create_question(subjects):
    """Example: Create and validate a sample question."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Create and Validate Questions")
    print("="*80)

    if not subjects:
        print("\n⚠️  No subjects loaded. Run example_load_from_json() first.")
        return

    # Get a sample topic hierarchy
    subject = subjects[0]
    section = subject.sections[0]
    topic = section.topics[0]
    subtopic = topic.subtopics[0] if topic.subtopics else None

    print(f"\n📝 Creating question for:")
    print(f"   Subject: {subject.name}")
    print(f"   Section: {section.name}")
    print(f"   Topic: {topic.name}")
    print(f"   SubTopic: {subtopic.name if subtopic else 'N/A'}")

    # Create a sample question
    question = Question(
        test_section=section.name,
        main_topic=topic.name,
        subtopic=subtopic.name if subtopic else "",
        difficulty=DifficultyLevel.MEDIUM,
        question_text_en="What is the determinant of a 2×2 identity matrix?",
        option_a_en="0",
        option_b_en="1",
        option_c_en="2",
        option_d_en="-1",
        correct_answer="B",
        explanation="The determinant of an identity matrix of any size is always 1. "
                    "For a 2×2 identity matrix I = [[1,0],[0,1]], det(I) = (1×1) - (0×0) = 1.",
        references=[
            "https://en.wikipedia.org/wiki/Determinant",
            "Linear Algebra and Its Applications by Gilbert Strang, Chapter 5"
        ],
        has_diagram=False,
        tags=["linear algebra", "determinant", "matrix", "identity matrix"]
    )

    print(f"\n✅ Created question: {question.question_id}")

    # Validate
    errors = question.validate()
    if errors:
        print(f"\n❌ Validation errors:")
        for error in errors:
            print(f"   - {error}")
    else:
        print(f"\n✅ Question is valid!")

    # Display question
    print(f"\n" + "-"*80)
    print(f"Question: {question.question_text_en}")
    print(f"\nOptions:")
    for label, text in question.get_options_dict().items():
        marker = "✓" if label == question.correct_answer else " "
        print(f"  [{marker}] {label}. {text}")
    print(f"\nCorrect Answer: {question.correct_answer}")
    print(f"\nExplanation: {question.explanation}")
    print(f"\nReferences:")
    for ref in question.references:
        print(f"  - {ref}")
    print(f"\nMetadata:")
    print(f"  Section: {question.test_section}")
    print(f"  Topic: {question.main_topic}")
    print(f"  SubTopic: {question.subtopic}")
    print(f"  Difficulty: {question.difficulty.value}")
    print(f"  Tags: {', '.join(question.tags)}")
    print("-"*80)

    return question


def example_invalid_question():
    """Example: Create an invalid question and see validation errors."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Invalid Question Validation")
    print("="*80)

    # Create an invalid question (missing options, duplicate options, etc.)
    question = Question(
        test_section="Engineering Mathematics",
        main_topic="Linear Algebra",
        subtopic="Matrices",
        difficulty=DifficultyLevel.EASY,
        question_text_en="What is a matrix?",
        option_a_en="A rectangular array of numbers",
        option_b_en="A rectangular array of numbers",  # Duplicate!
        option_c_en="",  # Empty!
        option_d_en="None of the above",
        correct_answer="X",  # Invalid!
        explanation="Too short",  # Too short!
        references=[]
    )

    print(f"\n🔍 Validating question...")
    errors = question.validate()

    if errors:
        print(f"\n❌ Found {len(errors)} validation error(s):")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    else:
        print(f"\n✅ Question is valid!")


def example_paper_config():
    """Example: Configure a complete exam paper."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Paper Configuration")
    print("="*80)

    # Define paper structure
    config = PaperConfig(
        paper_name="Metallurgical Engineering - Paper 1",
        subject="Metallurgical Engineering",
        total_questions=100,
        section_distribution={
            "Engineering Mathematics": 20,
            "Physics": 15,
            "Material Science": 25,
            "Aptitude": 20,
            "General Knowledge": 10,
            "Language": 10
        },
        difficulty_distribution={
            "Easy": 0.60,
            "Medium": 0.30,
            "Hard": 0.10
        }
    )

    print(f"\n📋 Paper: {config.paper_name}")
    print(f"📊 Total Questions: {config.total_questions}")
    print(f"\n📂 Section Distribution:")

    total_check = 0
    for section, count in config.section_distribution.items():
        print(f"\n  {section}: {count} questions")

        # Calculate difficulty breakdown
        difficulty_counts = config.get_difficulty_counts(count)
        for difficulty, diff_count in difficulty_counts.items():
            print(f"    - {difficulty}: {diff_count} questions")

        total_check += count

    print(f"\n✅ Total: {total_check} questions")

    # Validate
    if total_check != config.total_questions:
        print(f"\n⚠️  Warning: Section distribution ({total_check}) doesn't match total ({config.total_questions})")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("MCQ GENERATOR - EXAMPLE USAGE")
    print("="*80)

    # Example 1: Parse DOCX (if file exists)
    # subjects_from_docx = example_parse_docx()

    # Example 2: Load from JSON
    subjects = example_load_from_json()

    if subjects:
        # Example 3: Create valid question
        question = example_create_question(subjects)

    # Example 4: Invalid question
    example_invalid_question()

    # Example 5: Paper configuration
    example_paper_config()

    print("\n" + "="*80)
    print("✅ All examples completed!")
    print("="*80)


if __name__ == "__main__":
    main()
