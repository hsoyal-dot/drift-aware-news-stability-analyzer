# extraction/claim_extractor.py
"""Claim extraction module.

Extracts atomic factual claims from a news article variant using an LLM.
"""

import os
import json
import time
from typing import List, Dict
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

def _call_llm_for_claims(text: str, model_name: str, max_retries: int = 3) -> List[Dict]:
    """Call LLM to extract claims.
    
    Returns a list of claim dictionaries with keys: subject, predicate, object, confidence.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(model_name)
    prompt = (
        "Extract the TOP 10 most crucial, distinct factual claims from the following text. "
        "Do not extract every minor detail. Focus only on the core facts.\n"
        "Return the output STRICTLY as a JSON list of objects, where each object has "
        "'subject', 'predicate', 'object', and 'confidence' (float between 0 and 1). "
        "Do not include any explanation or markdown formatting outside the JSON.\n\n"
        f"Text:\n{text}"
    )
    
    response = None
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.1)
            )
            break
        except ResourceExhausted as e:
            if attempt == max_retries - 1:
                raise
            print(f"Rate limit hit in claim_extractor. Sleeping 40s... (Attempt {attempt+1}/{max_retries})")
            time.sleep(40)
        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                if attempt == max_retries - 1:
                    raise
                print(f"Rate limit hit in claim_extractor. Sleeping 40s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(40)
            else:
                raise
    
    result_text = response.text.strip()
    if result_text.startswith("```json"):
        result_text = result_text[7:]
    elif result_text.startswith("```"):
        result_text = result_text[3:]
    if result_text.endswith("```"):
        result_text = result_text[:-3]
        
    try:
        return json.loads(result_text.strip())
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from LLM response: {response.text}")
        return []

def extract_claims(text: str, config: Dict) -> List[Dict]:
    """Extract claims from the given text.

    Args:
        text: Article variant text.
        config: Configuration dict containing model name etc.
    Returns:
        List of claim dictionaries.
    """
    model = config.get("model", "gemini-pro")
    return _call_llm_for_claims(text, model)
