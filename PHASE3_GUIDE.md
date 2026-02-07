

# Phase 3: Multimodal MCQ Generation - Complete Guide

## Overview

Phase 3 extends the MCQ generator to work with **PDFs containing diagrams, formulas, and graphs**. The system:

1. **Extracts** text and images from PDF documents
2. **Pairs** each diagram with relevant context text
3. **Generates** questions that require interpreting the visual content
4. **Uses** vision-language models (VLMs) locally

---

## What's Been Built

### New Capabilities

✅ **PDF Extraction**
- Extract text and images from any PDF
- Identify diagrams, formulas, graphs
- Extract captions and nearby context
- Filter out small/irrelevant images

✅ **Smart Text-Image Pairing**
- Pair diagrams with captions
- Include nearby paragraphs for context
- Detect formula/diagram types automatically

✅ **Multimodal MCQ Generation**
- Generate questions requiring diagram interpretation
- Support for graphs, phase diagrams, circuits, formulas
- Validate that questions reference visual content

✅ **Mock VLM for Testing**
- Test entire pipeline without a real VLM
- Get dummy responses in correct format

---

## File Structure

```
OfflineQuizWhiz/
# Phase 3: Multimodal
├── multimodal_models.py         # Data structures (ExtractedImage, TextImagePair, etc.)
├── pdf_extractor.py              # PDF → text + images extraction
├── multimodal_prompts.py         # Prompt engineering for VLMs
├── vlm_client.py                 # Vision-language model HTTP client
├── multimodal_generator.py       # Main multimodal generator
└── example_multimodal.py         # Usage examples
```

---

## Installation

### 1. Install Phase 3 Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **PyMuPDF** (fitz) - PDF extraction
- **Pillow** - Image processing

### 2. (Optional) Set Up a Vision-Language Model

**For testing:** Use the built-in MockVLM (no setup needed)

**For production:** You'll need a local VLM. Options:

#### Option A: LLaVA (Recommended for beginners)
```bash
# Install ollama-python (if using Ollama with LLaVA)
pip install ollama

# Pull LLaVA model (if you're using Ollama)
ollama pull llava
```

#### Option B: Qwen-VL (Better quality)
- Download Qwen-VL weights
- Expose via HTTP endpoint (see Qwen-VL documentation)
- Update `vlm_client.py` with your endpoint

---

## Quick Start

### Test Without a Real VLM (Mock Mode)

```python
from example_multimodal import example_3_generate_with_mock

# Runs complete pipeline with mock VLM
example_3_generate_with_mock()
```

**Output:**
```
================================================================================
Generating 1 Medium Multimodal MCQ(s)
...
✅ Successfully generated 1 multimodal question(s)
```

---

## Usage Examples

### Example 1: Extract PDF

```python
from pdf_extractor import extract_pdf

# Extract first 5 pages
pdf_doc = extract_pdf("physics_textbook.pdf", pages=[1, 2, 3, 4, 5])

print(f"Total pages: {pdf_doc.total_pages}")
print(f"Total images: {pdf_doc.total_images}")

# Show pages with diagrams
for page in pdf_doc.get_pages_with_images():
    print(f"\nPage {page.page_number}:")
    print(f"  Text: {len(page.text)} chars")
    print(f"  Images: {len(page.images)}")

    for img in page.images:
        if img.caption:
            print(f"    - {img.caption}")
```

**Output:**
```
📄 Extracting PDF: physics_textbook.pdf
📊 Total pages: 5, Processing: 5

  Processing page 1...
    Text: 2847 chars
    Images: 2
      - Image(page=1, idx=0) (caption: Figure 1.1: Free body diagram...)
      - Image(page=1, idx=1) (caption: Figure 1.2: Force vectors...)

✅ Extracted 5 pages, 8 images
```

### Example 2: Create Text-Image Pairs

```python
from pdf_extractor import extract_pdf, create_text_image_pairs

# Extract PDF
pdf_doc = extract_pdf("materials_science.pdf", pages=[10, 11])

# Create pairs
pairs = create_text_image_pairs(pdf_doc)

for pair in pairs:
    print(f"\nPair from page {pair.page_number}:")
    print(f"  Images: {len(pair.images)}")
    print(f"  Text preview: {pair.text[:200]}...")
```

**Output:**
```
🔗 Creating text-image pairs...
✅ Created 3 text-image pair(s)

Pair from page 10:
  Images: 1
  Text preview: Caption: Figure 10.3: Iron-Carbon phase diagram

Context: The diagram shows equilibrium phases at different temperatures...
```

### Example 3: Generate MCQs (Mock VLM)

```python
from pdf_extractor import extract_pdf, create_text_image_pairs
from multimodal_generator import MultimodalMCQGenerator
from models import DifficultyLevel

# Extract and pair
pdf_doc = extract_pdf("physics.pdf", pages=[5])
pairs = create_text_image_pairs(pdf_doc)

# Generate with mock VLM
generator = MultimodalMCQGenerator(use_mock=True)

questions = generator.generate_from_pair(
    pair=pairs[0],
    subject="Physics",
    main_topic="Thermodynamics",
    subtopic="PV Diagrams",
    difficulty=DifficultyLevel.MEDIUM,
    n=2
)

for q in questions:
    print(f"\nQ: {q.question_text_en}")
    print(f"Correct: {q.correct_answer}")
    print(f"Has diagram: {q.has_diagram}")
```

### Example 4: Generate MCQs (Real VLM)

**Once you have a VLM running (e.g., LLaVA on Ollama):**

```python
from multimodal_generator import MultimodalMCQGenerator
from vlm_client import VLMConfig, VLMClient

# Configure VLM
vlm_config = VLMConfig(
    base_url="http://localhost:11434",  # Ollama endpoint
    model_name="llava",
    temperature=0.7,
    timeout_seconds=180
)

# Create client
vlm_client = VLMClient(config=vlm_config)

# Test connection
vlm_client.test_connection()

# Generate
generator = MultimodalMCQGenerator(vlm_client=vlm_client)

questions = generator.generate_from_pair(
    pair=my_text_image_pair,
    subject="Metallurgical Engineering",
    main_topic="Material Science",
    subtopic="Phase Diagrams - Iron Carbon",
    difficulty=DifficultyLevel.HARD,
    n=3
)
```

---

## How It Works

### 1. PDF Extraction Pipeline

```
PDF File → PyMuPDF → Text blocks + Images → Filtering → Captioning → PDFDocument
```

**Key features:**
- Extracts images with bounding boxes
- Finds captions using pattern matching
- Extracts nearby text for context
- Filters small/irrelevant images

**Code:**
```python
from pdf_extractor import PDFExtractor

extractor = PDFExtractor(
    min_image_size=10000,      # Skip images < 10KB
    min_image_dimension=100     # Skip images < 100px
)

pdf_doc = extractor.extract_pdf("myfile.pdf")
```

### 2. Text-Image Pairing

```
PDFDocument → Pairing Logic → TextImagePair objects
```

**Strategies:**
- **Same-page pairing**: Image + caption + nearby paragraphs
- **Topic detection**: Group by section headings
- **Caption extraction**: "Figure N:", "Diagram:", etc.

**Code:**
```python
from pdf_extractor import TextImagePairer

pairer = TextImagePairer(min_text_length=50)
pairs = pairer.create_pairs(pdf_doc)
```

### 3. Multimodal Prompt Construction

```
TextImagePair → Prompt Builder → VLM Prompt (text + images)
```

**Prompt includes:**
- System instructions for VLM
- Difficulty definitions
- Text context (caption + nearby text)
- Images (as base64)
- Few-shot examples
- JSON output format

**Example prompt structure:**
```
[System] You are an expert question writer...

[Context]
Caption: Figure 3.1: Iron-Carbon phase diagram
Text: The eutectoid point occurs at...

[Images]
Image 1: <base64 data>

[Task] Generate 2 Medium questions requiring the diagram

[Examples]
Example 1: [Complete MCQ referencing diagram]

[Output Format]
JSON array: [{"question_text_en": "...", ...}]
```

### 4. VLM Generation

```
Prompt + Images → VLM → JSON Response → Question Objects
```

**VLM client handles:**
- HTTP requests with multimodal data
- Retry logic
- JSON parsing
- Error handling

---

## Prompt Engineering for VLMs

### Key Principles

1. **Explicitly require diagram interpretation**
   ```
   "The question MUST require looking at the diagram to answer"
   ```

2. **Reference specific visual elements**
   ```
   "According to the graph shown, at what temperature..."
   "Looking at the labeled components in the circuit diagram..."
   ```

3. **Include diagram-specific few-shot examples**
   ```python
   # Example for phase diagrams
   "At what temperature does the eutectoid transformation occur?"
   # (requires reading specific point from diagram)
   ```

4. **Validate questions reference visuals**
   ```python
   # Generator checks for keywords: "shown", "diagram", "figure", etc.
   ```

### Difficulty Calibration

**Easy (Diagram):**
- Direct reading: "What is the value at point X?"
- Label identification: "Which component is labeled A?"

**Medium (Diagram):**
- Relationship interpretation: "Which material has higher toughness based on the stress-strain curves?"
- Comparison: "At 500°C, which phase is stable?"

**Hard (Diagram):**
- Multi-step analysis: "Predict the microstructure after cooling from 850°C to 400°C in 10s"
- Combining visual + theoretical knowledge

---

## Data Structures

### ExtractedImage
```python
@dataclass
class ExtractedImage:
    image_data: bytes          # Raw image
    page_number: int           # Page number (1-indexed)
    image_index: int           # Index on page
    bbox: Tuple[float, ...]    # Bounding box
    format: str                # png, jpeg, etc.
    caption: Optional[str]     # Extracted caption
    nearby_text: Optional[str] # Context text
```

### TextImagePair
```python
@dataclass
class TextImagePair:
    text: str                    # Caption + context
    images: List[ExtractedImage] # One or more images
    page_number: int             # Source page
    topic_hint: Optional[str]    # Detected topic
    source_pdf: Optional[str]    # PDF filename
```

### Question (Extended)
```python
# Standard Question fields plus:
source_pdf: Optional[str]   # Source PDF
has_diagram: bool           # Question uses diagram
```

---

## Configuration

### PDF Extraction Config

```python
from pdf_extractor import PDFExtractor

extractor = PDFExtractor(
    min_image_size=10000,        # Minimum image size (bytes)
    min_image_dimension=100,     # Minimum width/height (pixels)
    extract_vector_graphics=True # Extract vector graphics as images
)
```

### VLM Client Config

```python
from vlm_client import VLMConfig

config = VLMConfig(
    base_url="http://localhost:11435",
    model_name="llava",
    temperature=0.7,
    max_tokens=2048,
    timeout_seconds=180  # VLMs are slower
)
```

---

## Testing Without a VLM

Use **MockVLMClient** for development/testing:

```python
from multimodal_generator import MultimodalMCQGenerator

# Use mock - no real VLM needed!
generator = MultimodalMCQGenerator(use_mock=True)

questions = generator.generate_from_pair(...)
```

**Mock returns:**
- Valid JSON in correct format
- One sample MCQ about phase diagrams
- Useful for testing extraction/pairing pipeline

---

## Setting Up a Real VLM

### Option 1: LLaVA via Ollama (Easiest)

```bash
# Install Ollama (if not already)
brew install ollama

# Pull LLaVA
ollama pull llava

# Run Ollama
ollama serve
```

**Update config:**
```python
from vlm_client import VLMConfig

config = VLMConfig(
    base_url="http://localhost:11434",
    model_name="llava"
)
```

### Option 2: Qwen-VL (Better Quality)

1. Download Qwen-VL weights
2. Run local server (see Qwen-VL docs)
3. Expose HTTP endpoint
4. Update `vlm_client.py` with endpoint format

### Option 3: Custom VLM

Implement your own VLM client by extending `VLMClient`:

```python
class MyVLMClient(VLMClient):
    def _build_payload(self, prompt, images_base64, temperature, max_tokens):
        # Your custom payload format
        return {
            "text": prompt,
            "images": images_base64,
            ...
        }

    def _call_vlm(self, payload):
        # Your custom API call
        ...
```

---

## Troubleshooting

### Problem: No images extracted from PDF

**Solutions:**
1. Check if PDF has actual images (not scanned text)
2. Lower `min_image_size` threshold
3. Check `min_image_dimension` setting
4. Some PDFs have vector graphics - enable `extract_vector_graphics=True`

### Problem: Captions not detected

**Solutions:**
1. Check caption format in PDF (must be near image)
2. Add custom caption patterns in `pdf_extractor.py`:
   ```python
   caption_patterns = [
       r'(Your pattern here)',
       ...
   ]
   ```

### Problem: VLM returns invalid JSON

**Solutions:**
1. Use better VLM model (Qwen-VL > LLaVA)
2. Increase `max_tokens` (try 3000-4000)
3. Simplify prompt (fewer examples)
4. Add JSON schema validation in prompt

### Problem: Questions don't reference diagrams

**Solutions:**
1. Check validation - it requires keywords like "shown", "diagram"
2. Improve few-shot examples to emphasize visual references
3. Add explicit instruction in prompt: "Start question with 'According to the diagram shown...'"

---

## Performance Tips

### PDF Extraction
- **Extract specific pages only**: `extract_pdf("file.pdf", pages=[5, 6, 7])`
- **Adjust filter thresholds** for your PDFs
- **Cache extracted PDFs** - save `PDFDocument` to JSON

### VLM Generation
- **Typical times**: 60-120s per question with diagram
- **Batch questions**: Generate 1-3 per call (not 10+)
- **Image size**: Keep images under 2MB for faster processing
- **Quantized models**: Use 4-bit quantized VLMs for speed

---

## Complete Workflow

### From PDF to Questions

```python
# 1. Extract PDF
from pdf_extractor import extract_pdf, create_text_image_pairs
pdf_doc = extract_pdf("materials_science_ch3.pdf", pages=[10, 11, 12])

# 2. Create pairs
pairs = create_text_image_pairs(pdf_doc)

# 3. Generate questions for each pair
from multimodal_generator import MultimodalMCQGenerator
from models import DifficultyLevel

generator = MultimodalMCQGenerator(use_mock=True)  # or use real VLM

all_questions = []
for pair in pairs:
    questions = generator.generate_from_pair(
        pair=pair,
        subject="Metallurgical Engineering",
        main_topic="Material Science",
        subtopic="Phase Diagrams",
        difficulty=DifficultyLevel.MEDIUM,
        n=2  # 2 questions per diagram
    )
    all_questions.extend(questions)

# 4. Save to JSON
import json
with open("diagram_questions.json", 'w') as f:
    json.dump([q.to_dict() for q in all_questions], f, indent=2)

print(f"Generated {len(all_questions)} diagram-based questions!")
```

---

## Next Steps

### Immediate (Testing)
1. ✅ Run `python3 example_multimodal.py` with mock VLM
2. ✅ Extract a sample PDF
3. ✅ Inspect text-image pairs
4. ✅ Generate test questions

### This Week (Production)
5. Install PyMuPDF: `pip install PyMuPDF`
6. Extract your actual physics/engineering PDFs
7. Set up LLaVA or Qwen-VL locally
8. Generate real diagram-based questions

### Phase 4 (Web UI)
- FastAPI backend
- Upload PDFs via web interface
- SME review of generated questions
- Export to Excel/CSV
- Docker packaging

---

## Summary

You now have a **complete multimodal pipeline**:

✅ **Extract** text and diagrams from PDFs
✅ **Pair** images with context intelligently
✅ **Generate** questions requiring diagram interpretation
✅ **Validate** that questions reference visual content
✅ **Test** entire pipeline with mock VLM

**Ready to generate diagram-based questions!** 🚀

See `example_multimodal.py` for working code examples.
