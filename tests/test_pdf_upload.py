"""
Complete test: Upload PDF with images → Extract → Generate questions.

This simulates the full workflow a user would experience:
1. Upload a PDF
2. Extract diagrams and text
3. Generate diagram-based MCQs
4. Review and export questions

Usage:
    python3 test_pdf_upload.py path/to/your.pdf
"""

import sys
import json
from pathlib import Path
from src.extractors.pdf_extractor import extract_pdf, create_text_image_pairs
from src.generators.multimodal_generator import MultimodalMCQGenerator
from src.models.models import DifficultyLevel


def test_pdf_upload_workflow(pdf_path: str):
    """
    Simulate complete PDF upload and question generation workflow.

    Args:
        pdf_path: Path to PDF file
    """
    print("\n" + "="*80)
    print("PDF UPLOAD → QUESTION GENERATION WORKFLOW")
    print("="*80)

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"\n❌ Error: PDF not found: {pdf_path}")
        print("\nUsage: python3 test_pdf_upload.py path/to/your.pdf")
        return None

    print(f"\n📄 Processing: {pdf_path.name}")
    print(f"   Size: {pdf_path.stat().st_size / 1024:.1f} KB")

    # Step 1: Extract PDF
    print(f"\n{'─'*80}")
    print("STEP 1: EXTRACT PDF")
    print(f"{'─'*80}")

    try:
        # Extract first 5 pages (adjust as needed)
        pdf_doc = extract_pdf(str(pdf_path), pages=list(range(1, 6)))

        print(f"\n✅ Extraction complete!")
        print(f"   Pages: {pdf_doc.total_pages}")
        print(f"   Images: {pdf_doc.total_images}")
        print(f"   Pages with images: {len(pdf_doc.get_pages_with_images())}")

    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Step 2: Analyze content
    print(f"\n{'─'*80}")
    print("STEP 2: ANALYZE EXTRACTED CONTENT")
    print(f"{'─'*80}")

    for page in pdf_doc.pages[:3]:  # Show first 3 pages
        print(f"\n📄 Page {page.page_number}:")
        print(f"   Text: {len(page.text)} chars")
        print(f"   Has formulas: {'Yes' if page.has_formulas else 'No'}")
        print(f"   Diagrams: {len(page.images)}")

        if page.text:
            # Show first sentence
            first_sentence = page.text.split('.')[0][:100]
            print(f"   Preview: {first_sentence}...")

        # Show images
        for i, img in enumerate(page.images, 1):
            print(f"\n   📊 Image {i}:")
            print(f"      Size: {img.size/1024:.1f} KB")
            print(f"      Format: {img.format}")

            if img.caption:
                print(f"      Caption: {img.caption[:60]}...")
            else:
                print(f"      Caption: [Not detected]")

            # Save for review
            output_name = f"review_p{page.page_number}_img{i}.{img.format}"
            img.save(output_name)
            print(f"      💾 Saved: {output_name}")

    # Step 3: Create text-image pairs
    print(f"\n{'─'*80}")
    print("STEP 3: CREATE TEXT-IMAGE PAIRS")
    print(f"{'─'*80}")

    pairs = create_text_image_pairs(pdf_doc)

    print(f"\n✅ Created {len(pairs)} text-image pair(s)")

    if not pairs:
        print("\n⚠️  No suitable diagrams found for question generation")
        print("    PDF may not contain captioned diagrams")
        return None

    for i, pair in enumerate(pairs, 1):
        print(f"\n  Pair {i}:")
        print(f"    Source: Page {pair.page_number}")
        print(f"    Images: {len(pair.images)}")
        print(f"    Text: {len(pair.text)} chars")

        # Show text preview
        lines = pair.text.split('\n')[:3]
        for line in lines:
            if line.strip():
                print(f"    > {line.strip()[:60]}...")

    # Step 4: Generate questions
    print(f"\n{'─'*80}")
    print("STEP 4: GENERATE DIAGRAM-BASED MCQs")
    print(f"{'─'*80}")

    print(f"\n🤖 Using Mock VLM (for testing)")
    print("   (Replace with real VLM for production)\n")

    generator = MultimodalMCQGenerator(use_mock=True)

    all_questions = []

    # Generate from first 3 pairs
    for i, pair in enumerate(pairs[:3], 1):
        print(f"\n📝 Generating from Pair {i}...")

        try:
            questions = generator.generate_from_pair(
                pair=pair,
                subject="Physics",  # Adjust based on your PDF
                main_topic="Visual Analysis",
                subtopic="Diagram Interpretation",
                difficulty=DifficultyLevel.MEDIUM,
                n=2  # 2 questions per diagram
            )

            all_questions.extend(questions)
            print(f"   ✅ Generated {len(questions)} question(s)")

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue

    # Step 5: Review questions
    print(f"\n{'─'*80}")
    print("STEP 5: REVIEW GENERATED QUESTIONS")
    print(f"{'─'*80}")

    print(f"\n✅ Total questions: {len(all_questions)}")

    for i, q in enumerate(all_questions, 1):
        print(f"\n{'─'*60}")
        print(f"Question {i}/{len(all_questions)}")
        print(f"{'─'*60}")

        print(f"\n❓ {q.question_text_en}")

        print(f"\nOptions:")
        for label, text in q.get_options_dict().items():
            marker = "✓" if label == q.correct_answer else " "
            print(f"  [{marker}] {label}) {text}")

        print(f"\n✓ Correct: {q.correct_answer}")
        print(f"📚 Topic: {q.main_topic} → {q.subtopic}")
        print(f"🎯 Difficulty: {q.difficulty.value}")
        print(f"📄 Source: {q.source_pdf}")

        # Validation
        errors = q.validate()
        if errors:
            print(f"\n⚠️  Validation errors: {errors}")
        else:
            print(f"\n✅ Valid question")

    # Step 6: Export
    print(f"\n{'─'*80}")
    print("STEP 6: EXPORT QUESTIONS")
    print(f"{'─'*80}")

    # Export to JSON
    output_json = f"questions_{pdf_path.stem}.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump([q.to_dict() for q in all_questions], f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved to: {output_json}")
    print(f"   Questions: {len(all_questions)}")
    print(f"   File size: {Path(output_json).stat().st_size / 1024:.1f} KB")

    # Summary
    print(f"\n{'='*80}")
    print("✅ WORKFLOW COMPLETE!")
    print("="*80)

    print(f"\nProcessed:")
    print(f"  📄 PDF: {pdf_path.name}")
    print(f"  📊 Extracted: {pdf_doc.total_images} diagrams")
    print(f"  🔗 Created: {len(pairs)} text-image pairs")
    print(f"  ❓ Generated: {len(all_questions)} MCQs")

    print(f"\nOutputs:")
    print(f"  ✅ Questions: {output_json}")
    print(f"  ✅ Diagram images: review_p*_img*.* (in current directory)")

    print(f"\nNext steps:")
    print(f"  1. Review extracted diagrams (review_*.png files)")
    print(f"  2. Check questions in {output_json}")
    print(f"  3. Set up real VLM for production (see PHASE3_GUIDE.md)")
    print(f"  4. Adjust subject/topic/difficulty as needed")

    print("="*80 + "\n")

    return {
        'pdf': pdf_doc,
        'pairs': pairs,
        'questions': all_questions
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("\n" + "="*80)
        print("PDF UPLOAD TEST")
        print("="*80)
        print("\nUsage:")
        print("  python3 test_pdf_upload.py path/to/your.pdf")
        print("\nExample:")
        print("  python3 test_pdf_upload.py physics_chapter3.pdf")
        print("\nThis will:")
        print("  1. Extract diagrams and text from the PDF")
        print("  2. Create text-image pairs")
        print("  3. Generate diagram-based MCQs (mock VLM)")
        print("  4. Export questions to JSON")
        print("  5. Save extracted images for review")
        print("\n" + "="*80 + "\n")
        return

    pdf_path = sys.argv[1]
    test_pdf_upload_workflow(pdf_path)


if __name__ == "__main__":
    main()
