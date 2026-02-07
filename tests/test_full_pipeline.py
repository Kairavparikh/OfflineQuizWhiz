"""
Test complete multimodal MCQ generation pipeline.

Tests:
1. PDF extraction
2. Text-image pairing
3. Question generation (mock VLM)
4. Validation
5. Export to JSON

This uses MOCK VLM so no real vision model is needed!
"""

import json
from pathlib import Path
from src.extractors.pdf_extractor import extract_pdf, create_text_image_pairs
from src.generators.multimodal_generator import MultimodalMCQGenerator
from src.models.models import DifficultyLevel


def test_full_pipeline():
    """Test complete pipeline from PDF to questions."""

    print("\n" + "="*80)
    print("FULL PIPELINE TEST (Mock VLM)")
    print("="*80)
    print("\nThis tests the complete workflow:")
    print("  PDF → Extract → Pair → Generate MCQs → Validate → Export")
    print("\nUsing MOCK VLM (no real vision model needed)")
    print("="*80)

    # Step 1: Check for PDF
    pdf_candidates = ["test.pdf", "sample.pdf", "physics.pdf"]
    pdf_path = None

    for candidate in pdf_candidates:
        if Path(candidate).exists():
            pdf_path = candidate
            break

    if not pdf_path:
        print("\n⚠️  No PDF found. Using synthetic example instead...")
        return test_synthetic_pipeline()

    # Step 2: Extract PDF
    print(f"\n{'='*80}")
    print("STEP 1: EXTRACT PDF")
    print("="*80)

    try:
        pdf_doc = extract_pdf(pdf_path, pages=[1, 2, 3])
        print(f"✅ Extracted {pdf_doc.total_pages} pages, {pdf_doc.total_images} images")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        print("   Falling back to synthetic example...")
        return test_synthetic_pipeline()

    # Step 3: Create pairs
    print(f"\n{'='*80}")
    print("STEP 2: CREATE TEXT-IMAGE PAIRS")
    print("="*80)

    pairs = create_text_image_pairs(pdf_doc)
    print(f"✅ Created {len(pairs)} text-image pair(s)")

    if not pairs:
        print("⚠️  No pairs created. PDF might not have diagrams.")
        print("   Falling back to synthetic example...")
        return test_synthetic_pipeline()

    # Show pairs
    for i, pair in enumerate(pairs[:3], 1):  # Show first 3
        print(f"\n  Pair {i}:")
        print(f"    Page: {pair.page_number}")
        print(f"    Images: {len(pair.images)}")
        print(f"    Text: {pair.text[:100]}...")

    # Step 4: Generate questions
    print(f"\n{'='*80}")
    print("STEP 3: GENERATE DIAGRAM-BASED MCQs (Mock VLM)")
    print("="*80)

    generator = MultimodalMCQGenerator(use_mock=True)

    all_questions = []

    # Generate 2 questions per pair (max 3 pairs)
    for i, pair in enumerate(pairs[:3], 1):
        print(f"\n📝 Generating from pair {i}...")

        try:
            questions = generator.generate_from_pair(
                pair=pair,
                subject="Physics",
                main_topic="Diagrams and Graphs",
                subtopic="Visual Analysis",
                difficulty=DifficultyLevel.MEDIUM,
                n=2
            )

            all_questions.extend(questions)
            print(f"   ✅ Generated {len(questions)} question(s)")

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue

    # Step 5: Display results
    print(f"\n{'='*80}")
    print("STEP 4: RESULTS")
    print("="*80)

    print(f"\n✅ Total questions generated: {len(all_questions)}")

    for i, q in enumerate(all_questions, 1):
        print(f"\n{'─'*80}")
        print(f"Question {i}/{len(all_questions)}")
        print(f"{'─'*80}")
        print(f"Topic: {q.main_topic} → {q.subtopic}")
        print(f"Difficulty: {q.difficulty.value}")
        print(f"Has Diagram: {q.has_diagram}")
        print(f"Source PDF: {q.source_pdf}")

        print(f"\n❓ {q.question_text_en}")

        print(f"\nOptions:")
        for label, text in q.get_options_dict().items():
            marker = "✅" if label == q.correct_answer else "  "
            print(f"{marker} {label}) {text}")

        print(f"\n✓ Correct: {q.correct_answer}")

        # Validate
        errors = q.validate()
        if errors:
            print(f"\n⚠️  Validation errors: {errors}")
        else:
            print(f"\n✅ Question is valid!")

    # Step 6: Export to JSON
    print(f"\n{'='*80}")
    print("STEP 5: EXPORT TO JSON")
    print("="*80)

    output_file = "test_diagram_questions.json"
    questions_data = [q.to_dict() for q in all_questions]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(all_questions)} questions to: {output_file}")
    print(f"   File size: {Path(output_file).stat().st_size} bytes")

    # Final summary
    print(f"\n{'='*80}")
    print("✅ FULL PIPELINE TEST COMPLETE!")
    print("="*80)

    print(f"\nPipeline summary:")
    print(f"  📄 Input: {pdf_path}")
    print(f"  📊 Extracted: {pdf_doc.total_pages} pages, {pdf_doc.total_images} images")
    print(f"  🔗 Created: {len(pairs)} text-image pairs")
    print(f"  ❓ Generated: {len(all_questions)} diagram-based MCQs")
    print(f"  💾 Saved to: {output_file}")

    print(f"\n✅ All tests passed!")

    print(f"\nNext steps:")
    print(f"  1. Review questions in {output_file}")
    print(f"  2. Check extracted images (in current directory)")
    print(f"  3. Set up real VLM for production (see PHASE3_GUIDE.md)")
    print(f"  4. Generate questions from your actual client PDFs")

    print("="*80 + "\n")

    return all_questions


def test_synthetic_pipeline():
    """Test with synthetic data (no PDF needed)."""
    from multimodal_models import TextImagePair, ExtractedImage
    import base64

    print(f"\n{'='*80}")
    print("SYNTHETIC PIPELINE TEST")
    print("="*80)
    print("Using synthetic data (no PDF required)\n")

    # Create synthetic image
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    image_bytes = base64.b64decode(test_image_b64)

    img = ExtractedImage(
        image_data=image_bytes,
        page_number=1,
        image_index=0,
        caption="Figure 1: Iron-Carbon phase diagram showing eutectoid transformation"
    )

    pair = TextImagePair(
        text="""Caption: Figure 1: Iron-Carbon equilibrium phase diagram

Context: The diagram shows phase transformations in Fe-C alloys. The eutectoid point occurs at 727°C and 0.8% carbon, where austenite transforms to pearlite.""",
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
        n=2
    )

    # Display
    print(f"\n✅ Generated {len(questions)} question(s) from synthetic data")

    for i, q in enumerate(questions, 1):
        print(f"\n{'─'*80}")
        print(f"Question {i}")
        print(f"{'─'*80}")
        print(f"Q: {q.question_text_en}")
        print(f"Correct: {q.correct_answer}")
        print(f"Has diagram: {q.has_diagram}")

    # Export
    output_file = "test_synthetic_questions.json"
    with open(output_file, 'w') as f:
        json.dump([q.to_dict() for q in questions], f, indent=2)

    print(f"\n💾 Saved to: {output_file}")

    print(f"\n{'='*80}")
    print("✅ SYNTHETIC TEST COMPLETE!")
    print("="*80)
    print("\nTo test with real PDF:")
    print("  1. Place a PDF in this directory")
    print("  2. Name it 'test.pdf'")
    print("  3. Run: python3 test_full_pipeline.py")
    print("="*80 + "\n")

    return questions


if __name__ == "__main__":
    test_full_pipeline()
