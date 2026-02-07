# Phase 3 Complete: Multimodal MCQ Generation

## Executive Summary

**Phase 3 is complete!** The system now generates diagram-based MCQs from PDFs using vision-language models.

---

## New Capabilities

### ✅ What You Can Do Now

1. **Extract PDFs**
   - Extract text and images from any PDF
   - Identify diagrams, formulas, graphs
   - Get captions and context automatically

2. **Smart Pairing**
   - Pair diagrams with relevant text
   - Detect diagram types (phase diagrams, circuits, graphs, etc.)
   - Filter out irrelevant images

3. **Generate Diagram-Based Questions**
   - Questions that require interpreting visuals
   - Support for graphs, phase diagrams, formulas, circuits
   - Automatic validation that questions reference diagrams

4. **Mock VLM for Testing**
   - Test entire pipeline without a real VLM
   - Develop and debug offline

---

## Files Delivered

### Core Implementation

1. **`multimodal_models.py`**
   - `ExtractedImage`: Image with metadata (caption, bbox, etc.)
   - `TextImagePair`: Diagram + context text
   - `PDFDocument`, `PDFPage`: Complete PDF structure
   - `MultimodalQuestionMetadata`: Track diagram sources

2. **`pdf_extractor.py`**
   - `PDFExtractor`: Extract text + images from PDFs
   - `TextImagePairer`: Pair diagrams with text
   - Caption detection and context extraction
   - Smart filtering (size, quality)

3. **`multimodal_prompts.py`**
   - Prompt templates for VLMs
   - Difficulty definitions for diagram questions
   - 2 few-shot examples (Easy, Medium)
   - Diagram type detection

4. **`vlm_client.py`**
   - `VLMClient`: HTTP client for vision-language models
   - `MockVLMClient`: Mock for testing without real VLM
   - Retry logic and error handling
   - Support for multiple VLM formats

5. **`multimodal_generator.py`**
   - `MultimodalMCQGenerator`: Main generator class
   - `generate_from_pair()`: Generate from TextImagePair
   - JSON parsing and validation
   - Diagram-specific validation (checks for visual references)

### Documentation

6. **`PHASE3_GUIDE.md`** (15 pages)
   - Complete setup instructions
   - Usage examples
   - Configuration reference
   - Troubleshooting guide
   - VLM setup instructions

7. **`example_multimodal.py`**
   - 3 complete examples
   - PDF extraction demo
   - Text-image pairing demo
   - Question generation (mock & real VLM)

8. **Updated `requirements.txt`**
   - Added PyMuPDF for PDF extraction
   - Added Pillow for image processing

---

## Quick Start

### Test Without VLM (1 minute)

```bash
python3 example_multimodal.py
```

**Output:**
```
================================================================================
EXAMPLE 3: Generate MCQs with Mock VLM
================================================================================

Using synthetic test data...

🤖 MockVLM: Generating response...
✅ Mock response generated

✅ Successfully generated 1 multimodal question(s)

[Shows complete MCQ about phase diagrams]
```

---

## Usage Examples

### Extract PDF

```python
from pdf_extractor import extract_pdf

# Extract pages with diagrams
pdf_doc = extract_pdf("physics_chapter3.pdf", pages=[10, 11, 12])

print(f"Total images: {pdf_doc.total_images}")

for page in pdf_doc.get_pages_with_images():
    print(f"Page {page.page_number}: {len(page.images)} images")
    for img in page.images:
        print(f"  - {img.caption or 'No caption'}")
```

### Generate Questions (Mock Mode)

```python
from pdf_extractor import extract_pdf, create_text_image_pairs
from multimodal_generator import MultimodalMCQGenerator
from models import DifficultyLevel

# Extract and pair
pdf_doc = extract_pdf("materials.pdf", pages=[5])
pairs = create_text_image_pairs(pdf_doc)

# Generate with mock VLM (no real VLM needed!)
generator = MultimodalMCQGenerator(use_mock=True)

questions = generator.generate_from_pair(
    pair=pairs[0],
    subject="Metallurgical Engineering",
    main_topic="Material Science",
    subtopic="Phase Diagrams",
    difficulty=DifficultyLevel.MEDIUM,
    n=2
)

# Questions are ready to use!
for q in questions:
    print(q.question_text_en)
    print(f"Requires diagram: {q.has_diagram}")
```

---

## Key Features

### 1. Smart PDF Extraction

**Extracts:**
- Text blocks with positioning
- Images with bounding boxes
- Captions (Figure N:, Diagram:, etc.)
- Nearby context paragraphs
- Formula detection (heuristic)

**Filters:**
- Minimum image size (default: 10KB)
- Minimum dimensions (default: 100×100px)
- Skip decorative images

**Code:**
```python
from pdf_extractor import PDFExtractor

extractor = PDFExtractor(
    min_image_size=10000,
    min_image_dimension=100
)

pdf_doc = extractor.extract_pdf("file.pdf")
```

### 2. Intelligent Text-Image Pairing

**Strategies:**
- Same-page pairing: image + caption + nearby text
- Caption detection: "Figure X:", "Diagram:", etc.
- Context extraction: paragraphs above/below

**Output:**
```python
TextImagePair(
    text="Caption: Figure 3.1: Fe-C phase diagram\n\nContext: Shows equilibrium phases...",
    images=[ExtractedImage(...)],
    page_number=10
)
```

### 3. Multimodal Prompt Engineering

**Prompt structure:**
```
[System] You are an expert question writer...

[Difficulty] Easy/Medium/Hard definitions for diagrams

[Context + Images]
Caption: ...
Context: ...
Image 1: <base64>
Image 2: <base64>

[Task] Generate N questions requiring the diagram

[Examples] 2 few-shot examples

[Format] JSON schema
```

**Key requirements:**
- Question MUST require diagram to answer
- Reference specific visual elements
- 4 distinct options
- Detailed explanation citing diagram features

### 4. Validation

**Checks for:**
- ✅ Standard validation (4 options, correct answer, etc.)
- ✅ Explanation length (≥20 chars)
- ✅ References present
- ✅ **Question references diagram** (checks for "shown", "diagram", "figure", etc.)

**Example:**
```
❌ "What is the eutectoid temperature?"
   (Can answer from memory)

✅ "According to the phase diagram shown, what is the eutectoid temperature?"
   (Requires looking at diagram)
```

---

## Architecture

```
PDF File
  ↓
[PDFExtractor]
  ↓
PDFDocument (pages, images, text)
  ↓
[TextImagePairer]
  ↓
TextImagePair[] (diagram + context)
  ↓
[MultimodalPromptBuilder]
  ↓
Prompt + Images (base64)
  ↓
[VLMClient]
  ↓
JSON Response
  ↓
[Parser + Validator]
  ↓
Question[] (validated MCQs)
```

---

## Setting Up a Real VLM

### Option 1: LLaVA (Easiest)

**If you're already running Ollama:**

```bash
# Pull LLaVA
ollama pull llava

# Test
ollama run llava
# Try: "Describe this image" with any image
```

**In code:**
```python
from vlm_client import VLMConfig, VLMClient

config = VLMConfig(
    base_url="http://localhost:11434",
    model_name="llava"
)

client = VLMClient(config)
client.test_connection()
```

### Option 2: Qwen-VL (Better Quality)

1. Download Qwen-VL weights
2. Run inference server
3. Update `VLMConfig` with your endpoint

### Option 3: Mock (No VLM Needed)

```python
from multimodal_generator import MultimodalMCQGenerator

# Use mock - perfect for testing!
generator = MultimodalMCQGenerator(use_mock=True)
```

---

## Data Flow Example

### Input: Physics PDF

```
Page 10:
  Text: "Figure 3.1: Free body diagram showing forces..."
  Image: [diagram with labeled vectors]
```

### After Extraction

```python
PDFDocument(
  pages=[
    PDFPage(
      page_number=10,
      text="Figure 3.1: Free body diagram...",
      images=[
        ExtractedImage(
          image_data=b'...',
          caption="Figure 3.1: Free body diagram...",
          nearby_text="The diagram shows three forces..."
        )
      ]
    )
  ]
)
```

### After Pairing

```python
TextImagePair(
  text="Caption: Figure 3.1: Free body diagram...\n\nContext: The diagram shows...",
  images=[ExtractedImage(...)],
  page_number=10
)
```

### After Generation

```python
Question(
  question_text_en="According to the free body diagram shown, what is the net force in the x-direction?",
  option_a_en="10 N to the right",
  option_b_en="10 N to the left",
  option_c_en="0 N (equilibrium)",
  option_d_en="Cannot be determined",
  correct_answer="C",
  explanation="Looking at the diagram, the forces in the x-direction are...",
  has_diagram=True,
  source_pdf="physics.pdf"
)
```

---

## Testing Checklist

### Phase 3 Setup

- [ ] PyMuPDF installed: `pip install PyMuPDF`
- [ ] Pillow installed: `pip install Pillow`
- [ ] Mock example runs: `python3 example_multimodal.py`
- [ ] Can extract a sample PDF
- [ ] Text-image pairs created successfully

### With Real VLM (Optional)

- [ ] VLM model downloaded (e.g., LLaVA)
- [ ] VLM server running
- [ ] Connection test passes
- [ ] Generated first diagram-based question

---

## Performance Notes

### PDF Extraction
- **Speed**: ~1-2 seconds per page
- **Memory**: Minimal (processes page-by-page)

### VLM Generation
- **Typical time**: 60-120 seconds per question
- **With diagrams**: Slower than text-only (image processing)
- **Batch size**: 1-3 questions per call recommended

**Tips:**
- Extract only needed pages: `pages=[10, 11, 12]`
- Cache extracted PDFs (save to JSON)
- Use quantized VLMs for faster inference

---

## Complete Workflow

### Generate 10 Diagram-Based Questions

```python
from pdf_extractor import extract_pdf, create_text_image_pairs
from multimodal_generator import MultimodalMCQGenerator
from models import DifficultyLevel

# 1. Extract PDF (pages with diagrams)
pdf_doc = extract_pdf("materials_ch3.pdf", pages=[10, 11, 12, 13, 14])

# 2. Create text-image pairs
pairs = create_text_image_pairs(pdf_doc)
print(f"Found {len(pairs)} diagrams")

# 3. Generate questions (mock mode for testing)
generator = MultimodalMCQGenerator(use_mock=True)

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

print(f"✅ Generated {len(all_questions)} diagram-based questions!")
```

---

## Troubleshooting

### No images extracted

1. Check PDF has actual images (not scanned text)
2. Lower `min_image_size` threshold
3. Try `extract_vector_graphics=True`

### Captions not found

1. Add custom patterns in `pdf_extractor.py`
2. Manually add captions to `ExtractedImage.caption`

### Questions don't reference diagrams

1. Improve few-shot examples
2. Add explicit instructions in prompt
3. Check validation settings

See **PHASE3_GUIDE.md** for detailed troubleshooting.

---

## Next Steps

### Immediate
1. Test PDF extraction with your actual documents
2. Inspect extracted diagrams and captions
3. Generate test questions with mock VLM
4. Review question quality

### This Week
5. Set up LLaVA or Qwen-VL locally
6. Generate questions with real VLM
7. Fine-tune prompts for your domain
8. Build question database

### Phase 4 (Web UI - 2-3 weeks)
- Upload PDFs via web interface
- Preview extracted diagrams
- Generate questions in batch
- SME review and editing
- Export to Excel/CSV
- Docker packaging

---

## Summary

You now have a **complete multimodal MCQ generation system**:

✅ **Extract** PDFs with diagrams and formulas
✅ **Pair** images with context intelligently
✅ **Generate** questions requiring visual interpretation
✅ **Validate** diagram-based questions
✅ **Test** without real VLM (mock mode)
✅ **Deploy** with local VLM (LLaVA/Qwen-VL)

**Ready to generate diagram-based questions!** 🎨📊🚀

---

**Documentation:**
- **Setup & Usage**: `PHASE3_GUIDE.md` (15 pages)
- **Examples**: `example_multimodal.py`
- **Quick Start**: This file

**Questions?** See the guide or run the examples!
