# OfflineQuizWhiz – Local MCQ Generator

On-premises multiple-choice question (MCQ) generator for high-stakes technical exams. Generates questions from syllabus documents and PDFs using local LLMs (no cloud APIs).

## Project Overview

### Goal
Build a system that generates exam-quality MCQs with:
- Metadata: subject, topic, subtopic, difficulty level
- Content: question, 4 options, correct answer, explanation, references
- Paper-level configuration (e.g., 100 questions with specific difficulty distribution)
- SME review workflow via web UI

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Syllabus Parser                           │
│  (DOCX/PDF → Subject → Section → Topic → SubTopic)         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Question Generation Engine                      │
│  (Local LLM + Prompts → MCQs with metadata)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Paper Builder + Web UI                          │
│  (Configure, generate, review, export to Excel/CSV)         │
└─────────────────────────────────────────────────────────────┘
```

## Current Status: Phase 4 (Paper Assembly & Web Interface) ✅

### Phase 1 ✅ (Completed)
- ✅ Data models for Subject, Section, Topic, SubTopic, Question
- ✅ Question validation logic
- ✅ DOCX syllabus parser with heading/list extraction
- ✅ JSON serialization/deserialization
- ✅ Paper configuration model

### Phase 2 ✅ (Completed)
- ✅ LLM client for local endpoints (Ollama support)
- ✅ Prompt engineering with few-shot examples
- ✅ Difficulty-aware generation (Easy/Medium/Hard)
- ✅ `generate_mcqs()` function with validation
- ✅ Retry logic and error handling
- ✅ JSON parsing and Question object creation

### Phase 3 ✅ (Completed)
- ✅ PDF extraction (text + images with PyMuPDF)
- ✅ Diagram caption and context extraction
- ✅ Smart text-image pairing
- ✅ Vision-language model (VLM) client
- ✅ Multimodal prompt templates
- ✅ Diagram-based MCQ generation
- ✅ Mock VLM for testing without real model

### Phase 4 ✅ (Completed)
- ✅ Paper assembly system (build complete exam papers)
- ✅ Section-based distribution with difficulty control
- ✅ Question bank with duplicate prevention
- ✅ CSV/Excel export in client's format
- ✅ FastAPI backend with REST endpoints
- ✅ Web UI for paper generation and management
- ✅ Paper download and deletion features

### System Complete! 🎉
All phases implemented. Ready for production use.

---

## File Structure

```
OfflineQuizWhiz/
# Phase 1: Data Models & Syllabus Parsing
├── models.py                  # Data models (Subject, Question, etc.)
├── syllabus_parser.py         # DOCX → structured hierarchy
├── example_usage.py           # Phase 1 usage examples
├── test_models.py             # Phase 1 tests (no deps required)
├── sample_syllabus.json       # Example syllabus structure

# Phase 2: MCQ Generation Engine (Text-Only)
├── config.py                  # LLM and generation configuration
├── prompt_templates.py        # Prompt engineering with few-shot examples
├── llm_client.py              # HTTP client for local LLM endpoints
├── mcq_generator.py           # Main generator with validation
├── example_generator.py       # Phase 2 usage examples

# Phase 3: Multimodal (PDF + Diagrams)
├── multimodal_models.py       # Multimodal data structures
├── pdf_extractor.py           # PDF extraction (text + images)
├── multimodal_prompts.py      # VLM prompt templates
├── vlm_client.py              # Vision-language model client
├── multimodal_generator.py    # Multimodal MCQ generator
├── example_multimodal.py      # Phase 3 usage examples

# Phase 4: Paper Assembly & Web Interface
├── paper_builder.py           # Paper assembly system
├── csv_exporter.py            # CSV/Excel export
├── api.py                     # FastAPI backend
├── example_paper_generation.py # Paper generation examples
├── static/
│   └── index.html            # Web UI frontend
├── generated_papers/         # Output directory (auto-created)
└── question_bank_state.json  # Question usage tracking

# Testing & Documentation
├── test_models.py            # Phase 1 tests
├── test_phase2.py            # Phase 2 tests
├── test_pdf_upload.py        # PDF upload workflow test
├── test_pdf_extraction.py    # PDF extraction test
├── test_full_pipeline.py     # Complete pipeline test
├── test_real_vlm.py          # Real VLM integration test
├── run_all_tests.py          # Master test suite
│
├── requirements.txt          # Python dependencies
├── README.md                 # This file (overview)
├── START_HERE.md             # Quick start guide
├── QUICKSTART.md             # Phase 1 quick start
├── PHASE2_GUIDE.md           # Phase 2 complete guide
├── PHASE2_COMPLETE.md        # Phase 2 summary
├── PHASE3_GUIDE.md           # Phase 3 complete guide
├── PHASE3_COMPLETE.md        # Phase 3 summary
├── PHASE4_GUIDE.md           # Phase 4 complete guide
└── .gitignore                # Git ignore rules
```

---

## Installation

### Prerequisites
- Python 3.9+
- pip

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### 1. Parse a DOCX Syllabus

```python
from syllabus_parser import SyllabusParser

# Initialize parser
parser = SyllabusParser(
    subject_heading_level=1,   # Heading 1 = Subject
    section_heading_level=2,   # Heading 2 = Section
    topic_heading_level=3      # Heading 3 = Topic
)

# Parse DOCX
subjects = parser.parse_docx("Syllabus-for-SME.docx")

# Save to JSON
parser.subjects_to_json(subjects, "parsed_syllabus.json")
```

**Expected DOCX Structure:**
```
Heading 1: Metallurgical Engineering
  Heading 2: Engineering Mathematics
    Heading 3: Linear Algebra
      • Matrices and Determinants
      • System of Linear Equations
    Heading 3: Calculus
      • Limits and Continuity
      • Differentiation
```

### 2. Load Syllabus from JSON

```python
from syllabus_parser import SyllabusParser

parser = SyllabusParser()
subjects = parser.json_to_subjects("sample_syllabus.json")

# Access hierarchy
for subject in subjects:
    for section in subject.sections:
        for topic in section.topics:
            for subtopic in topic.subtopics:
                print(f"{subject.name} → {section.name} → {topic.name} → {subtopic.name}")
```

### 3. Create and Validate Questions

```python
from models import Question, DifficultyLevel

# Create question
question = Question(
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
    explanation="The determinant of an identity matrix is always 1.",
    references=["https://en.wikipedia.org/wiki/Determinant"]
)

# Validate
errors = question.validate()
if errors:
    print("Validation errors:", errors)
else:
    print("✅ Question is valid!")
```

### 4. Configure a Paper

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
        "Easy": 0.60,    # 60% easy
        "Medium": 0.30,  # 30% medium
        "Hard": 0.10     # 10% hard
    }
)

# Get difficulty breakdown for a section
counts = config.get_difficulty_counts(30)
# → {"Easy": 18, "Medium": 9, "Hard": 3}
```

### 5. Generate MCQs (Text-Only)

```bash
# Generate questions with Mistral
python3 example_generator.py
```

Or programmatically:
```python
from models import DifficultyLevel
from mcq_generator import generate_mcqs

questions = generate_mcqs(
    subject="Metallurgical Engineering",
    main_topic="Material Science",
    subtopic="Crystal Structure",
    difficulty=DifficultyLevel.MEDIUM,
    n=5  # Generate 5 questions
)
```

### 6. Generate Paper with Web UI (Recommended)

```bash
# Start the web interface
python3 api.py
```

Then open http://localhost:8000 in your browser:
1. Fill in paper details (name, subject)
2. Configure sections (questions, difficulty, topics)
3. Click "Generate Paper"
4. Download as CSV

### 7. Generate Paper Programmatically

```python
from models import PaperConfig
from paper_builder import PaperBuilder, PaperSection
from csv_exporter import export_paper_to_csv

# Define paper configuration
config = PaperConfig(
    paper_name="Metallurgical Engineering 2026",
    subject="Metallurgical Engineering",
    total_questions=100
)

# Define sections
sections = [
    PaperSection(
        name="Main Subject",
        question_count=60,
        difficulty_distribution={"Easy": 40, "Medium": 15, "Hard": 5},
        topics=[
            {"main_topic": "Material Science", "subtopic": "Crystal Structure"},
            {"main_topic": "Thermodynamics", "subtopic": "Phase Diagrams"}
        ]
    ),
    PaperSection(
        name="Aptitude",
        question_count=20,
        difficulty_distribution={"Easy": 15, "Medium": 5, "Hard": 0},
        topics=[
            {"main_topic": "Quantitative Aptitude", "subtopic": "Number Systems"}
        ]
    )
]

# Build and export
builder = PaperBuilder()
paper = builder.build_paper(config, sections)
export_paper_to_csv(paper, "exam_paper.csv")
```

### 8. Extract and Generate from PDFs

```bash
# Test PDF upload workflow
python3 test_pdf_upload.py your_textbook.pdf
```

This will:
- Extract diagrams and text from PDF
- Create text-image pairs
- Generate diagram-based MCQs
- Export to JSON

### 9. Run All Tests

```bash
# Test complete system
python3 run_all_tests.py
```

---

## Data Models

### Question Object

```python
@dataclass
class Question:
    # Metadata
    question_id: str              # Auto-generated UUID
    test_section: str             # e.g., "Engineering Mathematics"
    main_topic: str               # e.g., "Linear Algebra"
    subtopic: str                 # e.g., "Matrices and Determinants"
    difficulty: DifficultyLevel   # Easy / Medium / Hard

    # Content
    question_text_en: str         # Question in English
    option_a_en: str
    option_b_en: str
    option_c_en: str
    option_d_en: str
    correct_answer: str           # "A", "B", "C", or "D"
    explanation: str              # Solution/explanation
    references: List[str]         # URLs or book citations

    # Optional metadata
    created_at: datetime
    source_pdf: Optional[str]
    has_diagram: bool
    tags: List[str]
```

**Validation Rules:**
- All options must be non-empty and distinct
- `correct_answer` must be A, B, C, or D
- Explanation must be ≥20 characters
- Question text, test_section, and main_topic are required

### Syllabus Hierarchy

```python
Subject
  └─ Section(s)
      └─ Topic(s)
          └─ SubTopic(s)
```

**Example:**
```
Metallurgical Engineering (Subject)
  ├─ Engineering Mathematics (Section)
  │   ├─ Linear Algebra (Topic)
  │   │   ├─ Matrices and Determinants (SubTopic)
  │   │   └─ System of Linear Equations (SubTopic)
  │   └─ Calculus (Topic)
  │       ├─ Limits and Continuity (SubTopic)
  │       └─ Differentiation (SubTopic)
  └─ Physics (Section)
      └─ Mechanics (Topic)
          └─ Newton's Laws of Motion (SubTopic)
```

---

## DOCX Syllabus Parser

### How It Works

The parser extracts structured data from DOCX files by:
1. Identifying headings (Heading 1, 2, 3, etc.)
2. Extracting bullet/numbered lists
3. Cleaning list markers (1., •, -, etc.)
4. Extracting keywords from subtopic text
5. Building the Subject → Section → Topic → SubTopic hierarchy

### Supported List Formats

```
✅ 1. Item one
✅ 1) Item one
✅ a. Item one
✅ (a) Item one
✅ • Bullet item
✅ - Dash item
✅ * Asterisk item
✅ i. Roman numeral
```

### Configuration Options

```python
parser = SyllabusParser(
    subject_heading_level=1,    # Heading level for subjects
    section_heading_level=2,    # Heading level for sections
    topic_heading_level=3,      # Heading level for topics
    extract_keywords=True       # Auto-extract keywords from subtopics
)
```

### Output Format

**JSON Structure:**
```json
{
  "subjects": [
    {
      "name": "Metallurgical Engineering",
      "code": "SME",
      "sections": [
        {
          "name": "Engineering Mathematics",
          "topics": [
            {
              "name": "Linear Algebra",
              "subtopics": [
                {
                  "name": "Matrices and Determinants",
                  "keywords": ["matrix", "determinant", "eigenvalue"]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Testing Your Syllabus

1. **Prepare your DOCX:**
   - Use Heading 1 for Subject names
   - Use Heading 2 for Section names
   - Use Heading 3 for Topic names
   - Use bullet/numbered lists for SubTopics

2. **Parse and inspect:**
   ```python
   from syllabus_parser import SyllabusParser, print_syllabus_summary

   parser = SyllabusParser()
   subjects = parser.parse_docx("your_syllabus.docx")
   print_syllabus_summary(subjects)
   ```

3. **Check output:**
   - Are subjects/sections/topics extracted correctly?
   - Are subtopics in the right place?
   - Are list markers removed properly?

4. **Adjust heading levels if needed:**
   ```python
   parser = SyllabusParser(
       subject_heading_level=2,  # If subjects are Heading 2 in your DOCX
       section_heading_level=3,
       topic_heading_level=4
   )
   ```

---

## Next Steps (Phase 2+)

### Phase 2: MCQ Generation Engine
- [ ] Set up local LLM (Ollama / llama.cpp)
- [ ] Design prompts for MCQ generation
- [ ] Implement difficulty control
- [ ] Post-processing & validation
- [ ] Question database/storage

### Phase 3: Multimodal Support
- [ ] PDF parsing (PyMuPDF)
- [ ] Image/diagram extraction
- [ ] Upgrade to vision-language model
- [ ] Diagram-based question generation

### Phase 4: Web UI & Export
- [ ] FastAPI backend
- [ ] Web UI for SME review
- [ ] Excel/CSV export
- [ ] Docker packaging

---

## Development Notes

### Dependencies
- `python-docx`: DOCX parsing
- Standard library: `dataclasses`, `enum`, `typing`, `json`, `uuid`, `datetime`

### Python Version
- Requires Python 3.9+ (for `dataclasses` and type hints)

### Code Style
- Type hints throughout
- Dataclasses for data models
- Enums for controlled vocabulary
- Docstrings for all public functions

---

## Contact & Support

For questions or issues with this implementation, refer to:
- Example usage: `example_usage.py`
- Sample syllabus: `sample_syllabus.json`
- This documentation: `README.md`

---

## License

[To be determined by client]
