"""
Simple test to generate your first MCQ using the local LLM.
"""

from models import DifficultyLevel
from mcq_generator import generate_mcqs

print("\n" + "="*80)
print("GENERATING YOUR FIRST MCQ")
print("="*80)
print("\nThis will take ~30-60 seconds...")
print("The LLM is thinking and generating a complete question with explanation.\n")

try:
    questions = generate_mcqs(
        subject="Metallurgical Engineering",
        main_topic="Engineering Mathematics",
        subtopic="Linear Algebra - Matrices and Determinants",
        difficulty=DifficultyLevel.EASY,
        n=1
    )

    if questions:
        q = questions[0]

        print("\n" + "="*80)
        print("✅ SUCCESSFULLY GENERATED QUESTION!")
        print("="*80)

        print(f"\n📝 Question ID: {q.question_id}")
        print(f"📚 Topic: {q.main_topic} → {q.subtopic}")
        print(f"🎯 Difficulty: {q.difficulty.value}")

        print(f"\n❓ QUESTION:")
        print(f"{q.question_text_en}")

        print(f"\n📋 OPTIONS:")
        options = q.get_options_dict()
        for label, text in options.items():
            marker = "✅" if label == q.correct_answer else "  "
            print(f"{marker} {label}) {text}")

        print(f"\n✓ CORRECT ANSWER: {q.correct_answer}")

        print(f"\n💡 EXPLANATION:")
        print(f"{q.explanation}")

        if q.references:
            print(f"\n📖 REFERENCES:")
            for i, ref in enumerate(q.references, 1):
                print(f"   {i}. {ref}")

        print("\n" + "="*80)
        print("🎉 SUCCESS! Your MCQ generator is working!")
        print("="*80)

        # Validation check
        errors = q.validate()
        if errors:
            print(f"\n⚠️  Note: Question has validation issues: {errors}")
        else:
            print(f"\n✅ Question passed all validation checks!")
            print(f"   - Has 4 distinct options")
            print(f"   - Correct answer is valid (A/B/C/D)")
            print(f"   - Explanation is detailed ({len(q.explanation)} chars)")
            print(f"   - Has {len(q.references)} reference(s)")

        print(f"\n💾 To save this question to JSON:")
        print(f"   import json")
        print(f"   with open('my_question.json', 'w') as f:")
        print(f"       json.dump(q.to_dict(), f, indent=2)")

        print(f"\n📚 Next steps:")
        print(f"   - Try generating Medium or Hard questions")
        print(f"   - Generate multiple questions at once (n=5)")
        print(f"   - See example_generator.py for more examples")
        print(f"   - Read PHASE2_GUIDE.md for complete usage guide")
        print("="*80 + "\n")
    else:
        print("\n❌ No questions were generated")
        print("Check the output above for errors")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Check the model is available: ollama list")
    print("3. Test Ollama directly: ollama run mistral 'test'")
    print("\nFor more help, see PHASE2_GUIDE.md")
