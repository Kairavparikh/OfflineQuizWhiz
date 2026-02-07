"""
Simple test to verify paper builder works without test_section parameter issue.
"""

from models import PaperConfig, DifficultyLevel
from paper_builder import PaperBuilder, PaperSection

print("Testing paper builder...")

config = PaperConfig(
    paper_name="Simple Test",
    subject="Test Subject",
    total_questions=2
)

sections = [
    PaperSection(
        name="Test Section",
        question_count=2,
        difficulty_distribution={"Easy": 2, "Medium": 0, "Hard": 0},
        topics=[
            {"main_topic": "Test Topic", "subtopic": "Test Subtopic"}
        ]
    )
]

builder = PaperBuilder()
paper = builder.build_paper(config, sections)

print(f"✅ Paper built successfully!")
print(f"Total questions: {len(paper.questions)}")
for i, q in enumerate(paper.questions, 1):
    print(f"  Q{i}: {q.test_section} | {q.difficulty.value} | {q.question_text_en[:50]}...")
