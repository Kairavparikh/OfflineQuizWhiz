"""
Setup verification script.

Checks that all components are properly installed and configured.

Run:
    python3 verify_setup.py
"""

import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    print("\n" + "="*80)
    print("1. CHECKING PYTHON VERSION")
    print("="*80)

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 9:
        print("✅ Python version is compatible (>= 3.9)")
        return True
    else:
        print("❌ Python version is too old (need >= 3.9)")
        return False


def check_dependencies():
    """Check required Python packages."""
    print("\n" + "="*80)
    print("2. CHECKING DEPENDENCIES")
    print("="*80)

    required = [
        ("requests", "HTTP client for LLM"),
        ("docx", "python-docx", "DOCX parsing"),
        ("fitz", "PyMuPDF", "PDF extraction"),
        ("PIL", "Pillow", "Image processing"),
        ("fastapi", "FastAPI", "Web API"),
        ("uvicorn", "Uvicorn", "ASGI server"),
    ]

    all_ok = True

    for item in required:
        if len(item) == 2:
            module_name, description = item
            package_name = module_name
        else:
            module_name, package_name, description = item

        try:
            __import__(module_name)
            print(f"✅ {package_name:20s} - {description}")
        except ImportError:
            print(f"❌ {package_name:20s} - {description} (NOT INSTALLED)")
            all_ok = False

    if not all_ok:
        print("\n⚠️  Missing dependencies. Install with:")
        print("    pip install -r requirements.txt")

    return all_ok


def check_ollama():
    """Check Ollama connection."""
    print("\n" + "="*80)
    print("3. CHECKING OLLAMA CONNECTION")
    print("="*80)

    try:
        import requests
        from config import DEFAULT_LLM_CONFIG

        # Test connection
        response = requests.get(
            DEFAULT_LLM_CONFIG.base_url.replace("/api/generate", "/api/tags"),
            timeout=5
        )

        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running at {DEFAULT_LLM_CONFIG.base_url}")
            print(f"   Available models: {len(models)}")

            # Check for Mistral
            mistral_found = False
            for model in models:
                name = model.get('name', '')
                if 'mistral' in name.lower():
                    print(f"   ✅ Found: {name}")
                    mistral_found = True

            if not mistral_found:
                print("   ⚠️  Mistral model not found")
                print("   Install with: ollama pull mistral")
                return False

            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("\n   Make sure Ollama is running:")
        print("     1. Start Ollama: ollama serve")
        print("     2. Pull Mistral: ollama pull mistral")
        return False


def check_file_structure():
    """Check that all required files exist."""
    print("\n" + "="*80)
    print("4. CHECKING FILE STRUCTURE")
    print("="*80)

    required_files = [
        # Core modules
        "models.py",
        "config.py",
        "mcq_generator.py",
        "paper_builder.py",
        "csv_exporter.py",
        "api.py",

        # Phase 3
        "pdf_extractor.py",
        "multimodal_generator.py",

        # Web UI
        "static/index.html",

        # Documentation
        "README.md",
        "GETTING_STARTED.md",
        "requirements.txt"
    ]

    all_ok = True

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (MISSING)")
            all_ok = False

    return all_ok


def check_imports():
    """Check that core modules can be imported."""
    print("\n" + "="*80)
    print("5. CHECKING MODULE IMPORTS")
    print("="*80)

    modules = [
        "models",
        "config",
        "mcq_generator",
        "paper_builder",
        "csv_exporter",
        "pdf_extractor",
        "multimodal_generator",
        "api"
    ]

    all_ok = True

    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            print(f"❌ {module_name} - {str(e)[:50]}")
            all_ok = False

    return all_ok


def test_basic_functionality():
    """Test basic question creation."""
    print("\n" + "="*80)
    print("6. TESTING BASIC FUNCTIONALITY")
    print("="*80)

    try:
        from models import Question, DifficultyLevel

        # Create test question
        q = Question(
            test_section="Test Section",
            main_topic="Test Topic",
            subtopic="Test Subtopic",
            difficulty=DifficultyLevel.EASY,
            question_text_en="What is 2+2?",
            option_a_en="3",
            option_b_en="4",
            option_c_en="5",
            option_d_en="6",
            correct_answer="B",
            explanation="Basic arithmetic: 2 + 2 = 4",
            references=["Math textbook"]
        )

        # Validate
        errors = q.validate()
        if errors:
            print(f"❌ Question validation failed: {errors}")
            return False

        # Convert to dict
        q_dict = q.to_dict()

        print("✅ Created and validated test question")
        print(f"   Question ID: {q.question_id}")
        print(f"   Difficulty: {q.difficulty.value}")
        print(f"   Valid: {q.is_valid()}")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    print("\n" + "="*80)
    print("OFFLINEQUIZWHIZ - SETUP VERIFICATION")
    print("="*80)
    print("\nThis script verifies that your MCQ generation system is properly set up.")
    print("="*80)

    results = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Ollama Connection": check_ollama(),
        "File Structure": check_file_structure(),
        "Module Imports": check_imports(),
        "Basic Functionality": test_basic_functionality()
    }

    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)

    passed = 0
    total = len(results)

    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:.<40} {status}")
        if result:
            passed += 1

    print("="*80)
    print(f"Overall: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 ALL CHECKS PASSED!")
        print("\nYour system is fully set up and ready to use!")
        print("\nNext steps:")
        print("  1. Start web UI: python3 api.py")
        print("  2. Open browser: http://localhost:8000")
        print("  3. Generate your first paper!")
        print("\nOr run examples:")
        print("  python3 example_paper_generation.py")
    elif passed >= total - 1:
        print("\n✅ MOSTLY READY!")
        print("\nMost checks passed. Review failures above.")
        print("Ollama check may fail if you haven't started it yet.")
        print("\nTo start Ollama:")
        print("  ollama serve")
    else:
        print("\n⚠️  SETUP INCOMPLETE")
        print("\nSeveral checks failed. Please:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Start Ollama: ollama serve")
        print("  3. Pull Mistral: ollama pull mistral")
        print("  4. Run this script again: python3 verify_setup.py")

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
