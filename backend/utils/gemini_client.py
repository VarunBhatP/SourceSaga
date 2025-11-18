"""
Google Gemini API client with OpenRouter fallback.
"""
import os
import time
from typing import Optional
import google.generativeai as genai


def get_gemini_client():
    """Configure and return Gemini API client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    return genai


def query_gemini(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
    model: str = "gemini-2.0-flash-exp",
    max_retries: int = 2,  # Reduced retries
    use_fallback: bool = True  # NEW: Enable fallback
) -> Optional[str]:
    """
    Query Google Gemini API with OpenRouter fallback.
    """
    try:
        get_gemini_client()
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        if use_fallback:
            return _fallback_to_openrouter(prompt, max_tokens, temperature)
        return None
    
    for attempt in range(max_retries):
        try:
            print(f"  🤖 Calling Gemini ({model})...")
            
            gemini_model = genai.GenerativeModel(model)
            
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
            )
            
            if response and response.text:
                result = response.text.strip()
                print(f"  ✅ Generated {len(result)} characters")
                return result
            else:
                print(f"  ⚠️ Empty response from Gemini")
                return None
        
        except Exception as e:
            error_msg = str(e)
            
            # Handle rate limiting
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"  ⏳ Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"  ⚠️ Gemini rate limited, switching to fallback...")
                    if use_fallback:
                        return _fallback_to_openrouter(prompt, max_tokens, temperature)
                    return None
            
            # Other errors
            print(f"  ❌ Error: {error_msg[:200]}")
            
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            
            if use_fallback:
                return _fallback_to_openrouter(prompt, max_tokens, temperature)
            
            return None
    
    return None


def _fallback_to_openrouter(prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
    """Fallback to OpenRouter if Gemini fails."""
    try:
        from utils.openrouter_client import query_llm_openrouter
        
        print(f"  🔄 Falling back to OpenRouter...")
        
        return query_llm_openrouter(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            model="google/gemini-2.0-flash-exp:free",
            fallback_models=["meta-llama/llama-3.2-3b-instruct:free"]
        )
    except Exception as e:
        print(f"  ❌ Fallback also failed: {e}")
        return None
