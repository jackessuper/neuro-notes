import re

import config
import pytest
from build import build_site, chapters_for, grouped_chapters, load_pages, parse_markdown
from conftest import GROUPS, SECTIONS, SETTINGS, build_with, write


def read(out, rel):
    return (out / rel).read_text(encoding="utf-8")


# ---- parsing ---------------------------------------------------------------


def test_parse_markdown_returns_lowercased_meta_html_and_toc():
    meta, html, toc = parse_markdown("Title: Hello\nOrder: 3\n\n## One\n\ntext\n\n## Two\n\nmore\n")
    assert meta == {"title": "Hello", "order": "3"}
    assert '<h2 id="one">One</h2>' in html
    assert [t["name"] for t in toc] == ["One", "Two"]


def test_parse_markdown_empty_input_gives_empty_meta_and_html():
    meta, html, toc = parse_markdown("")
    assert meta == {}
    assert html == ""
    assert toc == []


def test_parse_markdown_admonition_renders_styled_div():
    _, html, _ = parse_markdown('!!! danger "Stop"\n    Now.\n')
    assert '<div class="admonition danger">' in html
    assert '<p class="admonition-title">Stop</p>' in html


def test_parse_markdown_wraps_tables_in_scroll_container():
    _, html, _ = parse_markdown("Title: X\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    assert html.startswith('<div class="table-scroll"><table>')
    assert html.rstrip().endswith("</table></div>")


def test_parse_markdown_does_not_double_wrap_author_scroll_container():
    src = 'Title: X\n\n<div class="table-scroll" markdown="1">\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n</div>\n'
    _, html, _ = parse_markdown(src)
    assert html.count('class="table-scroll"') == 1


def test_parse_markdown_fenced_code_renders_pre_block():
    _, html, _ = parse_markdown("Title: X\n\n```\nTitle: How to do an LP\n```\n")
    assert html.startswith("<pre><code>Title: How to do an LP")


def test_load_pages_missing_title_raises(tmp_path):
    root = tmp_path / "c"
    write(root / "index.md", "No front matter here.\n")
    with pytest.raises(ValueError, match="missing required 'Title:'"):
        load_pages(root)


def test_load_pages_non_integer_order_raises(tmp_path):
    root = tmp_path / "c"
    write(root / "guide" / "x.md", "Title: X\nOrder: first\n\nbody\n")
    with pytest.raises(ValueError, match="'Order:' must be an integer"):
        load_pages(root)


def test_load_pages_rejects_nested_directories(tmp_path):
    root = tmp_path / "c"
    write(root / "guide" / "deep" / "x.md", "Title: X\n\nbody\n")
    with pytest.raises(ValueError, match="one directory deep"):
        load_pages(root)


def test_load_pages_skips_underscore_prefixed_files(tmp_path):
    root = tmp_path / "c"
    write(root / "_notes.md", "scratch, no title\n")
    write(root / "index.md", "Title: Home\n\nhi\n")
    assert [p.slug for p in load_pages(root)] == ["index"]


# ---- status ------------------------------------------------------------------


def _status_of(tmp_path, front):
    root = tmp_path / "c"
    write(root / "guide" / "x.md", f"Title: X\n{front}\nbody\n")
    return load_pages(root)[0].status


def test_load_page_reads_status_case_insensitively(tmp_path):
    assert _status_of(tmp_path, "Status: Soon\n") == "soon"


@pytest.mark.parametrize(
    "front, expected",
    [
        ("Draft: true\n", "draft"),
        ("Draft: false\n", "ready"),
        ("", "ready"),
        ("Status: draft\nDraft: false\n", "draft"),
    ],
)
def test_load_page_status_falls_back_to_legacy_draft_flag(tmp_path, front, expected):
    assert _status_of(tmp_path, front) == expected


def test_load_page_unknown_status_raises(tmp_path):
    root = tmp_path / "c"
    write(root / "guide" / "x.md", "Title: X\nStatus: finished\n\nbody\n")
    with pytest.raises(ValueError, match="unknown 'Status:' 'finished'"):
        load_pages(root)


def test_draft_property_tracks_status(tmp_path):
    root = tmp_path / "c"
    write(root / "guide" / "d.md", "Title: D\nStatus: draft\n\nbody\n")
    write(root / "guide" / "s.md", "Title: S\nStatus: soon\n\nbody\n")
    by_slug = {p.slug: p for p in load_pages(root)}
    assert by_slug["d"].draft is True
    assert by_slug["s"].draft is False


# ---- ordering -----------------------------------------------------------------


def test_chapters_for_orders_by_group_then_order(content):
    pages = load_pages(content)
    assert [c.slug for c in chapters_for(pages, "guide", GROUPS)] == ["alpha", "beta", "gamma", "delta"]


def test_chapters_for_unknown_group_raises(tmp_path):
    root = tmp_path / "c"
    write(root / "guide" / "x.md", "Title: X\nGroup: nonsense\n\nbody\n")
    with pytest.raises(ValueError, match="unknown group 'nonsense'"):
        chapters_for(load_pages(root), "guide", GROUPS)


def test_grouped_chapters_skips_empty_groups_and_appends_ungrouped(tmp_path):
    root = tmp_path / "c"
    write(root / "guide" / "a.md", "Title: A\nGroup: stroke\n\nbody\n")
    write(root / "guide" / "b.md", "Title: B\n\nbody\n")
    chapters = chapters_for(load_pages(root), "guide", GROUPS)
    groups = grouped_chapters(chapters, GROUPS)
    assert [(label, [c.slug for c in cs]) for label, cs in groups] == [
        ("Stroke", ["a"]),
        ("Other chapters", ["b"]),
    ]


# ---- build output ---------------------------------------------------------------


def test_build_writes_every_page_and_static_assets(built):
    out, written = built
    rel = sorted(p.relative_to(out).as_posix() for p in written)
    assert rel == [
        "guide/alpha.html",
        "guide/beta.html",
        "guide/delta.html",
        "guide/gamma.html",
        "guide/index.html",
        "index.html",
    ]
    assert (out / "static" / "style.css").exists()
    assert (out / ".nojekyll").exists()


def test_home_page_has_title_body_and_section_card(built):
    out, _ = built
    html = read(out, "index.html")
    assert "<title>Welcome – Test Notes</title>" in html
    assert "Home body." in html
    assert 'href="guide/index.html"' in html
    assert "Survival Guide" in html
    assert 'href="static/style.css"' in html


TALLY_RE = re.compile(r'<span class="badge (\w+)">(\d+) [^<]+</span>')


def test_home_section_card_counts_chapters_by_status(built):
    out, _ = built
    card = read(out, "index.html").split('class="card"')[1]
    assert TALLY_RE.findall(card) == [("ready", "2"), ("draft", "1"), ("soon", "1")]
    assert '<span class="badge soon">1 coming soon</span>' in card


def test_home_section_card_omits_statuses_with_no_chapters(content, tmp_path):
    (content / "guide" / "alpha.md").unlink()
    out = build_with(content, tmp_path)
    assert [k for k, _ in TALLY_RE.findall(read(out, "index.html"))] == ["ready", "soon"]


ROW_RE = re.compile(r'<li data-status="(\w+)">\s*<a href="\.\./guide/([a-z-]+)\.html"')


def pager(html):
    """{'prev': slug, 'next': slug} for the chapter pager links present on a page."""
    return dict(re.findall(r'class="pill (prev|next)" href="\.\./guide/([a-z-]+)\.html"', html))


def test_section_index_lists_chapters_grouped_in_order_with_status(built):
    out, _ = built
    html = read(out, "guide/index.html")
    assert html.index("<h3>Core</h3>") < html.index("<h3>Stroke</h3>")
    assert ROW_RE.findall(html) == [("draft", "alpha"), ("ready", "beta"), ("ready", "gamma"), ("soon", "delta")]
    assert re.findall(r'<span class="badge (\w+)">(Ready|Draft|Coming soon)</span>\s*<span class="chapter-desc">', html)
    assert "Second in core." in html
    assert '<span class="badge soon">Coming soon</span>' in html


def test_section_index_key_explains_and_counts_each_status(built):
    out, _ = built
    html = read(out, "guide/index.html")
    key = re.findall(
        r'<li><span class="badge (\w+)">[^<]+</span>\s*<span class="status-blurb">[^<]*<span class="status-count">\((\d+)\)</span>',
        html,
    )
    assert key == [("ready", "2"), ("draft", "1"), ("soon", "1")]
    assert html.index('class="status-key"') < html.index("<h3>Core</h3>")


def test_chapter_page_has_heading_description_toc_and_prev_next(built):
    out, _ = built
    html = read(out, "guide/beta.html")
    assert "<h1>Beta chapter 🅷".replace("🅷", "🅱️") in html
    assert '<p class="lede">Second in core.</p>' in html
    assert 'aria-label="On this page"' in html
    assert 'href="#first-heading"' in html and 'href="#second-heading"' in html
    assert pager(html) == {"prev": "alpha", "next": "gamma"}
    assert 'href="../static/style.css"' in html


def test_first_and_last_readable_chapters_omit_missing_prev_next(built):
    out, _ = built
    assert pager(read(out, "guide/alpha.html")) == {"next": "beta"}
    assert pager(read(out, "guide/gamma.html")) == {"prev": "beta"}


def test_pager_skips_coming_soon_chapters(built):
    out, _ = built
    assert "guide/delta.html" not in read(out, "guide/gamma.html").split('class="pagination')[1]
    assert pager(read(out, "guide/delta.html")) == {"prev": "gamma"}


def test_coming_soon_chapter_shows_planned_sections_instead_of_skeleton(built):
    out, _ = built
    html = read(out, "guide/delta.html")
    assert '<p class="badge soon">Coming soon</p>' in html
    assert '<div class="admonition todo coming-soon">' in html
    assert re.findall(r'<li class="planned-item">(.*?)</li>', html) == ["Planned one", "Planned two"]
    assert "Skeleton note for the author." not in html
    assert '<h2 id="planned-one"' not in html
    assert '<meta name="robots" content="noindex">' in html
    assert "noindex" not in read(out, "guide/beta.html")


def test_ready_chapter_shows_ready_badge(built):
    out, _ = built
    html = read(out, "guide/beta.html")
    assert '<p class="badge ready">Ready – reviewed</p>' in html
    assert "badge draft" not in html


def test_toc_keeps_smart_quote_entities_unescaped(tmp_path):
    root = tmp_path / "c"
    write(root / "index.md", "Title: Home\n\nhi\n")
    write(
        root / "guide" / "index.md",
        "Title: Guide\n\nintro\n",
    )
    write(
        root / "guide" / "q.md",
        'Title: Q\nGroup: core\nOrder: 1\n\n## The four kinds of "diagnosis"\n\nx\n\n## Two\n\ny\n',
    )
    out = tmp_path / "o"
    build_site(
        content_dir=root,
        out_dir=out,
        static_dir=config.STATIC_DIR,
        templates_dir=config.TEMPLATES_DIR,
        settings=dict(SETTINGS),
        sections=SECTIONS,
        guide_groups=GROUPS,
    )
    html = read(out, "guide/q.html")
    assert "&amp;ldquo;" not in html
    assert 'href="#the-four-kinds-of-diagnosis">The four kinds of &ldquo;diagnosis&rdquo;</a>' in html


def test_chapter_without_two_h2s_has_no_toc(built):
    out, _ = built
    assert 'aria-label="On this page"' not in read(out, "guide/alpha.html")


def test_draft_chapter_shows_badge_and_admonition_renders(built):
    out, _ = built
    html = read(out, "guide/alpha.html")
    assert '<p class="badge draft">Draft – not yet reviewed</p>' in html
    assert '<div class="admonition warning">' in html


def test_table_renders_in_chapter_inside_scroll_container(built):
    out, _ = built
    assert '<div class="table-scroll"><table>' in read(out, "guide/gamma.html")


def test_footer_shows_author_and_disclaimer_without_feedback_link(built):
    out, _ = built
    html = read(out, "index.html")
    assert "made by Dr Test" in html
    assert "Not a substitute for local guidelines" in html
    assert "mailto:" not in html


def test_feedback_email_adds_nav_and_footer_links(content, tmp_path):
    out = build_with(content, tmp_path, feedback_email="notes@example.com")
    html = read(out, "guide/beta.html")
    assert html.count('href="mailto:notes@example.com?subject=Test%20Notes%20feedback"') == 2
    assert ">Feedback</a>" in html and ">Send feedback</a>" in html


def test_goatcounter_script_only_when_configured(content, tmp_path, built):
    out_plain, _ = built
    assert "goatcounter" not in read(out_plain, "index.html")
    out = build_with(content, tmp_path, goatcounter_code="mysite")
    html = read(out, "index.html")
    assert 'data-goatcounter="https://mysite.goatcounter.com/count"' in html
    assert 'src="//gc.zgo.at/count.js"' in html


def test_site_url_adds_canonical_and_og_url(content, tmp_path):
    out = build_with(content, tmp_path, site_url="https://example.net/")
    html = read(out, "guide/beta.html")
    assert '<link rel="canonical" href="https://example.net/guide/beta.html">' in html
    assert '<meta property="og:url" content="https://example.net/guide/beta.html">' in html


def test_site_url_writes_cname_file_with_bare_host(content, tmp_path, built):
    out_plain, _ = built
    assert not (out_plain / "CNAME").exists()
    out = build_with(content, tmp_path, site_url="https://neurotips.net/")
    assert (out / "CNAME").read_text() == "neurotips.net\n"


def test_chapter_in_unlisted_section_raises(tmp_path):
    root = tmp_path / "c"
    write(root / "index.md", "Title: Home\n\nhi\n")
    write(root / "nerdbox" / "x.md", "Title: X\n\nbody\n")
    with pytest.raises(ValueError, match="not listed in config.SECTIONS"):
        build_site(
            content_dir=root,
            out_dir=tmp_path / "o",
            static_dir=config.STATIC_DIR,
            templates_dir=config.TEMPLATES_DIR,
            settings=dict(SETTINGS),
            sections=SECTIONS,
            guide_groups=GROUPS,
        )


# ---- the real content tree -----------------------------------------------------


def test_real_content_builds_with_all_listed_chapters(tmp_path):
    out = tmp_path / "real"
    build_site(out_dir=out, settings=dict(SETTINGS))
    expected = {
        "differential",
        "localisation",
        "stroke-call",
        "stroke-imaging",
        "mri-head",
        "lp",
        "lp-results",
        "stroke-workup",
        "stroke-secondary-prevention",
        "headache",
        "migraine",
        "iih",
    }
    built = {p.stem for p in (out / "guide").glob("*.html")} - {"index"}
    assert built == expected
    index = read(out, "guide/index.html")
    order = [slug for _status, slug in ROW_RE.findall(index)]
    assert order == [
        "differential",
        "localisation",
        "stroke-call",
        "stroke-imaging",
        "mri-head",
        "lp",
        "lp-results",
        "stroke-workup",
        "stroke-secondary-prevention",
        "headache",
        "migraine",
        "iih",
    ]


def test_real_content_every_chapter_has_group_and_order():
    pages = load_pages(config.CONTENT_DIR)
    for p in pages:
        if p.section == "guide" and not p.is_index:
            assert p.group in dict(config.GUIDE_GROUPS), p.slug
            assert p.order != 999, f"{p.slug} has no Order:"


def test_real_content_every_chapter_sets_an_explicit_status():
    statuses = {key for key, _label, _blurb in config.STATUSES}
    for p in load_pages(config.CONTENT_DIR):
        if p.section == "guide" and not p.is_index:
            assert p.meta.get("status", "").lower() in statuses, f"{p.slug} needs a Status: line"


# ---- front matter written by Pages CMS ------------------------------------


def test_parse_markdown_accepts_yaml_fenced_front_matter():
    meta, html, _ = parse_markdown("---\nTitle: Hello\nOrder: 3\nDraft: true\n---\n\nBody.\n")
    assert meta == {"title": "Hello", "order": "3", "draft": "true"}
    assert html == "<p>Body.</p>"


def test_parse_markdown_strips_yaml_quotes_from_meta_values():
    meta, _, _ = parse_markdown("---\nTitle: \"Stroke: the basics\"\nDescription: 'It''s short'\n---\n\nx\n")
    assert meta["title"] == "Stroke: the basics"
    assert meta["description"] == "It's short"


def test_real_content_front_matter_is_yaml_fenced_for_the_cms():
    for path in sorted(config.CONTENT_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{path.name}: Pages CMS needs a '---' fenced front matter block"
        assert "\n---\n" in text[4:], f"{path.name}: front matter block is not closed"


def test_pages_cms_config_covers_every_front_matter_key():
    import yaml

    cfg = yaml.safe_load((config.PROJECT_ROOT / ".pages.yml").read_text(encoding="utf-8"))
    chapters = next(c for c in cfg["content"] if c["name"] == "chapters")
    assert chapters["path"] == "content/guide"
    names = {f["name"] for f in chapters["fields"]}
    assert {"Title", "Emoji", "Description", "Group", "Order", "Status", "body"} <= names
    group = next(f for f in chapters["fields"] if f["name"] == "Group")
    assert [v["name"] for v in group["options"]["values"]] == [k for k, _ in config.GUIDE_GROUPS]
    status = next(f for f in chapters["fields"] if f["name"] == "Status")
    assert [v["name"] for v in status["options"]["values"]] == [k for k, _, _ in config.STATUSES]
