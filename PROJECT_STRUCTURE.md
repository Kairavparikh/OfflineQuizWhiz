# OfflineQuizWhiz - Project Structure

## Directory Organization

```
OfflineQuizWhiz/
├── README.md                  # Main project documentation
├── requirements.txt           # Python dependencies
├── run_server.py             # Main entry point for API server
│
├── src/                      # Source code
│   ├── models/              # Data models
│   │   ├── models.py        # Core Question, Subject, etc.
│   │   └── multimodal_models.py  # Image, PDF models
│   │
│   ├── generators/          # Question generators
│   │   ├── mcq_generator.py      # Text-based MCQ generation
│   │   ├── multimodal_generator.py  # Image-based MCQ generation
│   │   ├── llm_client.py         # Ollama LLM client (Mistral)
│   │   ├── vlm_client.py         # Ollama VLM client (LLaVA)
│   │   ├── prompt_templates.py   # Text prompts
│   │   └── multimodal_prompts.py # Vision prompts
│   │
│   ├── extractors/          # PDF extraction
│   │   └── pdf_extractor.py      # Extract text + images from PDFs
│   │
│   ├── exporters/           # Export utilities
│   │   └── csv_exporter.py       # Export to CSV/Excel
│   │
│   ├── web/                 # Web interface
│   │   ├── api.py                # FastAPI backend
│   │   └── static/               # Frontend HTML/CSS/JS
│   │
│   ├── paper_builder.py     # Assemble complete exam papers
│   ├── syllabus_parser.py   # Parse syllabus JSON
│   └── config.py            # Configuration
│
├── tests/                   # Test files
│   ├── verify_setup.py      # System verification
│   ├── test_models.py       # Model tests
│   ├── test_generate.py     # Generation tests
│   ├── test_pdf_extraction.py  # PDF tests
│   ├── test_vlm_with_pdf.py    # VLM tests
│   └── ...
│
├── examples/                # Example scripts
│   ├── example_usage.py     # Basic usage
│   ├── example_generator.py # Generator examples
│   ├── example_multimodal.py # Multimodal examples
│   ├── example_paper_generation.py # Paper generation
│   └── ...
│
├── docs/                    # Documentation
│   ├── GETTING_STARTED.md   # Quick start guide
│   ├── QUICKSTART.md        # Quick reference
│   ├── START_HERE.md        # Introduction
│   ├── PHASE2_GUIDE.md      # Text generation guide
│   ├── PHASE3_GUIDE.md      # Multimodal guide
│   ├── PHASE4_GUIDE.md      # Paper assembly guide
│   ├── VLM_SETUP_COMPLETE.md # VLM setup docs
│   └── SYSTEM_READY.md      # System status
│
├── data/                    # Sample data
│   ├── sample_syllabus.json # Example syllabus
│   └── test.pdf             # Test PDF
│
├── output/                  # Generated files
│   ├── generated_papers/    # Paper JSON and CSV files
│   ├── question_bank_state.json  # Used question tracking
│   └── *.csv                # Generated CSV files
│
└── logs/                    # Log files
    └── *.log
```

## Key Files

### Entry Points

- **run_server.py** - Start the web server
  ```bash
  python3 run_server.py
  ```

- **examples/example_usage.py** - Basic CLI usage examples

### Core Modules

- **src/models/** - All data structures (Question, Subject, etc.)
- **src/generators/** - Question generation logic
- **src/paper_builder.py** - Assembles complete exam papers
- **src/web/api.py** - REST API and web interface

### Testing

- **tests/verify_setup.py** - Check system requirements
- **tests/test_vlm_with_pdf.py** - Test VLM with real PDF
- **tests/run_all_tests.py** - Run all tests

## Import Structure

All imports now use the `src.` prefix:

```python
from src.models.models import Question, DifficultyLevel
from src.generators.mcq_generator import generate_mcqs
from src.paper_builder import PaperBuilder
from src.exporters.csv_exporter import export_paper_to_csv
```

## Running the System

### 1. Start API Server
```bash
python3 run_server.py
```
Then open http://localhost:8000

### 2. Run Tests
```bash
python3 tests/verify_setup.py
python3 tests/test_vlm_with_pdf.py
```

### 3. Run Examples
```bash
python3 examples/example_usage.py
python3 examples/example_paper_generation.py
```

## Output Files

All generated files go to `output/`:
- Papers: `output/generated_papers/<paper_id>.json` and `.csv`
- Question bank state: `output/question_bank_state.json`
- Extracted images: `output/extracted_*.jpeg`

## Logs

All logs go to `logs/`:
- API server logs: `logs/api_server.log`
- Generation logs: `logs/paper_generation_output.txt`
