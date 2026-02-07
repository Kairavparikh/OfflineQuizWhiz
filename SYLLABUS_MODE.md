# Syllabus Mode Feature

## Overview

The PDF upload interface now supports **two modes** for generating MCQs:

1. **PDF Content Mode** (default) - Generates questions from the actual content in the PDF
2. **Syllabus Mode** (new) - Parses PDF as a syllabus and generates questions for each topic

---

## How It Works

### PDF Content Mode

This is the original mode:
- Extracts text and diagrams from PDF
- Analyzes the actual content
- Generates questions based on what it reads
- Best for: Textbooks, lecture notes, study materials

**Example:**
```
PDF contains: "Photosynthesis is the process by which plants..."
Question generated: "What is the primary function of photosynthesis?"
```

### Syllabus Mode (NEW!)

This mode treats the PDF as a curriculum outline:
- Parses the PDF structure to identify topics and subtopics
- Generates questions for each topic area
- Uses general knowledge about the topics (not just PDF content)
- Best for: Course syllabi, curriculum documents, topic lists

**Example:**
```
PDF contains: "1. Photosynthesis
              2. Cellular Respiration"
Questions generated:
- Q1: "What is the primary function of photosynthesis?"
- Q2: "Which organelle is responsible for cellular respiration?"
```

---

## Supported Syllabus Formats

The syllabus parser recognizes these common patterns:

### Numbered Lists
```
1. Introduction to Biology
2. Cell Structure
3. Genetics
```

### Roman Numerals
```
I. Classical Mechanics
II. Thermodynamics
III. Electromagnetism
```

### Lettered Lists
```
A. Data Structures
B. Algorithms
C. Database Management
```

### Bulleted Lists with Sub-items
```
• Programming Fundamentals
  - Variables and Data Types
  - Control Structures
  - Functions

• Object-Oriented Programming
  - Classes and Objects
  - Inheritance
  - Polymorphism
```

### Hierarchical Structure
```
1. Engineering Mathematics
   1.1 Linear Algebra
   1.2 Calculus
   1.3 Differential Equations

2. Material Science
   2.1 Crystal Structure
   2.2 Phase Diagrams
```

---

## How to Use

### Step 1: Choose Your Mode

When uploading a PDF, you'll see a **Mode** dropdown:

```
Mode: [ PDF Content - Generate questions from the PDF content itself ]
      [ Syllabus - Parse topics and generate questions for each topic ]
```

Select the appropriate mode based on your PDF type.

### Step 2: Upload PDF

- **For Content Mode**: Upload textbooks, notes, articles
- **For Syllabus Mode**: Upload course outlines, curriculum PDFs, topic lists

### Step 3: Configure Settings

- Subject/Topic: General subject area (e.g., "Physics", "Computer Science")
- Number of Questions: Total questions to generate
- Difficulty: Easy/Medium/Hard

### Step 4: Generate!

The system will:
- **Content Mode**: Extract content → Generate questions about that content
- **Syllabus Mode**: Parse topics → Generate questions for each topic

---

## Examples

### Example 1: Course Syllabus

**Input PDF (syllabus.pdf):**
```
CS101 - Introduction to Computer Science

Course Outline:
1. Programming Fundamentals
   - Variables and Data Types
   - Control Flow
   - Functions

2. Data Structures
   - Arrays and Lists
   - Stacks and Queues
   - Trees and Graphs

3. Algorithms
   - Sorting Algorithms
   - Search Algorithms
   - Complexity Analysis
```

**Using Syllabus Mode:**
- Parses: 9 topics found
  1. Programming Fundamentals → Variables and Data Types
  2. Programming Fundamentals → Control Flow
  3. Programming Fundamentals → Functions
  4. Data Structures → Arrays and Lists
  5. Data Structures → Stacks and Queues
  ... and so on

- Generates questions distributed across all topics
- Questions test knowledge of each concept area

**Result:** 10 questions covering all major topics from the syllabus

### Example 2: Textbook Chapter

**Input PDF (chapter3.pdf):**
```
Chapter 3: Photosynthesis

Photosynthesis is the process by which green plants use sunlight
to synthesize nutrients from carbon dioxide and water. This process
occurs in the chloroplasts, specifically in the thylakoid membranes...

[3 pages of detailed content about photosynthesis]
```

**Using Content Mode:**
- Extracts all text from the chapter
- Analyzes the specific information provided
- Generates questions based on the actual content

**Result:** 10 questions testing comprehension of the chapter content

---

## Technical Details

### Syllabus Parsing Algorithm

The system uses regex pattern matching to identify:

1. **Main Topics**: Lines starting with:
   - Numbers: `1.`, `2.`, `3.`
   - Roman numerals: `I.`, `II.`, `III.`
   - Letters: `A.`, `B.`, `C.`

2. **Subtopics**: Lines with:
   - Bullets: `•`, `●`, `○`, `►`, `▪`
   - Dashes: `-`, `–`, `—`
   - Nested numbers: `1.1`, `1.2`, `2.1`
   - Lowercase letters: `a)`, `b)`, `c)`

3. **Fallback**: If no structure detected, each non-empty line becomes a topic

### Question Distribution

In Syllabus Mode, questions are distributed as follows:

```python
# If syllabus has 10 topics and user wants 15 questions:
questions_per_topic = 15 / 10 = 1.5 → rounds to 1-2 questions per topic

# Topics get questions in order until quota is met
Topic 1: 2 questions
Topic 2: 2 questions
Topic 3: 2 questions
...
Topic 8: 1 question
Total: 15 questions
```

### Content Mode Workflow

```
1. Extract PDF → text + images
2. Create text-image pairs (diagrams + captions)
3. Generate from diagrams using VLM (if diagrams exist)
4. Fill remaining with text-based questions
5. Return mixed question set
```

### Syllabus Mode Workflow

```
1. Extract PDF → full text
2. Parse text → identify topics and subtopics
3. For each topic:
   - Generate N questions for that topic area
   - Use AI's general knowledge of the subject
4. Return questions distributed across topics
```

---

## When to Use Each Mode

### Use Content Mode When:
✅ PDF contains detailed information/explanations
✅ You want questions about the specific content
✅ PDF has diagrams/figures to analyze
✅ Working with: textbooks, articles, research papers, lecture notes

### Use Syllabus Mode When:
✅ PDF is a course outline or curriculum
✅ PDF lists topics without detailed explanations
✅ You want broad coverage across many topics
✅ Working with: syllabi, curriculum guides, topic lists, study plans

---

## Benefits

### Syllabus Mode Benefits:
- ✅ **Fast**: No need for detailed content, just topic names
- ✅ **Broad Coverage**: Automatically covers all listed topics
- ✅ **Flexible**: Works with any topic list format
- ✅ **Comprehensive**: Ensures no topics are missed

### Content Mode Benefits:
- ✅ **Specific**: Questions match the exact content provided
- ✅ **Contextual**: Can reference specific examples from text
- ✅ **Visual**: Can incorporate diagrams and figures
- ✅ **Detailed**: Tests deep understanding of specific material

---

## Tips for Best Results

### For Syllabus Mode:
1. **Clear Structure**: Use numbered or bulleted lists
2. **Descriptive Names**: Use clear topic names (e.g., "Linear Algebra" not "Math 1")
3. **Hierarchy**: Organize with main topics and subtopics
4. **Completeness**: Include all topics you want covered

### For Content Mode:
1. **Quality Content**: Include detailed explanations
2. **Clear Text**: Avoid heavily formatted or scanned documents
3. **Diagrams**: Include clear, labeled diagrams if applicable
4. **Reasonable Length**: 5-50 pages works best

---

## Limitations

### Syllabus Mode:
- Questions are based on general knowledge, not specific PDF content
- May not match your exact curriculum interpretation
- Requires AI to have knowledge of the topic area
- Cannot reference specific examples from your materials

### Content Mode:
- Processing time increases with PDF length
- Heavily formatted PDFs may not extract well
- Requires clear, readable text
- Diagram extraction depends on PDF quality

---

## Troubleshooting

### "No topics found in syllabus"
**Problem**: Parser couldn't identify topic structure

**Solutions**:
- Ensure topics are numbered, bulleted, or clearly formatted
- Try adding line breaks between topics
- Simplify formatting (remove excessive styling)
- Switch to Content Mode if PDF has detailed content

### "Questions don't match my syllabus"
**Problem**: AI generated different questions than expected

**Solutions**:
- Use more descriptive topic names
- Add subtopics for more specific questions
- Try Content Mode if you have detailed materials
- Adjust difficulty level

### "Only generated X out of Y questions"
**Problem**: System couldn't generate all requested questions

**Solutions**:
- Check topic names are valid subject areas
- Reduce number of questions requested
- Ensure Ollama is running with sufficient resources
- Try smaller batches (5-10 questions at a time)

---

## Future Enhancements

Potential improvements:
1. **Smart Mode Detection**: Auto-detect whether PDF is syllabus or content
2. **Topic Filtering**: Allow user to select which topics to generate for
3. **Question Distribution Control**: Specify questions per topic
4. **Hybrid Mode**: Combine syllabus structure with content analysis
5. **Format Support**: Excel/CSV syllabus uploads
6. **Topic Suggestions**: AI suggests additional related topics

---

## Summary

The dual-mode system gives you flexibility:

**Have a syllabus?** → Use **Syllabus Mode** for broad topic coverage

**Have content?** → Use **Content Mode** for specific question generation

Both modes:
- Support all difficulty levels
- Export to standard CSV format
- Include image tagging (Content Mode)
- Validate questions for quality
- Use same web interface

**Result**: Flexible MCQ generation for any educational material!

---

**Last Updated**: 2026-02-07
**Version**: 1.2.0
**Status**: Production Ready
