"""
Client for Vision-Language Model (VLM) endpoints.

Supports multimodal generation with:
- Text prompts
- Multiple images (as base64)
- Similar API to text-only LLM client
"""

import json
import time
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from llm_client import LLMError  # Reuse same error class


@dataclass
class VLMConfig:
    """Configuration for Vision-Language Model endpoint."""

    # VLM endpoint
    base_url: str = "http://localhost:11435"  # Different port from text-only
    generate_endpoint: str = "/api/generate"  # Qwen-VL / LLaVA style

    # Model settings
    model_name: str = "llava"  # or "qwen-vl", etc.
    temperature: float = 0.7
    max_tokens: int = 2048

    # Timeout settings
    timeout_seconds: int = 180  # VLMs are slower
    max_retries: int = 3
    retry_delay_seconds: int = 3


class VLMClient:
    """
    Client for calling local Vision-Language Model endpoints.

    Supports:
    - Text + image(s) input
    - JSON response parsing
    - Retry logic
    """

    def __init__(self, config: Optional[VLMConfig] = None):
        """
        Initialize VLM client.

        Args:
            config: VLM configuration (uses default if None)
        """
        self.config = config or VLMConfig()
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })

    def generate_multimodal(
        self,
        prompt: str,
        images_base64: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text from VLM given text prompt and images.

        Args:
            prompt: Text prompt
            images_base64: List of base64-encoded images
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens (overrides config)

        Returns:
            Generated text

        Raises:
            LLMError: If generation fails after retries
        """
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens

        # Build request payload
        payload = self._build_payload(prompt, images_base64, temperature, max_tokens)

        # Try with retries
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                response = self._call_vlm(payload)
                return response
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    print(f"⚠️  VLM call failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                    print(f"   Retrying in {self.config.retry_delay_seconds}s...")
                    time.sleep(self.config.retry_delay_seconds)
                else:
                    print(f"❌ VLM call failed after {self.config.max_retries} attempts")

        raise LLMError(f"Failed to generate response after {self.config.max_retries} attempts: {last_error}")

    def _build_payload(
        self,
        prompt: str,
        images_base64: List[str],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Build request payload for VLM API."""
        # Format depends on VLM API
        # This is a generic format - adjust for your specific VLM

        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "images": images_base64,  # List of base64 strings
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        return payload

    def _call_vlm(self, payload: Dict[str, Any]) -> str:
        """
        Make HTTP call to VLM endpoint.

        Args:
            payload: Request payload

        Returns:
            Generated text

        Raises:
            LLMError: If HTTP request fails
        """
        url = f"{self.config.base_url}{self.config.generate_endpoint}"

        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise LLMError(f"HTTP request failed: {e}")

        # Parse response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse JSON response: {e}")

        # Extract text (format varies by VLM)
        if "response" in data:
            return data["response"].strip()
        elif "text" in data:
            return data["text"].strip()
        elif "content" in data:
            return data["content"].strip()
        elif "output" in data:
            return data["output"].strip()
        else:
            raise LLMError(f"Unexpected response format. Keys: {list(data.keys())}")

    def test_connection(self) -> bool:
        """
        Test connection to VLM endpoint.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test with minimal image
            test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="  # 1x1 red pixel
            response = self.generate_multimodal(
                "Describe this image briefly",
                [test_image],
                temperature=0.1,
                max_tokens=50
            )
            print(f"✅ VLM connection successful!")
            print(f"   Endpoint: {self.config.base_url}{self.config.generate_endpoint}")
            print(f"   Model: {self.config.model_name}")
            print(f"   Test response: {response[:50]}...")
            return True
        except Exception as e:
            print(f"❌ VLM connection failed: {e}")
            print(f"   Endpoint: {self.config.base_url}{self.config.generate_endpoint}")
            return False


# Alternative: Mock VLM client for testing without actual VLM
class MockVLMClient:
    """
    Mock VLM client for testing multimodal pipeline without a real VLM.

    Returns dummy responses in the correct format.
    """

    def __init__(self, config: Optional[VLMConfig] = None):
        """Initialize mock client."""
        self.config = config or VLMConfig()
        print("⚠️  Using MockVLMClient - responses will be dummy data")

    def generate_multimodal(
        self,
        prompt: str,
        images_base64: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate mock response.

        Returns a dummy JSON with one MCQ to test the pipeline.
        """
        print(f"\n🤖 MockVLM: Generating response...")
        print(f"   Prompt length: {len(prompt)} chars")
        print(f"   Images: {len(images_base64)}")

        # Simulate processing time
        time.sleep(2)

        # Return dummy MCQ in correct format
        mock_response = """[
  {
    "question_text_en": "Based on the diagram shown, what is the primary transformation occurring at the eutectoid point?",
    "option_a_en": "Liquid to solid transformation",
    "option_b_en": "Austenite transforms to pearlite (ferrite + cementite)",
    "option_c_en": "Ferrite transforms to austenite",
    "option_d_en": "Cementite decomposes into graphite",
    "correct_answer": "B",
    "explanation": "The diagram shows the Fe-C phase diagram where the eutectoid point at 727°C marks the transformation of austenite (γ) into a lamellar structure of ferrite (α) and cementite (Fe3C) known as pearlite. This is a solid-state transformation occurring at a fixed composition (0.8% C) and temperature.",
    "references": [
      "https://en.wikipedia.org/wiki/Iron-carbon_phase_diagram",
      "Phase Transformations in Metals and Alloys by Porter & Easterling, Chapter 5"
    ]
  }
]"""

        print(f"✅ Mock response generated ({len(mock_response)} chars)")
        return mock_response

    def test_connection(self) -> bool:
        """Mock connection test always succeeds."""
        print("✅ MockVLM connection OK (mock mode)")
        return True


def create_vlm_client(
    base_url: Optional[str] = None,
    model_name: Optional[str] = None,
    use_mock: bool = False
) -> VLMClient:
    """
    Factory function to create VLM client.

    Args:
        base_url: Base URL for VLM endpoint
        model_name: Model name
        use_mock: Use mock client for testing (no real VLM needed)

    Returns:
        VLM client instance
    """
    config = VLMConfig()

    if base_url:
        config.base_url = base_url
    if model_name:
        config.model_name = model_name

    if use_mock:
        return MockVLMClient(config)
    else:
        return VLMClient(config)


def test_vlm_endpoint(
    base_url: str = "http://localhost:11435",
    model: str = "llava",
    use_mock: bool = False
) -> bool:
    """
    Quick test of VLM endpoint.

    Args:
        base_url: Base URL
        model: Model name
        use_mock: Use mock client

    Returns:
        True if successful
    """
    client = create_vlm_client(base_url=base_url, model_name=model, use_mock=use_mock)
    return client.test_connection()
