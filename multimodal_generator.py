"""
Multimodal MCQ generator using vision-language models.

Main function: generate_multimodal_mcqs(text, images, difficulty, n)

Generates questions that require interpreting diagrams, formulas, or graphs.
"""

import json
import re
from typing import List, Optional

from models import Question, DifficultyLevel
from multimodal_models import TextImagePair, MultimodalQuestionMetadata
from multimodal_prompts import build_multimodal_prompt, get_diagram_type_hint
from vlm_client import VLMClient, create_vlm_client, MockVLMClient
from config import GenerationConfig, DEFAULT_GENERATION_CONFIG


class MultimodalMCQGenerator:
    """
    Generator for creating diagram-based MCQs using vision-language models.

    Usage:
        generator = MultimodalMCQGenerator()
        questions = generator.generate_from_pair(
            pair=text_image_pair,
            subject="Physics",
            main_topic="Mechanics",
            subtopic="Free Body Diagrams",
            difficulty=DifficultyLevel.MEDIUM,
            n=3
        )
    """

    def __init__(
        self,
        vlm_client: Optional[VLMClient] = None,
        generation_config: Optional[GenerationConfig] = None,
        use_mock: bool = False
    ):
        """
        Initialize multimodal MCQ generator.

        Args:
            vlm_client: VLM client (creates default if None)
            generation_config: Generation config (uses default if None)
            use_mock: Use mock VLM for testing (no real VLM needed)
        """
        if use_mock:
            self.vlm_client = MockVLMClient()
        else:
            self.vlm_client = vlm_client or create_vlm_client()

        self.config = generation_config or DEFAULT_GENERATION_CONFIG

    def generate_from_pair(
        self,
        pair: TextImagePair,
        subject: str,
        main_topic: str,
        subtopic: str,
        difficulty: DifficultyLevel,
        n: int = 1,
        test_section: Optional[str] = None
    ) -> List[Question]:
        """
        Generate MCQs from a text-image pair.

        Args:
            pair: Text-image pair with diagram and context
            subject: Subject name
            main_topic: Main topic
            subtopic: Subtopic
            difficulty: Difficulty level
            n: Number of questions
            test_section: Test section name (defaults to main_topic)

        Returns:
            List of validated Question objects
        """
        test_section = test_section or main_topic

        print(f"\n{'='*80}")
        print(f"Generating {n} {difficulty.value} Multimodal MCQ(s)")
        print(f"Topic: {subject} → {main_topic} → {subtopic}")
        print(f"Images: {len(pair.images)}")
        print(f"{'='*80}")

        questions = []
        attempts = 0
        max_attempts = n * (1 + self.config.max_validation_retries)

        while len(questions) < n and attempts < max_attempts:
            remaining = n - len(questions)
            attempts += 1

            print(f"\n📝 Attempt {attempts}: Generating {remaining} question(s)...")

            try:
                # Infer diagram type from text
                diagram_type = get_diagram_type_hint(pair.text)

                # Build prompt
                prompt = build_multimodal_prompt(
                    text_context=pair.text,
                    num_images=len(pair.images),
                    difficulty=difficulty,
                    subject=subject,
                    main_topic=main_topic,
                    subtopic=subtopic,
                    num_questions=remaining,
                    diagram_type=diagram_type
                )

                # Get images as base64
                images_base64 = pair.get_image_base64_list()

                # Call VLM
                print(f"🤖 Calling VLM (prompt: {len(prompt)} chars, images: {len(images_base64)})...")
                response_text = self.vlm_client.generate_multimodal(
                    prompt=prompt,
                    images_base64=images_base64
                )
                print(f"✅ Received response ({len(response_text)} chars)")

                # Parse JSON
                question_dicts = self._parse_vlm_response(response_text)
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
                            difficulty=difficulty,
                            pair=pair
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

        print(f"\n{'='*80}")
        print(f"✅ Successfully generated {len(questions)} multimodal question(s)")
        print(f"{'='*80}\n")

        return questions

    def _parse_vlm_response(self, response_text: str) -> List[dict]:
        """Parse VLM response to extract JSON array of questions."""
        # Same logic as text-only generator
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)

        if not json_match:
            # Try to find single object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = f"[{json_match.group(0)}]"
            else:
                raise ValueError("No JSON found in VLM response")
        else:
            json_str = json_match.group(0)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            # Try to clean
            json_str = self._clean_json(json_str)
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON in VLM response: {e}")

        # Ensure it's a list
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError(f"Expected JSON array, got {type(data)}")

        return data

    def _clean_json(self, json_str: str) -> str:
        """Clean up malformed JSON."""
        # Remove trailing commas
        json_str = re.sub(r',(\s*[\]}])', r'\1', json_str)
        return json_str

    def _dict_to_question(
        self,
        q_dict: dict,
        test_section: str,
        main_topic: str,
        subtopic: str,
        difficulty: DifficultyLevel,
        pair: TextImagePair
    ) -> Question:
        """Convert dictionary to Question object with multimodal metadata."""
        required_fields = [
            "question_text_en", "option_a_en", "option_b_en",
            "option_c_en", "option_d_en", "correct_answer", "explanation"
        ]

        missing = [f for f in required_fields if f not in q_dict]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        # Extract references
        references = q_dict.get("references", [])
        if isinstance(references, str):
            references = [references]

        # Create Question
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
            references=[str(r).strip() for r in references],
            source_pdf=pair.source_pdf,
            has_diagram=True
        )

        return question

    def _passes_additional_validation(self, question: Question) -> bool:
        """Additional validation for multimodal questions."""
        # Same as text-only for now
        if len(question.explanation) < self.config.min_explanation_length:
            print(f"      ⚠️  Explanation too short")
            return False

        if self.config.require_references and len(question.references) < self.config.min_references:
            print(f"      ⚠️  Not enough references")
            return False

        # Check for diagram-specific keywords in question
        # (Ensures question actually requires the diagram)
        diagram_keywords = [
            "shown", "diagram", "figure", "graph", "image", "above",
            "below", "illustrated", "depicted", "displayed", "curve",
            "plot", "chart", "table"
        ]

        question_lower = question.question_text_en.lower()
        if not any(keyword in question_lower for keyword in diagram_keywords):
            print(f"      ⚠️  Question doesn't reference diagram/image")
            return False

        return True


# Convenience function
def generate_multimodal_mcqs(
    text: str,
    images_base64: List[str],
    subject: str,
    main_topic: str,
    subtopic: str,
    difficulty: DifficultyLevel,
    n: int = 1,
    vlm_base_url: Optional[str] = None,
    vlm_model: Optional[str] = None,
    use_mock: bool = False
) -> List[Question]:
    """
    Convenience function to generate multimodal MCQs.

    Args:
        text: Context text (caption + nearby text)
        images_base64: List of base64-encoded images
        subject: Subject name
        main_topic: Main topic
        subtopic: Subtopic
        difficulty: Difficulty level
        n: Number of questions
        vlm_base_url: VLM endpoint URL (optional)
        vlm_model: VLM model name (optional)
        use_mock: Use mock VLM for testing

    Returns:
        List of Question objects
    """
    # Create VLM client
    vlm_client = create_vlm_client(
        base_url=vlm_base_url,
        model_name=vlm_model,
        use_mock=use_mock
    )

    # Create generator
    generator = MultimodalMCQGenerator(vlm_client=vlm_client, use_mock=use_mock)

    # Create a TextImagePair (need to reconstruct ExtractedImage objects)
    # For simplicity in this convenience function, we'll work directly with the generator
    # In practice, use generate_from_pair() with proper TextImagePair objects

    from multimodal_models import ExtractedImage, TextImagePair
    import base64

    images = []
    for i, img_b64 in enumerate(images_base64):
        img_bytes = base64.b64decode(img_b64)
        images.append(ExtractedImage(
            image_data=img_bytes,
            page_number=1,
            image_index=i
        ))

    pair = TextImagePair(
        text=text,
        images=images,
        page_number=1
    )

    return generator.generate_from_pair(
        pair=pair,
        subject=subject,
        main_topic=main_topic,
        subtopic=subtopic,
        difficulty=difficulty,
        n=n
    )
