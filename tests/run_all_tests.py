"""
Master test script - runs all tests for all 3 phases.

Tests:
- Phase 1: Data models
- Phase 2: Text-only MCQ generation
- Phase 3: Multimodal (PDF + diagrams)
"""

import sys
from pathlib import Path


def run_phase1_tests():
    """Test Phase 1: Data models and syllabus parsing."""
    print("\n" + "="*80)
    print("PHASE 1 TESTS: Data Models & Syllabus Parsing")
    print("="*80)

    try:
        import subprocess
        result = subprocess.run(
            ["python3", "test_models.py"],
            capture_output=True,
            text=True,
            timeout=30
        )

        print(result.stdout)

        if result.returncode == 0:
            print("✅ Phase 1 tests PASSED")
            return True
        else:
            print("❌ Phase 1 tests FAILED")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error running Phase 1 tests: {e}")
        return False


def run_phase2_tests():
    """Test Phase 2: Text-only MCQ generation."""
    print("\n" + "="*80)
    print("PHASE 2 TESTS: Text-Only MCQ Generation")
    print("="*80)

    try:
        import subprocess
        result = subprocess.run(
            ["python3", "test_phase2.py"],
            capture_output=True,
            text=True,
            timeout=30
        )

        print(result.stdout)

        if result.returncode == 0:
            print("✅ Phase 2 tests PASSED")
            return True
        else:
            print("❌ Phase 2 tests FAILED")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error running Phase 2 tests: {e}")
        return False


def run_phase2_generation_test():
    """Test actual question generation with Mistral."""
    print("\n" + "="*80)
    print("PHASE 2 LIVE TEST: Generate Question with Mistral")
    print("="*80)

    try:
        from models import DifficultyLevel
        from mcq_generator import generate_mcqs

        print("\n🤖 Generating 1 Easy question with Mistral...")
        print("(This takes ~30-60 seconds)\n")

        questions = generate_mcqs(
            subject="Test Subject",
            main_topic="Test Topic",
            subtopic="Test Subtopic",
            difficulty=DifficultyLevel.EASY,
            n=1
        )

        if questions:
            q = questions[0]
            print(f"\n✅ Successfully generated question!")
            print(f"   Q: {q.question_text_en[:60]}...")
            print(f"   Correct: {q.correct_answer}")
            return True
        else:
            print("❌ No questions generated")
            return False

    except Exception as e:
        print(f"❌ Live generation failed: {e}")
        print("   (This is OK if Ollama/Mistral is not running)")
        return False


def run_phase3_tests():
    """Test Phase 3: Multimodal (mock mode)."""
    print("\n" + "="*80)
    print("PHASE 3 TESTS: Multimodal MCQ Generation (Mock VLM)")
    print("="*80)

    try:
        import subprocess
        result = subprocess.run(
            ["python3", "example_multimodal.py"],
            capture_output=True,
            text=True,
            timeout=60
        )

        print(result.stdout)

        if "✅ Examples completed!" in result.stdout or "Successfully generated" in result.stdout:
            print("✅ Phase 3 tests PASSED")
            return True
        else:
            print("❌ Phase 3 tests FAILED")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error running Phase 3 tests: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("OFFLINEQUIZWHIZ - COMPLETE TEST SUITE")
    print("="*80)
    print("\nThis will test all 3 phases:")
    print("  Phase 1: Data models & syllabus parsing")
    print("  Phase 2: Text-only MCQ generation")
    print("  Phase 3: Multimodal (PDF + diagrams)")
    print("\n" + "="*80)

    results = {
        "Phase 1 (Data Models)": False,
        "Phase 2 (Prompts & Parsing)": False,
        "Phase 2 (Live Generation)": False,
        "Phase 3 (Multimodal)": False
    }

    # Phase 1
    results["Phase 1 (Data Models)"] = run_phase1_tests()

    # Phase 2
    results["Phase 2 (Prompts & Parsing)"] = run_phase2_tests()
    results["Phase 2 (Live Generation)"] = run_phase2_generation_test()

    # Phase 3
    results["Phase 3 (Multimodal)"] = run_phase3_tests()

    # Summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)

    passed = 0
    total = 0

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
        total += 1

    print("="*80)
    print(f"Overall: {passed}/{total} test suites passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is fully functional.")
    elif passed >= total - 1:
        print("\n✅ Most tests passed. System is mostly functional.")
        print("   (Live generation test may fail if LLM is not running)")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)

    if results["Phase 1 (Data Models)"] and results["Phase 2 (Prompts & Parsing)"] and results["Phase 3 (Multimodal)"]:
        print("\n✅ All core tests passed!")
        print("\nYou can now:")
        print("  1. Extract your client's PDFs")
        print("  2. Generate diagram-based questions")
        print("  3. Set up a real VLM for production")
        print("\nNext: Read PHASE3_GUIDE.md for production setup")
    else:
        print("\nReview failed tests and check:")
        print("  - Dependencies installed: pip install -r requirements.txt")
        print("  - For live generation: Ollama running with Mistral model")
        print("  - For PDF extraction: PyMuPDF installed")

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
