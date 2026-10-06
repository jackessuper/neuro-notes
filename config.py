"""Site settings. Everything is an env var with a sensible default; `.env` is loaded if present."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CONTENT_DIR = PROJECT_ROOT / "content"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"
OUTPUT_DIR = PROJECT_ROOT / "site"


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (KEY=value lines, # comments). Never overrides a real env var."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        os.environ.setdefault(key, value)


_load_dotenv(PROJECT_ROOT / ".env")


def site_settings() -> dict:
    """Read settings fresh each call so tests can override via env."""
    return {
        "name": os.getenv("SITE_NAME", "NeuroTips"),
        "tagline": os.getenv("SITE_TAGLINE", "A survival guide for people getting started in neurology."),
        "author": os.getenv("SITE_AUTHOR", ""),
        "feedback_email": os.getenv("FEEDBACK_EMAIL", ""),
        "goatcounter_code": os.getenv("GOATCOUNTER_CODE", ""),
        "site_url": os.getenv("SITE_URL", "").rstrip("/"),
        "favicon_emoji": os.getenv("FAVICON_EMOJI", "🧠"),
    }


PORT = int(os.getenv("PORT", "5017"))

# Top-level sections. Each maps to content/<slug>/ with its own index.md and chapters.
# Order here is the nav order and the order of cards on the home page.
SECTIONS = [
    {
        "slug": "guide",
        "title": "Survival Guide",
        "emoji": "🧭",
        "blurb": "The no-nonsense guide to your first weeks on a neurology ward or on call.",
        "cta": "Take me to the Survival Guide",
    },
]

# Chapter groupings inside the survival guide, in display order.
# A chapter's `group:` front-matter value must match one of these keys.
GUIDE_GROUPS = [
    ("core", "Core skills 🧰"),
    ("stroke", "Stroke 🧠"),
    ("headache", "Headache 🤕"),
]
