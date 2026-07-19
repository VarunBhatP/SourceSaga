"""
Grok API client via xAI's OpenAI-compatible endpoint.
"""
import os
import time
from typing import List, Optional

from openai import OpenAI


def get_grok_client() -> OpenAI:
    """Get a configured xAI client."""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY not found in environment variables")

    return OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=api_key,
    )


def query_grok(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
    model: str = "grok-3-mini",
    fallback_models: Optional[List[str]] = None,
    max_retries: int = 2,
) -> Optional[str]:
    """
    Query Grok with retry and fallback support.

    Defaults to lower-cost models first so the app works better on trial/free credits.
    """
    if fallback_models is None:
        fallback_models = ["grok-4.1-fast", "grok-4.3"]

    def fallback_to_free_models() -> Optional[str]:
        """Use OpenRouter free models when xAI/Grok is unavailable."""
        try:
            from utils.openrouter_client import query_llm_openrouter

            print("  Falling back to OpenRouter free models...")
            return query_llm_openrouter(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                model="google/gemini-2.0-flash-exp:free",
                fallback_models=[
                    "google/gemini-flash-1.5:free",
                    "meta-llama/llama-3.2-3b-instruct:free",
                ],
            )
        except Exception as fallback_error:
            print(f"  Fallback error: {fallback_error}")
            return None

    models_to_try = [model] + [name for name in fallback_models if name != model]

    try:
        client = get_grok_client()
    except ValueError as error:
        print(f"ERROR: {error}")
        return fallback_to_free_models()

    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                print(f"  Calling Grok ({model_name})...")

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                result = response.choices[0].message.content
                if result:
                    result = result.strip()
                    print(f"  Generated {len(result)} characters")
                    return result

                print("  Empty response")
                break

            except Exception as error:
                error_msg = str(error)

                if "429" in error_msg or "rate" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = 5 * (attempt + 1)
                        print(f"  Rate limited. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    print(f"  Rate limited on {model_name}, trying next model...")
                    break

                if "404" in error_msg or "model" in error_msg.lower() and "not found" in error_msg.lower():
                    print(f"  {model_name} unavailable, trying next model...")
                    break

                print(f"  Error: {error_msg[:200]}")

                if "403" in error_msg or "permission-denied" in error_msg.lower() or "credits" in error_msg.lower():
                    print("  xAI account has no active credits. Switching to free fallback...")
                    return fallback_to_free_models()

                if "401" in error_msg or "unauthorized" in error_msg.lower():
                    print("  Check XAI_API_KEY in .env")
                    return fallback_to_free_models()

                if attempt < max_retries - 1:
                    print("  Retrying...")
                    time.sleep(3)
                    continue

                break

    print("  All Grok models failed")
    return fallback_to_free_models()
