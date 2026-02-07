"""
Generate a Medium difficulty question.
"""

from models import DifficultyLevel
from mcq_generator import generate_mcqs

print("\n🎯 Generating MEDIUM difficulty question...")
print("Topic: Material Science - Crystal Structure\n")

questions = generate_mcqs(
    subject='Metallurgical Engineering',
    main_topic='Material Science',
    subtopic='Crystal Structure - BCC, FCC, HCP',
    difficulty=DifficultyLevel.MEDIUM,
    n=1
)

if questions:
    q = questions[0]

    print("\n" + "="*80)
    print("MEDIUM DIFFICULTY QUESTION")
    print("="*80)

    print(f"\n❓ QUESTION:")
    print(f"{q.question_text_en}")

    print(f"\n📋 OPTIONS:")
    for label, text in q.get_options_dict().items():
        marker = "✅" if label == q.correct_answer else "  "
        print(f"{marker} {label}) {text}")

    print(f"\n✓ CORRECT ANSWER: {q.correct_answer}")

    print(f"\n💡 EXPLANATION:")
    print(f"{q.explanation}")

    print("\n" + "="*80)
    print(f"Difficulty: {q.difficulty.value}")
    print(f"References: {len(q.references)}")
    print("="*80 + "\n")
else:
    print("❌ Failed to generate question")
