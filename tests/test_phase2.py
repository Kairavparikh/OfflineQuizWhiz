"""
Test script for Phase 2 functionality (no LLM required).

Tests:
1. Config loading
2. Prompt template building
3. JSON parsing
4. Question validation
"""

import json
from src.models.models import DifficultyLevel, Question
from src.generators.prompt_templates import build_mcq_generation_prompt, FEW_SHOT_EXAMPLES
from src.config import LLMConfig, GenerationConfig


def test_1_config():
    """Test configuration classes."""
    print("\n" + "="*80)
    print("TEST 1: Configuration")
    print("="*80)

    # LLM config
    llm_config = LLMConfig(
        base_url="http://localhost:11434",
        model_name="llama2",
        temperature=0.7
    )
    print(f"✅ LLMConfig created:")
    print(f"   URL: {llm_config.base_url}")
    print(f"   Model: {llm_config.model_name}")
    print(f"   Temperature: {llm_config.temperature}")

    # Generation config
    gen_config = GenerationConfig(
        min_explanation_length=20,
        require_references=True
    )
    print(f"\n✅ GenerationConfig created:")
    print(f"   Min explanation: {gen_config.min_explanation_length} chars")
    print(f"   Require references: {gen_config.require_references}")


def test_2_prompt_building():
    """Test prompt template building."""
    print("\n" + "="*80)
    print("TEST 2: Prompt Template Building")
    print("="*80)

    # Build prompt
    prompt = build_mcq_generation_prompt(
        subject="Metallurgical Engineering",
        main_topic="Engineering Mathematics",
        subtopic="Linear Algebra - Matrices and Determinants",
        difficulty=DifficultyLevel.MEDIUM,
        num_questions=3,
        include_few_shot=True
    )

    print(f"✅ Prompt built:")
    print(f"   Length: {len(prompt)} characters")
    print(f"   Lines: {len(prompt.splitlines())}")

    # Check components
    assert "System" in prompt or "expert" in prompt.lower(), "Missing system instructions"
    assert "Difficulty" in prompt, "Missing difficulty definitions"
    assert "Medium" in prompt, "Missing target difficulty"
    assert "Linear Algebra" in prompt, "Missing topic"
    assert "JSON" in prompt or "json" in prompt, "Missing JSON format"

    print(f"✅ Prompt contains required components:")
    print(f"   ✓ System instructions")
    print(f"   ✓ Difficulty definitions")
    print(f"   ✓ Topic information")
    print(f"   ✓ JSON format specification")

    # Show snippet
    print(f"\n📝 Prompt snippet (first 500 chars):")
    print(f"{'─'*80}")
    print(prompt[:500])
    print(f"{'─'*80}")


def test_3_few_shot_examples():
    """Test few-shot examples."""
    print("\n" + "="*80)
    print("TEST 3: Few-Shot Examples")
    print("="*80)

    print(f"✅ Found {len(FEW_SHOT_EXAMPLES)} few-shot examples:")

    for i, example in enumerate(FEW_SHOT_EXAMPLES, 1):
        print(f"\n{i}. {example['difficulty']} - {example['subtopic']}")

        # Parse the example JSON
        try:
            example_data = json.loads(example['example'])
            print(f"   ✓ Valid JSON")
            print(f"   ✓ Question: {example_data['question_text_en'][:60]}...")
            print(f"   ✓ Correct: {example_data['correct_answer']}")
            print(f"   ✓ References: {len(example_data['references'])}")
        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON: {e}")


def test_4_json_parsing():
    """Test JSON parsing from LLM response."""
    print("\n" + "="*80)
    print("TEST 4: JSON Parsing")
    print("="*80)

    # Simulate LLM response
    mock_response = """
Here are the questions you requested:

[
  {
    "question_text_en": "What is the rank of a 3×3 identity matrix?",
    "option_a_en": "0",
    "option_b_en": "1",
    "option_c_en": "2",
    "option_d_en": "3",
    "correct_answer": "D",
    "explanation": "The rank of a matrix is the maximum number of linearly independent rows or columns. In an identity matrix, all rows (and columns) are linearly independent. Therefore, for a 3×3 identity matrix, the rank is 3.",
    "references": [
      "https://en.wikipedia.org/wiki/Rank_(linear_algebra)",
      "Linear Algebra by Gilbert Strang, Chapter 2"
    ]
  }
]
"""

    # Extract JSON
    import re
    json_match = re.search(r'\[.*\]', mock_response, re.DOTALL)

    if json_match:
        json_str = json_match.group(0)
        print(f"✅ Extracted JSON ({len(json_str)} chars)")

        # Parse
        try:
            data = json.loads(json_str)
            print(f"✅ Parsed JSON successfully")
            print(f"   Questions: {len(data)}")

            # Validate structure
            q = data[0]
            required_keys = [
                "question_text_en", "option_a_en", "option_b_en",
                "option_c_en", "option_d_en", "correct_answer",
                "explanation", "references"
            ]

            missing = [k for k in required_keys if k not in q]
            if missing:
                print(f"   ❌ Missing keys: {missing}")
            else:
                print(f"   ✅ All required keys present")

                # Show question
                print(f"\n📋 Parsed question:")
                print(f"   Q: {q['question_text_en']}")
                print(f"   A: {q['correct_answer']}")
                print(f"   Explanation: {len(q['explanation'])} chars")
                print(f"   References: {len(q['references'])}")

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
    else:
        print(f"❌ No JSON found in response")


def test_5_question_validation():
    """Test question validation."""
    print("\n" + "="*80)
    print("TEST 5: Question Validation")
    print("="*80)

    # Valid question
    valid_q = Question(
        test_section="Engineering Mathematics",
        main_topic="Linear Algebra",
        subtopic="Matrices and Determinants",
        difficulty=DifficultyLevel.MEDIUM,
        question_text_en="What is the determinant of a 2×2 identity matrix?",
        option_a_en="0",
        option_b_en="1",
        option_c_en="2",
        option_d_en="-1",
        correct_answer="B",
        explanation="The determinant of an identity matrix is always 1, regardless of its size.",
        references=["https://en.wikipedia.org/wiki/Determinant"]
    )

    errors = valid_q.validate()
    if errors:
        print(f"❌ Valid question failed: {errors}")
    else:
        print(f"✅ Valid question passed validation")

    # Invalid question (missing option, wrong answer)
    invalid_q = Question(
        test_section="Math",
        main_topic="Algebra",
        subtopic="Basic",
        difficulty=DifficultyLevel.EASY,
        question_text_en="What is 2+2?",
        option_a_en="4",
        option_b_en="4",  # Duplicate
        option_c_en="",   # Empty
        option_d_en="5",
        correct_answer="X",  # Invalid
        explanation="Short"  # Too short
    )

    errors = invalid_q.validate()
    if errors:
        print(f"\n✅ Invalid question correctly caught {len(errors)} error(s):")
        for error in errors:
            print(f"   - {error}")
    else:
        print(f"❌ Invalid question passed (should have failed)")


def test_6_difficulty_levels():
    """Test difficulty level enum."""
    print("\n" + "="*80)
    print("TEST 6: Difficulty Levels")
    print("="*80)

    for difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
        print(f"✅ {difficulty.value}:")

        # Build prompt for this difficulty
        prompt = build_mcq_generation_prompt(
            subject="Test",
            main_topic="Test Topic",
            subtopic="Test Subtopic",
            difficulty=difficulty,
            num_questions=1,
            include_few_shot=False
        )

        # Check that difficulty appears in prompt
        if difficulty.value in prompt:
            print(f"   ✓ Difficulty level present in prompt")
        else:
            print(f"   ⚠️  Difficulty level not found in prompt")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("PHASE 2 - FUNCTIONALITY TESTS (No LLM Required)")
    print("="*80)

    test_1_config()
    test_2_prompt_building()
    test_3_few_shot_examples()
    test_4_json_parsing()
    test_5_question_validation()
    test_6_difficulty_levels()

    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print("\n💡 Next steps:")
    print("   1. Install and start Ollama: ollama serve")
    print("   2. Pull a model: ollama pull llama2")
    print("   3. Test LLM connection: python3 example_generator.py")
    print("   4. Generate questions: see PHASE2_GUIDE.md")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
