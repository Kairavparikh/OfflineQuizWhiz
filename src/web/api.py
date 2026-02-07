"""
FastAPI backend for MCQ generation system.

Endpoints:
- GET /subjects - List available subjects and topics
- POST /generate-paper - Generate a complete exam paper
- GET /download-paper/{paper_id} - Download paper as CSV
- GET /papers - List all generated papers
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import uuid
from datetime import datetime
import tempfile
import shutil

from src.models.models import DifficultyLevel, Question, PaperConfig
from src.paper_builder import Paper, PaperBuilder, PaperSection, QuestionBank
from src.exporters.csv_exporter import export_paper_to_csv
from src.extractors.pdf_extractor import extract_pdf, create_text_image_pairs
from src.generators.mcq_generator import generate_mcqs


# Pydantic models for API requests/responses
class TopicSpec(BaseModel):
    """Topic specification for paper generation."""
    main_topic: str
    subtopic: str


class SectionRequest(BaseModel):
    """Section configuration for paper generation."""
    name: str = Field(..., description="Section name (e.g., 'Main Subject', 'Aptitude')")
    question_count: int = Field(..., ge=1, le=200, description="Number of questions")
    difficulty_distribution: Dict[str, int] = Field(
        ...,
        description="Difficulty distribution, e.g., {'Easy': 40, 'Medium': 15, 'Hard': 5}"
    )
    topics: List[TopicSpec] = Field(..., description="Topics to cover in this section")


class GeneratePaperRequest(BaseModel):
    """Request body for generating a paper."""
    paper_name: str = Field(..., description="Name of the exam paper")
    subject: str = Field(..., description="Subject/exam area")
    sections: List[SectionRequest] = Field(..., description="Section configurations")


class PaperSummary(BaseModel):
    """Summary of a generated paper."""
    paper_id: str
    paper_name: str
    subject: str
    total_questions: int
    created_at: str


class SubjectInfo(BaseModel):
    """Subject information with sections and topics."""
    name: str
    sections: List[Dict[str, Any]]


# Initialize FastAPI app
app = FastAPI(
    title="MCQ Generation API",
    description="API for generating exam papers with MCQs",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state
PAPERS_DIR = Path("generated_papers")
PAPERS_DIR.mkdir(exist_ok=True)

PAPERS_INDEX_FILE = PAPERS_DIR / "papers_index.json"

question_bank = QuestionBank()


def load_papers_index() -> Dict[str, PaperSummary]:
    """Load index of generated papers."""
    if PAPERS_INDEX_FILE.exists():
        with open(PAPERS_INDEX_FILE, 'r') as f:
            data = json.load(f)
            return {k: PaperSummary(**v) for k, v in data.items()}
    return {}


def save_papers_index(papers: Dict[str, PaperSummary]):
    """Save index of generated papers."""
    with open(PAPERS_INDEX_FILE, 'w') as f:
        json.dump({k: v.dict() for k, v in papers.items()}, f, indent=2)


@app.get("/", response_class=HTMLResponse)
def root():
    """Serve the PDF upload UI."""
    # Use __file__ to get path relative to this api.py file
    api_dir = Path(__file__).parent
    upload_file = api_dir / "static" / "upload.html"

    if upload_file.exists():
        with open(upload_file, 'r') as f:
            return f.read()
    else:
        # Fallback to API info
        return """
        <html>
            <body>
                <h1>MCQ Generation API</h1>
                <p>Version: 1.0.0</p>
                <p>Upload file not found at: {}</p>
                <ul>
                    <li><a href="/docs">API Documentation</a></li>
                    <li><a href="/subjects">Subjects</a></li>
                    <li><a href="/papers">Papers</a></li>
                </ul>
            </body>
        </html>
        """.format(upload_file)


@app.get("/api")
def api_info():
    """API information endpoint."""
    return {
        "message": "MCQ Generation API",
        "version": "1.0.0",
        "endpoints": {
            "upload_pdf": "/upload-pdf (POST)",
            "subjects": "/subjects",
            "generate_paper": "/generate-paper (POST)",
            "download_paper": "/download-paper/{paper_id}",
            "papers": "/papers"
        }
    }


def parse_syllabus_from_text(text: str) -> List[Dict[str, str]]:
    """
    Parse syllabus text to extract topics and subtopics.

    Uses pattern matching to identify:
    - Main topics (numbered, bold, or headers)
    - Subtopics (nested bullets, indented items)

    Returns:
        List of dicts with 'main_topic' and 'subtopic' keys
    """
    import re

    topics = []
    lines = text.split('\n')

    current_main_topic = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if this is a main topic (numbered like "1.", "I.", or bold headers)
        # Pattern: starts with number/roman numeral followed by dot or parenthesis
        main_topic_match = re.match(r'^(?:\d+\.?|\(?[IVXivx]+\)|[A-Z]\.)\s+(.+)', line)

        if main_topic_match:
            current_main_topic = main_topic_match.group(1).strip()
            # Clean up common formatting
            current_main_topic = re.sub(r'[:\-–—]$', '', current_main_topic).strip()
            topics.append({
                'main_topic': current_main_topic,
                'subtopic': 'General Concepts'
            })
        # Check if this is a subtopic (starts with bullet, dash, or lowercase letter)
        elif current_main_topic:
            subtopic_match = re.match(r'^(?:[-•●○►▪]|\(?[a-z]\)|\d+\.\d+)\s+(.+)', line)
            if subtopic_match:
                subtopic = subtopic_match.group(1).strip()
                subtopic = re.sub(r'[:\-–—]$', '', subtopic).strip()
                topics.append({
                    'main_topic': current_main_topic,
                    'subtopic': subtopic
                })

    # If no structure found, try simpler approach - each non-empty line is a topic
    if not topics:
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:  # Skip very short lines
                topics.append({
                    'main_topic': line[:50],  # Use first 50 chars as topic
                    'subtopic': 'General Concepts'
                })

    return topics


@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    subject: str = Form("General"),
    num_questions: int = Form(5),
    difficulty: str = Form("MEDIUM"),
    mode: str = Form("content")
):
    """
    Upload a PDF and generate MCQs from it.

    This endpoint supports two modes:

    1. CONTENT MODE (default):
       - Extracts text and images from PDF
       - Generates MCQs based on the actual content

    2. SYLLABUS MODE:
       - Parses PDF as a syllabus/curriculum
       - Identifies topics and subtopics
       - Generates questions for each topic area

    Args:
        file: PDF file
        subject: Subject/topic name
        num_questions: Total questions to generate
        difficulty: Easy/Medium/Hard
        mode: "content" or "syllabus"
    """
    try:
        print(f"\n{'='*80}")
        print(f"PDF UPLOAD: {file.filename}")
        print(f"{'='*80}")
        print(f"Subject: {subject}")
        print(f"Questions: {num_questions}")
        print(f"Difficulty: {difficulty}")
        print(f"Mode: {mode}")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name

        try:
            # Extract PDF content
            print(f"\n📄 Extracting content from PDF...")
            pdf_doc = extract_pdf(tmp_path, pages=None)  # Extract all pages
            print(f"   ✅ Extracted {pdf_doc.total_pages} pages, {pdf_doc.total_images} images")

            # Parse difficulty
            try:
                difficulty_level = DifficultyLevel[difficulty.upper()]
            except KeyError:
                difficulty_level = DifficultyLevel.MEDIUM

            # Generate questions
            print(f"\n🤖 Generating {num_questions} questions...")
            questions = []

            # Handle based on mode
            if mode == "syllabus":
                # SYLLABUS MODE: Parse topics and generate questions for each topic
                print(f"\n📋 SYLLABUS MODE: Parsing topics from PDF...")

                # Extract text from all pages
                full_text = "\n".join([page.text for page in pdf_doc.pages])

                # Parse syllabus to extract topics
                topics = parse_syllabus_from_text(full_text)
                print(f"   ✅ Found {len(topics)} topic(s)")

                if not topics:
                    raise ValueError("No topics found in syllabus. Please check PDF format.")

                # Display first few topics
                for i, topic in enumerate(topics[:5], 1):
                    print(f"      {i}. {topic['main_topic']} → {topic['subtopic']}")
                if len(topics) > 5:
                    print(f"      ... and {len(topics) - 5} more")

                # Distribute questions across topics
                questions_per_topic = max(1, num_questions // len(topics))
                remaining_questions = num_questions

                print(f"\n🤖 Generating ~{questions_per_topic} question(s) per topic...")

                for i, topic in enumerate(topics):
                    if remaining_questions <= 0:
                        break

                    # Generate questions for this topic
                    n = min(questions_per_topic, remaining_questions)

                    try:
                        topic_questions = generate_mcqs(
                            subject=subject,
                            main_topic=topic['main_topic'],
                            subtopic=topic['subtopic'],
                            difficulty=difficulty_level,
                            n=n
                        )

                        questions.extend(topic_questions)
                        remaining_questions -= len(topic_questions)
                        print(f"   ✅ Generated {len(topic_questions)} for {topic['main_topic']}")

                    except Exception as e:
                        print(f"   ⚠️  Failed for {topic['main_topic']}: {e}")
                        continue

            else:
                # CONTENT MODE: Generate from actual PDF content
                print(f"\n📄 CONTENT MODE: Analyzing PDF content...")

                # Create text-image pairs for multimodal generation
                pairs = create_text_image_pairs(pdf_doc)
                print(f"   ✅ Created {len(pairs)} text-image pair(s)")

                questions = []

                # If we have diagram pairs, use multimodal generation
                if pairs and len(pairs) > 0:
                    builder = PaperBuilder(question_bank=question_bank, use_real_vlm=True)

                    # Generate questions from first few pairs
                    questions_per_pair = max(1, num_questions // len(pairs))

                    for i, pair in enumerate(pairs[:num_questions]):
                        try:
                            pair_questions = builder.multimodal_generator.generate_from_pair(
                                pair=pair,
                                subject=subject,
                                main_topic=subject,
                                subtopic="Content Analysis",
                                difficulty=difficulty_level,
                                n=min(questions_per_pair, num_questions - len(questions))
                            )
                            questions.extend(pair_questions)
                            print(f"   ✅ Generated {len(pair_questions)} questions from pair {i+1}")

                            if len(questions) >= num_questions:
                                break
                        except Exception as e:
                            print(f"   ⚠️  Failed to generate from pair {i+1}: {e}")
                            continue

                # Fill remaining with text-based questions
                if len(questions) < num_questions:
                    remaining = num_questions - len(questions)
                    print(f"   Generating {remaining} additional text-based questions...")

                    # Extract some text content for context
                    text_content = ""
                    for page in pdf_doc.pages[:3]:  # Use first 3 pages
                        text_content += page.text[:500] + "\n"

                    text_questions = generate_mcqs(
                        subject=subject,
                        main_topic=subject,
                        subtopic="PDF Content",
                        difficulty=difficulty_level,
                        n=remaining
                    )
                    questions.extend(text_questions)
                    print(f"   ✅ Generated {len(text_questions)} text-based questions")

            # Trim to exact number requested
            questions = questions[:num_questions]

            # Create paper
            paper_id = str(uuid.uuid4())
            paper = Paper(
                paper_id=paper_id,
                paper_name=f"PDF Upload - {file.filename}",
                subject=subject,
                questions=questions,
                created_at=datetime.now().isoformat()
            )

            # Save paper
            paper_file = PAPERS_DIR / f"{paper_id}.json"
            with open(paper_file, 'w') as f:
                json.dump(paper.to_dict(), f, indent=2)

            # Export to CSV
            csv_file = PAPERS_DIR / f"{paper_id}.csv"
            export_paper_to_csv(paper, str(csv_file))

            # Update papers index
            papers_index = load_papers_index()
            summary = PaperSummary(
                paper_id=paper_id,
                paper_name=paper.paper_name,
                subject=paper.subject,
                total_questions=len(paper.questions),
                created_at=paper.created_at
            )
            papers_index[paper_id] = summary
            save_papers_index(papers_index)

            print(f"\n✅ Paper generated successfully!")
            print(f"   Paper ID: {paper_id}")
            print(f"   Questions: {len(questions)}")
            print(f"{'='*80}\n")

            # Return results
            return {
                "paper_id": paper_id,
                "paper_name": paper.paper_name,
                "total_questions": len(questions),
                "questions": [q.to_dict() for q in questions]
            }

        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.get("/subjects", response_model=List[SubjectInfo])
def get_subjects():
    """
    Get available subjects and topics from syllabus.

    This endpoint looks for syllabus JSON files in the current directory.
    """
    syllabus_files = list(Path(".").glob("*syllabus*.json"))

    if not syllabus_files:
        # Return sample structure if no syllabus found
        return [
            SubjectInfo(
                name="Sample Subject",
                sections=[
                    {
                        "name": "Main Subject",
                        "topics": [
                            {"main_topic": "Topic 1", "subtopic": "Subtopic 1"},
                            {"main_topic": "Topic 2", "subtopic": "Subtopic 2"}
                        ]
                    },
                    {
                        "name": "Aptitude",
                        "topics": [
                            {"main_topic": "Quantitative Aptitude", "subtopic": "Number Systems"}
                        ]
                    }
                ]
            )
        ]

    # Parse first syllabus file found
    syllabus_file = syllabus_files[0]

    try:
        with open(syllabus_file, 'r') as f:
            data = json.load(f)

        # Convert to SubjectInfo format
        subjects = []
        for subject_data in data.get('subjects', []):
            sections = []
            for section in subject_data.get('sections', []):
                topics = []
                for topic in section.get('topics', []):
                    for subtopic in topic.get('subtopics', []):
                        topics.append({
                            "main_topic": topic['name'],
                            "subtopic": subtopic['name']
                        })

                sections.append({
                    "name": section['name'],
                    "topics": topics
                })

            subjects.append(SubjectInfo(
                name=subject_data['name'],
                sections=sections
            ))

        return subjects

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing syllabus: {str(e)}")


@app.post("/generate-paper", response_model=PaperSummary)
def generate_paper(request: GeneratePaperRequest, background_tasks: BackgroundTasks):
    """
    Generate a complete exam paper.

    This endpoint:
    1. Converts request to internal format
    2. Generates questions for each section
    3. Exports to CSV
    4. Returns paper summary

    Note: Question generation may take several minutes depending on paper size.
    """
    try:
        print(f"\n{'='*80}")
        print(f"API: Generating paper '{request.paper_name}'")
        print(f"{'='*80}")

        # Convert request to internal format
        from models import PaperConfig

        total_questions = sum(s.question_count for s in request.sections)

        config = PaperConfig(
            paper_name=request.paper_name,
            subject=request.subject,
            total_questions=total_questions
        )

        sections = []
        for section_req in request.sections:
            topics = [
                {"main_topic": t.main_topic, "subtopic": t.subtopic}
                for t in section_req.topics
            ]

            section = PaperSection(
                name=section_req.name,
                question_count=section_req.question_count,
                difficulty_distribution=section_req.difficulty_distribution,
                topics=topics
            )
            sections.append(section)

        # Generate paper (use real VLM for diagram-based questions)
        builder = PaperBuilder(question_bank=question_bank, use_real_vlm=True)
        paper = builder.build_paper(config, sections)

        # Save paper JSON
        paper_file = PAPERS_DIR / f"{paper.paper_id}.json"
        with open(paper_file, 'w') as f:
            json.dump(paper.to_dict(), f, indent=2)

        # Export to CSV
        csv_file = PAPERS_DIR / f"{paper.paper_id}.csv"
        export_paper_to_csv(paper, str(csv_file))

        # Update papers index
        papers_index = load_papers_index()
        summary = PaperSummary(
            paper_id=paper.paper_id,
            paper_name=paper.paper_name,
            subject=paper.subject,
            total_questions=len(paper.questions),
            created_at=paper.created_at
        )
        papers_index[paper.paper_id] = summary
        save_papers_index(papers_index)

        print(f"\n✅ Paper generated successfully!")
        print(f"   Paper ID: {paper.paper_id}")
        print(f"   Questions: {len(paper.questions)}")

        return summary

    except Exception as e:
        print(f"\n❌ Error generating paper: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating paper: {str(e)}")


@app.get("/papers", response_model=List[PaperSummary])
def list_papers():
    """
    List all generated papers.

    Returns summaries of all papers that have been generated.
    """
    papers_index = load_papers_index()
    return list(papers_index.values())


@app.get("/download-paper/{paper_id}")
def download_paper(paper_id: str):
    """
    Download a generated paper as CSV.

    Args:
        paper_id: UUID of the paper to download

    Returns:
        CSV file with all questions
    """
    csv_file = PAPERS_DIR / f"{paper_id}.csv"

    if not csv_file.exists():
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

    # Get paper name for filename
    papers_index = load_papers_index()
    paper_summary = papers_index.get(paper_id)

    if paper_summary:
        # Use paper name in filename
        filename = f"{paper_summary.paper_name.replace(' ', '_')}.csv"
    else:
        filename = f"paper_{paper_id}.csv"

    return FileResponse(
        path=csv_file,
        media_type="text/csv",
        filename=filename
    )


@app.get("/paper/{paper_id}")
def get_paper(paper_id: str):
    """
    Get complete paper details including all questions.

    Args:
        paper_id: UUID of the paper

    Returns:
        Complete paper data
    """
    paper_file = PAPERS_DIR / f"{paper_id}.json"

    if not paper_file.exists():
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

    with open(paper_file, 'r') as f:
        paper_data = json.load(f)

    return paper_data


@app.delete("/paper/{paper_id}")
def delete_paper(paper_id: str):
    """
    Delete a generated paper.

    Args:
        paper_id: UUID of the paper to delete
    """
    paper_file = PAPERS_DIR / f"{paper_id}.json"
    csv_file = PAPERS_DIR / f"{paper_id}.csv"

    if not paper_file.exists():
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

    # Delete files
    paper_file.unlink()
    if csv_file.exists():
        csv_file.unlink()

    # Update index
    papers_index = load_papers_index()
    if paper_id in papers_index:
        del papers_index[paper_id]
        save_papers_index(papers_index)

    return {"message": f"Paper {paper_id} deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("MCQ GENERATION API SERVER")
    print("="*80)
    print("\nStarting server...")
    print("  - API docs: http://localhost:8000/docs")
    print("  - Health check: http://localhost:8000/")
    print("\nPress Ctrl+C to stop")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
