# Getting Started with OfflineQuizWhiz

Complete setup and usage guide for the MCQ generation system.

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt
```

### 2. Start Ollama (for Question Generation)

```bash
# Make sure Ollama is running with Mistral
ollama serve

# In another terminal, verify model is available
ollama list
```

You should see `mistral:latest` in the list.

### 3. Start the Web Interface

```bash
# Start the API server
python3 api.py
```

Open http://localhost:8000 in your browser.

### 4. Generate Your First Paper

In the web UI:
1. **Paper Name**: "Test Exam 2026"
2. **Subject**: "Test Subject"
3. **Section 1**:
   - Name: "Main Subject"
   - Questions: 10
   - Easy: 6, Medium: 3, Hard: 1
4. **Add a Topic**:
   - Main Topic: "General Knowledge"
   - Subtopic: "Basic Concepts"
5. Click **"Generate Paper"**
6. Wait 5-10 minutes (question generation takes time)
7. Click **"Download CSV"** when complete

**You now have a complete exam paper!** ✅

---

## 📋 System Components

### Phase 1: Data Models ✅
- Structured syllabus (Subject → Section → Topic → SubTopic)
- Question data model with validation
- Paper configuration

### Phase 2: Text-Based Generation ✅
- MCQ generation using Mistral/Ollama
- Difficulty-aware prompts (Easy/Medium/Hard)
- Automatic validation and retry

### Phase 3: Multimodal (PDF + Diagrams) ✅
- PDF extraction with PyMuPDF
- Diagram caption detection
- Vision-language model support
- Diagram-based MCQ generation

### Phase 4: Paper Assembly & Web UI ✅
- Complete paper assembly (~100 questions)
- Section and difficulty distribution
- CSV/Excel export
- Web interface for easy paper generation

---

## 🎯 Common Use Cases

### Use Case 1: Generate Text-Only Questions

```bash
python3 -c "
from models import DifficultyLevel
from mcq_generator import generate_mcqs

questions = generate_mcqs(
    subject='Physics',
    main_topic='Mechanics',
    subtopic='Newton\'s Laws',
    difficulty=DifficultyLevel.MEDIUM,
    n=5
)

for q in questions:
    print(f'Q: {q.question_text_en}')
    print(f'Answer: {q.correct_answer}')
    print()
"
```

### Use Case 2: Extract Diagrams from PDF

```bash
# Place your PDF in the current directory as 'test.pdf'
python3 test_pdf_extraction.py test.pdf
```

This will:
- Extract diagrams from the PDF
- Save them as `extracted_page1_img1.png`, etc.
- Show captions and context

### Use Case 3: Generate Full Exam Paper

```bash
# Run the example paper generation
python3 example_paper_generation.py
```

This demonstrates:
- 20-question basic paper
- 100-question full exam with multiple sections
- Custom difficulty distributions

### Use Case 4: Use Web UI (Recommended)

```bash
# Start server
python3 api.py

# Open browser to http://localhost:8000
# Use the web UI to configure and generate papers
```

---

## 📁 Key Files

### Configuration
- `config.py` - LLM settings (model name, endpoint, temperature)
- `requirements.txt` - Python dependencies

### Core Modules
- `models.py` - Data structures (Question, Subject, etc.)
- `mcq_generator.py` - Text-based MCQ generation
- `multimodal_generator.py` - Diagram-based MCQ generation
- `paper_builder.py` - Paper assembly system
- `csv_exporter.py` - Export to CSV/Excel

### Web Interface
- `api.py` - FastAPI backend
- `static/index.html` - Frontend UI

### Testing
- `test_models.py` - Test data models
- `test_phase2.py` - Test text generation
- `test_pdf_extraction.py` - Test PDF extraction
- `test_full_pipeline.py` - Test complete workflow
- `run_all_tests.py` - Run all tests

### Examples
- `example_usage.py` - Phase 1 examples
- `example_generator.py` - Phase 2 examples
- `example_multimodal.py` - Phase 3 examples
- `example_paper_generation.py` - Phase 4 examples

### Documentation
- `README.md` - Project overview
- `START_HERE.md` - Original quick start
- `PHASE2_GUIDE.md` - Text generation guide
- `PHASE3_GUIDE.md` - Multimodal guide
- `PHASE4_GUIDE.md` - Paper assembly & web UI guide
- `GETTING_STARTED.md` - This file

---

## 🔧 Configuration

### LLM Settings

Edit `config.py`:

```python
DEFAULT_LLM_CONFIG = LLMConfig(
    base_url="http://localhost:11434",  # Ollama endpoint
    model_name="mistral",                # Model to use
    temperature=0.7,                     # Creativity (0.0-1.0)
    max_tokens=2048                      # Max response length
)
```

### Question Generation Settings

In `config.py`:

```python
GENERATION_CONFIG = GenerationConfig(
    max_retries=3,           # Retry failed generations
    retry_delay_seconds=2,   # Wait between retries
    timeout_seconds=180      # Max time per question
)
```

### Paper Builder Settings

When creating papers:

```python
# Default difficulty distribution
difficulty_distribution = {
    "Easy": 0.60,    # 60% easy
    "Medium": 0.30,  # 30% medium
    "Hard": 0.10     # 10% hard
}
```

---

## 🧪 Testing

### Test Everything

```bash
# Run complete test suite
python3 run_all_tests.py
```

This tests:
- ✅ Phase 1: Data models
- ✅ Phase 2: Text generation (with Mistral)
- ✅ Phase 3: Multimodal pipeline (mock VLM)

### Test Individual Components

```bash
# Test data models (no dependencies)
python3 test_models.py

# Test text-based generation
python3 test_phase2.py

# Test PDF extraction
python3 test_pdf_extraction.py test.pdf

# Test full pipeline
python3 test_full_pipeline.py
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
pip install -r requirements.txt
```

### "Connection failed to Ollama"

**Check:**
1. Is Ollama running? `ollama serve`
2. Is Mistral installed? `ollama list`
3. If not: `ollama pull mistral`

### "404 Not Found" when generating

**Cause:** Wrong model name in config

**Solution:** Edit `config.py`, line 18:
```python
model_name: str = "mistral"  # Use model from 'ollama list'
```

### Questions are low quality

**Try:**
1. Use `temperature=0.5` for more focused responses
2. Add more few-shot examples in `prompt_templates.py`
3. Use better base model (e.g., `llama2:13b` instead of `7b`)

### Web UI shows "Connection Failed"

**Check:**
1. Is API running? `python3 api.py`
2. Check URL: http://localhost:8000 (not 8080, 3000, etc.)
3. Check browser console for errors (F12)

### Paper generation takes too long

**Normal:** Each question takes ~30-60 seconds with Mistral-7B

**To speed up:**
1. Use GPU server for faster generation
2. Start with smaller papers (10-20 questions)
3. Use parallel generation (future enhancement)

### Excel export not working

**Solution:**
```bash
pip install openpyxl
```

Or use CSV export instead (always works).

---

## 📊 Understanding Output

### CSV Export Format

```csv
Test Section,Main Topic,Sub-topic,Difficulty Level,Question ID,Question (English),Option A,Option B,Option C,Option D,Correct Answer,Explanation,References
Main Subject,Material Science,Crystal Structure,Medium,abc-123,What is the coordination number...,12,8,6,4,A,In FCC structure...,Callister Chapter 3
```

### Question Validation

Each question is validated for:
- ✅ All 4 options are non-empty and distinct
- ✅ Correct answer is A, B, C, or D
- ✅ Explanation is ≥20 characters
- ✅ Metadata (section, topic, subtopic) is present

Invalid questions are automatically regenerated.

---

## 🎓 Best Practices

### 1. Start Small
- Test with 10-20 questions before generating 100
- Verify quality of generated questions
- Adjust prompts if needed

### 2. Use Appropriate Difficulty
- **Easy**: Direct recall, definitions (e.g., "What is the formula for...")
- **Medium**: Application, 1-2 steps (e.g., "Calculate the value when...")
- **Hard**: Multi-step reasoning (e.g., "Given conditions A, B, C, determine...")

### 3. Topic Distribution
- More topics = better coverage but fewer questions per topic
- Fewer topics = deeper coverage of specific areas

### 4. Review Before Export
- Check generated questions for accuracy
- Verify explanations are clear
- Ensure references are relevant

### 5. Question Bank Management
- Track used questions to avoid duplicates
- Clear question bank when starting fresh:
  ```python
  from paper_builder import QuestionBank
  bank = QuestionBank()
  bank.clear()
  ```

---

## 🚢 Production Deployment

### For Client Deployment

1. **Install on GPU server** for faster generation
2. **Set up Ollama** with larger model (13B or 70B)
3. **Configure CORS** in `api.py` for specific origin
4. **Add authentication** (JWT tokens)
5. **Set up systemd service** for auto-start
6. **Use reverse proxy** (nginx) for HTTPS
7. **Add rate limiting** to prevent abuse

See `PHASE4_GUIDE.md` for detailed production setup.

---

## 📚 Additional Resources

### Documentation
- `README.md` - Project overview
- `PHASE2_GUIDE.md` - Complete text generation guide (15 pages)
- `PHASE3_GUIDE.md` - Complete multimodal guide (15 pages)
- `PHASE4_GUIDE.md` - Complete paper assembly guide

### API Documentation
Start the server and visit:
- http://localhost:8000/docs - Interactive API docs (Swagger)
- http://localhost:8000/redoc - Alternative API docs

### Example Scripts
- `example_usage.py` - Basic usage
- `example_generator.py` - Text generation
- `example_multimodal.py` - PDF + diagrams
- `example_paper_generation.py` - Complete papers

---

## 🎉 You're Ready!

Your MCQ generation system is fully set up and ready to use.

### Next Steps:

1. ✅ Test with small papers (10-20 questions)
2. ✅ Review generated questions for quality
3. ✅ Adjust prompts/settings if needed
4. ✅ Generate full exam papers (100 questions)
5. ✅ Export to CSV for client
6. ✅ Deploy to production server

### Need Help?

- Check troubleshooting section above
- Review detailed guides (PHASE2/3/4_GUIDE.md)
- Check API docs at /docs endpoint
- Review example scripts

**Happy generating!** 🚀
