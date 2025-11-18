"""
OpenRouter API client with automatic retry and model fallback.
"""
import os
import time
from typing import Optional, List
from openai import OpenAI


def get_openrouter_client():
    """Get configured OpenRouter client."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "SourceSage",
        }
    )


def query_llm_openrouter(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
    model: str = "google/gemini-2.0-flash-exp:free",  # Default to Gemini
    fallback_models: Optional[List[str]] = None,
    max_retries: int = 2
) -> Optional[str]:
    """
    Query OpenRouter's API with automatic retry and model fallback.
    
    Recommended Free Models:
    - google/gemini-2.0-flash-exp:free (BEST - Fast, high rate limits)
    - google/gemini-flash-1.5:free (Also good)
    - meta-llama/llama-3.2-3b-instruct:free (Backup)
    
    Args:
        prompt: The input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        model: Primary model to use
        fallback_models: List of backup models to try if primary fails
        max_retries: Number of retries per model
        
    Returns:
        Generated text or None if all attempts fail
    """
    # Set default fallback models if not provided
    if fallback_models is None:
        fallback_models = [
            "google/gemini-flash-1.5:free",
            "meta-llama/llama-3.2-3b-instruct:free"
        ]
    
    # Try primary model, then fallbacks
    models_to_try = [model] + fallback_models
    
    try:
        client = get_openrouter_client()
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        return None
    
    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                model_short = model_name.split('/')[1][:25]
                print(f"  🤖 Calling {model_short}...")
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                result = response.choices[0].message.content
                
                if result:
                    print(f"  ✅ Generated {len(result)} characters")
                    return result.strip()
                else:
                    print(f"  ⚠️ Empty response")
                    break  # Try next model
            
            except Exception as e:
                error_msg = str(e)
                
                # Handle rate limiting
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = 5 * (attempt + 1)  # 5s, 10s
                        print(f"  ⏳ Rate limited. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"  ⚠️ Rate limited on {model_short}, trying next model...")
                        break  # Try next model
                
                # Handle model not available
                if "404" in error_msg or "No endpoints" in error_msg:
                    print(f"  ⚠️ {model_short} not available, trying next...")
                    break
                
                # Handle other errors
                print(f"  ❌ Error: {error_msg[:150]}")
                
                if "401" in error_msg or "unauthorized" in error_msg.lower():
                    print("  💡 Check OPENROUTER_API_KEY")
                    return None
                
                if attempt < max_retries - 1:
                    print(f"  🔄 Retrying...")
                    time.sleep(3)
                    continue
                else:
                    break  # Try next model
    
    print(f"  ❌ All models failed or rate limited")
    return None
