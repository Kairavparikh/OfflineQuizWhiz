# Quick Start Guide

## What's Been Built (Phase 1)

✅ **Complete data model system** for MCQ generation:
- Subject → Section → Topic → SubTopic hierarchy
- Question object with metadata, content, validation
- Paper configuration for exam assembly
- JSON serialization/deserialization

✅ **DOCX Syllabus Parser** that extracts:
- Subjects from Heading 1
- Sections from Heading 2
- Topics from Heading 3
- SubTopics from bullet/numbered lists
- Auto-extracted keywords

✅ **Validation & Testing**:
- Question validation (options, correct answer, explanations)
- Full test suite demonstrating all features
- Sample data and examples

---

## Files Delivered

```
OfflineQuizWhiz/
├── models.py                  # Core data models
├── syllabus_parser.py         # DOCX → JSON parser
├── example_usage.py           # Complete usage examples
├── test_models.py             # Validation tests (no deps)
├── sample_syllabus.json       # Example structure
├── requirements.txt           # Dependencies
├── README.md                  # Full documentation
└── QUICKSTART.md              # This file
```

---

## Test It Right Now (No Installation)

```bash
# Run the test suite (no dependencies needed)
python3 test_models.py
```

This will:
- ✅ Create sample Subject/Topic/Question objects
- ✅ Validate a correct question
- ✅ Show validation errors for invalid questions
- ✅ Demonstrate JSON serialization
- ✅ Configure a sample exam paper
- ✅ Load the sample syllabus JSON

---

## Install & Parse Your Syllabus

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install python-docx
pip install -r requirements.txt
```

### 2. Prepare Your DOCX

Make sure your syllabus uses:
- **Heading 1** for Subject names
- **Heading 2** for Section names
- **Heading 3** for Topic names
- **Bullets/numbers** for SubTopics

Example:
```
Heading 1: Metallurgical Engineering
  Heading 2: Engineering Mathematics
    Heading 3: Linear Algebra
      1. Matrices and Determinants
      2. System of Linear Equations
    Heading 3: Calculus
      • Limits and Continuity
      • Differentiation
```

### 3. Parse Your Syllabus

```python
from syllabus_parser import SyllabusParser, print_syllabus_summary

# Parse DOCX
parser = SyllabusParser()
subjects = parser.parse_docx("Syllabus-for-SME.docx")

# View structure
print_syllabus_summary(subjects)

# Save to JSON
parser.subjects_to_json(subjects, "my_syllabus.json")
```

### 4. Use the Parsed Data

```python
# Load from JSON
subjects = parser.json_to_subjects("my_syllabus.json")

# Access hierarchy
for subject in subjects:
    print(f"Subject: {subject.name}")
    for section in subject.sections:
        print(f"  Section: {section.name}")
        for topic in section.topics:
            print(f"    Topic: {topic.name}")
            for subtopic in topic.subtopics:
                print(f"      • {subtopic.name}")
                print(f"        Keywords: {', '.join(subtopic.keywords)}")
```

---

## Create Questions Manually

```python
from models import Question, DifficultyLevel

question = Question(
    test_section="Engineering Mathematics",
    main_topic="Linear Algebra",
    subtopic="Matrices and Determinants",
    difficulty=DifficultyLevel.MEDIUM,
    question_text_en="What is the rank of a 3×3 identity matrix?",
    option_a_en="0",
    option_b_en="1",
    option_c_en="2",
    option_d_en="3",
    correct_answer="D",
    explanation="The rank of a matrix is the maximum number of linearly "
                "independent rows/columns. All rows in an identity matrix "
                "are linearly independent, so rank = 3.",
    references=[
        "https://en.wikipedia.org/wiki/Rank_(linear_algebra)",
        "Linear Algebra by Gilbert Strang, Chapter 2"
    ]
)

# Validate
if question.is_valid():
    print("✅ Question ready!")
else:
    print("❌ Errors:", question.validate())
```

---

## Configure a Paper

```python
from models import PaperConfig

config = PaperConfig(
    paper_name="Metallurgical Engineering - Paper 1",
    subject="Metallurgical Engineering",
    total_questions=100,
    section_distribution={
        "Engineering Mathematics": 30,
        "Physics": 20,
        "Material Science": 30,
        "Aptitude": 20
    },
    difficulty_distribution={
        "Easy": 0.60,    # 60% easy questions
        "Medium": 0.30,  # 30% medium
        "Hard": 0.10     # 10% hard
    }
)

# Get difficulty breakdown for each section
for section, count in config.section_distribution.items():
    breakdown = config.get_difficulty_counts(count)
    print(f"{section}: {count} questions")
    print(f"  Easy: {breakdown['Easy']}, Medium: {breakdown['Medium']}, Hard: {breakdown['Hard']}")
```

Output:
```
Engineering Mathematics: 30 questions
  Easy: 18, Medium: 9, Hard: 3
Physics: 20 questions
  Easy: 12, Medium: 6, Hard: 2
...
```

---

## What's Next (Phase 2)

Once you approve Phase 1, we'll build:

1. **Local LLM Integration**
   - Set up Ollama or llama.cpp
   - Design prompts for MCQ generation
   - Implement `generate_mcqs(topic, difficulty, count)` function

2. **Question Generator**
   - Given: "Engineering Mathematics → Linear Algebra → Matrices"
   - Output: 5 valid MCQs in your format

3. **Command-Line Tool**
   ```bash
   python generate.py \
     --syllabus my_syllabus.json \
     --subject "Metallurgical Engineering" \
     --section "Engineering Mathematics" \
     --questions 20 \
     --output questions.csv
   ```

---

## Questions?

- **Full docs:** `README.md`
- **Code examples:** `example_usage.py`
- **Test without installation:** `python3 test_models.py`

Ready to move to Phase 2? Send confirmation and we'll start on the LLM integration!
