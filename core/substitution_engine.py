"""
Ingredient substitution engine powered by Anthropic.
One API call expands the available ingredient set before scoring.
"""
import json
import logging
from typing import Dict, List, Set
import anthropic
from config import CONFIG

logger = logging.getLogger(__name__)
_client = anthropic.Anthropic(api_key=CONFIG.ANTHROPIC_API_KEY)

SUBSTITUTION_PROMPT = """
You are a professional chef assistant. Given a list of available ingredients
in spanish, return a JSON object mapping each available ingredient to a list of recipe 
ingredient names it could substitute or cover in a Spanish recipe context.

Only include substitutions that make culinary sense. Be generous but realistic.

Example input: ["yogur griego", "harina de maiz", "pechuga de pollo"]
Example output:
{
  "yogur griego": ["nata", "nata agria", "crema de leche", "yogur"],
  "harina de maiz": ["maicena", "fecula de maiz", "harina"],
  "pechuga de pollo": ["pollo", "carne de pollo", "filete de pollo"]
}

Return ONLY valid JSON. No markdown, no explanation.
Available ingredients: {ingredients}
"""

_cache: Dict[str, Set[str]] = {}

def expand_ingredients(ingredients: List[str]) -> Set[str]:
    """
    Takes detected ingredients, returns expanded set including
    what each ingredient can substitute in recipes.
    Results are cached per session.
    """
    cache_key = ",".join(sorted(ingredients))
    if cache_key in _cache:
        logger.info("Substitution cache hit")
        return _cache[cache_key]

    base_set = {i.lower().strip() for i in ingredients}

    try:
        prompt = SUBSTITUTION_PROMPT.format(ingredients=json.dumps(ingredients, ensure_ascii=False))
        response = _client.messages.create(
            model=CONFIG.VISION_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
		text = response.content[0].text
        mapping: Dict[str, List[str]] = json.loads(text)

        expanded = base_set.copy()
        for substitutes in mapping.values():
            expanded.update(s.lower().strip() for s in substitutes)

        logger.info(f"Expanded {len(base_set)} ingredients to {len(expanded)} with substitutions")
        _cache[cache_key] = expanded
        return expanded

    except Exception as e:
        logger.warning(f"Substitution engine failed, using base set: {e}")
        return base_set
