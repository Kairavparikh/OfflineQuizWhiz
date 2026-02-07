"""
Example: Complete paper generation workflow.

This demonstrates how to:
1. Define paper configuration
2. Specify sections with topics
3. Generate complete exam paper
4. Export to CSV/Excel

Run:
    python3 example_paper_generation.py
"""

from models import PaperConfig, DifficultyLevel
from paper_builder import PaperBuilder, PaperSection
from csv_exporter import export_paper_to_csv, export_paper_to_excel


def example_basic_paper():
    """
    Example 1: Generate a basic paper with one section.

    This creates a simple 20-question paper for testing.
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: BASIC PAPER (20 Questions)")
    print("="*80)

    config = PaperConfig(
        paper_name="Sample Test 2026",
        subject="Metallurgical Engineering",
        total_questions=20
    )

    sections = [
        PaperSection(
            name="Main Subject",
            question_count=20,
            difficulty_distribution={
                "Easy": 12,    # 60%
                "Medium": 6,   # 30%
                "Hard": 2      # 10%
            },
            topics=[
                {"main_topic": "Material Science", "subtopic": "Crystal Structure"},
                {"main_topic": "Thermodynamics", "subtopic": "Phase Diagrams"}
            ]
        )
    ]

    # Build paper
    builder = PaperBuilder()
    paper = builder.build_paper(config, sections)

    # Export
    print("\nExporting to CSV...")
    export_paper_to_csv(paper, f"paper_{paper.paper_id}.csv")

    print("\nExporting to Excel...")
    export_paper_to_excel(paper, f"paper_{paper.paper_id}.xlsx")

    return paper


def example_full_exam_paper():
    """
    Example 2: Generate a full exam paper with multiple sections.

    This mimics a real exam structure:
    - Main Subject: 60 questions
    - Aptitude: 20 questions
    - General Knowledge: 10 questions
    - Language: 10 questions
    Total: 100 questions
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: FULL EXAM PAPER (100 Questions)")
    print("="*80)

    config = PaperConfig(
        paper_name="Metallurgical Engineering Exam 2026",
        subject="Metallurgical Engineering",
        total_questions=100
    )

    sections = [
        # Main Subject - 60 questions
        PaperSection(
            name="Main Subject",
            question_count=60,
            difficulty_distribution={
                "Easy": 40,    # ~67%
                "Medium": 15,  # ~25%
                "Hard": 5      # ~8%
            },
            topics=[
                {"main_topic": "Material Science", "subtopic": "Crystal Structure"},
                {"main_topic": "Material Science", "subtopic": "Defects and Diffusion"},
                {"main_topic": "Thermodynamics", "subtopic": "Phase Diagrams"},
                {"main_topic": "Thermodynamics", "subtopic": "Phase Transformations"},
                {"main_topic": "Mechanical Metallurgy", "subtopic": "Mechanical Properties"},
                {"main_topic": "Mechanical Metallurgy", "subtopic": "Heat Treatment"}
            ]
        ),

        # Aptitude - 20 questions
        PaperSection(
            name="Aptitude",
            question_count=20,
            difficulty_distribution={
                "Easy": 15,    # 75%
                "Medium": 5,   # 25%
                "Hard": 0
            },
            topics=[
                {"main_topic": "Quantitative Aptitude", "subtopic": "Number Systems"},
                {"main_topic": "Quantitative Aptitude", "subtopic": "Percentages"},
                {"main_topic": "Logical Reasoning", "subtopic": "Pattern Recognition"}
            ]
        ),

        # General Knowledge - 10 questions
        PaperSection(
            name="General Knowledge",
            question_count=10,
            difficulty_distribution={
                "Easy": 8,     # 80%
                "Medium": 2,   # 20%
                "Hard": 0
            },
            topics=[
                {"main_topic": "Current Affairs", "subtopic": "Science and Technology"},
                {"main_topic": "History", "subtopic": "Indian Independence"}
            ]
        ),

        # Language - 10 questions
        PaperSection(
            name="Language",
            question_count=10,
            difficulty_distribution={
                "Easy": 10,    # 100%
                "Medium": 0,
                "Hard": 0
            },
            topics=[
                {"main_topic": "English Grammar", "subtopic": "Tenses"},
                {"main_topic": "Vocabulary", "subtopic": "Synonyms and Antonyms"}
            ]
        )
    ]

    # Build paper
    builder = PaperBuilder()
    paper = builder.build_paper(config, sections)

    # Export
    print("\nExporting to CSV...")
    csv_file = f"full_exam_{paper.paper_id}.csv"
    export_paper_to_csv(paper, csv_file)

    print("\nExporting to Excel...")
    excel_file = f"full_exam_{paper.paper_id}.xlsx"
    export_paper_to_excel(paper, excel_file)

    print("\n" + "="*80)
    print("✅ FULL EXAM PAPER COMPLETE!")
    print("="*80)
    print(f"\nPaper Details:")
    print(f"  Name: {paper.paper_name}")
    print(f"  Subject: {paper.subject}")
    print(f"  Total Questions: {len(paper.questions)}")
    print(f"\nSection Breakdown:")

    section_counts = {}
    for q in paper.questions:
        section_counts[q.test_section] = section_counts.get(q.test_section, 0) + 1

    for section, count in section_counts.items():
        print(f"  - {section}: {count} questions")

    print(f"\nDifficulty Breakdown:")
    difficulty_counts = {}
    for q in paper.questions:
        diff = q.difficulty.value
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

    for diff, count in difficulty_counts.items():
        print(f"  - {diff}: {count} questions ({count/len(paper.questions)*100:.1f}%)")

    print(f"\nFiles Generated:")
    print(f"  ✅ CSV: {csv_file}")
    print(f"  ✅ Excel: {excel_file}")

    return paper


def example_custom_distribution():
    """
    Example 3: Custom difficulty distribution per section.

    Shows how different sections can have different difficulty profiles.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: CUSTOM DIFFICULTY DISTRIBUTION")
    print("="*80)

    config = PaperConfig(
        paper_name="Custom Distribution Test",
        subject="Mixed Topics",
        total_questions=50
    )

    sections = [
        # Easy section for beginners
        PaperSection(
            name="Fundamentals",
            question_count=20,
            difficulty_distribution={
                "Easy": 20,    # 100% easy
                "Medium": 0,
                "Hard": 0
            },
            topics=[
                {"main_topic": "Basics", "subtopic": "Introduction"}
            ]
        ),

        # Mixed difficulty for intermediate
        PaperSection(
            name="Intermediate",
            question_count=20,
            difficulty_distribution={
                "Easy": 10,    # 50%
                "Medium": 10,  # 50%
                "Hard": 0
            },
            topics=[
                {"main_topic": "Applied Concepts", "subtopic": "Problem Solving"}
            ]
        ),

        # Advanced section
        PaperSection(
            name="Advanced",
            question_count=10,
            difficulty_distribution={
                "Easy": 0,
                "Medium": 5,   # 50%
                "Hard": 5      # 50%
            },
            topics=[
                {"main_topic": "Complex Analysis", "subtopic": "Multi-step Problems"}
            ]
        )
    ]

    builder = PaperBuilder()
    paper = builder.build_paper(config, sections)

    export_paper_to_csv(paper, f"custom_dist_{paper.paper_id}.csv")

    return paper


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("PAPER GENERATION EXAMPLES")
    print("="*80)
    print("\nThis script demonstrates different paper generation scenarios:")
    print("  1. Basic paper (20 questions)")
    print("  2. Full exam paper (100 questions, multiple sections)")
    print("  3. Custom difficulty distribution")
    print("\n" + "="*80)

    # Example 1: Basic paper
    paper1 = example_basic_paper()

    # Example 2: Full exam
    paper2 = example_full_exam_paper()

    # Example 3: Custom distribution
    paper3 = example_custom_distribution()

    print("\n" + "="*80)
    print("✅ ALL EXAMPLES COMPLETE!")
    print("="*80)
    print(f"\nGenerated {len([paper1, paper2, paper3])} papers")
    print("\nNext steps:")
    print("  1. Review generated CSV/Excel files")
    print("  2. Check questions in each paper")
    print("  3. Adjust section/difficulty distributions as needed")
    print("  4. Use the web UI for easier paper generation")
    print("\nTo start web UI:")
    print("  python3 api.py")
    print("  Then open: http://localhost:8000")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
