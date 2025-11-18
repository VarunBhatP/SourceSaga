"""
Cerebras API client - Ultra-fast inference.
"""
import os
from typing import Optional
from cerebras.cloud.sdk import Cerebras


def get_cerebras_client():
    """Get configured Cerebras client."""
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        raise ValueError("CEREBRAS_API_KEY not found in environment variables")
    
    return Cerebras(api_key=api_key)


def query_cerebras(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
    model: str = "llama-3.3-70b"  # ✅ Correct format: llama-3.3-70b
) -> Optional[str]:
    """
    Query Cerebras ultra-fast inference API.
    
    Available Free Models:
    - llama-3.3-70b (Best - Most powerful, very fast)
    - llama3.1-8b (Faster, smaller)
    - deepseek-r1-distill-llama-70b (Good reasoning)
    
    Args:
        prompt: The input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        model: Model to use
        
    Returns:
        Generated text or None if error
    """
    try:
        client = get_cerebras_client()
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        return None
    
    try:
        print(f"  🧠 Calling Cerebras ({model})...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if response.choices and response.choices[0].message.content:
            result = response.choices[0].message.content.strip()
            print(f"  ⚡ Generated {len(result)} characters (ultra-fast)")
            return result
        else:
            print(f"  ⚠️ Empty response")
            return None
    
    except Exception as e:
        error_msg = str(e)
        print(f"  ❌ Error: {error_msg[:200]}")
        
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            print("  💡 Check CEREBRAS_API_KEY in .env")
        elif "429" in error_msg or "rate" in error_msg.lower():
            print("  💡 Rate limited")
        elif "404" in error_msg or "not_found" in error_msg.lower():
            print("  💡 Model not found. Available: llama-3.3-70b, llama3.1-8b")
        
        return None
