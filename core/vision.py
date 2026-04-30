"""
Ingredient detection using Gemini.
"""
import json
import logging
import unicodedata
from typing import List, Dict, Any

import base64
import google.generativeai as genai

from config import CONFIG
from models import DetectedIngredient

logger = logging.getLogger(__name__)

# ============================================================================
# INICIALIZACIÓN GEMINI
# ============================================================================

genai.configure(api_key=CONFIG.GEMINI_API_KEY)
_model = genai.GenerativeModel(CONFIG.GEMINI_MODEL)

PROMPT = """
Eres un asistente especializado en identificar ingredientes de cocina en imágenes de neveras.

Analiza la imagen y devuelve ÚNICAMENTE un array JSON válido, sin texto adicional, sin markdown, sin bloques de código.

Formato exacto:
[
    {"name": "zanahoria", "confidence": 0.95, "emoji": "🥕"},
    {"name": "leche entera", "confidence": 0.90, "emoji": "🥛"}
]

REGLAS para "name":
- En ESPAÑOL, concreto y cocinero (lo que pondría un chef en una receta)
- Puedes poner nombres como "pechuga de pollo", "queso manchego", "zumo de naranja"
- No pongas nombres generales como "comida", "verdura", "botella", "producto", "cosa marrón"
- No pongas nombres de marca → pon el ingrediente real ("ketchup", no "Heinz")
- Si solo ves el envase pero no puedes identificar el contenido → omítelo
- Si ves un plato preparado o tupperware con contenido no identificable → omítelo
- Si ves un ingrediente procesado reconocible → ponlo ("jamón cocido", "mermelada de fresa")

REGLAS para "confidence":
- 0.9 → visible con claridad
- 0.7 → parcialmente visible u ocluido
- 0.5 → intuyes que está pero no lo ves bien
- Si la confianza sería menor de 0.5 → omite el ingrediente directamente

REGLAS para "emoji":
- El emoji que mejor represente VISUALMENTE ese ingrediente específico
- Un emoji por ingrediente, el más preciso posible
- Por ejemplo: "salmón" → 🐟, "huevo" → 🥚, "mantequilla" → 🧈, "ajo" → 🧄
- Evitar usar 🥘 ni 🍽️ como respuesta genérica solo usalo en casos extremos que no sepas qué representa el ingrediente.
"""

# ============================================================================
# NORMALIZE (del vision.py original)
# ============================================================================

def _normalize(name: str) -> str:
    n = name.lower().strip()
    n = unicodedata.normalize("NFD", n)
    n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    if n.endswith("oes"):
        n = n[:-2]
    elif n.endswith("s") and not n.endswith("ss"):
        n = n[:-1]
    return n

# ============================================================================
# DETECT GEMINI
# ============================================================================

class VisionError(Exception):
    pass

def detect_gemini(image_path: str) -> List[Dict[str, Any]]:
    """Sends the image to Gemini and returns raw ingredient list."""
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        image_part = {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image_data,
            }
        }
        response = _model.generate_content(
            [PROMPT, image_part],
            generation_config={"temperature": 0.1},
        )
        text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        logger.info(f"Gemini detectó {len(result)} ingredientes en bruto")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"Gemini devolvió JSON inválido: {e}")
        raise VisionError(f"Respuesta de Gemini no es JSON válido: {e}")
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        raise VisionError(str(e))

# ============================================================================
# CLEANING & VALIDATION
# ============================================================================

def clean_ingredients(
    raw: List[Dict[str, Any]],
    min_confidence: float = CONFIG.DEFAULT_CONFIDENCE,
) -> List[DetectedIngredient]:
    seen = set()
    cleaned = []

    for item in sorted(raw, key=lambda x: -float(x.get("confidence", 0))):
        try:
            conf = float(item.get("confidence", 0))
            name = item.get("name", "").strip()

            if not name or conf < min_confidence:
                continue

            name_norm = _normalize(name)

            if name_norm in seen:
                continue

            seen.add(name_norm)
            emoji_raw = item.get("emoji", "")
            emoji = emoji_raw if emoji_raw and emoji_raw.strip() else "🥘"
            cleaned.append(DetectedIngredient(
                name=name,    
                confidence=conf,
                raw_detection=str(item),
                emoji=emoji,
            ))
            logger.debug(f"  ✓ {name} ({conf:.0%})")

        except Exception as e:
            logger.warning(f"Error procesando item {item}: {e}")
            continue

    logger.info(f"Ingredientes limpios: {len(cleaned)}")
    return cleaned

# ============================================================================
# MAIN FUNCTION                      
# ============================================================================

def detectar_ingredientes(image_path: str) -> List[DetectedIngredient]:
    """
    Main function gets image path, return list of DetectedIngredient.
    Fallback to VisionError if fails.
    """
    raw = detect_gemini(image_path)
    logger.info(f"RAW GEMINI RESPONSE: {raw}")
    return clean_ingredients(raw)


# ============================================================================
# FOR TESTING PRE DEMO
# ============================================================================

if __name__ == "__main__":
    import sys
    img = sys.argv[1] if len(sys.argv) > 1 else "foto_nevera.png"
    print(f"\n Analizando: {img}\n")
    ingredientes = detectar_ingredientes(img)
    print(f"INGREDIENTES DETECTADOS ({len(ingredientes)}):")
    for i in ingredientes:
        print(f"  {i.emoji} {i.name:<30} {i.confidence:.0%}  [{i.category}]")
