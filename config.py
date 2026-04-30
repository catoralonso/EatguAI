"""
Centralized configuration for EatguAI.
Colors, thresholds and app behaviour.
"""
from dataclasses import dataclass, field
from typing import Dict
import os

# ============================================================================
# COLOR PALETTE - NIGHT FRIDGE MODE
# ============================================================================
@dataclass(frozen=True)
class Colors:
    """Palette inspired by ice, soft neon and deep darkness."""

    # Background
    BG_PRIMARY:    str = "#0a0a0f"
    BG_SECONDARY:  str = "#13131f"
    BG_TERTIARY:   str = "#0f0f1a"

    # Accents
    ICE_BLUE:      str = "#7dd3fc"
    ICE_GLOW:      str = "rgba(125, 211, 252, 0.15)"
    PURPLE_NEBULA: str = "#a78bfa"
    TEAL_AURORA:   str = "#14b8a6"

    # States
    SUCCESS: str = "#34d399"
    WARNING: str = "#fbbf24"
    ERROR:   str = "#f87171"
    INFO:    str = "#60a5fa"

    # Text
    TEXT_PRIMARY:   str = "#f8fafc"
    TEXT_SECONDARY: str = "#94a3b8"
    TEXT_MUTED:     str = "#64748b"

    # Borders and effects
    BORDER_GLOW:   str = "rgba(125, 211, 252, 0.25)"
    BORDER_SUBTLE: str = "rgba(255, 255, 255, 0.08)"
    SHADOW_ICE:    str = "0 0 20px rgba(125, 211, 252, 0.15)"


# ============================================================================
# TYPOGRAPHY
# ============================================================================
@dataclass(frozen=True)
class Typography:
    DISPLAY: str = "'Syne', sans-serif"
    BODY:    str = "'DM Sans', sans-serif"
    DATA:    str = "'JetBrains Mono', monospace"
    ACCENT:  str = "'Space Grotesk', sans-serif"


# ============================================================================
# APP CONFIGURATION
# ============================================================================
def _find_recipes_file() -> str:
    """Looks for the recipes JSON in data/ first, then in the root."""
    candidates = [
        "data/recetas_backend_proceso_ultra.json",
        "recetas_backend_proceso_ultra.json",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # Returns preffered path even if it doesn't exists (fallback with message error)
    return candidates[0]

@dataclass
class AppConfig:
    # ── Gemini Key ────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = field(default_factory=lambda: os.environ.get("GEMINI_API_KEY", ""))

    # ── Paths ────────────────────────────────────────────────────────────────
    DATA_DIR:      str = "data"
    RECIPES_FILE:  str = field(default_factory=_find_recipes_file)
    RATINGS_FILE:  str = "data/ratings.csv"
    SESSION_FILE:  str = "data/session_state.json"
    LOG_FILE:      str = "data/app.log"

    # ── Gemini / Vision ──────────────────────────────────────────────────────
    GEMINI_MODEL:       str   = "gemini-2.0-flash-001"
    DEFAULT_CONFIDENCE: float = 0.5
    MAX_INGREDIENTS:    int   = 20

    # ── Recommendations ──────────────────────────────────────────────────────
    DEFAULT_N_RECIPES: int = 5
    MAX_N_RECIPES:     int = 10

    # ── Operation modes ───────────────────────────────────────────────────
    # IMPORTANT: we use literal color strings, NOT Colors.X,
    # because the Colors dataclass is not instantiated at this point.
    MODES: Dict[str, Dict] = field(default_factory=lambda: {
        "survival": {
            "name": "Survival",
            "icon": "🧊",
            "description": "Cocina con lo que tienes AHORA",
            "color": "#7dd3fc",       # ICE_BLUE
            "accent": "#14b8a6",      # TEAL_AURORA
            "max_missing": 2,
            "dificultad_bonus": {"baja": 20, "media": 0, "alta": -30},
            "show_techniques": False,
            "show_pairings": False,
            "show_plating": False,
        },
        "chef": {
            "name": "Chef Pro",
            "icon": "👨‍🍳",
            "description": "Experiencias gastronómicas completas",
            "color": "#a78bfa",      
            "accent": "#c4b5fd",     
            "max_missing": 5,
            "dificultad_bonus": {"baja": 0, "media": 20, "alta": 40},
            "show_techniques": True,
            "show_pairings": True,
            "show_plating": True,
        },
    })

    def ensure_dirs(self):
        """Creates required directories if they don't exist."""
        os.makedirs(self.DATA_DIR, exist_ok=True)

    def get_mode(self, mode_key: str) -> Dict:
        """Returns the config for a given mode, falling back to survival"""
        return self.MODES.get(mode_key, self.MODES["survival"])
        
# ============================================================================
# GLOBAL INSTANCES — import from any module
# ============================================================================
COLORS = Colors()
TYPO   = Typography()
CONFIG = AppConfig()
CONFIG.ensure_dirs()
