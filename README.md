# Cassaro Beauty

Static storefront for **Cassaro Beauty** — a premium online retailer of skincare,
cosmetics and beauty essentials based in South Africa, with an initial focus on
Korean skincare.

Cassaro Beauty is a retailer. All products are sold in their original brand
packaging as supplied; the site must never imply the products are made or
formulated in-house.

## Run locally

```bash
python3 build.py
python3 -m http.server 4321 --bind 127.0.0.1 -d dist
# http://127.0.0.1:4321/
```

The browser caches the stylesheet aggressively — hard-reload after CSS changes.

## Layout

```
layout/base.html   shared chrome: announcement bar, header, mega menus,
                   mobile drawer, support strip, newsletter, footer
pages/*.html       one content fragment per page (edit these)
pages.json         page manifest: file, title, nav key, meta description
build.py           assembles pages + layout -> dist/, expands macros
assets/css         site.css — all design tokens live in :root
assets/js          site.js — drawer, tabs, accordions, quantity steppers
assets/products    product photography and cover images
assets/brand       Cassaro Beauty logo variants
dist/              generated output — do not edit by hand
```

## Build

`python3 build.py` after any edit. It removes stale pages from `dist/` that are
no longer in the manifest, so deleted pages cannot linger.

### Macros

Repeating components are defined once in `build.py` and expanded at build time:

| Macro | Renders |
|---|---|
| `{{CARD\|image\|brand\|name}}` | product card, auto-linked via `PRODUCT_PAGES` |
| `{{POST\|image\|category\|title}}` | journal card |
| `{{FAQ\|question\|answer\|state}}` | accordion row |
| `{{PH\|label\|extra-class}}` | image, or a labelled placeholder if unmapped |
| `{{MARQUEE}}` | scrolling category strip |

`IMAGES` maps a placeholder label to a real file. Unmapped labels render as a
clearly-labelled placeholder, so missing imagery stays visible rather than
silently blank.

`PRODUCT_PAGES` maps a product name to its own page. Add an entry and every card
using that name re-points itself — no per-card edits.

## Branding

All colour, type and spacing tokens are in `assets/css/site.css` under `:root`.
Palette is taken from the Cassaro Beauty brand guidelines: Cocoa `#6F4A34`,
Gilt `#B8894F`, Cacao `#241812`, Cream `#F4ECE1`, Porcelain `#FBF7F0`.

## Outstanding

- Prices show `R___` throughout; no prices have been invented.
- Ratings, stock levels and review content are placeholders pending real data.
- Makeup and Fragrance are "coming soon" pages — no stock yet.
- Journal article imagery and body copy still to be supplied.
- Tailwind-free, no build toolchain; deploy `dist/` as static files.
