"""
Prompt templates for multimodal (vision-language) MCQ generation.

Designed for VLMs that can process both text and images to generate
questions that require interpreting diagrams, formulas, or graphs.
"""

from typing import List
from src.models.models import DifficultyLevel


# System prompt for multimodal generation
MULTIMODAL_SYSTEM_PROMPT = """You are an expert question writer for technical examinations in engineering and science. You have been provided with one or more diagrams, graphs, or formula images along with contextual text.

Your task is to generate multiple-choice questions (MCQs) that:

1. **Require the diagram/image** to answer correctly - the question should NOT be answerable from text alone
2. **Test visual understanding** - interpreting graphs, reading diagrams, analyzing formulas shown in the image
3. **Are technically accurate** based on the diagram and context provided
4. **Match the specified difficulty level**
5. **Include detailed explanations** that reference specific elements of the diagram

IMPORTANT: The question must explicitly require looking at the provided image(s). Students should need to interpret visual information to answer.
"""


# Multimodal difficulty definitions
MULTIMODAL_DIFFICULTY_DEFINITIONS = """
**Difficulty Level Definitions (for diagram-based questions):**

1. **Easy**:
   - Direct reading from the diagram (e.g., "What is the value at point X on the graph?")
   - Identifying labeled components (e.g., "Which part is labeled as the cathode?")
   - Simple pattern recognition
   - Example: "According to the phase diagram shown, at what temperature does the eutectoid transformation occur?"

2. **Medium**:
   - Interpreting relationships shown in the diagram
   - Comparing multiple elements or data points
   - Applying concepts to read/analyze the diagram
   - Requires 1-2 steps combining visual + conceptual knowledge
   - Example: "Based on the stress-strain curve shown, which material exhibits the highest toughness?"

3. **Hard**:
   - Multi-step analysis using the diagram
   - Predicting outcomes based on diagram patterns
   - Combining multiple diagrams or comparing with theoretical knowledge
   - Requires deep understanding of both the visual and underlying concepts
   - Example: "Using the T-T-T diagram shown, predict the microstructure that will form if the steel is cooled from 850°C to 400°C in 10 seconds."
"""


# Few-shot examples for multimodal generation
MULTIMODAL_FEW_SHOT_EXAMPLES = [
    {
        "difficulty": "Easy",
        "diagram_description": "A binary phase diagram showing temperature vs composition for an iron-carbon system, with clearly labeled regions for austenite, ferrite, cementite, and pearlite. The eutectoid point is marked at 727°C and 0.8% C.",
        "example": """{
  "question_text_en": "According to the Fe-C phase diagram shown, at what temperature does the eutectoid transformation occur?",
  "option_a_en": "912°C",
  "option_b_en": "1147°C",
  "option_c_en": "727°C",
  "option_d_en": "1394°C",
  "correct_answer": "C",
  "explanation": "Looking at the phase diagram, the eutectoid point is clearly marked at the intersection where the A1 line (at 727°C) meets the eutectoid composition (0.8% C). At this point, austenite transforms into pearlite (a mixture of ferrite and cementite). The other temperatures shown are: 912°C (lower critical A3 for pure iron), 1147°C (eutectic point), and 1394°C (peritectic point).",
  "references": [
    "https://en.wikipedia.org/wiki/Iron%E2%80%93carbon_phase_diagram",
    "Phase Transformations in Metals and Alloys by David A. Porter, Chapter 5"
  ]
}"""
    },
    {
        "difficulty": "Medium",
        "diagram_description": "A stress-strain curve showing three different materials (A, B, C). Material A shows high ultimate tensile strength but low elongation. Material B shows moderate strength with high elongation. Material C shows low strength with very high elongation.",
        "example": """{
  "question_text_en": "Based on the stress-strain curves shown for materials A, B, and C, which material exhibits the highest toughness?",
  "option_a_en": "Material A",
  "option_b_en": "Material B",
  "option_c_en": "Material C",
  "option_d_en": "All three have equal toughness",
  "correct_answer": "B",
  "explanation": "Toughness is the ability of a material to absorb energy before fracture, represented by the total area under the stress-strain curve. Examining the diagram: Material A has high strength but fractures early (small area), Material C has high elongation but low stress (moderate area), while Material B shows the best combination of both strength and ductility, giving it the largest area under the curve and thus the highest toughness. Toughness requires both the ability to withstand stress AND the ability to deform, which Material B demonstrates best.",
  "references": [
    "https://en.wikipedia.org/wiki/Toughness",
    "Materials Science and Engineering: An Introduction by William D. Callister, Chapter 6"
  ]
}"""
    }
]


def build_multimodal_prompt(
    text_context: str,
    num_images: int,
    difficulty: DifficultyLevel,
    subject: str,
    main_topic: str,
    subtopic: str,
    num_questions: int = 1,
    diagram_type: str = "diagram"
) -> str:
    """
    Build a prompt for multimodal MCQ generation.

    Args:
        text_context: Extracted text (caption + nearby context)
        num_images: Number of images provided
        difficulty: Difficulty level
        subject: Subject name
        main_topic: Main topic
        subtopic: Subtopic
        num_questions: Number of questions to generate
        diagram_type: Type of diagram (e.g., "graph", "circuit", "phase diagram")

    Returns:
        Complete prompt for VLM
    """
    difficulty_str = difficulty.value if isinstance(difficulty, DifficultyLevel) else difficulty

    # Image reference text
    if num_images == 1:
        image_ref = "the diagram shown"
    else:
        image_ref = f"the {num_images} diagrams/images provided"

    prompt_parts = [
        MULTIMODAL_SYSTEM_PROMPT,
        "",
        MULTIMODAL_DIFFICULTY_DEFINITIONS,
        "",
        f"**Context and Diagram(s):**",
        f"You have been provided with {image_ref} and the following context:",
        "",
        "```",
        text_context,
        "```",
        "",
        f"**Your Task:**",
        f"Generate {num_questions} multiple-choice question(s) that:",
        f"- **Requires interpreting {image_ref} to answer**",
        f"- Tests understanding of the {diagram_type}",
        f"- Subject: {subject}",
        f"- Main Topic: {main_topic}",
        f"- Sub-topic: {subtopic}",
        f"- Difficulty Level: {difficulty_str}",
        "",
        "**Requirements:**",
        "1. The question MUST require looking at the image(s) to answer correctly",
        "2. Reference specific elements visible in the diagram (e.g., 'point A on the graph', 'the labeled component', 'the curve shown')",
        "3. Provide 4 distinct options (A, B, C, D)",
        "4. Include a detailed explanation that:",
        "   - Describes what to look for in the diagram",
        "   - Explains WHY the correct answer is right based on visual evidence",
        "   - References specific features/values/labels from the image",
        "5. Provide at least 2 credible references",
        "",
    ]

    # Add few-shot examples
    prompt_parts.extend([
        "**Examples of well-formed diagram-based MCQs:**",
        ""
    ])

    # Select relevant examples
    for i, example_data in enumerate(MULTIMODAL_FEW_SHOT_EXAMPLES, 1):
        prompt_parts.extend([
            f"Example {i} ({example_data['difficulty']} difficulty):",
            f"[Imagine a diagram showing: {example_data['diagram_description']}]",
            "```json",
            example_data['example'],
            "```",
            ""
        ])

    # Output format
    prompt_parts.extend([
        "**Output Format:**",
        f"Respond with a JSON array containing {num_questions} question object(s).",
        "Each object must have these exact keys:",
        "```json",
        "[",
        "  {",
        '    "question_text_en": "Your question that requires the diagram...",',
        '    "option_a_en": "First option",',
        '    "option_b_en": "Second option",',
        '    "option_c_en": "Third option",',
        '    "option_d_en": "Fourth option",',
        '    "correct_answer": "A",  // Must be A, B, C, or D',
        '    "explanation": "Detailed explanation referencing specific diagram elements...",',
        '    "references": [',
        '      "https://example.com/source1",',
        '      "Textbook Name by Author, Chapter X"',
        '    ]',
        "  }",
        "]",
        "```",
        "",
        "**Critical Reminders:**",
        "- Output ONLY the JSON array, no additional text",
        "- Ensure the question REQUIRES the diagram/image to answer",
        "- Reference specific visual elements in your explanation",
        "- Match the difficulty level appropriately",
        "",
        f"Now generate {num_questions} diagram-based question(s):"
    ])

    return "\n".join(prompt_parts)


# Example of what the prompt looks like with placeholders
MULTIMODAL_PROMPT_EXAMPLE = """
=== EXAMPLE MULTIMODAL PROMPT ===

[System Instructions]
You are an expert question writer...

[Difficulty Definitions]
Easy: Direct reading from diagram...
Medium: Interpreting relationships...
Hard: Multi-step analysis...

[Context and Images]
Image 1: [Base64 encoded image data]
Image 2: [Base64 encoded image data]

Text Context:
```
Caption: Figure 3: Iron-Carbon equilibrium phase diagram showing various phases and transformation temperatures.

Context: The diagram shows the relationship between temperature and carbon content in iron-carbon alloys. Key features include the eutectoid point at 727°C and 0.8% C, where austenite transforms to pearlite...
```

[Task]
Generate 2 Medium-difficulty questions that require interpreting the phase diagram.

[Examples]
Example 1 (Easy): [...]
Example 2 (Medium): [...]

[Output Format]
JSON array with question objects...

===================================
"""


def get_diagram_type_hint(text: str) -> str:
    """
    Infer diagram type from caption/context text.

    Args:
        text: Caption or context text

    Returns:
        Diagram type hint (e.g., "graph", "circuit", "phase diagram")
    """
    text_lower = text.lower()

    type_keywords = {
        "phase diagram": ["phase diagram", "equilibrium diagram", "binary diagram"],
        "graph": ["graph", "plot", "curve", "chart"],
        "circuit": ["circuit", "schematic", "wiring"],
        "flowchart": ["flowchart", "flow chart", "process flow"],
        "structure": ["structure", "crystal structure", "molecular structure"],
        "mechanism": ["mechanism", "process", "reaction mechanism"],
        "table": ["table", "data table"],
        "formula": ["formula", "equation", "expression"],
    }

    for diagram_type, keywords in type_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return diagram_type

    return "diagram"  # Default
