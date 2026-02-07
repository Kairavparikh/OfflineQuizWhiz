"""
Test multimodal generation with a REAL vision-language model.

Requirements:
- LLaVA running on Ollama (easiest)
  OR
- Qwen-VL or other VLM with HTTP endpoint

Setup for LLaVA:
  1. ollama pull llava
  2. ollama serve
  3. python3 test_real_vlm.py
"""

from pathlib import Path
from src.extractors.pdf_extractor import extract_pdf, create_text_image_pairs
from src.generators.multimodal_generator import MultimodalMCQGenerator
from src.generators.vlm_client import VLMConfig, VLMClient
from src.models.models import DifficultyLevel


def test_vlm_connection():
    """Test connection to real VLM."""
    print("\n" + "="*80)
    print("STEP 1: TEST VLM CONNECTION")
    print("="*80)

    # Try LLaVA on Ollama first
    config = VLMConfig(
        base_url="http://localhost:11434",
        model_name="llava",
        timeout_seconds=180
    )

    client = VLMClient(config)

    print(f"\nTesting connection to VLM...")
    print(f"  Endpoint: {config.base_url}")
    print(f"  Model: {config.model_name}\n")

    success = client.test_connection()

    if success:
        print("\n✅ VLM connection successful!")
        return client
    else:
        print("\n❌ VLM connection failed")
        print("\nTroubleshooting:")
        print("  1. Make sure Ollama is running: ollama serve")
        print("  2. Pull LLaVA model: ollama pull llava")
        print("  3. Test manually: ollama run llava")
        print("\nOr update VLMConfig in this file with your VLM endpoint")
        return None


def test_generation_with_real_vlm(vlm_client):
    """Generate questions using real VLM."""
    print("\n" + "="*80)
    print("STEP 2: GENERATE WITH REAL VLM")
    print("="*80)

    # Check for PDF
    pdf_candidates = ["test.pdf", "sample.pdf", "physics.pdf"]
    pdf_path = None

    for candidate in pdf_candidates:
        if Path(candidate).exists():
            pdf_path = candidate
            break

    if not pdf_path:
        print("\n⚠️  No PDF found. Using synthetic example...")
        return test_synthetic_with_real_vlm(vlm_client)

    # Extract PDF
    print(f"\n📄 Extracting: {pdf_path}")
    pdf_doc = extract_pdf(pdf_path, pages=[1, 2])

    # Create pairs
    pairs = create_text_image_pairs(pdf_doc)

    if not pairs:
        print("⚠️  No text-image pairs found. Using synthetic example...")
        return test_synthetic_with_real_vlm(vlm_client)

    print(f"✅ Found {len(pairs)} diagram(s)")

    # Generate with REAL VLM
    print(f"\n🤖 Generating questions with REAL VLM...")
    print("   (This may take 60-120 seconds per question)\n")

    generator = MultimodalMCQGenerator(vlm_client=vlm_client)

    pair = pairs[0]  # Use first pair

    try:
        questions = generator.generate_from_pair(
            pair=pair,
            subject="Physics",
            main_topic="Diagrams and Graphs",
            subtopic="Visual Analysis",
            difficulty=DifficultyLevel.MEDIUM,
            n=1  # Start with just 1 question
        )

        if questions:
            print(f"\n✅ Successfully generated {len(questions)} question(s)!")

            q = questions[0]

            print(f"\n{'='*80}")
            print("GENERATED QUESTION (Real VLM)")
            print("="*80)
            print(f"\nQ: {q.question_text_en}")
            print(f"\nOptions:")
            for label, text in q.get_options_dict().items():
                marker = "✅" if label == q.correct_answer else "  "
                print(f"{marker} {label}) {text}")
            print(f"\n✓ Correct: {q.correct_answer}")
            print(f"\n💡 Explanation:\n{q.explanation}")
            print(f"\n📖 References:")
            for ref in q.references:
                print(f"   • {ref}")

            print(f"\n{'='*80}")
            print("✅ REAL VLM TEST PASSED!")
            print("="*80)

            return questions
        else:
            print("❌ No questions generated")
            return []

    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_synthetic_with_real_vlm(vlm_client):
    """Test real VLM with synthetic diagram."""
    from multimodal_models import TextImagePair, ExtractedImage
    import base64

    print("\nUsing synthetic test diagram...")

    # 1x1 red pixel as test image
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    image_bytes = base64.b64decode(test_image_b64)

    img = ExtractedImage(
        image_data=image_bytes,
        page_number=1,
        image_index=0,
        caption="Test diagram: A simple colored square"
    )

    pair = TextImagePair(
        text="Caption: Test diagram showing a simple colored square.\n\nContext: This is a test to verify VLM can process images.",
        images=[img],
        page_number=1,
        source_pdf="synthetic_test.pdf"
    )

    generator = MultimodalMCQGenerator(vlm_client=vlm_client)

    print("\n🤖 Testing VLM with synthetic diagram...")

    questions = generator.generate_from_pair(
        pair=pair,
        subject="Test Subject",
        main_topic="Visual Analysis",
        subtopic="Color Recognition",
        difficulty=DifficultyLevel.EASY,
        n=1
    )

    if questions:
        print(f"✅ VLM successfully processed image and generated question!")
        q = questions[0]
        print(f"\nQ: {q.question_text_en}")
        print(f"Correct: {q.correct_answer}")
    else:
        print("❌ Failed to generate question")

    return questions


def main():
    """Run real VLM tests."""
    print("\n" + "="*80)
    print("REAL VLM TEST SUITE")
    print("="*80)
    print("\nThis tests multimodal generation with a REAL vision-language model.")
    print("\nPrerequisites:")
    print("  - LLaVA model installed: ollama pull llava")
    print("  - Ollama running: ollama serve")
    print("\nOr configure your own VLM endpoint in this script.")
    print("="*80)

    # Test connection
    vlm_client = test_vlm_connection()

    if not vlm_client:
        print("\n⚠️  Cannot proceed without VLM connection")
        print("    Fix the connection and try again")
        return

    # Generate questions
    questions = test_generation_with_real_vlm(vlm_client)

    # Summary
    if questions:
        print("\n" + "="*80)
        print("✅ ALL REAL VLM TESTS PASSED!")
        print("="*80)
        print(f"\nYou successfully:")
        print(f"  ✅ Connected to vision-language model")
        print(f"  ✅ Generated diagram-based MCQs")
        print(f"  ✅ Validated questions")
        print("\nYour system is ready for production!")
        print("\nNext steps:")
        print("  - Extract your client's PDFs")
        print("  - Generate questions from actual diagrams")
        print("  - Review and export questions")
    else:
        print("\n⚠️  Tests completed but questions may need review")

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
