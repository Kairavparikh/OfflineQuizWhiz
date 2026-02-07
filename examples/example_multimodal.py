"""
Example usage of multimodal MCQ generation (PDF + diagrams).

Demonstrates:
1. Extracting PDFs (text + images)
2. Creating text-image pairs
3. Generating diagram-based MCQs (with mock VLM)
4. Full pipeline from PDF to questions
"""

from pathlib import Path
from src.models.models import DifficultyLevel
from src.extractors.pdf_extractor import extract_pdf, create_text_image_pairs
from src.generators.multimodal_generator import MultimodalMCQGenerator


def example_1_extract_pdf():
    """Example: Extract text and images from a PDF."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Extract PDF")
    print("="*80)

    pdf_path = "sample_physics.pdf"  # Replace with your PDF

    if not Path(pdf_path).exists():
        print(f"\n⚠️  PDF not found: {pdf_path}")
        print("📝 To use this example:")
        print("   1. Place a physics/engineering PDF in the current directory")
        print("   2. Update 'pdf_path' variable in this script")
        print("   3. Run again")
        return None

    try:
        # Extract PDF
        pdf_doc = extract_pdf(pdf_path, pages=[1, 2, 3])  # First 3 pages

        # Summary
        print(f"\n📊 Extraction Summary:")
        print(f"   Total pages: {pdf_doc.total_pages}")
        print(f"   Total images: {pdf_doc.total_images}")

        # Show pages with images
        pages_with_imgs = pdf_doc.get_pages_with_images()
        print(f"\n📄 Pages with images: {len(pages_with_imgs)}")

        for page in pages_with_imgs:
            print(f"\n  Page {page.page_number}:")
            print(f"    Text: {len(page.text)} chars")
            print(f"    Images: {len(page.images)}")
            for img in page.images:
                print(f"      - {img}")

        return pdf_doc

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def example_2_create_pairs():
    """Example: Create text-image pairs."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Create Text-Image Pairs")
    print("="*80)

    # First extract PDF
    pdf_path = "sample_physics.pdf"

    if not Path(pdf_path).exists():
        print(f"\n⚠️  PDF not found: {pdf_path}")
        print("   Skipping this example.")
        return []

    try:
        pdf_doc = extract_pdf(pdf_path, pages=[1, 2])

        # Create pairs
        pairs = create_text_image_pairs(pdf_doc)

        print(f"\n📋 Created {len(pairs)} text-image pair(s):")
        for i, pair in enumerate(pairs, 1):
            print(f"\n  Pair {i}:")
            print(f"    Page: {pair.page_number}")
            print(f"    Text length: {len(pair.text)} chars")
            print(f"    Images: {len(pair.images)}")
            print(f"    Text preview: {pair.text[:150]}...")

        return pairs

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return []


def example_3_generate_with_mock():
    """Example: Generate MCQs using mock VLM (no real VLM needed)."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Generate MCQs with Mock VLM")
    print("="*80)
    print("This example uses a mock VLM so you can test without a real vision model.\n")

    pdf_path = "sample_physics.pdf"

    if not Path(pdf_path).exists():
        print(f"\n⚠️  PDF not found: {pdf_path}")
        print("   Using synthetic example instead...")
        return example_3b_synthetic_pair()

    try:
        # Extract and create pairs
        pdf_doc = extract_pdf(pdf_path, pages=[1])
        pairs = create_text_image_pairs(pdf_doc)

        if not pairs:
            print("⚠️  No text-image pairs found")
            return []

        # Use first pair
        pair = pairs[0]

        print(f"\n📝 Using pair from page {pair.page_number}")
        print(f"   Text: {len(pair.text)} chars")
        print(f"   Images: {len(pair.images)}")

        # Generate with mock VLM
        generator = MultimodalMCQGenerator(use_mock=True)

        questions = generator.generate_from_pair(
            pair=pair,
            subject="Physics",
            main_topic="Mechanics",
            subtopic="Free Body Diagrams",
            difficulty=DifficultyLevel.MEDIUM,
            n=1
        )

        if questions:
            print_question(questions[0])

        return questions

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def example_3b_synthetic_pair():
    """Generate with a synthetic text-image pair (for testing)."""
    from multimodal_models import TextImagePair, ExtractedImage
    import base64

    print("\nUsing synthetic test data...\n")

    # Create a minimal test image (1x1 pixel)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    image_bytes = base64.b64decode(test_image_b64)

    # Create ExtractedImage
    img = ExtractedImage(
        image_data=image_bytes,
        page_number=1,
        image_index=0,
        caption="Figure 1: Iron-Carbon phase diagram"
    )

    # Create TextImagePair
    pair = TextImagePair(
        text="""Caption: Figure 1: Iron-Carbon equilibrium phase diagram showing phase transformations.

Context: The diagram shows the equilibrium phases present in iron-carbon alloys at different temperatures and compositions. The eutectoid point occurs at 727°C and 0.8% carbon, where austenite transforms to pearlite.""",
        images=[img],
        page_number=1,
        source_pdf="synthetic_example.pdf"
    )

    # Generate
    generator = MultimodalMCQGenerator(use_mock=True)

    questions = generator.generate_from_pair(
        pair=pair,
        subject="Metallurgical Engineering",
        main_topic="Material Science",
        subtopic="Phase Diagrams",
        difficulty=DifficultyLevel.MEDIUM,
        n=1
    )

    if questions:
        print_question(questions[0])

    return questions


def print_question(question):
    """Pretty-print a question."""
    print("\n" + "-"*80)
    print(f"ID: {question.question_id}")
    print(f"Topic: {question.main_topic} → {question.subtopic}")
    print(f"Difficulty: {question.difficulty.value}")
    print(f"Has Diagram: {question.has_diagram}")
    if question.source_pdf:
        print(f"Source PDF: {question.source_pdf}")

    print(f"\n❓ QUESTION:")
    print(f"{question.question_text_en}")

    print(f"\n📋 OPTIONS:")
    for label, text in question.get_options_dict().items():
        marker = "✅" if label == question.correct_answer else "  "
        print(f"{marker} {label}) {text}")

    print(f"\n✓ CORRECT ANSWER: {question.correct_answer}")

    print(f"\n💡 EXPLANATION:")
    print(f"{question.explanation}")

    if question.references:
        print(f"\n📖 REFERENCES:")
        for ref in question.references:
            print(f"   • {ref}")

    print("-"*80)


def main():
    """Run examples."""
    print("\n" + "="*80)
    print("MULTIMODAL MCQ GENERATOR - EXAMPLES")
    print("="*80)
    print("\nPhase 3: Diagram-based question generation")
    print("="*80)

    # Example 1: Extract PDF
    # pdf_doc = example_1_extract_pdf()

    # Example 2: Create pairs
    # pairs = example_2_create_pairs()

    # Example 3: Generate with mock VLM (works without real VLM)
    example_3_generate_with_mock()

    print("\n" + "="*80)
    print("✅ Examples completed!")
    print("="*80)
    print("\n💡 Next steps:")
    print("   - Install PyMuPDF: pip install PyMuPDF")
    print("   - Place a physics/engineering PDF in this directory")
    print("   - Run: python3 example_multimodal.py")
    print("   - For real VLM: Set up Qwen-VL or LLaVA locally")
    print("   - See PHASE3_GUIDE.md for complete setup")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
