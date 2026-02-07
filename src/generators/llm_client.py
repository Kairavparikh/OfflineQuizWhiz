"""
Client for interacting with local LLM endpoints.

Supports:
- Ollama API format
- Generic POST /generate endpoints
- Retry logic and error handling
"""

import json
import time
import requests
from typing import Optional, Dict, Any
from src.config import LLMConfig, DEFAULT_LLM_CONFIG


class LLMClient:
    """
    Client for calling local LLM endpoints.

    Supports multiple API formats:
    - Ollama: POST /api/generate with streaming or non-streaming
    - Generic: POST /generate with JSON payload
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM client.

        Args:
            config: LLM configuration (uses default if not provided)
        """
        self.config = config or DEFAULT_LLM_CONFIG
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[list] = None
    ) -> str:
        """
        Generate text from the local LLM.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens (overrides config)
            stop_sequences: List of sequences that stop generation

        Returns:
            Generated text

        Raises:
            LLMError: If generation fails after retries
        """
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens

        # Build request payload
        payload = self._build_payload(prompt, temperature, max_tokens, stop_sequences)

        # Try with retries
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                response = self._call_llm(payload)
                return response
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    print(f"⚠️  LLM call failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                    print(f"   Retrying in {self.config.retry_delay_seconds}s...")
                    time.sleep(self.config.retry_delay_seconds)
                else:
                    print(f"❌ LLM call failed after {self.config.max_retries} attempts")

        raise LLMError(f"Failed to generate response after {self.config.max_retries} attempts: {last_error}")

    def _build_payload(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        stop_sequences: Optional[list]
    ) -> Dict[str, Any]:
        """Build request payload based on API format."""
        # Ollama format
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "stream": False,  # We want complete response, not streaming
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        if stop_sequences:
            payload["options"]["stop"] = stop_sequences

        return payload

    def _call_llm(self, payload: Dict[str, Any]) -> str:
        """
        Make HTTP call to LLM endpoint.

        Args:
            payload: Request payload

        Returns:
            Generated text

        Raises:
            requests.RequestException: If HTTP request fails
            ValueError: If response format is invalid
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

        # Parse response based on API format
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse JSON response: {e}")

        # Extract text from Ollama format
        if "response" in data:
            return data["response"].strip()
        # Extract from generic format
        elif "text" in data:
            return data["text"].strip()
        elif "content" in data:
            return data["content"].strip()
        else:
            raise LLMError(f"Unexpected response format. Keys: {list(data.keys())}")

    def test_connection(self) -> bool:
        """
        Test connection to LLM endpoint.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.generate("Test", temperature=0.1, max_tokens=10)
            print(f"✅ LLM connection successful!")
            print(f"   Endpoint: {self.config.base_url}{self.config.generate_endpoint}")
            print(f"   Model: {self.config.model_name}")
            print(f"   Test response: {response[:50]}...")
            return True
        except Exception as e:
            print(f"❌ LLM connection failed: {e}")
            print(f"   Endpoint: {self.config.base_url}{self.config.generate_endpoint}")
            return False


class GenericLLMClient(LLMClient):
    """
    Client for generic POST /generate endpoints.

    Use this if your LLM has a simpler API format.
    """

    def _build_payload(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        stop_sequences: Optional[list]
    ) -> Dict[str, Any]:
        """Build simple payload for generic endpoints."""
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if stop_sequences:
            payload["stop"] = stop_sequences

        return payload


class LLMError(Exception):
    """Exception raised for LLM-related errors."""
    pass


def create_llm_client(
    base_url: Optional[str] = None,
    model_name: Optional[str] = None,
    api_type: str = "ollama"
) -> LLMClient:
    """
    Factory function to create LLM client.

    Args:
        base_url: Base URL for LLM endpoint (uses default if None)
        model_name: Model name (uses default if None)
        api_type: Type of API ("ollama" or "generic")

    Returns:
        Configured LLM client
    """
    config = LLMConfig()

    if base_url:
        config.base_url = base_url
    if model_name:
        config.model_name = model_name

    if api_type == "generic":
        config.generate_endpoint = "/generate"
        return GenericLLMClient(config)
    else:
        return LLMClient(config)


# Convenience function for quick testing
def test_llm_endpoint(base_url: str = "http://localhost:11434", model: str = "llama2"):
    """
    Quick test of LLM endpoint.

    Args:
        base_url: Base URL
        model: Model name

    Returns:
        True if successful
    """
    client = create_llm_client(base_url=base_url, model_name=model)
    return client.test_connection()
