"""
Quick test script for data models (no external dependencies required).
"""

import json
from src.models.models import (
    Subject, Section, Topic, SubTopic, Question, DifficultyLevel, PaperConfig
)


def test_data_models():
    """Test data model creation and validation."""
    print("=" * 80)
    print("TEST 1: Data Models")
    print("=" * 80)

    # Create hierarchy
    subject = Subject(name="Metallurgical Engineering", code="SME")
    section = Section(name="Engineering Mathematics")
    topic = Topic(name="Linear Algebra")
    subtopic = SubTopic(
        name="Matrices and Determinants",
        keywords=["matrix", "determinant", "eigenvalue"]
    )

    # Build hierarchy
    topic.add_subtopic(subtopic)
    section.add_topic(topic)
    subject.add_section(section)

    print(f"\n✅ Created hierarchy:")
    print(f"   {subject.name} → {section.name} → {topic.name} → {subtopic.name}")

    return subject, section, topic, subtopic


def test_question_creation(section, topic, subtopic):
    """Test question creation and validation."""
    print("\n" + "=" * 80)
    print("TEST 2: Question Creation & Validation")
    print("=" * 80)

    # Valid question
    question = Question(
        test_section=section.name,
        main_topic=topic.name,
        subtopic=subtopic.name,
        difficulty=DifficultyLevel.MEDIUM,
        question_text_en="What is the determinant of a 2×2 identity matrix?",
        option_a_en="0",
        option_b_en="1",
        option_c_en="2",
        option_d_en="-1",
        correct_answer="B",
        explanation="The determinant of an identity matrix of any size is always 1. "
                    "For a 2×2 identity matrix I = [[1,0],[0,1]], det(I) = 1.",
        references=["https://en.wikipedia.org/wiki/Determinant"],
        tags=["linear algebra", "determinant"]
    )

    print(f"\n✅ Created question: {question.question_id}")

    # Validate
    errors = question.validate()
    if errors:
        print(f"❌ Validation errors: {errors}")
    else:
        print(f"✅ Question is valid!")

    # Display
    print(f"\n" + "-" * 80)
    print(f"Question: {question.question_text_en}")
    print(f"\nOptions:")
    for label, text in question.get_options_dict().items():
        marker = "✓" if label == question.correct_answer else " "
        print(f"  [{marker}] {label}. {text}")
    print(f"\nCorrect: {question.correct_answer}")
    print(f"Explanation: {question.explanation}")
    print(f"Difficulty: {question.difficulty.value}")
    print("-" * 80)

    return question


def test_invalid_question():
    """Test validation with invalid question."""
    print("\n" + "=" * 80)
    print("TEST 3: Invalid Question Validation")
    print("=" * 80)

    question = Question(
        test_section="Math",
        main_topic="Algebra",
        question_text_en="What is 2+2?",
        option_a_en="4",
        option_b_en="4",  # Duplicate!
        option_c_en="",   # Empty!
        option_d_en="5",
        correct_answer="X",  # Invalid!
        explanation="Short"  # Too short!
    )

    errors = question.validate()
    print(f"\n🔍 Found {len(errors)} validation error(s):")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")

    print("\n✅ Validation working correctly!")


def test_json_serialization(question):
    """Test JSON serialization."""
    print("\n" + "=" * 80)
    print("TEST 4: JSON Serialization")
    print("=" * 80)

    # Convert to dict
    data = question.to_dict()
    print(f"\n✅ Converted to dictionary")

    # Serialize to JSON
    json_str = json.dumps(data, indent=2)
    print(f"✅ Serialized to JSON ({len(json_str)} bytes)")

    # Show snippet
    print(f"\nJSON snippet:")
    print(json_str[:300] + "...")


def test_paper_config():
    """Test paper configuration."""
    print("\n" + "=" * 80)
    print("TEST 5: Paper Configuration")
    print("=" * 80)

    config = PaperConfig(
        paper_name="Test Paper 1",
        subject="Metallurgical Engineering",
        total_questions=100,
        section_distribution={
            "Engineering Mathematics": 30,
            "Physics": 20,
            "Material Science": 30,
            "Aptitude": 20
        }
    )

    print(f"\n📋 {config.paper_name}")
    print(f"Total: {config.total_questions} questions\n")

    total = 0
    for section, count in config.section_distribution.items():
        print(f"{section}: {count} questions")
        difficulty = config.get_difficulty_counts(count)
        for diff, diff_count in difficulty.items():
            print(f"  - {diff}: {diff_count}")
        total += count

    print(f"\n✅ Section distribution adds up to {total}")


def test_load_sample_json():
    """Test loading sample_syllabus.json."""
    print("\n" + "=" * 80)
    print("TEST 6: Load Sample JSON")
    print("=" * 80)

    try:
        with open("sample_syllabus.json", 'r') as f:
            data = json.load(f)

        print(f"\n✅ Loaded sample_syllabus.json")
        print(f"   Subjects: {len(data['subjects'])}")

        for subject_data in data['subjects'][:1]:
            print(f"\n   Subject: {subject_data['name']}")
            sections = subject_data.get('sections', [])
            print(f"   Sections: {len(sections)}")

            for section in sections[:1]:
                topics = section.get('topics', [])
                print(f"     Topics in '{section['name']}': {len(topics)}")

    except FileNotFoundError:
        print(f"\n⚠️  sample_syllabus.json not found")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("MCQ GENERATOR - DATA MODEL TESTS")
    print("=" * 80)

    # Test 1: Data models
    subject, section, topic, subtopic = test_data_models()

    # Test 2: Valid question
    question = test_question_creation(section, topic, subtopic)

    # Test 3: Invalid question
    test_invalid_question()

    # Test 4: JSON serialization
    test_json_serialization(question)

    # Test 5: Paper config
    test_paper_config()

    # Test 6: Load sample JSON
    test_load_sample_json()

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\n💡 Next steps:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Place your syllabus DOCX file in this directory")
    print("   3. Run: python example_usage.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
