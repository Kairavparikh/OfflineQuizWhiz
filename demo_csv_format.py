"""
Demo script showing the CSV export in client's exact format.
"""

from models import Question, DifficultyLevel
from csv_exporter import export_questions_to_csv
import uuid

# Create sample question matching the template format
question = Question(
    question_id="1",
    test_section="Metallurgical Engineering",
    main_topic="Engineering Mathematics",
    subtopic="Linear Algebra\nMatrices and Determinants",
    difficulty=DifficultyLevel.MEDIUM,
    question_text_en="Four matrices of orders 2×3, 3×3, 3×2, and 3×1 are given. For which of these matrices can the determinant be calculated?",
    option_a_en="2 × 3 matrix",
    option_b_en="3 × 3 matrix",
    option_c_en="3 × 2 matrix",
    option_d_en="3 × 1 matrix",
    correct_answer="B",
    explanation="Determinants: Only defined for square matrices (n x n).",
    references=[
        "https://allen.in/jee/maths/determinants-and-matrices",
        "https://www.cuemath.com/algebra/matrices-and-determinants/",
        "https://www.geeksforgeeks.org/dsa/determinant-of-a-matrix/"
    ]
)

# Export to CSV
export_questions_to_csv([question], "demo_client_format.csv")

print("\n" + "="*80)
print("CSV EXPORT - CLIENT FORMAT")
print("="*80)
print("\nGenerated file: demo_client_format.csv")
print("\nThis CSV includes:")
print("  ✅ All required columns from client template")
print("  ✅ Hindi translation placeholders (empty for now)")
print("  ✅ 'Translation for options required?' field")
print("  ✅ Numbered references list")
print("  ✅ 'Solution/Workout/Explanation' field")
print("  ✅ Correct Answer formatted as 'Option B'")
print("\nOpen demo_client_format.csv to see the exact format!")
print("="*80)
