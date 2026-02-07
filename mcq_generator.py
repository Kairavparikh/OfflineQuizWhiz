"""
Core MCQ generator using local LLM.

Main function: generate_mcqs(subject, main_topic, subtopic, difficulty, n)
Returns a list of validated Question objects.
"""

import json
import re
from typing import List, Optional, Dict, Any
from models import Question, DifficultyLevel
from llm_client import LLMClient, LLMError, create_llm_client
from prompt_templates import build_mcq_generation_prompt
from config import GenerationConfig, DEFAULT_GENERATION_CONFIG


class MCQGenerator:
    """
    Generator for creating MCQs using a local LLM.

    Usage:
        generator = MCQGenerator()
        questions = generator.generate_mcqs(
            subject="Metallurgical Engineering",
            main_topic="Engineering Mathematics",
            subtopic="Linear Algebra - Matrices and Determinants",
            difficulty=DifficultyLevel.MEDIUM,
            n=5
        )
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        generation_config: Optional[GenerationConfig] = None
    ):
        """
        Initialize MCQ generator.

        Args:
            llm_client: LLM client (creates default if None)
            generation_config: Generation config (uses default if None)
        """
        self.llm_client = llm_client or create_llm_client()
        self.config = generation_config or DEFAULT_GENERATION_CONFIG

    def generate_mcqs(
        self,
        subject: str,
        main_topic: str,
        subtopic: str,
        difficulty: DifficultyLevel,
        n: int = 1,
        test_section: Optional[str] = None
    ) -> List[Question]:
        """
        Generate N MCQs for the given topic and difficulty.

        Args:
            subject: Subject name (e.g., "Metallurgical Engineering")
            main_topic: Main topic (e.g., "Engineering Mathematics")
            subtopic: Subtopic (e.g., "Linear Algebra - Matrices")
            difficulty: Difficulty level (Easy/Medium/Hard)
            n: Number of questions to generate
            test_section: Test section name (defaults to main_topic if None)

        Returns:
            List of validated Question objects

        Raises:
            MCQGenerationError: If generation fails
        """
        test_section = test_section or main_topic

        print(f"\n{'='*80}")
        print(f"Generating {n} {difficulty.value} MCQ(s)")
        print(f"Topic: {subject} → {main_topic} → {subtopic}")
        print(f"{'='*80}")

        questions = []
        attempts = 0
        max_attempts = n * (1 + self.config.max_validation_retries)

        while len(questions) < n and attempts < max_attempts:
            remaining = n - len(questions)
            attempts += 1

            print(f"\n📝 Attempt {attempts}: Generating {remaining} question(s)...")

            try:
                # Build prompt
                prompt = build_mcq_generation_prompt(
                    subject=subject,
                    main_topic=main_topic,
                    subtopic=subtopic,
                    difficulty=difficulty,
                    num_questions=remaining,
                    include_few_shot=self.config.use_few_shot
                )

                # Call LLM
                print(f"🤖 Calling LLM (prompt length: {len(prompt)} chars)...")
                response_text = self.llm_client.generate(prompt)
                print(f"✅ Received response ({len(response_text)} chars)")

                # Parse JSON
                question_dicts = self._parse_llm_response(response_text)
                print(f"📋 Parsed {len(question_dicts)} question(s)")

                # Convert to Question objects and validate
                for i, q_dict in enumerate(question_dicts, 1):
                    if len(questions) >= n:
                        break

                    try:
                        question = self._dict_to_question(
                            q_dict,
                            test_section=test_section,
                            main_topic=main_topic,
                            subtopic=subtopic,
                            difficulty=difficulty
                        )

                        # Validate
                        errors = question.validate()
                        if errors:
                            print(f"   ⚠️  Question {i} validation failed:")
                            for error in errors:
                                print(f"      - {error}")
                            continue

                        # Additional validation
                        if not self._passes_additional_validation(question):
                            continue

                        questions.append(question)
                        print(f"   ✅ Question {i} valid: {question.question_text_en[:60]}...")

                    except Exception as e:
                        print(f"   ❌ Question {i} failed: {e}")
                        continue

            except Exception as e:
                print(f"❌ Generation attempt {attempts} failed: {e}")
                continue

        if len(questions) < n:
            print(f"\n⚠️  Warning: Only generated {len(questions)}/{n} valid questions after {attempts} attempts")

        if len(questions) == 0:
            raise MCQGenerationError(f"Failed to generate any valid questions after {attempts} attempts")

        print(f"\n{'='*80}")
        print(f"✅ Successfully generated {len(questions)} question(s)")
        print(f"{'='*80}\n")

        return questions

    def _parse_llm_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response to extract JSON array of questions.

        Args:
            response_text: Raw LLM response

        Returns:
            List of question dictionaries

        Raises:
            ValueError: If parsing fails
        """
        # Try to find JSON array in response
        # Look for [...] pattern
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)

        if not json_match:
            # Try to find single object and wrap it
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = f"[{json_match.group(0)}]"
            else:
                raise ValueError("No JSON found in LLM response")
        else:
            json_str = json_match.group(0)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            # Try to clean up common issues
            json_str = self._clean_json(json_str)
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON in LLM response: {e}")

        # Ensure it's a list
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError(f"Expected JSON array or object, got {type(data)}")

        return data

    def _clean_json(self, json_str: str) -> str:
        """
        Attempt to clean up malformed JSON.

        Args:
            json_str: Potentially malformed JSON string

        Returns:
            Cleaned JSON string
        """
        # Remove trailing commas before ] or }
        json_str = re.sub(r',(\s*[\]}])', r'\1', json_str)

        # Fix unescaped quotes in strings (basic attempt)
        # This is tricky and not perfect, but handles some cases

        return json_str

    def _dict_to_question(
        self,
        q_dict: Dict[str, Any],
        test_section: str,
        main_topic: str,
        subtopic: str,
        difficulty: DifficultyLevel
    ) -> Question:
        """
        Convert dictionary to Question object.

        Args:
            q_dict: Question dictionary from LLM
            test_section: Test section name
            main_topic: Main topic
            subtopic: Subtopic
            difficulty: Difficulty level

        Returns:
            Question object

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = [
            "question_text_en",
            "option_a_en",
            "option_b_en",
            "option_c_en",
            "option_d_en",
            "correct_answer",
            "explanation"
        ]

        # Check required fields
        missing = [f for f in required_fields if f not in q_dict]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        # Extract references (handle both list and string)
        references = q_dict.get("references", [])
        if isinstance(references, str):
            references = [references]
        elif not isinstance(references, list):
            references = []

        # Create Question object
        question = Question(
            test_section=test_section,
            main_topic=main_topic,
            subtopic=subtopic,
            difficulty=difficulty,
            question_text_en=str(q_dict["question_text_en"]).strip(),
            option_a_en=str(q_dict["option_a_en"]).strip(),
            option_b_en=str(q_dict["option_b_en"]).strip(),
            option_c_en=str(q_dict["option_c_en"]).strip(),
            option_d_en=str(q_dict["option_d_en"]).strip(),
            correct_answer=str(q_dict["correct_answer"]).strip().upper(),
            explanation=str(q_dict["explanation"]).strip(),
            references=[str(r).strip() for r in references]
        )

        return question

    def _passes_additional_validation(self, question: Question) -> bool:
        """
        Additional validation checks beyond Question.validate().

        Args:
            question: Question to validate

        Returns:
            True if passes all checks
        """
        # Check explanation length
        if len(question.explanation) < self.config.min_explanation_length:
            print(f"      ⚠️  Explanation too short ({len(question.explanation)} < {self.config.min_explanation_length} chars)")
            return False

        # Check references
        if self.config.require_references and len(question.references) < self.config.min_references:
            print(f"      ⚠️  Not enough references ({len(question.references)} < {self.config.min_references})")
            return False

        # Check that options are not too similar
        options = [
            question.option_a_en.lower(),
            question.option_b_en.lower(),
            question.option_c_en.lower(),
            question.option_d_en.lower()
        ]

        # Basic similarity check (exact duplicates already caught by Question.validate())
        # Check for options that are too short (likely lazy generation)
        if any(len(opt) < 2 for opt in options):
            print(f"      ⚠️  One or more options are too short")
            return False

        return True


class MCQGenerationError(Exception):
    """Exception raised when MCQ generation fails."""
    pass


# Convenience function
def generate_mcqs(
    subject: str,
    main_topic: str,
    subtopic: str,
    difficulty: DifficultyLevel,
    n: int = 1,
    llm_base_url: Optional[str] = None,
    llm_model: Optional[str] = None
) -> List[Question]:
    """
    Convenience function to generate MCQs.

    Args:
        subject: Subject name
        main_topic: Main topic
        subtopic: Subtopic
        difficulty: Difficulty level
        n: Number of questions
        llm_base_url: LLM endpoint URL (optional)
        llm_model: LLM model name (optional)

    Returns:
        List of Question objects
    """
    # Create LLM client
    llm_client = create_llm_client(
        base_url=llm_base_url,
        model_name=llm_model
    )

    # Create generator
    generator = MCQGenerator(llm_client=llm_client)

    # Generate
    return generator.generate_mcqs(
        subject=subject,
        main_topic=main_topic,
        subtopic=subtopic,
        difficulty=difficulty,
        n=n
    )
