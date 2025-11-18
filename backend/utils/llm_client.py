"""
Hugging Face LLM client for calling free inference APIs.
"""
import os
import requests
from typing import Optional

HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_BASE = "https://api-inference.huggingface.co/models"


def query_llm(
    model_id: str,
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7
) -> Optional[str]:
    """
    Query a Hugging Face model via the Inference API.
    
    Args:
        model_id: The Hugging Face model identifier
        prompt: The input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Generated text or None if error
    """
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(
            f"{HF_API_BASE}/{model_id}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return str(result)
        else:
            print(f"LLM API Error: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return None
