# comparison/claim_comparator.py
"""Claim comparator module.

Computes semantic similarity between claims across variants and groups them.
"""

from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer

# Cache the model to avoid reloading on each run within the same process
_loaded_model = None
_loaded_model_name = ""

def _get_embedding_model(model_name: str) -> SentenceTransformer:
    global _loaded_model, _loaded_model_name
    if _loaded_model is None or _loaded_model_name != model_name:
        _loaded_model = SentenceTransformer(model_name)
        _loaded_model_name = model_name
    return _loaded_model

def compare_claims(claims_list: List[List[Dict]], config: Dict) -> List[Dict]:
    """Compare claims across variants.

    Args:
        claims_list: List of claim lists, one per variant.
        config: Configuration dict, may contain similarity threshold.
    Returns:
        A list of grouped claim dictionaries with similarity scores.
    """
    threshold = config.get("similarity_threshold", 0.85)
    model_name = config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
    
    embedder = _get_embedding_model(model_name)
    
    # Flatten all claims with reference to variant index
    all_claims = []
    texts_to_embed = []
    
    for var_idx, claims in enumerate(claims_list):
        for claim in claims:
            all_claims.append({"variant": var_idx, "claim": claim})
            text = f"{claim.get('subject','')} {claim.get('predicate','')} {claim.get('object','')}"
            texts_to_embed.append(text)
            
    if not texts_to_embed:
        return []
        
    embeddings = embedder.encode(texts_to_embed)
    
    for i, emb in enumerate(embeddings):
        all_claims[i]["embedding"] = emb
        
    groups = []
    visited = set()
    for i, c1 in enumerate(all_claims):
        if i in visited:
            continue
        group = [c1]
        visited.add(i)
        for j in range(i + 1, len(all_claims)):
            if j in visited:
                continue
            c2 = all_claims[j]
            # normalized embeddings from sentence_transformers could simplify distance,
            # but we can compute cosine explicitly
            sim = np.dot(c1["embedding"], c2["embedding"]) / (
                np.linalg.norm(c1["embedding"]) * np.linalg.norm(c2["embedding"]))
            if sim >= threshold:
                group.append(c2)
                visited.add(j)
        groups.append(group)
        
    # Summarize groups
    result = []
    for grp in groups:
        example = grp[0]["claim"]
        variants = sorted({item["variant"] for item in grp})
        result.append({"example_claim": example, "variants": variants, "size": len(grp)})
        
    return result
