# CLAUDE.md

Static educational website for neurology trainees (site name **NeuroTips**, env `SITE_NAME`; the directory and repo keep the `neuro-notes` slug), modelled on [gasnotes.net](https://gasnotes.net): one narrow column, big readable text, a coloured sticky header, rounded callouts, dark mode, works equally on a phone and a desktop. Starts with a **Survival Guide** (12 chapters); more sections (study tools, deep dives) can be added later via `config.SECTIONS`.

**Keep the colourful Gas Notes look** (purple header, solid-colour callouts and badges). A muted "field manual" redesign was built on 2026-10-24 (branch `feature/frontend-redesign`, never merged) and rejected by the readers the clinician asked: the colours are what break the pages up.

Clinical content is written or reviewed by the clinician. Every chapter has a `Status:` (`ready` / `draft` / `soon`, see Content model); the chapter files are the source of truth for which is which. The differential chapter is a paraphrase of Meltzer's *How to Think Like a Neurologist* ch. 1 (source credited in the page footer).

## Run

```bash
python3 build.py              # render content/ -> site/
python3 build.py serve        # build, serve at http://127.0.0.1:5017/, rebuild on save
python3 build.py build --out /tmp/site
python3 -m pytest tests/ -v   # 51 tests, build into tmp_path only
```

Config is env vars with defaults (`config.py`; `.env` is read if present, see `.env.example`): `SITE_NAME`, `SITE_TAGLINE`, `SITE_AUTHOR`, `FEEDBACK_EMAIL`, `GOATCOUNTER_CODE`, `SITE_URL`, `PORT`, `FAVICON_EMOJI`.

## Architecture

```
content/                 Markdown source (one directory deep: <section>/<page>.md)
  index.md               Home page (rendered with templates/home.html + section cards; each card counts its chapters by status)
  style-guide.md         Kitchen-sink reference for authors; built at /style-guide.html, not in nav
  guide/index.md         Survival Guide landing page (chapter list is generated)
  guide/<slug>.md        One chapter each
templates/               Jinja2: base.html, home.html, page.html, section_index.html, chapter.html
static/style.css         The only stylesheet (copied to site/static/); images go in static/images/
build.py                 Loader, renderer, dev server with a 1 s mtime-poll watcher
config.py                Settings + SECTIONS (nav/home cards) + GUIDE_GROUPS (chapter grouping) + STATUSES
site/                    Build output (gitignored). GitHub Pages builds it in CI.
.github/workflows/pages.yml   Tests + build + deploy on push to main; site settings come from repo Variables
```

### Content model

Front matter is python-markdown `meta` style (`Key: value` lines) **between `---` fences** — the fences are what Pages CMS reads and writes, and a test fails if a content file lacks them. Values arrive YAML-quoted when they contain a colon or apostrophe; `build._unquote()` strips the quotes:

| Key | Required | Meaning |
|---|---|---|
| `Title` | yes | Page title (h1 + `<title>`); build fails without it |
| `Emoji` | no | Shown after the title and in chapter lists |
| `Description` | no | Chapter-list subtitle and meta description (not shown on the chapter page itself) |
| `Group` | chapters | Key from `config.GUIDE_GROUPS` (`core`, `stroke`, `headache`); unknown keys fail the build |
| `Order` | chapters | Integer sort key within the group (fails the build if not an integer) |
| `Status` | chapters | Key from `config.STATUSES`: `ready` (green badge in chapter lists only), `draft` (yellow "Draft – not yet reviewed" badge), `soon` (grey "Coming soon" badge). Case-insensitive; unknown values fail the build; a test requires every real chapter to set it |
| `Draft` | legacy | Only read when `Status` is absent: `true` → `draft`, otherwise `ready` |

Chapter order on the index and for prev/next pills = group order, then `Order`, then title. The pills (`build.readable_neighbours`) **skip `soon` chapters**. A `soon` chapter's page shows a "Not written yet" box listing its `##` headings instead of the body (the skeleton and its `!!! todo` stay in the source for the author) and gets `<meta name="robots" content="noindex">`. Status shows as a badge on every chapter-list row, in a key with counts above the chapter list, and as counts on the home-page section card. A chapter page is Gas Notes-plain: title, then body (no breadcrumb, lede or contents box; user decision 2026-11-03), with a badge under the title only for `draft` and `soon`, never for `ready`. Files starting with `_` are ignored. Nesting deeper than `section/page.md` fails the build.

Markdown extensions: `meta`, `toc` (h2–h3; gives headings their `id`s for deep links and supplies a `soon` page's planned list), `tables`, `admonition` (`!!! note|tip|warning|danger|todo "Title"`), `attr_list`, `md_in_html`, `fenced_code`, `sane_lists`, `smarty`. Every `<table>` is auto-wrapped in `<div class="table-scroll">` by `build.wrap_tables()` so wide tables pan sideways on phones (author-wrapped tables are not double-wrapped). Planned-section names are rendered `|safe` because `smarty` emits entities. The full feature set with examples is `content/style-guide.md`.

### Templates and links

All links are **relative**: templates receive `root` (`""` for root pages, `../` for section pages) so the built site works from `file://`, a sub-path on GitHub Pages, or any host. Authors link between chapters as `[LP](lp.html)` and to home as `../index.html`.

GoatCounter is only emitted when `GOATCOUNTER_CODE` is set; the feedback link (nav + footer) only when `FEEDBACK_EMAIL` is set. Canonical/OpenGraph URL tags and the GitHub Pages `CNAME` file (bare host of `SITE_URL`) only when `SITE_URL` is set.

## Editing in the browser (Pages CMS)

`.pages.yml` at the repo root configures [Pages CMS](https://app.pagescms.org) (hosted; sign in with GitHub, install its GitHub App on `jackessuper` for this repo). It lists the Survival Guide chapters as a collection (`content/guide`, front-matter fields as form inputs: Title, Emoji, Description, Group select, Order, Status select defaulting to draft) plus the home page, guide landing page and style guide as single files. The body is a Markdown **code** field, not rich-text, so the `!!! note` callouts and tables survive a save untouched. Saving commits to `main`, which triggers the Pages deploy (about a minute). Field names must match the front-matter keys' capitalisation exactly; `tests/test_build.py::test_pages_cms_config_covers_every_front_matter_key` checks the config against `config.GUIDE_GROUPS` and `config.STATUSES`, and PyYAML is in `requirements.txt` only for that test.

## Deployment

GitHub Pages via the workflow: in the repo, Settings → Pages → Source = "GitHub Actions", then set the site settings under Settings → Secrets and variables → Actions → **Variables** (`SITE_NAME`, `FEEDBACK_EMAIL`, `GOATCOUNTER_CODE`, `SITE_URL`, …). Repo: `github.com/jackessuper/neuro-notes` (public; Pages source = GitHub Actions). Custom domain **neurotips.net** (bought on Cloudflare 2026-10-06): apex A records → 185.199.108.153 / .109.153 / .110.153 / .111.153, `www` CNAME → `jackessuper.github.io`, Cloudflare proxy OFF (DNS only) so GitHub can issue the certificate.

## Gotchas

- Port 5017 (next free after music-pipeline's 5016). The dev server binds 127.0.0.1; pass `--host 0.0.0.0` to view from a phone on the LAN/Tailscale.
- The watcher rebuilds on any change under `content/`, `templates/`, `static/`; a content error is logged and the previous build keeps serving. It does **not** reload `build.py`/`config.py` — restart `serve` after editing Python.
- Since 2026-11, Homebrew's `python3` is 3.15 without `markdown`/`jinja2`; run and test with `/usr/bin/python3` (3.9, has the deps) or `pip install -r requirements.txt` into the interpreter you use.
- Visual check after CSS/template edits: Playwright screenshots at desktop and 375 px widths (see root CLAUDE.md → Visual verification).
- Emoji favicon is a data-URI SVG; change it with `FAVICON_EMOJI`.
