# generation/variant_generator.py
"""Variant generation module.

Generates semantically consistent variants of a news article using a LLM.
"""

import os
import json
import time
from typing import List, Dict
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

def _call_llm(prompt: str, model_name: str, temperature: float = 0.7, max_retries: int = 3) -> str:
    """Call the LLM with the given prompt."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    
    # Initialize the model 
    # Notice the change of name convention for default Gemini api: e.g. gemini-1.5-pro
    model = genai.GenerativeModel(model_name)
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )
            return response.text
        except ResourceExhausted as e:
            if attempt == max_retries - 1:
                raise
            print(f"Rate limit hit in variant_generator. Sleeping 40s... (Attempt {attempt+1}/{max_retries})")
            time.sleep(40)
        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                if attempt == max_retries - 1:
                    raise
                print(f"Rate limit hit in variant_generator. Sleeping 40s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(40)
            else:
                raise

def _build_prompt(article: str) -> str:
    """Construct a prompt that asks the model to rewrite the article while preserving factual content."""
    return (
        "You are given a news article. Rewrite it in a different style and wording, "
        "but keep all factual information, entities, dates, and numbers unchanged. "
        "Provide the rewritten article only.\n\nArticle:\n" + article
    )

def generate_variants(article: str, config: Dict) -> List[Dict[str, str]]:
    """Generate a list of variant articles.

    Args:
        article: The original news article text.
        config: Configuration dictionary containing:
            - model: name of the LLM to use (e.g., "gemini-pro", "gpt-4o").
            - num_variants: how many variants to generate.
            - temperature: sampling temperature for the LLM.
    Returns:
        A list of dictionaries with "style" and "text" keys.
    """
    model = config.get("model", "gemini-pro")
    num_variants = config.get("num_variants", 3)
    temperature = config.get("temperature", 0.7)

    styles = [
        {"name": "Sensational & Emotional", "desc": "Focus heavily on the human impact, urgency, and dramatic tone."},
        {"name": "Formal & Objective", "desc": "Use a cold, academic, and highly neutral tone focusing only on hard facts."},
        {"name": "Concise & Analytical", "desc": "Get straight to the point quickly, using brief and analytical phrasing."}
    ]

    variants = []
    for i in range(num_variants):
        style_info = styles[i % len(styles)]
        prompt = (
            f"You are given a news article. Rewrite it in a {style_info['name']} style. {style_info['desc']} "
            "Keep all factual information, entities, dates, and numbers exactly unchanged. "
            "Maintain the core semantic meaning, just change the tone and structure. "
            "Provide the rewritten article ONLY.\n\nArticle:\n" + article
        )
        variant_text = _call_llm(prompt, model_name=model, temperature=temperature)
        variants.append({"style": style_info["name"], "text": variant_text})
        
    return variants
