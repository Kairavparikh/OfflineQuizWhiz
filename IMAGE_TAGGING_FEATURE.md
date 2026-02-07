# Image Tagging Feature for Diagram-Based Questions

## Overview

Questions generated from diagrams now include image reference tags to help test creators identify which diagrams go with which questions!

---

## What's New

### 1. Image Reference Fields

Every diagram-based question now includes:

- **Image Reference**: A unique identifier for the diagram (e.g., `page2_diagram1`)
- **Image Description**: Human-readable description of the diagram

### 2. Enhanced CSV Export

CSV files now have **21 columns** (previously 19):

| Column # | Name | Description |
|----------|------|-------------|
| 1-19 | (existing) | Test Section, Question, Options, Answer, etc. |
| **20** | **Image Reference** | Filename/ID of the diagram |
| **21** | **Image Description** | Description of the diagram |

### 3. Automatic Tagging

When generating questions from PDFs:
1. System extracts diagrams from PDF pages
2. Each diagram gets a unique reference (e.g., `page2_diagram1`)
3. Questions generated from that diagram are automatically tagged
4. Description comes from the diagram's caption or context

---

## How It Works

### Example Flow

```
PDF Upload
   ↓
Extract diagrams
   ├─ Page 2, Diagram 1: Muscle spindle anatomy
   ├─ Page 3, Diagram 1: Fe-C phase diagram
   └─ Page 5, Diagram 2: Circuit schematic
   ↓
Generate questions
   ├─ Q1: "According to the diagram..."
   │     → Image Reference: "page2_diagram1"
   │     → Image Description: "Muscle spindle anatomy showing afferent fibers"
   │
   ├─ Q2: "In the phase diagram shown..."
   │     → Image Reference: "page3_diagram1"
   │     → Image Description: "Fe-C phase diagram"
   │
   └─ Q3: "What is the resistance of R2?"
         → Image Reference: "page5_diagram2"
         → Image Description: "Circuit schematic with resistors and capacitors"
```

---

## CSV Format Example

```csv
...,"Reference(s)","Image Reference","Image Description"
...,"1. https://...",page2_diagram1,"Muscle spindle anatomy showing afferent fibers"
...,"1. https://...",page3_diagram1,"Fe-C equilibrium phase diagram"
...,"1. https://...","","" (text-based question - no diagram)
```

---

## Using the Image References

### When Creating Tests

1. **Download the CSV** after generating questions
2. **Look at the Image Reference column** to see which questions need diagrams
3. **Match the image reference** to the extracted diagram files
4. **Use the Image Description** to verify you have the right diagram
5. **Include the diagram** in your test paper with the question

### Example Workflow

```
Step 1: Generate questions from PDF
   ↓
Step 2: Download CSV file
   ↓
Step 3: Filter for questions with Image Reference
   ↓
Step 4: For each question:
   - Find image file: page2_diagram1.jpg (in extracted_images/ folder)
   - Verify using Image Description
   - Include with question in test paper
```

---

## Image Reference Format

### Naming Convention

```
page{N}_diagram{M}
```

- `N` = Page number in PDF
- `M` = Diagram number on that page (starts from 1)

### Examples

- `page2_diagram1` → First diagram from page 2
- `page5_diagram3` → Third diagram from page 5
- `page10_diagram1` → First diagram from page 10

---

## Technical Details

### Data Model

```python
@dataclass
class Question:
    # ... existing fields ...

    # Image tagging fields
    has_diagram: bool = False  # True if question requires a diagram
    image_reference: Optional[str] = None  # e.g., "page2_diagram1"
    image_description: Optional[str] = None  # Human-readable description
```

### Automatic Population

When generating from diagrams, the system automatically:

```python
# Create image reference
image_ref = f"page{pair.page_number}_diagram{img.image_index + 1}"

# Use caption as description, or create one
image_desc = img.caption if img.caption else f"Diagram from page {pair.page_number}"

# Attach to question
question.image_reference = image_ref
question.image_description = image_desc
question.has_diagram = True
```

---

## Examples

### Example 1: Anatomy Diagram

**Question:**
> "According to the diagram, which part of the mammalian muscle is most densely innervated with muscle spindles?"

**CSV Fields:**
- Image Reference: `page2_diagram1`
- Image Description: `Muscle spindle distribution showing innervation density in different body regions`
- Has Diagram: `Yes`

**When creating test:**
- Include diagram file: `page2_diagram1.jpg`
- Place diagram above or below the question
- Ensure diagram is clear and legible

### Example 2: Phase Diagram

**Question:**
> "In the phase diagram shown, at what temperature does the eutectoid transformation occur?"

**CSV Fields:**
- Image Reference: `page4_diagram2`
- Image Description: `Fe-C equilibrium phase diagram showing transformation temperatures`
- Has Diagram: `Yes`

**When creating test:**
- Include diagram file: `page4_diagram2.jpg`
- Ensure axis labels are visible
- Consider larger size for readability

### Example 3: Text-Only Question

**Question:**
> "What is the primary function of muscle spindles in the somatosensory system?"

**CSV Fields:**
- Image Reference: `` (empty)
- Image Description: `` (empty)
- Has Diagram: `No`

**When creating test:**
- No diagram needed
- Just include the question text

---

## Benefits

### For Test Creators

✅ **Easy identification** - Instantly see which questions need diagrams
✅ **Clear matching** - Reference links question to specific diagram
✅ **Description verification** - Confirm you have the right diagram
✅ **Organized workflow** - System of diagram files and references
✅ **No confusion** - Never wonder which diagram goes with which question

### For Quality Control

✅ **Audit trail** - Track which PDF page each question came from
✅ **Consistency** - Standardized naming convention
✅ **Documentation** - Descriptions explain what each diagram shows
✅ **Validation** - Verify diagrams match question content

---

## Best Practices

### 1. Save Extracted Diagrams

```bash
# When generating questions, also save the extracted diagrams
output/
  ├── paper_abc123.csv          # Questions with image references
  └── extracted_images/
      ├── page2_diagram1.jpg     # Saved from PDF
      ├── page3_diagram1.jpg
      └── page5_diagram2.jpg
```

### 2. Use Image Description

- **Review descriptions** before finalizing test
- **Update if needed** for clarity
- **Use in test instructions** if helpful

### 3. Filter by Has Diagram

```python
# Get only diagram-based questions
diagram_questions = [q for q in questions if q.has_diagram]

# Get only text-based questions
text_questions = [q for q in questions if not q.has_diagram]
```

### 4. Quality Check

Before finalizing test:
- [ ] All diagram references have corresponding image files
- [ ] Image descriptions are accurate
- [ ] Diagrams are clear and legible
- [ ] No duplicate references (unless intentional)

---

## Future Enhancements

Potential additions:

1. **Actual image file saving** - Auto-save extracted diagrams with reference names
2. **Image preview in web UI** - Show thumbnail of diagram in results table
3. **Batch download** - Download all referenced diagrams at once
4. **Image validation** - Verify diagrams exist before export
5. **Custom naming** - Allow custom image reference format
6. **Diagram library** - Reuse diagrams across multiple tests

---

## FAQ

**Q: What if a question references multiple diagrams?**
A: Currently supports one diagram per question. Multiple diagrams should be combined into a single composite image.

**Q: Can I rename the image references?**
A: Yes! Edit the CSV file before creating the test. Just ensure you update the actual image filenames too.

**Q: What if the image description is wrong?**
A: Edit it in the CSV file. The description is just a helper - the reference is what matters.

**Q: Do text-based questions have image references?**
A: No. The Image Reference and Image Description fields will be empty for text-only questions.

**Q: Can I filter questions by image reference in the CSV?**
A: Yes! Sort or filter by column 20 (Image Reference). Empty cells = text-only questions.

**Q: What image format should I use?**
A: JPEG recommended for photos/diagrams. PNG for charts/graphs with transparency. SVG for vector diagrams if supported.

---

## Summary

The image tagging feature makes it **easy to create tests** from PDF-generated questions by:

✅ Automatically tagging diagram-based questions
✅ Providing unique references for each diagram
✅ Including human-readable descriptions
✅ Exporting everything in the CSV file
✅ Maintaining full compatibility with existing format

**Result:** Test creators can quickly identify which diagrams go with which questions, ensuring accurate and professional test papers!

---

**Date Added**: 2026-02-07
**Version**: 1.1.0
**Status**: Production Ready
