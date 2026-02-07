"""
Configuration for the MCQ Generator system.
"""

import os
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configuration for local LLM endpoint."""

    # LLM endpoint
    base_url: str = "http://localhost:11434"  # Default Ollama endpoint
    generate_endpoint: str = "/api/generate"  # Ollama format

    # Model settings
    model_name: str = "mistral"  # Default model (change if using different model)
    temperature: float = 0.7  # Higher = more creative, lower = more deterministic
    max_tokens: int = 2048  # Maximum tokens in response

    # Timeout settings
    timeout_seconds: int = 120  # 2 minutes max per request

    # Retry settings
    max_retries: int = 3
    retry_delay_seconds: int = 2

    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """
        Create config from environment variables.

        Environment variables:
            LLM_BASE_URL: Base URL for LLM endpoint
            LLM_MODEL: Model name
            LLM_TEMPERATURE: Sampling temperature
            LLM_MAX_TOKENS: Maximum tokens
        """
        return cls(
            base_url=os.getenv("LLM_BASE_URL", cls.base_url),
            model_name=os.getenv("LLM_MODEL", cls.model_name),
            temperature=float(os.getenv("LLM_TEMPERATURE", cls.temperature)),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", cls.max_tokens)),
        )


# Default configuration
DEFAULT_LLM_CONFIG = LLMConfig(
    base_url="http://localhost:11434",
    generate_endpoint="/api/generate",
    model_name="mistral",
    temperature=0.7,
    max_tokens=2048,
    timeout_seconds=120
)


# Generation settings
@dataclass
class GenerationConfig:
    """Configuration for MCQ generation behavior."""

    # Validation
    min_explanation_length: int = 20  # Minimum characters in explanation
    require_references: bool = True  # Require at least one reference
    min_references: int = 1  # Minimum number of references

    # Retry behavior
    max_validation_retries: int = 2  # Retries per question if validation fails

    # Output format
    include_metadata: bool = True  # Include creation timestamp, source info

    # Prompt engineering
    use_few_shot: bool = True  # Include few-shot examples in prompts
    num_few_shot_examples: int = 2  # Number of examples to include


DEFAULT_GENERATION_CONFIG = GenerationConfig()
