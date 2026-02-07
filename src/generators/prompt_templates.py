"""
Prompt templates for MCQ generation.

Contains:
- System instructions
- Difficulty level definitions
- Few-shot examples
- JSON output format specifications
"""

from typing import Dict, Any
from src.models.models import DifficultyLevel


# Difficulty level definitions
DIFFICULTY_DEFINITIONS = """
**Difficulty Level Definitions:**

1. **Easy**:
   - Direct recall of definitions, formulas, or basic facts
   - Requires minimal reasoning or calculation
   - Single-step problems
   - Example: "What is the determinant of an identity matrix?"

2. **Medium**:
   - Application of concepts or formulas to solve problems
   - Requires 1-2 steps of reasoning or calculation
   - May combine 2 related concepts
   - Example: "Calculate the eigenvalues of a given 2×2 matrix"

3. **Hard**:
   - Multi-step reasoning or complex problem-solving
   - Combines multiple concepts from different topics
   - Requires deep understanding and analysis
   - Example: "Prove that similar matrices have the same eigenvalues"
"""


# Few-shot examples
FEW_SHOT_EXAMPLES = [
    {
        "difficulty": "Easy",
        "subject": "Metallurgical Engineering",
        "main_topic": "Engineering Mathematics",
        "subtopic": "Linear Algebra - Matrices and Determinants",
        "example": """{
  "question_text_en": "What is the determinant of a 2×2 identity matrix?",
  "option_a_en": "0",
  "option_b_en": "1",
  "option_c_en": "2",
  "option_d_en": "-1",
  "correct_answer": "B",
  "explanation": "The determinant of an identity matrix of any size is always 1. For a 2×2 identity matrix I = [[1,0],[0,1]], det(I) = (1×1) - (0×0) = 1. This is a fundamental property: the identity matrix represents no scaling or rotation, hence determinant = 1.",
  "references": [
    "https://en.wikipedia.org/wiki/Determinant",
    "Linear Algebra and Its Applications by Gilbert Strang, Chapter 5, Section 5.1"
  ]
}"""
    },
    {
        "difficulty": "Medium",
        "subject": "Metallurgical Engineering",
        "main_topic": "Material Science",
        "subtopic": "Crystal Structure - Crystal Systems",
        "example": """{
  "question_text_en": "A metal crystallizes in a face-centered cubic (FCC) structure. What is the coordination number of each atom?",
  "option_a_en": "6",
  "option_b_en": "8",
  "option_c_en": "12",
  "option_d_en": "4",
  "correct_answer": "C",
  "explanation": "In an FCC structure, each atom is surrounded by 12 nearest neighbors: 4 atoms in the plane above, 4 in the same plane (at face centers), and 4 in the plane below. This gives FCC its high packing efficiency of 74%. Common FCC metals include aluminum, copper, and gold.",
  "references": [
    "https://en.wikipedia.org/wiki/Cubic_crystal_system#Face-centered_cubic",
    "Materials Science and Engineering: An Introduction by William D. Callister, Chapter 3"
  ]
}"""
    },
    {
        "difficulty": "Hard",
        "subject": "Metallurgical Engineering",
        "main_topic": "Material Science",
        "subtopic": "Phase Diagrams - Iron-Carbon Diagram",
        "example": """{
  "question_text_en": "A steel sample containing 0.8% carbon is slowly cooled from 1000°C to room temperature. At approximately what temperature will it undergo the eutectoid transformation?",
  "option_a_en": "1147°C",
  "option_b_en": "912°C",
  "option_c_en": "727°C",
  "option_d_en": "600°C",
  "correct_answer": "C",
  "explanation": "The eutectoid transformation in the Fe-C system occurs at 727°C (1341°F) when austenite transforms into pearlite (a mixture of ferrite and cementite). This is a critical temperature in steel heat treatment. The composition with 0.8% C is the eutectoid composition, meaning it will transform entirely to pearlite at this single temperature, unlike hypo- or hypereutectoid steels which transform over a temperature range.",
  "references": [
    "https://en.wikipedia.org/wiki/Iron%E2%80%93carbon_phase_diagram",
    "Phase Diagrams in Metallurgy by F.N. Rhines, Chapter 4",
    "Callister's Materials Science and Engineering, 10th Edition, Chapter 9, Section 9.18"
  ]
}"""
    }
]


# System prompt
SYSTEM_PROMPT = """You are an expert question writer for high-stakes technical examinations in engineering and science. Your task is to generate multiple-choice questions (MCQs) that are:

1. **Technically accurate** and based on well-established concepts
2. **Clear and unambiguous** in wording
3. **Appropriately challenging** for the specified difficulty level
4. **Educational** with detailed explanations that teach the concept
5. **Well-referenced** with credible sources (textbooks, academic websites)

You must follow the exact JSON format specified and ensure all questions have exactly 4 options with only one correct answer.
"""


def build_mcq_generation_prompt(
    subject: str,
    main_topic: str,
    subtopic: str,
    difficulty: DifficultyLevel,
    num_questions: int = 1,
    include_few_shot: bool = True
) -> str:
    """
    Build a complete prompt for MCQ generation.

    Args:
        subject: Subject name (e.g., "Metallurgical Engineering")
        main_topic: Main topic (e.g., "Engineering Mathematics")
        subtopic: Subtopic (e.g., "Linear Algebra - Matrices and Determinants")
        difficulty: Difficulty level
        num_questions: Number of questions to generate
        include_few_shot: Whether to include few-shot examples

    Returns:
        Complete prompt string
    """
    difficulty_str = difficulty.value if isinstance(difficulty, DifficultyLevel) else difficulty

    prompt_parts = [
        SYSTEM_PROMPT,
        "",
        DIFFICULTY_DEFINITIONS,
        "",
        "**Your Task:**",
        f"Generate {num_questions} multiple-choice question(s) with the following parameters:",
        f"- Subject: {subject}",
        f"- Main Topic: {main_topic}",
        f"- Sub-topic: {subtopic}",
        f"- Difficulty Level: {difficulty_str}",
        "",
        "**Requirements:**",
        "1. Each MCQ must have:",
        "   - A clear, specific question in English",
        "   - Exactly 4 options (A, B, C, D)",
        "   - All options must be plausible and distinct",
        "   - Exactly one correct answer",
        "   - A detailed explanation (minimum 50 words) that:",
        "     * Explains WHY the correct answer is right",
        "     * Provides context and teaches the concept",
        "     * May explain why wrong options are incorrect (if helpful)",
        "   - At least 2 credible references:",
        "     * Academic websites (Wikipedia, university sites, .edu domains)",
        "     * Textbook citations with chapter/section numbers",
        "     * Format: \"Book Title by Author, Chapter X\" or \"https://...\"",
        "",
        "2. Match the difficulty level:",
        f"   - {difficulty_str}: {_get_difficulty_hint(difficulty_str)}",
        "",
        "3. Ensure technical accuracy - verify all facts, formulas, and concepts",
        "",
    ]

    # Add few-shot examples
    if include_few_shot:
        prompt_parts.extend([
            "**Examples of well-formed MCQs:**",
            ""
        ])

        # Select relevant examples (same difficulty or one easier)
        relevant_examples = _select_relevant_examples(difficulty_str)

        for i, example_data in enumerate(relevant_examples, 1):
            prompt_parts.extend([
                f"Example {i} ({example_data['difficulty']} difficulty):",
                f"Topic: {example_data['subtopic']}",
                "```json",
                example_data['example'],
                "```",
                ""
            ])

    # Output format specification
    prompt_parts.extend([
        "**Output Format:**",
        f"Respond with a JSON array containing {num_questions} question object(s).",
        "Each object must have these exact keys:",
        "```json",
        "[",
        "  {",
        '    "question_text_en": "Your question here?",',
        '    "option_a_en": "First option",',
        '    "option_b_en": "Second option",',
        '    "option_c_en": "Third option",',
        '    "option_d_en": "Fourth option",',
        '    "correct_answer": "A",  // Must be A, B, C, or D',
        '    "explanation": "Detailed explanation of the correct answer and concept...",',
        '    "references": [',
        '      "https://example.com/source1",',
        '      "Textbook Name by Author, Chapter X, Section Y"',
        '    ]',
        "  }",
        "]",
        "```",
        "",
        "**Important:**",
        "- Output ONLY the JSON array, no additional text",
        "- Ensure valid JSON syntax (use double quotes, escape special characters)",
        "- All text must be in English",
        "- Verify that the correct_answer letter matches the actual correct option",
        "",
        f"Now generate {num_questions} question(s) following all requirements above:"
    ])

    return "\n".join(prompt_parts)


def _get_difficulty_hint(difficulty: str) -> str:
    """Get a hint for the specified difficulty level."""
    hints = {
        "Easy": "Direct recall, definitions, basic facts. Single-step reasoning.",
        "Medium": "Application of concepts, 1-2 step problems, combining related concepts.",
        "Hard": "Multi-step reasoning, complex problems, combining multiple concepts, analysis or proof."
    }
    return hints.get(difficulty, "")


def _select_relevant_examples(difficulty: str) -> list:
    """
    Select relevant few-shot examples based on difficulty.

    Strategy:
    - Easy: Show 1-2 Easy examples
    - Medium: Show 1 Easy + 1 Medium example
    - Hard: Show 1 Medium + 1 Hard example
    """
    if difficulty == "Easy":
        # Show Easy examples only
        return [ex for ex in FEW_SHOT_EXAMPLES if ex["difficulty"] == "Easy"][:2]
    elif difficulty == "Medium":
        # Show one Easy and one Medium
        easy = [ex for ex in FEW_SHOT_EXAMPLES if ex["difficulty"] == "Easy"][:1]
        medium = [ex for ex in FEW_SHOT_EXAMPLES if ex["difficulty"] == "Medium"][:1]
        return easy + medium
    else:  # Hard
        # Show Medium and Hard examples
        medium = [ex for ex in FEW_SHOT_EXAMPLES if ex["difficulty"] == "Medium"][:1]
        hard = [ex for ex in FEW_SHOT_EXAMPLES if ex["difficulty"] == "Hard"][:1]
        return medium + hard


# Validation prompt (for checking/improving generated questions)
VALIDATION_PROMPT_TEMPLATE = """Review this MCQ for quality and correctness:

{question_json}

Check for:
1. Technical accuracy
2. Clear, unambiguous wording
3. 4 distinct, plausible options
4. Correct answer is actually correct
5. Explanation is detailed and educational
6. References are credible

If there are issues, output an improved version in the same JSON format.
If it's already good, output the original JSON unchanged.

Output only the JSON, no other text.
"""


def build_validation_prompt(question_dict: Dict[str, Any]) -> str:
    """
    Build a prompt to validate/improve a generated question.

    Args:
        question_dict: Question data as dictionary

    Returns:
        Validation prompt
    """
    import json
    question_json = json.dumps(question_dict, indent=2, ensure_ascii=False)
    return VALIDATION_PROMPT_TEMPLATE.format(question_json=question_json)
