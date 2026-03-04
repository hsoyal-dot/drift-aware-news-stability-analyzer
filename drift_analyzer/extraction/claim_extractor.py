# extraction/claim_extractor.py
"""Claim extraction module.

Extracts atomic factual claims from a news article variant using an LLM.
"""

import os
import json
from typing import List, Dict
import google.generativeai as genai

def _call_llm_for_claims(text: str, model_name: str) -> List[Dict]:
    """Call LLM to extract claims.
    
    Returns a list of claim dictionaries with keys: subject, predicate, object, confidence.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(model_name)
    prompt = (
        "Extract all key atomic factual claims from the following text. "
        "Return the output STRICTLY as a JSON list of objects, where each object has "
        "'subject', 'predicate', 'object', and 'confidence' (float between 0 and 1). "
        "Do not include any explanation or markdown formatting outside the JSON.\n\n"
        f"Text:\n{text}"
    )
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.1)
    )
    
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
