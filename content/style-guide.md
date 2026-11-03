---
Title: Writing style guide
Emoji: ✍️
Description: Every formatting feature the site supports, in one page. Not linked from the navigation.
Status: draft
---

This page is the kitchen sink. Copy from it when writing a chapter. Chapters live in `content/guide/*.md` and start with a front-matter block between `---` lines (that is what the browser editor at app.pagescms.org reads and writes):

```
---
Title: How to do an LP
Banner: Lumbar puncture
Emoji: 💉
Emoji2: 🧠
Description: One sentence shown on the chapter list and as the search-engine summary.
Group: core
Order: 60
Status: soon
---
```

Every page opens with a Gas Notes-style banner: `Banner` (or the `Title` if you leave it out) in white over a checkerboard of `Emoji` and `Emoji2` (`Emoji2` defaults to the site's 🧠). Keep `Banner` short — two or three words read best on a phone. `Group` must be one of the keys in `config.GUIDE_GROUPS`; `Order` sorts within the group. `Status` is how far the chapter has got, and every chapter list on the site shows it:

| Status | Shows as | Use it when |
|---|---|---|
| `soon` | Grey "Coming soon" badge | Not started. The page shows only the planned `##` headings, and prev/next skips it. |
| `draft` | Yellow "Draft" badge | Written, still being checked. |
| `ready` | Green "Ready" badge in the chapter list; nothing on the page itself | Written and reviewed. |

## Headings

Use `##` for the main sections of a chapter (the page title is already the `h1`). Use `###` for sub-sections. Emoji in headings are fine and encouraged: `## Anaphylaxis 🐝`.

## Callouts

Five flavours, written as `!!! kind "Title"` followed by an indented paragraph.

!!! note "Note"
    The default. Good for key teaching points.

!!! tip "Tip"
    Practical shortcuts and things that save time.

!!! warning "Warning"
    Common traps and things that go wrong.

!!! danger "Danger"
    Time-critical or life-threatening. Use sparingly so it keeps its weight.

!!! todo "To do"
    For your own notes while drafting. Remove before publishing.

## Tables

| Feature | Peripheral | Central |
|---|---|---|
| Nystagmus | Unidirectional, fatigues | Direction-changing, vertical |
| Head impulse | Abnormal (corrective saccade) | Normal |
| Skew | Absent | May be present |

Every table is wrapped in a scroll container automatically, so wide tables pan sideways on a phone instead of breaking the layout.

## Lists

1. Numbered steps for procedures.
2. Keep each step to one action.
    - Indent four spaces for sub-points.
    - Bullets for things that have no order.

## Emphasis and code

*Italics* for terms, **bold** for the thing to remember, `code` for drug doses or exact wording you want copied (`tenecteplase 0.25 mg/kg`).

## Images

Put images in `static/images/` and reference them with a path relative to the page: `![Alt text](../static/images/example.png)`. Add `{ .image-50 }` after the image to shrink it to half width.

## Links

Link between chapters with relative paths: `[the LP chapter](lp.html)`. Link to the home page with `../index.html`.

## Quotes

> A blockquote is for quoting a guideline or a wise registrar.

---

A horizontal rule (`---`) separates loosely related blocks.
