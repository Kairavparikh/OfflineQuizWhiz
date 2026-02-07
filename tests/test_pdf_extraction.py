"""
Test PDF extraction capabilities.
"""

import sys
from pathlib import Path
from src.extractors.pdf_extractor import extract_pdf, create_text_image_pairs

def test_extraction():
    """Test extracting a PDF."""

    # Try to find a PDF
    pdf_candidates = [
        "test.pdf",
        "sample.pdf",
        "physics.pdf",
        "materials.pdf"
    ]

    pdf_path = None
    for candidate in pdf_candidates:
        if Path(candidate).exists():
            pdf_path = candidate
            break

    if not pdf_path:
        print("\n" + "="*80)
        print("NO PDF FOUND")
        print("="*80)
        print("\nTo test PDF extraction:")
        print("  1. Place any PDF file in this directory")
        print("  2. Name it 'test.pdf' (or update this script)")
        print("  3. Run: python3 test_pdf_extraction.py")
        print("\nOr provide path as argument:")
        print("  python3 test_pdf_extraction.py path/to/your.pdf")
        print("="*80 + "\n")
        return

    print("\n" + "="*80)
    print(f"TESTING PDF EXTRACTION: {pdf_path}")
    print("="*80)

    try:
        # Extract first 3 pages
        print(f"\n📄 Extracting first 3 pages...")
        pdf_doc = extract_pdf(pdf_path, pages=[1, 2, 3])

        # Summary
        print(f"\n" + "="*80)
        print("EXTRACTION SUMMARY")
        print("="*80)
        print(f"✅ Total pages extracted: {pdf_doc.total_pages}")
        print(f"✅ Total images found: {pdf_doc.total_images}")
        print(f"✅ Pages with images: {len(pdf_doc.get_pages_with_images())}")

        # Detailed view
        print(f"\n" + "="*80)
        print("DETAILED PAGE-BY-PAGE")
        print("="*80)

        for page in pdf_doc.pages:
            print(f"\n📄 Page {page.page_number}:")
            print(f"   Text length: {len(page.text)} chars")
            print(f"   Has formulas: {page.has_formulas}")
            print(f"   Has diagrams: {page.has_diagrams}")
            print(f"   Images: {len(page.images)}")

            if page.text:
                preview = page.text[:200].replace('\n', ' ')
                print(f"   Text preview: {preview}...")

            for i, img in enumerate(page.images, 1):
                print(f"\n   Image {i}:")
                print(f"      Size: {img.size} bytes ({img.size/1024:.1f} KB)")
                print(f"      Format: {img.format}")
                if img.caption:
                    print(f"      Caption: {img.caption[:80]}...")
                if img.nearby_text:
                    preview = img.nearby_text[:100].replace('\n', ' ')
                    print(f"      Context: {preview}...")

                # Save image for inspection
                img.save(f"extracted_page{page.page_number}_img{i}.{img.format}")
                print(f"      💾 Saved as: extracted_page{page.page_number}_img{i}.{img.format}")

        # Test pairing
        print(f"\n" + "="*80)
        print("TEXT-IMAGE PAIRING")
        print("="*80)

        pairs = create_text_image_pairs(pdf_doc)

        print(f"\n📋 Created {len(pairs)} text-image pair(s)")

        for i, pair in enumerate(pairs, 1):
            print(f"\n  Pair {i}:")
            print(f"     Page: {pair.page_number}")
            print(f"     Images: {len(pair.images)}")
            print(f"     Text length: {len(pair.text)} chars")
            print(f"     Source: {pair.source_pdf}")

            # Show text preview
            text_preview = pair.text[:150].replace('\n', ' ')
            print(f"     Text: {text_preview}...")

        # Test success
        print(f"\n" + "="*80)
        print("✅ PDF EXTRACTION TEST PASSED!")
        print("="*80)
        print(f"\nExtracted content:")
        print(f"  - {pdf_doc.total_pages} pages")
        print(f"  - {pdf_doc.total_images} images")
        print(f"  - {len(pairs)} text-image pairs ready for question generation")

        print(f"\nNext steps:")
        print(f"  1. Check extracted images (saved in current directory)")
        print(f"  2. Review text-image pairs above")
        print(f"  3. Run: python3 test_full_pipeline.py")
        print("="*80 + "\n")

        return pdf_doc, pairs

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    # Check for PDF path argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if Path(pdf_path).exists():
            # Create symlink or copy for testing
            import shutil
            shutil.copy(pdf_path, "test.pdf")
            print(f"Using PDF: {pdf_path}")

    test_extraction()
