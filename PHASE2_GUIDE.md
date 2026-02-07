# Phase 2: MCQ Generator - Setup & Usage Guide

## Overview

Phase 2 implements the **core MCQ generation engine** using a local LLM. The system:

1. Takes syllabus topics and difficulty levels as input
2. Generates high-quality MCQs using carefully crafted prompts
3. Validates all questions for correctness and completeness
4. Returns structured `Question` objects ready to use

---

## New Files Added

```
OfflineQuizWhiz/
├── config.py                 # LLM and generation configuration
├── prompt_templates.py       # Prompt engineering with few-shot examples
├── llm_client.py            # HTTP client for local LLM
├── mcq_generator.py         # Main generator with validation
└── example_generator.py     # Usage examples
```

---

## Prerequisites

### 1. Install Ollama (Recommended)

**macOS (M-series):**
```bash
# Download and install from https://ollama.ai
# Or use Homebrew:
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Pull a Model

```bash
# Start Ollama service
ollama serve

# Pull a model (in another terminal)
ollama pull llama2           # ~4GB, good for development
# or
ollama pull mistral          # ~4GB, better quality
# or
ollama pull llama3.1:8b      # ~5GB, higher quality
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Quick Start

### 1. Test Your LLM Connection

```bash
python3 example_generator.py
```

This will test the connection to Ollama on `http://localhost:11434`.

**Expected output:**
```
✅ LLM connection successful!
   Endpoint: http://localhost:11434/api/generate
   Model: llama2
   Test response: ...
```

### 2. Generate Your First Question

```python
from models import DifficultyLevel
from mcq_generator import generate_mcqs

# Generate 1 Easy question
questions = generate_mcqs(
    subject="Metallurgical Engineering",
    main_topic="Engineering Mathematics",
    subtopic="Linear Algebra - Matrices and Determinants",
    difficulty=DifficultyLevel.EASY,
    n=1
)

# Print the question
q = questions[0]
print(f"Question: {q.question_text_en}")
print(f"Correct: {q.correct_answer}")
print(f"Explanation: {q.explanation}")
```

---

## Configuration

### LLM Endpoint Configuration

Edit `config.py` or set environment variables:

```python
# config.py
DEFAULT_LLM_CONFIG = LLMConfig(
    base_url="http://localhost:11434",  # Your LLM endpoint
    model_name="llama2",                # Your model
    temperature=0.7,                    # Creativity (0-1)
    max_tokens=2048,                    # Max response length
    timeout_seconds=120                 # Request timeout
)
```

**Environment variables:**
```bash
export LLM_BASE_URL="http://localhost:11434"
export LLM_MODEL="mistral"
export LLM_TEMPERATURE="0.8"
```

### Generation Configuration

```python
# config.py
DEFAULT_GENERATION_CONFIG = GenerationConfig(
    min_explanation_length=20,      # Minimum explanation chars
    require_references=True,        # Require references
    min_references=1,               # Minimum number of refs
    max_validation_retries=2,       # Retries for invalid questions
    use_few_shot=True,              # Include examples in prompt
    num_few_shot_examples=2         # Number of examples
)
```

---

## Usage Examples

### Example 1: Generate Single Question

```python
from models import DifficultyLevel
from mcq_generator import generate_mcqs

questions = generate_mcqs(
    subject="Metallurgical Engineering",
    main_topic="Material Science",
    subtopic="Crystal Structure - BCC, FCC, HCP",
    difficulty=DifficultyLevel.MEDIUM,
    n=1
)

# Access question data
q = questions[0]
print(f"Question ID: {q.question_id}")
print(f"Question: {q.question_text_en}")
print(f"Options: A={q.option_a_en}, B={q.option_b_en}, ...")
print(f"Correct: {q.correct_answer}")
```

### Example 2: Generate Multiple Questions

```python
# Generate 5 Medium questions
questions = generate_mcqs(
    subject="Metallurgical Engineering",
    main_topic="Engineering Mathematics",
    subtopic="Calculus - Differentiation",
    difficulty=DifficultyLevel.MEDIUM,
    n=5
)

print(f"Generated {len(questions)} questions")
```

### Example 3: Generate Different Difficulty Levels

```python
all_questions = []

for difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
    questions = generate_mcqs(
        subject="Metallurgical Engineering",
        main_topic="Physics",
        subtopic="Thermodynamics - Heat Transfer",
        difficulty=difficulty,
        n=2
    )
    all_questions.extend(questions)

# Now you have 6 questions: 2 Easy, 2 Medium, 2 Hard
```

### Example 4: Save to JSON

```python
import json

questions = generate_mcqs(
    subject="Metallurgical Engineering",
    main_topic="Material Science",
    subtopic="Phase Diagrams - Iron-Carbon",
    difficulty=DifficultyLevel.HARD,
    n=3
)

# Convert to JSON
questions_data = [q.to_dict() for q in questions]

# Save
with open("my_questions.json", 'w') as f:
    json.dump(questions_data, f, indent=2)
```

### Example 5: Generate from Syllabus

```python
from syllabus_parser import SyllabusParser
from models import DifficultyLevel
from mcq_generator import generate_mcqs

# Load syllabus
parser = SyllabusParser()
subjects = parser.json_to_subjects("sample_syllabus.json")

# Generate questions for each topic
all_questions = []

subject = subjects[0]  # Metallurgical Engineering
section = subject.sections[0]  # Engineering Mathematics

for topic in section.topics:
    for subtopic in topic.subtopics[:2]:  # First 2 subtopics
        questions = generate_mcqs(
            subject=subject.name,
            main_topic=topic.name,
            subtopic=subtopic.name,
            difficulty=DifficultyLevel.MEDIUM,
            n=2
        )
        all_questions.extend(questions)

print(f"Generated {len(all_questions)} total questions")
```

---

## How It Works

### 1. Prompt Engineering

The system uses **carefully crafted prompts** with:

- **System instructions**: Role definition and quality guidelines
- **Difficulty definitions**: Clear definitions of Easy/Medium/Hard
- **Few-shot examples**: 2-3 examples matching the target difficulty
- **Output format**: Strict JSON schema
- **Validation requirements**: Rules for references, explanation length, etc.

**Example prompt structure:**
```
System: You are an expert question writer for technical exams...

Difficulty Definitions:
- Easy: Direct recall, single-step...
- Medium: 1-2 steps, application...
- Hard: Multi-step, complex reasoning...

Examples:
[Example 1: Easy question with full answer]
[Example 2: Medium question with full answer]

Your Task:
Generate 3 Medium questions for:
- Subject: Metallurgical Engineering
- Topic: Linear Algebra - Matrices

Output Format:
[
  {
    "question_text_en": "...",
    "option_a_en": "...",
    ...
  }
]
```

### 2. Generation Pipeline

```
User Input → Prompt Builder → LLM Client → JSON Parser → Validator → Question Objects
```

1. **Prompt Builder**: Fills template with topic, difficulty, examples
2. **LLM Client**: Calls local LLM via HTTP POST
3. **JSON Parser**: Extracts and parses JSON from response
4. **Validator**: Checks format, duplicates, references, etc.
5. **Question Objects**: Returns validated `Question` instances

### 3. Validation

Each question must pass:

**Basic validation** (from `Question.validate()`):
- ✅ 4 non-empty options
- ✅ All options distinct (no duplicates)
- ✅ Correct answer is A, B, C, or D
- ✅ Explanation ≥20 characters
- ✅ Required metadata present

**Additional validation** (from `MCQGenerator`):
- ✅ Explanation ≥ configured minimum length
- ✅ At least N references (configurable)
- ✅ Options not too short (≥2 chars)

**Retry logic**:
- If a question fails validation, generate a new one
- Up to `max_validation_retries` attempts per question
- Final output contains only valid questions

---

## Prompt Template Customization

### Add Your Own Few-Shot Examples

Edit `prompt_templates.py`:

```python
FEW_SHOT_EXAMPLES = [
    {
        "difficulty": "Easy",
        "subject": "Your Subject",
        "main_topic": "Your Topic",
        "subtopic": "Your Subtopic",
        "example": """{
  "question_text_en": "Your example question?",
  "option_a_en": "Option A",
  ...
  "explanation": "Your detailed explanation...",
  "references": ["https://...", "Book by Author"]
}"""
    },
    # Add more examples...
]
```

### Adjust Difficulty Definitions

Edit `DIFFICULTY_DEFINITIONS` in `prompt_templates.py` to match your client's expectations.

---

## Troubleshooting

### Problem: "LLM connection failed"

**Solutions:**
1. Check Ollama is running: `ollama serve`
2. Verify model is pulled: `ollama list`
3. Test manually: `curl http://localhost:11434/api/generate -d '{"model":"llama2","prompt":"test"}'`
4. Check firewall/network settings
5. Update `config.py` with correct endpoint

### Problem: "Invalid JSON in LLM response"

**Solutions:**
1. Use a better model (mistral, llama3.1 instead of llama2)
2. Increase `max_tokens` in config (try 3000-4000)
3. Simplify the prompt (reduce few-shot examples)
4. Lower `temperature` for more deterministic output (try 0.5)

### Problem: "No questions generated" / "All questions fail validation"

**Solutions:**
1. Check LLM output manually (add debug prints in `mcq_generator.py`)
2. Reduce validation strictness in `config.py`:
   ```python
   min_explanation_length=10  # Lower threshold
   require_references=False   # Don't require refs for testing
   ```
3. Increase `max_validation_retries`
4. Use a more capable model

### Problem: Questions are low quality

**Solutions:**
1. **Use better models**: llama3.1, mistral, mixtral
2. **Improve prompts**: Add more specific examples in `prompt_templates.py`
3. **Adjust temperature**: Lower (0.5-0.6) for more factual, higher (0.8-0.9) for more creative
4. **Add validation rules**: Custom checks in `_passes_additional_validation()`

---

## Performance Tips

### M-Series Mac Optimization

1. **Use quantized models** for faster inference:
   ```bash
   ollama pull llama2:7b-q4_0   # 4-bit quantization
   ```

2. **Adjust batch sizes**:
   - Generate 1-3 questions per call (not 10+)
   - Multiple small calls > one giant call

3. **Monitor memory**:
   ```bash
   # Check Ollama memory usage
   ps aux | grep ollama
   ```

### Generation Speed

Typical times on M4 Mac (24GB):
- **llama2 (7B)**: ~30-60s per question
- **mistral (7B)**: ~40-70s per question
- **llama3.1 (8B)**: ~50-80s per question

Batch generation of 5 questions ≈ 3-5 minutes total.

---

## Next Steps

### Integration with Paper Builder

Generate complete papers:

```python
from models import PaperConfig, DifficultyLevel
from mcq_generator import generate_mcqs

# Define paper
config = PaperConfig(
    paper_name="Test Paper 1",
    total_questions=20,
    section_distribution={
        "Engineering Mathematics": 10,
        "Material Science": 10
    },
    difficulty_distribution={
        "Easy": 0.6,
        "Medium": 0.3,
        "Hard": 0.1
    }
)

# Generate questions
all_questions = []

for section, count in config.section_distribution.items():
    difficulty_counts = config.get_difficulty_counts(count)

    for difficulty_str, diff_count in difficulty_counts.items():
        difficulty = DifficultyLevel[difficulty_str.upper()]

        questions = generate_mcqs(
            subject="Metallurgical Engineering",
            main_topic=section,
            subtopic="General",  # Or iterate through subtopics
            difficulty=difficulty,
            n=diff_count
        )

        all_questions.extend(questions)

# Now export to Excel/CSV (Phase 4)
```

### Phase 3: Multimodal (PDFs + Diagrams)

Next phase will add:
- PDF parsing
- Diagram extraction
- Vision-language model support
- Diagram-based question generation

---

## Questions?

- **Prompt engineering**: See `prompt_templates.py`
- **LLM integration**: See `llm_client.py`
- **Generator logic**: See `mcq_generator.py`
- **Examples**: Run `python3 example_generator.py`

Ready for Phase 3? Let me know!
