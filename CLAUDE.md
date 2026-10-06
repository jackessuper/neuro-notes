# CLAUDE.md

Static educational website for neurology trainees, modelled on [gasnotes.net](https://gasnotes.net): one narrow column, big readable text, a coloured sticky header, rounded callouts, dark mode, works equally on a phone and a desktop. Starts with a **Survival Guide** (12 chapter stubs); more sections (study tools, deep dives) can be added later via `config.SECTIONS`.

Clinical content is written or reviewed by the clinician. Chapters are `Draft: true` until reviewed. The differential chapter is a paraphrase of Meltzer's *How to Think Like a Neurologist* ch. 1 (source credited in the page footer).

## Run

```bash
python3 build.py              # render content/ -> site/
python3 build.py serve        # build, serve at http://127.0.0.1:5017/, rebuild on save
python3 build.py build --out /tmp/site
python3 -m pytest tests/ -v   # 29 tests, build into tmp_path only
```

Config is env vars with defaults (`config.py`; `.env` is read if present, see `.env.example`): `SITE_NAME`, `SITE_TAGLINE`, `SITE_AUTHOR`, `FEEDBACK_EMAIL`, `GOATCOUNTER_CODE`, `SITE_URL`, `PORT`, `FAVICON_EMOJI`.

## Architecture

```
content/                 Markdown source (one directory deep: <section>/<page>.md)
  index.md               Home page (rendered with templates/home.html + section cards)
  style-guide.md         Kitchen-sink reference for authors; built at /style-guide.html, not in nav
  guide/index.md         Survival Guide landing page (chapter list is generated)
  guide/<slug>.md        One chapter each
templates/               Jinja2: base.html, home.html, page.html, section_index.html, chapter.html
static/style.css         The only stylesheet (copied to site/static/); images go in static/images/
build.py                 Loader, renderer, dev server with a 1 s mtime-poll watcher
config.py                Settings + SECTIONS (nav/home cards) + GUIDE_GROUPS (chapter grouping)
site/                    Build output (gitignored). GitHub Pages builds it in CI.
.github/workflows/pages.yml   Tests + build + deploy on push to main; site settings come from repo Variables
```

### Content model

Front matter is python-markdown `meta` style (`Key: value` lines before the first blank line):

| Key | Required | Meaning |
|---|---|---|
| `Title` | yes | Page title (h1 + `<title>`); build fails without it |
| `Emoji` | no | Shown after the title and in chapter lists |
| `Description` | no | Lede under the title, chapter-list subtitle, meta description |
| `Group` | chapters | Key from `config.GUIDE_GROUPS` (`core`, `stroke`, `headache`); unknown keys fail the build |
| `Order` | chapters | Integer sort key within the group (fails the build if not an integer) |
| `Draft` | no | `true` shows a Draft badge on the chapter and in the list |

Chapter order on the index and for prev/next pills = group order, then `Order`, then title. Files starting with `_` are ignored. Nesting deeper than `section/page.md` fails the build.

Markdown extensions: `meta`, `toc` (h2–h3; an "On this page" box appears when a chapter has ≥2 h2s), `tables`, `admonition` (`!!! note|tip|warning|danger|todo "Title"`), `attr_list`, `md_in_html`, `fenced_code`, `sane_lists`, `smarty`. Every `<table>` is auto-wrapped in `<div class="table-scroll">` by `build.wrap_tables()` so wide tables pan sideways on phones (author-wrapped tables are not double-wrapped). TOC entries are rendered `|safe` because `smarty` emits entities. The full feature set with examples is `content/style-guide.md`.

### Templates and links

All links are **relative**: templates receive `root` (`""` for root pages, `../` for section pages) so the built site works from `file://`, a sub-path on GitHub Pages, or any host. Authors link between chapters as `[LP](lp.html)` and to home as `../index.html`.

GoatCounter is only emitted when `GOATCOUNTER_CODE` is set; the feedback link (nav + footer) only when `FEEDBACK_EMAIL` is set. Canonical/OpenGraph URL tags only when `SITE_URL` is set.

## Deployment

GitHub Pages via the workflow: in the repo, Settings → Pages → Source = "GitHub Actions", then set the site settings under Settings → Secrets and variables → Actions → **Variables** (`SITE_NAME`, `FEEDBACK_EMAIL`, `GOATCOUNTER_CODE`, `SITE_URL`, …). Remote: `git@github.com:jackessuper/neuro-notes.git` (not yet pushed).

## Gotchas

- Port 5017 (next free after music-pipeline's 5016). The dev server binds 127.0.0.1; pass `--host 0.0.0.0` to view from a phone on the LAN/Tailscale.
- The watcher rebuilds on any change under `content/`, `templates/`, `static/`; a content error is logged and the previous build keeps serving.
- Visual check after CSS/template edits: Playwright screenshots at desktop and 375 px widths (see root CLAUDE.md → Visual verification).
- Emoji favicon is a data-URI SVG; change it with `FAVICON_EMOJI`.
