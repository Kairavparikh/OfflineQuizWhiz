# 🚀 Start Here - OfflineQuizWhiz

Welcome! This is your **complete MCQ generation system** (Phases 1 & 2).

---

## ✅ What's Been Built

### Phase 1: Data Models & Syllabus Parser
- ✅ Subject/Topic/Question data models
- ✅ DOCX syllabus parser
- ✅ JSON serialization
- ✅ Question validation
- ✅ Paper configuration

### Phase 2: MCQ Generation Engine
- ✅ Local LLM integration (Ollama)
- ✅ Robust prompt engineering with few-shot examples
- ✅ `generate_mcqs()` function
- ✅ Difficulty control (Easy/Medium/Hard)
- ✅ Automatic validation and retry
- ✅ JSON parsing and error handling

---

## 🎯 What You Can Do Right Now

```python
from models import DifficultyLevel
from mcq_generator import generate_mcqs

# Generate 5 Medium-difficulty questions
questions = generate_mcqs(
    subject="Metallurgical Engineering",
    main_topic="Engineering Mathematics",
    subtopic="Linear Algebra - Matrices and Determinants",
    difficulty=DifficultyLevel.MEDIUM,
    n=5
)

# Each question has:
# - Question text, 4 options, correct answer
# - Detailed explanation
# - References (URLs + textbooks)
# - All metadata (topic, difficulty, etc.)
```

---

## 📋 Quick Start (3 Steps)

### 1. Test Without LLM (1 minute)

```bash
# Test Phase 1 (data models, validation)
python3 test_models.py

# Test Phase 2 (prompts, parsing, validation)
python3 test_phase2.py
```

**Both should show:** ✅ ALL TESTS PASSED!

### 2. Install Local LLM (5-10 minutes)

**On macOS:**
```bash
# Install Ollama
brew install ollama

# Start Ollama
ollama serve
```

**In another terminal:**
```bash
# Pull a model (choose one)
ollama pull llama2          # 4GB, fastest
ollama pull mistral         # 4GB, better quality
ollama pull llama3.1:8b     # 5GB, best quality
```

### 3. Generate Your First Questions (2 minutes)

```bash
# Test LLM connection
python3 example_generator.py
```

**Expected output:**
```
✅ LLM connection successful!
   Endpoint: http://localhost:11434/api/generate
   Model: llama2
```

Then uncomment an example in `example_generator.py` and run it to generate real questions!

---

## 📚 Documentation Guide

### Quick References

| File | Purpose |
|------|---------|
| **START_HERE.md** | This file - quick overview |
| **QUICKSTART.md** | Phase 1 quick start (data models, syllabus parsing) |
| **PHASE2_GUIDE.md** | Complete Phase 2 setup & usage guide |
| **PHASE2_COMPLETE.md** | Phase 2 summary & testing checklist |
| **README.md** | Full project documentation |

### Code Examples

| File | Description |
|------|-------------|
| `example_usage.py` | Phase 1 examples (syllabus parsing, questions) |
| `example_generator.py` | Phase 2 examples (generating MCQs) |
| `test_models.py` | Phase 1 tests (no dependencies) |
| `test_phase2.py` | Phase 2 tests (no LLM needed) |

### Core Implementation

| File | What It Does |
|------|--------------|
| `models.py` | Data classes (Subject, Question, etc.) |
| `syllabus_parser.py` | Parse DOCX → structured hierarchy |
| `config.py` | LLM & generation configuration |
| `prompt_templates.py` | Prompts with few-shot examples |
| `llm_client.py` | HTTP client for local LLM |
| `mcq_generator.py` | Main generator function |

---

## 🎓 Common Workflows

### Workflow 1: Parse Syllabus → Generate Questions

```python
# 1. Parse syllabus
from syllabus_parser import SyllabusParser
parser = SyllabusParser()
subjects = parser.parse_docx("Syllabus-for-SME.docx")

# 2. Generate questions for a topic
from models import DifficultyLevel
from mcq_generator import generate_mcqs

subject = subjects[0]
section = subject.sections[0]
topic = section.topics[0]

questions = generate_mcqs(
    subject=subject.name,
    main_topic=topic.name,
    subtopic=topic.subtopics[0].name,
    difficulty=DifficultyLevel.MEDIUM,
    n=5
)

# 3. Save to JSON
import json
with open("questions.json", 'w') as f:
    json.dump([q.to_dict() for q in questions], f, indent=2)
```

### Workflow 2: Generate Complete Paper

```python
from models import PaperConfig, DifficultyLevel
from mcq_generator import generate_mcqs

# Define paper structure
config = PaperConfig(
    paper_name="Metallurgical Engineering - Paper 1",
    total_questions=20,
    section_distribution={
        "Engineering Mathematics": 10,
        "Material Science": 10
    },
    difficulty_distribution={
        "Easy": 0.60,
        "Medium": 0.30,
        "Hard": 0.10
    }
)

# Generate all questions
all_questions = []

for section, count in config.section_distribution.items():
    difficulty_counts = config.get_difficulty_counts(count)

    for difficulty_str, num in difficulty_counts.items():
        difficulty = DifficultyLevel[difficulty_str.upper()]

        qs = generate_mcqs(
            subject="Metallurgical Engineering",
            main_topic=section,
            subtopic="General",
            difficulty=difficulty,
            n=num
        )
        all_questions.extend(qs)

print(f"✅ Generated {len(all_questions)} total questions")
```

### Workflow 3: Custom LLM Configuration

```python
from config import LLMConfig
from llm_client import create_llm_client
from mcq_generator import MCQGenerator

# Custom config
config = LLMConfig(
    base_url="http://localhost:11434",
    model_name="mistral",  # Better model
    temperature=0.8,       # More creative
    max_tokens=3000        # Longer responses
)

# Create generator
client = create_llm_client(
    base_url=config.base_url,
    model_name=config.model_name
)
generator = MCQGenerator(llm_client=client)

# Generate
questions = generator.generate_mcqs(
    subject="Metallurgical Engineering",
    main_topic="Material Science",
    subtopic="Phase Diagrams",
    difficulty=DifficultyLevel.HARD,
    n=3
)
```

---

## 🔧 Configuration

### Environment Variables (Optional)

```bash
# Set custom LLM endpoint
export LLM_BASE_URL="http://localhost:11434"
export LLM_MODEL="mistral"
export LLM_TEMPERATURE="0.7"
export LLM_MAX_TOKENS="2048"
```

### Or Edit `config.py` Directly

```python
# config.py
DEFAULT_LLM_CONFIG = LLMConfig(
    base_url="http://localhost:11434",  # Your endpoint
    model_name="mistral",               # Your model
    temperature=0.7,                    # 0-1 (higher = more creative)
    max_tokens=2048                     # Max response length
)
```

---

## 🐛 Troubleshooting

### Problem: LLM connection failed

1. Check Ollama is running: `ollama serve`
2. Verify model: `ollama list`
3. Test manually: `curl http://localhost:11434/api/generate -d '{"model":"llama2","prompt":"test"}'`

### Problem: Questions are low quality

1. **Use better model:** `ollama pull mistral` or `ollama pull llama3.1:8b`
2. **Adjust temperature:** Lower (0.5-0.6) for more factual
3. **Add better examples:** Edit `prompt_templates.py`

### Problem: Generation is slow

1. **Use quantized models:** `ollama pull llama2:7b-q4_0`
2. **Generate fewer questions per call:** 1-3 instead of 10+
3. **Reduce max_tokens:** Try 1500-2000

See **PHASE2_GUIDE.md** for complete troubleshooting.

---

## 📊 File Structure

```
OfflineQuizWhiz/
├── START_HERE.md          ⬅️ You are here!
├── QUICKSTART.md          Phase 1 quick start
├── PHASE2_GUIDE.md        Phase 2 complete guide
├── PHASE2_COMPLETE.md     Phase 2 summary
├── README.md              Full documentation
│
├── models.py              Data models
├── syllabus_parser.py     DOCX parser
├── config.py              Configuration
├── prompt_templates.py    Prompt engineering
├── llm_client.py          LLM HTTP client
├── mcq_generator.py       Main generator
│
├── example_usage.py       Phase 1 examples
├── example_generator.py   Phase 2 examples
├── test_models.py         Phase 1 tests
└── test_phase2.py         Phase 2 tests
```

---

## ✨ Next Steps

### Immediate (Today)
1. ✅ Run tests: `python3 test_models.py && python3 test_phase2.py`
2. ✅ Install Ollama: `brew install ollama && ollama serve`
3. ✅ Pull model: `ollama pull mistral`
4. ✅ Test connection: `python3 example_generator.py`

### This Week
5. Generate your first questions from your actual syllabus
6. Test different difficulty levels
7. Experiment with different models (llama2 vs mistral vs llama3.1)
8. Fine-tune prompts in `prompt_templates.py`

### Phase 3 (Next 2-3 Weeks)
- PDF parsing (extract text + diagrams)
- Vision-language model integration
- Diagram-based question generation

### Phase 4 (Following 2-3 Weeks)
- FastAPI backend
- Web UI for SME review
- Excel/CSV export
- Docker packaging

---

## 🎉 You're Ready!

Everything is set up and tested. Start with:

```bash
# Run all tests
python3 test_models.py
python3 test_phase2.py

# Then start Ollama and generate questions
ollama serve
python3 example_generator.py
```

**Questions?** Check:
- PHASE2_GUIDE.md for detailed setup
- example_generator.py for code examples
- PHASE2_COMPLETE.md for testing checklist

**Ready to move to Phase 3?** Let me know!

---

*Built with ❤️ on M4 Mac - 100% on-premises, no cloud APIs*
