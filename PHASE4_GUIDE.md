# Phase 4: Paper Assembly & Web Interface

Complete guide for building exam papers and using the web UI.

---

## Overview

Phase 4 adds:
1. **Paper Assembly System** - Build complete exam papers (~100 MCQs) with section/difficulty distributions
2. **CSV/Excel Export** - Export papers in client's format
3. **Web Interface** - FastAPI backend + HTML/JS frontend for easy paper generation
4. **Question Bank** - Track used questions to prevent duplicates

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Paper Assembly](#paper-assembly)
3. [CSV/Excel Export](#csvexcel-export)
4. [Web Interface](#web-interface)
5. [API Reference](#api-reference)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies for Phase 4:
- `fastapi` - Web API framework
- `uvicorn` - ASGI server
- `aiofiles` - Async file operations
- `openpyxl` - Excel export (optional)

### 2. Test Paper Generation (Python)

```bash
# Run example paper generation
python3 example_paper_generation.py
```

This will:
- Generate 3 example papers (20, 100, and 50 questions)
- Export to CSV and Excel
- Show section and difficulty breakdowns

### 3. Start Web Interface

```bash
# Start API server
python3 api.py
```

Then open: http://localhost:8000

You'll see the web UI for generating papers.

---

## Paper Assembly

### Basic Concept

A **Paper** consists of multiple **Sections**, each with:
- Question count
- Difficulty distribution (Easy/Medium/Hard)
- Topics to cover

### Creating a Paper (Python)

```python
from models import PaperConfig
from paper_builder import PaperBuilder, PaperSection
from csv_exporter import export_paper_to_csv

# 1. Define paper configuration
config = PaperConfig(
    paper_name="Metallurgical Engineering 2026",
    subject="Metallurgical Engineering",
    total_questions=100
)

# 2. Define sections
sections = [
    PaperSection(
        name="Main Subject",
        question_count=60,
        difficulty_distribution={
            "Easy": 40,    # 40 easy questions
            "Medium": 15,  # 15 medium questions
            "Hard": 5      # 5 hard questions
        },
        topics=[
            {"main_topic": "Material Science", "subtopic": "Crystal Structure"},
            {"main_topic": "Thermodynamics", "subtopic": "Phase Diagrams"}
        ]
    ),

    PaperSection(
        name="Aptitude",
        question_count=20,
        difficulty_distribution={
            "Easy": 15,
            "Medium": 5,
            "Hard": 0
        },
        topics=[
            {"main_topic": "Quantitative Aptitude", "subtopic": "Number Systems"}
        ]
    )
]

# 3. Build paper
builder = PaperBuilder()
paper = builder.build_paper(config, sections)

# 4. Export
export_paper_to_csv(paper, "exam_paper.csv")
```

### Paper Structure

```
Paper (100 questions)
├── Main Subject (60 questions)
│   ├── Easy: 40 questions
│   ├── Medium: 15 questions
│   └── Hard: 5 questions
│
├── Aptitude (20 questions)
│   ├── Easy: 15 questions
│   └── Medium: 5 questions
│
├── General Knowledge (10 questions)
│   └── Easy: 10 questions
│
└── Language (10 questions)
    └── Easy: 10 questions
```

### Question Distribution

The system automatically distributes questions across topics:
- If a section has 60 questions and 3 topics
- Each topic gets ~20 questions
- Distributed across Easy/Medium/Hard based on section's difficulty distribution

### Duplicate Prevention

The `QuestionBank` tracks all generated question IDs:
- Questions are never reused across papers
- State is persisted to `question_bank_state.json`
- Clear with caution: `question_bank.clear()`

---

## CSV/Excel Export

### CSV Export

```python
from csv_exporter import export_paper_to_csv

export_paper_to_csv(paper, "output.csv")
```

**CSV Columns** (matching client's template):
```
Test Section | Main Topic | Sub-topic | Difficulty Level | Question ID |
Question (English) | Option A | Option B | Option C | Option D |
Correct Answer | Explanation | References
```

### Excel Export

```python
from csv_exporter import export_paper_to_excel

export_paper_to_excel(paper, "output.xlsx")
```

**Features:**
- Formatted headers (blue background, white text)
- Auto-adjusted column widths
- Text wrapping for long content
- Same columns as CSV

### Export Individual Questions

```python
from csv_exporter import export_questions_to_csv

# Export just a subset of questions
questions = [q1, q2, q3]
export_questions_to_csv(questions, "subset.csv")
```

---

## Web Interface

### Starting the Server

```bash
python3 api.py
```

This starts:
- API server on http://localhost:8000
- Frontend UI at http://localhost:8000
- API docs at http://localhost:8000/docs

### Using the Web UI

**Step 1: Fill Paper Details**
- Paper Name: "Metallurgical Engineering 2026"
- Subject: "Metallurgical Engineering"

**Step 2: Configure First Section**
- Section Name: "Main Subject"
- Total Questions: 60
- Difficulty: Easy=40, Medium=15, Hard=5
- Add Topics: Click "Add Topic" for each topic

**Step 3: Add More Sections**
- Click "Add Section" for Aptitude, GK, Language, etc.
- Configure each section's distribution

**Step 4: Generate**
- Click "Generate Paper"
- Wait for generation (may take several minutes)
- Paper appears in "Generated Papers" list

**Step 5: Download**
- Click "Download CSV" to get the paper
- Open in Excel or import to your system

### Features

✅ **Real-time Generation**
- Shows progress during generation
- Displays loading indicator

✅ **Paper Management**
- List all generated papers
- Download papers as CSV
- Delete old papers

✅ **Section Builder**
- Add unlimited sections
- Custom difficulty per section
- Multiple topics per section

✅ **Validation**
- Checks for empty fields
- Ensures topics are added
- Validates distributions

---

## API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Get Subjects
```http
GET /subjects
```

**Response:**
```json
[
  {
    "name": "Metallurgical Engineering",
    "sections": [
      {
        "name": "Main Subject",
        "topics": [
          {"main_topic": "Material Science", "subtopic": "Crystal Structure"}
        ]
      }
    ]
  }
]
```

#### 2. Generate Paper
```http
POST /generate-paper
Content-Type: application/json

{
  "paper_name": "Exam 2026",
  "subject": "Metallurgical Engineering",
  "sections": [
    {
      "name": "Main Subject",
      "question_count": 60,
      "difficulty_distribution": {
        "Easy": 40,
        "Medium": 15,
        "Hard": 5
      },
      "topics": [
        {"main_topic": "Material Science", "subtopic": "Crystal Structure"}
      ]
    }
  ]
}
```

**Response:**
```json
{
  "paper_id": "uuid",
  "paper_name": "Exam 2026",
  "subject": "Metallurgical Engineering",
  "total_questions": 60,
  "created_at": "2026-02-06T12:00:00"
}
```

#### 3. List Papers
```http
GET /papers
```

**Response:**
```json
[
  {
    "paper_id": "uuid",
    "paper_name": "Exam 2026",
    "subject": "Metallurgical Engineering",
    "total_questions": 100,
    "created_at": "2026-02-06T12:00:00"
  }
]
```

#### 4. Download Paper
```http
GET /download-paper/{paper_id}
```

**Response:** CSV file download

#### 5. Get Paper Details
```http
GET /paper/{paper_id}
```

**Response:** Full paper JSON with all questions

#### 6. Delete Paper
```http
DELETE /paper/{paper_id}
```

**Response:**
```json
{
  "message": "Paper {paper_id} deleted successfully"
}
```

---

## File Structure

```
OfflineQuizWhiz/
├── api.py                      # FastAPI backend
├── paper_builder.py            # Paper assembly logic
├── csv_exporter.py            # CSV/Excel export
├── example_paper_generation.py # Example usage
│
├── static/
│   └── index.html             # Web UI
│
├── generated_papers/          # Generated papers (created automatically)
│   ├── {paper_id}.json       # Paper data
│   ├── {paper_id}.csv        # CSV export
│   └── papers_index.json     # Paper index
│
└── question_bank_state.json  # Tracks used question IDs
```

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
pip install fastapi uvicorn
```

### Error: "No topics specified for section"

**Cause:** Section has no topics added

**Solution:** Add at least one topic to each section:
```python
topics=[
    {"main_topic": "Topic Name", "subtopic": "Subtopic Name"}
]
```

### Error: "Port 8000 already in use"

**Solution:**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn api:app --port 8001
```

### Questions Taking Too Long to Generate

**Cause:** Each question takes ~30-60 seconds with Mistral

**Solutions:**
1. Start with smaller papers (20 questions) for testing
2. Use faster model (if available)
3. Run on GPU server for faster generation
4. Generate sections in parallel (future enhancement)

### Excel Export Not Working

**Cause:** `openpyxl` not installed

**Solution:**
```bash
pip install openpyxl
```

Or use CSV export instead:
```python
export_paper_to_csv(paper, "output.csv")  # Always works
```

### Web UI Shows "Connection Failed"

**Checks:**
1. Is API server running? `python3 api.py`
2. Check console for errors
3. Verify URL: http://localhost:8000
4. Check CORS settings in `api.py`

### Question Bank Growing Too Large

**Solution:** Clear used questions (use carefully!):
```python
from paper_builder import QuestionBank

bank = QuestionBank()
bank.clear()  # Resets all used question IDs
```

---

## Performance Tips

### 1. Generate in Batches
For large papers, generate sections separately:
```python
# Instead of 100 questions at once
# Generate 4 sections of 25 each
```

### 2. Use Mock VLM for Testing
```python
generator = MultimodalMCQGenerator(use_mock=True)
```
Mock VLM is instant (no actual LLM calls)

### 3. Cache Syllabus
Load syllabus once and reuse:
```python
syllabus = parse_docx("syllabus.docx")
# Store in memory for multiple papers
```

### 4. Background Tasks
Use FastAPI background tasks for long operations:
```python
@app.post("/generate-paper")
async def generate_paper(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(builder.build_paper, config, sections)
    return {"status": "generating"}
```

---

## Production Deployment

### Security Checklist

✅ **CORS Configuration**
```python
# In api.py, replace "*" with specific origins
allow_origins=["https://your-domain.com"]
```

✅ **Environment Variables**
```bash
export OLLAMA_HOST="http://your-gpu-server:11434"
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

✅ **Authentication** (add JWT tokens)
```python
from fastapi.security import HTTPBearer
security = HTTPBearer()
```

✅ **Rate Limiting**
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t mcq-generator .
docker run -p 8000:8000 mcq-generator
```

### Systemd Service (Linux)

```ini
# /etc/systemd/system/mcq-api.service
[Unit]
Description=MCQ Generator API
After=network.target

[Service]
Type=simple
User=mcq
WorkingDirectory=/opt/mcq-generator
ExecStart=/usr/bin/python3 api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mcq-api
sudo systemctl start mcq-api
```

---

## Next Steps

✅ **Phase 4 Complete!** You now have:
- Paper assembly system
- CSV/Excel export
- Web interface
- API backend

### Future Enhancements

1. **User Authentication** - Add login/permissions
2. **PDF Upload via Web UI** - Upload PDFs through frontend
3. **Question Review** - Edit/approve questions before export
4. **Templates** - Save paper configurations as templates
5. **Analytics** - Track difficulty distribution, topic coverage
6. **Batch Generation** - Generate multiple papers in one go
7. **Question Pool** - Store and reuse generated questions

### Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review example scripts in `example_*.py` files
3. Check API docs at http://localhost:8000/docs
4. Review console logs for detailed errors

---

**Congratulations!** 🎉

Your MCQ generation system is now complete with:
- ✅ Phase 1: Data models and syllabus parsing
- ✅ Phase 2: Text-based MCQ generation
- ✅ Phase 3: Multimodal (PDF + diagrams)
- ✅ Phase 4: Paper assembly and web interface

You're ready to generate exam papers for your client!
