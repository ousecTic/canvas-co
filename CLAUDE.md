# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A small content/data folder for **Canvas & Co**, a two-person art-print studio in
Portland, OR (see [company.md](company.md)). It contains the studio's catalog and
sales data plus hand-authored static HTML pages built from that data. There is no
build system, package manager, or test suite — pages are plain self-contained HTML
files that open directly in a browser.

## Data is the source of truth

Two CSVs drive everything; treat them as canonical and derive figures from them
rather than hardcoding numbers from memory:

- **[products.csv](products.csv)** — the catalog: `name,category,price,image`. Three
  categories only: `Landscape`, `Botanical`, `Abstract`. The `image` column points
  to an SVG in `images/` (all art is 400×300 SVG, 4:3).
- **[sales.csv](sales.csv)** — one row per order line:
  `order_id,date,customer_name,email,category,product,quantity,unit_price,line_total`.
  Covers Jan–Jun 2026.

When a task involves "best-selling", revenue, or any metric, **recompute it from
`sales.csv`** and state which metric you used. "Units sold" sums `quantity`;
"revenue" sums `line_total`. Note these can disagree and can tie — e.g. by units the
two top Landscape prints tie, so the metric and tiebreak must be made explicit.

## Pages

- **[index.html](index.html)** — the customer-facing one-page site featuring the
  best-selling print per category. Self-contained (inline CSS, references SVGs in
  `images/`). Must follow the studio voice (below).
- **[sales-report.html](sales-report.html)** — an internal sales dashboard (KPIs,
  charts, product table) styled separately from the public site. This is a private
  business view; keep its numbers consistent with `sales.csv`.

Keep the two visual styles distinct: `index.html` is warm/serif/cream (storefront),
`sales-report.html` is a clean dark-header dashboard (internal).

## Design & voice

All design guidelines — voice, look & feel, and color tokens for customer-facing
work — live in **[design.md](design.md)**. Read it before changing any customer-facing
copy or styling (e.g. `index.html`). It does not apply to the internal sales report.

## Previewing

Pages are static. To preview locally, serve the folder (e.g.
`python -m http.server 8765`) and open `http://localhost:8765/index.html` — the
Preview MCP launch config for this lives in [.claude/launch.json](.claude/launch.json)
(server name `canvas-co`). Always verify visual changes by screenshotting at both
desktop and mobile widths.
