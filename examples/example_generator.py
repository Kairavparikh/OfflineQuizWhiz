"""
Example usage of the MCQ generator.

Demonstrates:
1. Testing LLM connection
2. Generating questions at different difficulty levels
3. Saving questions to JSON
4. Error handling
"""

import json
from pathlib import Path
from src.models.models import DifficultyLevel, Question
from src.generators.mcq_generator import MCQGenerator, generate_mcqs
from src.generators.llm_client import create_llm_client, test_llm_endpoint
from src.config import LLMConfig


def example_1_test_connection():
    """Test connection to local LLM."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Test LLM Connection")
    print("="*80)

    # Test default endpoint (Ollama on localhost:11434)
    success = test_llm_endpoint(
        base_url="http://localhost:11434",
        model="llama2"
    )

    if not success:
        print("\n⚠️  LLM connection failed. Make sure:")
        print("   1. Ollama is running: ollama serve")
        print("   2. Model is pulled: ollama pull llama2")
        print("   3. Endpoint is correct (default: http://localhost:11434)")
        print("\n   Or update config.py with your LLM endpoint details")
        return False

    return True


def example_2_generate_single_question():
    """Generate a single Easy question."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Generate Single Easy Question")
    print("="*80)

    try:
        questions = generate_mcqs(
            subject="Metallurgical Engineering",
            main_topic="Engineering Mathematics",
            subtopic="Linear Algebra - Matrices and Determinants",
            difficulty=DifficultyLevel.EASY,
            n=1
        )

        if questions:
            question = questions[0]
            print_question(question)
            return questions
        else:
            print("❌ No questions generated")
            return []

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def example_3_generate_multiple_difficulties():
    """Generate questions at different difficulty levels."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Generate Questions at Multiple Difficulty Levels")
    print("="*80)

    all_questions = []

    for difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
        print(f"\n--- Generating {difficulty.value} question ---")

        try:
            questions = generate_mcqs(
                subject="Metallurgical Engineering",
                main_topic="Material Science",
                subtopic="Crystal Structure - Crystal Systems",
                difficulty=difficulty,
                n=1
            )

            if questions:
                all_questions.extend(questions)
                print(f"✅ Generated {len(questions)} {difficulty.value} question(s)")
            else:
                print(f"⚠️  No {difficulty.value} questions generated")

        except Exception as e:
            print(f"❌ Failed to generate {difficulty.value} question: {e}")

    return all_questions


def example_4_generate_batch():
    """Generate multiple questions in one call."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Generate Batch of Questions")
    print("="*80)

    try:
        questions = generate_mcqs(
            subject="Metallurgical Engineering",
            main_topic="Engineering Mathematics",
            subtopic="Calculus - Differentiation",
            difficulty=DifficultyLevel.MEDIUM,
            n=3
        )

        print(f"\n✅ Generated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"\n{i}. {q.question_text_en}")
            print(f"   Correct: {q.correct_answer}")

        return questions

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def example_5_save_to_json():
    """Generate questions and save to JSON."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Save Generated Questions to JSON")
    print("="*80)

    try:
        # Generate a few questions
        questions = generate_mcqs(
            subject="Metallurgical Engineering",
            main_topic="Physics",
            subtopic="Thermodynamics - Laws of Thermodynamics",
            difficulty=DifficultyLevel.MEDIUM,
            n=2
        )

        if not questions:
            print("⚠️  No questions to save")
            return

        # Convert to JSON
        questions_data = [q.to_dict() for q in questions]

        # Save to file
        output_file = "generated_questions.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved {len(questions)} question(s) to {output_file}")
        print(f"   File size: {Path(output_file).stat().st_size} bytes")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_6_custom_llm_config():
    """Use custom LLM configuration."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Custom LLM Configuration")
    print("="*80)

    # Create custom config
    custom_config = LLMConfig(
        base_url="http://localhost:11434",  # Your LLM endpoint
        model_name="llama2",  # Your model
        temperature=0.8,  # Higher = more creative
        max_tokens=3000,
        timeout_seconds=180
    )

    # Create client with custom config
    llm_client = create_llm_client(
        base_url=custom_config.base_url,
        model_name=custom_config.model_name
    )

    # Create generator
    generator = MCQGenerator(llm_client=llm_client)

    # Generate
    try:
        questions = generator.generate_mcqs(
            subject="Metallurgical Engineering",
            main_topic="Material Science",
            subtopic="Phase Diagrams - Binary Phase Diagrams",
            difficulty=DifficultyLevel.HARD,
            n=1
        )

        if questions:
            print(f"\n✅ Generated with custom config:")
            print_question(questions[0])

    except Exception as e:
        print(f"❌ Error: {e}")


def print_question(question: Question):
    """Pretty-print a question."""
    print("\n" + "-"*80)
    print(f"ID: {question.question_id}")
    print(f"Topic: {question.main_topic} → {question.subtopic}")
    print(f"Difficulty: {question.difficulty.value}")
    print(f"\nQuestion: {question.question_text_en}")
    print(f"\nOptions:")

    for label, text in question.get_options_dict().items():
        marker = "✓" if label == question.correct_answer else " "
        print(f"  [{marker}] {label}. {text}")

    print(f"\nCorrect Answer: {question.correct_answer}")
    print(f"\nExplanation:\n{question.explanation}")

    if question.references:
        print(f"\nReferences:")
        for ref in question.references:
            print(f"  • {ref}")

    print("-"*80)


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("MCQ GENERATOR - EXAMPLE USAGE")
    print("="*80)
    print("\nPrerequisites:")
    print("  1. Install Ollama: https://ollama.ai")
    print("  2. Pull a model: ollama pull llama2")
    print("  3. Start Ollama: ollama serve")
    print("="*80)

    # Example 1: Test connection
    if not example_1_test_connection():
        print("\n⚠️  Skipping other examples due to connection failure")
        print("    Fix the connection and try again")
        return

    # Example 2: Single question
    # example_2_generate_single_question()

    # Example 3: Multiple difficulties
    # example_3_generate_multiple_difficulties()

    # Example 4: Batch generation
    # example_4_generate_batch()

    # Example 5: Save to JSON
    # example_5_save_to_json()

    # Example 6: Custom config
    # example_6_custom_llm_config()

    print("\n" + "="*80)
    print("✅ Examples completed!")
    print("="*80)
    print("\n💡 Next steps:")
    print("   1. Uncomment the example you want to run in main()")
    print("   2. Adjust LLM settings in config.py if needed")
    print("   3. Start generating questions!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
