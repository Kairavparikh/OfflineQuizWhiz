"""
Direct test of Ollama API to diagnose the issue.
"""

import requests
import json

print("\n" + "="*80)
print("TESTING OLLAMA API DIRECTLY")
print("="*80)

# Test 1: Check if Ollama is responding
print("\n1. Testing if Ollama server is reachable...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    print(f"   ✅ Server is reachable (status: {response.status_code})")

    if response.status_code == 200:
        data = response.json()
        models = data.get('models', [])
        print(f"\n   Available models:")
        for model in models:
            print(f"   - {model.get('name', 'unknown')}")

        if models:
            model_name = models[0].get('name', '').split(':')[0]
            print(f"\n   Using model: {model_name}")
        else:
            print("\n   ⚠️  No models found! Run: ollama pull mistral")
            model_name = "mistral"
    else:
        model_name = "mistral"

except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to Ollama!")
    print("   Make sure Ollama is running: ollama serve")
    exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    model_name = "mistral"

# Test 2: Try to generate with the model
print(f"\n2. Testing generation with model '{model_name}'...")

payload = {
    "model": model_name,
    "prompt": "What is 2+2? Answer in one sentence.",
    "stream": False
}

try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=30
    )

    print(f"   Status code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        answer = data.get('response', 'No response')
        print(f"   ✅ Generation successful!")
        print(f"   Response: {answer[:100]}")

        print("\n" + "="*80)
        print("✅ OLLAMA IS WORKING CORRECTLY!")
        print("="*80)
        print(f"\nYour model name is: {model_name}")
        print(f"\nUpdate config.py to use this model:")
        print(f"   model_name=\"{model_name}\"")

    elif response.status_code == 404:
        print(f"   ❌ 404 Error - Model not found!")
        print(f"   The model '{model_name}' might not be available.")
        print(f"\n   Try these commands:")
        print(f"   1. ollama list          # See available models")
        print(f"   2. ollama pull mistral  # Download mistral")
        print(f"   3. ollama run mistral   # Test it works")

    else:
        print(f"   ❌ Unexpected status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")

except requests.exceptions.Timeout:
    print("   ❌ Request timed out (model might be loading)")
    print("   Wait a moment and try again")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*80)
