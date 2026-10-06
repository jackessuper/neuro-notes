"""Static site builder: content/**/*.md -> site/**/*.html.

Usage:
    python3 build.py              # build into site/
    python3 build.py serve        # build, serve on PORT, rebuild on change
    python3 build.py build --out /tmp/site
"""

import argparse
import functools
import http.server
import logging
import shutil
import sys
import threading
import time
import urllib.parse
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import config
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger("neuro-notes")

MARKDOWN_EXTENSIONS = [
    "meta",
    "toc",
    "tables",
    "admonition",
    "attr_list",
    "md_in_html",
    "fenced_code",
    "sane_lists",
    "smarty",
]
MARKDOWN_EXTENSION_CONFIGS = {"toc": {"toc_depth": "2-3"}}


@dataclass
class Page:
    source: Path
    rel_path: Path  # e.g. guide/lp.html
    section: str  # '' for root pages, else first directory name
    slug: str  # file stem
    title: str
    html: str
    meta: dict
    toc: list = field(default_factory=list)
    emoji: str = ""
    description: str = ""
    group: str = ""
    order: int = 999
    draft: bool = False

    @property
    def is_index(self) -> bool:
        return self.slug == "index"

    @property
    def url(self) -> str:
        return self.rel_path.as_posix()

    @property
    def root(self) -> str:
        """Relative prefix back to the site root, so the site works from any sub-path."""
        depth = len(self.rel_path.parts) - 1
        return "../" * depth


def parse_markdown(text: str):
    md = markdown.Markdown(extensions=MARKDOWN_EXTENSIONS, extension_configs=MARKDOWN_EXTENSION_CONFIGS)
    html = wrap_tables(md.convert(text))
    meta = {k.lower(): (v[0] if len(v) == 1 else "\n".join(v)) for k, v in md.Meta.items()}
    toc = getattr(md, "toc_tokens", [])
    return meta, html, toc


def wrap_tables(html: str) -> str:
    """Wrap each <table> in a scroll container so wide tables pan sideways on phones.

    Tables the author already wrapped in `<div class="table-scroll">` are left alone.
    """
    out = []
    pos = 0
    while True:
        start = html.find("<table", pos)
        if start == -1:
            out.append(html[pos:])
            break
        end = html.find("</table>", start)
        if end == -1:
            out.append(html[pos:])
            break
        end += len("</table>")
        before = html[pos:start]
        already = before.rstrip().endswith('<div class="table-scroll">')
        out.append(before)
        if already:
            out.append(html[start:end])
        else:
            out.append('<div class="table-scroll">' + html[start:end] + "</div>")
        pos = end
    return "".join(out)


def _as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "yes", "1", "on"}


def load_page(source: Path, content_dir: Path) -> Page:
    text = source.read_text(encoding="utf-8")
    meta, html, toc = parse_markdown(text)
    rel = source.relative_to(content_dir)
    if "title" not in meta:
        raise ValueError(f"{rel}: missing required 'Title:' front matter")
    if len(rel.parts) > 2:
        raise ValueError(f"{rel}: content may only be one directory deep (section/page.md)")
    section = rel.parts[0] if len(rel.parts) == 2 else ""
    order_raw = meta.get("order", "999")
    try:
        order = int(order_raw)
    except ValueError as exc:
        raise ValueError(f"{rel}: 'Order:' must be an integer, got {order_raw!r}") from exc
    return Page(
        source=source,
        rel_path=rel.with_suffix(".html"),
        section=section,
        slug=rel.stem,
        title=meta["title"],
        html=html,
        meta=meta,
        toc=toc,
        emoji=meta.get("emoji", ""),
        description=meta.get("description", ""),
        group=meta.get("group", ""),
        order=order,
        draft=_as_bool(meta.get("draft", "false")),
    )


def load_pages(content_dir: Path) -> list:
    sources = sorted(p for p in content_dir.rglob("*.md") if not p.name.startswith("_"))
    return [load_page(p, content_dir) for p in sources]


def chapters_for(pages: list, section: str, groups: list) -> list:
    """Chapters of a section in display order: by group order, then Order:, then title."""
    group_rank = {key: i for i, (key, _label) in enumerate(groups)}
    chapters = [p for p in pages if p.section == section and not p.is_index]
    for ch in chapters:
        if ch.group and ch.group not in group_rank:
            raise ValueError(f"{ch.rel_path}: unknown group {ch.group!r}; known: {sorted(group_rank)}")
    return sorted(
        chapters,
        key=lambda p: (group_rank.get(p.group, len(group_rank)), p.order, p.title.lower()),
    )


def grouped_chapters(chapters: list, groups: list) -> list:
    """[(label, [chapters]), ...] in group order, skipping empty groups; ungrouped last."""
    out = []
    for key, label in groups:
        members = [c for c in chapters if c.group == key]
        if members:
            out.append((label, members))
    loose = [c for c in chapters if not c.group]
    if loose:
        out.append(("Other chapters", loose))
    return out


def _jinja_env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def build_site(
    content_dir: Path = config.CONTENT_DIR,
    out_dir: Path = config.OUTPUT_DIR,
    static_dir: Path = config.STATIC_DIR,
    templates_dir: Path = config.TEMPLATES_DIR,
    settings: dict = None,
    sections: list = None,
    guide_groups: list = None,
) -> list:
    """Render every page and copy static assets. Returns the list of written output paths."""
    settings = settings if settings is not None else config.site_settings()
    sections = sections if sections is not None else config.SECTIONS
    guide_groups = guide_groups if guide_groups is not None else config.GUIDE_GROUPS

    pages = load_pages(content_dir)
    env = _jinja_env(templates_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    section_chapters = {s["slug"]: chapters_for(pages, s["slug"], guide_groups) for s in sections}
    section_by_slug = {s["slug"]: s for s in sections}

    settings = dict(settings, site_url=settings.get("site_url", "").rstrip("/"))
    feedback_href = ""
    if settings.get("feedback_email"):
        subject = urllib.parse.quote(f"{settings['name']} feedback")
        feedback_href = f"mailto:{settings['feedback_email']}?subject={subject}"

    base_ctx = {
        "settings": settings,
        "sections": sections,
        "feedback_href": feedback_href,
        "year": date.today().year,
    }

    for page in pages:
        ctx = dict(base_ctx, page=page, root=page.root)
        if page.section == "" and page.is_index:
            template = env.get_template("home.html")
        elif page.section == "":
            template = env.get_template("page.html")
        elif page.is_index:
            if page.section not in section_by_slug:
                raise ValueError(f"{page.rel_path}: section {page.section!r} is not listed in config.SECTIONS")
            chapters = section_chapters[page.section]
            ctx.update(
                section=section_by_slug[page.section],
                groups=grouped_chapters(chapters, guide_groups),
            )
            template = env.get_template("section_index.html")
        else:
            if page.section not in section_by_slug:
                raise ValueError(f"{page.rel_path}: section {page.section!r} is not listed in config.SECTIONS")
            chapters = section_chapters[page.section]
            idx = chapters.index(page)
            ctx.update(
                section=section_by_slug[page.section],
                prev=chapters[idx - 1] if idx > 0 else None,
                next=chapters[idx + 1] if idx + 1 < len(chapters) else None,
                show_toc=sum(1 for t in page.toc if t["level"] == 2) >= 2,
            )
            template = env.get_template("chapter.html")

        target = out_dir / page.rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(template.render(**ctx), encoding="utf-8")
        written.append(target)

    if static_dir.exists():
        shutil.copytree(static_dir, out_dir / "static", dirs_exist_ok=True)
    (out_dir / ".nojekyll").write_text("")
    host = urllib.parse.urlsplit(settings["site_url"]).hostname if settings["site_url"] else None
    if host:
        # GitHub Pages reads the custom domain from a CNAME file at the site root.
        (out_dir / "CNAME").write_text(host + "\n")
    logger.info("Built %d pages into %s", len(written), out_dir)
    return written


# ---------------------------------------------------------------------------
# Dev server


def _snapshot(dirs: list) -> dict:
    snap = {}
    for d in dirs:
        if not d.exists():
            continue
        for p in d.rglob("*"):
            if p.is_file():
                snap[str(p)] = p.stat().st_mtime_ns
    return snap


def _watch(out_dir: Path, interval: float, stop: threading.Event) -> None:
    dirs = [config.CONTENT_DIR, config.TEMPLATES_DIR, config.STATIC_DIR]
    last = _snapshot(dirs)
    while not stop.is_set():
        time.sleep(interval)
        current = _snapshot(dirs)
        if current != last:
            last = current
            try:
                build_site(out_dir=out_dir)
                logger.info("Rebuilt after change")
            except Exception:
                logger.error("Rebuild failed; fix the content and save again", exc_info=True)


def serve(out_dir: Path, host: str, port: int) -> None:
    build_site(out_dir=out_dir)
    stop = threading.Event()
    threading.Thread(target=_watch, args=(out_dir, 1.0, stop), daemon=True).start()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out_dir))
    with http.server.ThreadingHTTPServer((host, port), handler) as httpd:
        logger.info("Serving %s at http://%s:%d/ (Ctrl-C to stop)", out_dir, host, port)
        try:
            httpd.serve_forever()
        finally:
            stop.set()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build the static site.")
    parser.add_argument("command", nargs="?", choices=["build", "serve"], default="build")
    parser.add_argument("--out", type=Path, default=config.OUTPUT_DIR)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=config.PORT)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        if args.command == "serve":
            serve(args.out, args.host, args.port)
        else:
            build_site(out_dir=args.out)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
