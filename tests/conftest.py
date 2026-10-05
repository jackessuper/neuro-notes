import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config  # noqa: E402

SETTINGS = {
    "name": "Test Notes",
    "tagline": "A test tagline.",
    "author": "Dr Test",
    "feedback_email": "",
    "goatcounter_code": "",
    "site_url": "",
    "favicon_emoji": "🧠",
}

SECTIONS = [
    {
        "slug": "guide",
        "title": "Survival Guide",
        "emoji": "🧭",
        "blurb": "Blurb.",
        "cta": "Go",
    }
]
GROUPS = [("core", "Core"), ("stroke", "Stroke")]


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def content(tmp_path):
    """A minimal content tree: home, guide index, three chapters across two groups."""
    root = tmp_path / "content"
    write(root / "index.md", "Title: Welcome\n\n# Welcome 👋\n\nHome body.\n")
    write(root / "guide" / "index.md", "Title: Survival Guide\nEmoji: 🧭\n\nIntro.\n")
    write(
        root / "guide" / "beta.md",
        "Title: Beta chapter\nEmoji: 🅱️\nDescription: Second in core.\nGroup: core\nOrder: 20\n\n"
        "## First heading\n\nText.\n\n## Second heading\n\nMore.\n",
    )
    write(
        root / "guide" / "alpha.md",
        'Title: Alpha chapter\nGroup: core\nOrder: 10\nDraft: true\n\n!!! warning "Careful"\n    Watch out.\n\nBody.\n',
    )
    write(
        root / "guide" / "gamma.md",
        "Title: Gamma chapter\nGroup: stroke\nOrder: 5\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
    )
    return root


@pytest.fixture
def built(content, tmp_path):
    """Build the fixture content tree and return (out_dir, written paths)."""
    from build import build_site

    out = tmp_path / "site"
    written = build_site(
        content_dir=content,
        out_dir=out,
        static_dir=config.STATIC_DIR,
        templates_dir=config.TEMPLATES_DIR,
        settings=dict(SETTINGS),
        sections=SECTIONS,
        guide_groups=GROUPS,
    )
    return out, written


def build_with(content, tmp_path, **overrides):
    from build import build_site

    settings = dict(SETTINGS, **overrides)
    out = tmp_path / "site-override"
    build_site(
        content_dir=content,
        out_dir=out,
        static_dir=config.STATIC_DIR,
        templates_dir=config.TEMPLATES_DIR,
        settings=settings,
        sections=SECTIONS,
        guide_groups=GROUPS,
    )
    return out
