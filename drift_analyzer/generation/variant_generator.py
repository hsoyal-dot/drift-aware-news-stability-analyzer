# generation/variant_generator.py
"""Variant generation module.

Generates semantically consistent variants of a news article using a LLM.
"""

import os
import json
from typing import List, Dict
import google.generativeai as genai

def _call_llm(prompt: str, model_name: str, temperature: float = 0.7) -> str:
    """Call the LLM with the given prompt."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    
    # Initialize the model 
    # Notice the change of name convention for default Gemini api: e.g. gemini-1.5-pro
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=temperature)
    )
    return response.text

def _build_prompt(article: str) -> str:
    """Construct a prompt that asks the model to rewrite the article while preserving factual content."""
    return (
        "You are given a news article. Rewrite it in a different style and wording, "
        "but keep all factual information, entities, dates, and numbers unchanged. "
        "Provide the rewritten article only.\n\nArticle:\n" + article
    )

def generate_variants(article: str, config: Dict) -> List[str]:
    """Generate a list of variant articles.

    Args:
        article: The original news article text.
        config: Configuration dictionary containing:
            - model: name of the LLM to use (e.g., \"gemini-pro\", \"gpt-4o\").
            - num_variants: how many variants to generate.
            - temperature: sampling temperature for the LLM.
    Returns:
        A list of variant strings.
    """
    model = config.get("model", "gemini-pro")
    num_variants = config.get("num_variants", 3)
    temperature = config.get("temperature", 0.7)

    prompt = _build_prompt(article)
    variants = []
    for i in range(num_variants):
        # In a real system, you might vary the prompt slightly per iteration
        variant = _call_llm(prompt, model_name=model, temperature=temperature)
        variants.append(variant)
    return variants
