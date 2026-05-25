# Invasive Mapping Web Showcase — Design Spec

**Date:** 2026-05-25  
**Project:** Mapping Invasive Plant Distribution in the Hadwen Arboretum  
**Team:** Annan Shrestha, Bikal Shrestha, Nathan Clark  
**Sponsor:** Professor John Rogan, Clark University  

---

## Overview

A single-page portfolio web showcase of the invasive plant mapping project. Built with Python Flask, it presents the poster content as an interactive narrative story — visually compelling enough for a portfolio, scientifically faithful to the original research.

**Primary audience:** Portfolio reviewers (future employers, grad school admissions)  
**Style:** Nature/Clean — light greens, earthy tones, white space  
**Tech stack:** Python Flask + Jinja2 + Chart.js + vanilla CSS  

---

## Architecture

```
arbo/
├── app.py                  # Flask server — loads CSVs, serves routes
├── templates/
│   └── index.html          # Single Jinja2 template (all sections)
├── static/
│   ├── css/
│   │   └── style.css       # All styles
│   ├── js/
│   │   └── charts.js       # Chart.js config + scroll animations
│   └── images/             # Copied from project root at setup
│       ├── BBLayout.jpg
│       ├── JKLayout.jpg
│       ├── NMLayout.jpg
│       └── OBLayout.jpg
├── invasive_summary.csv    # Already exists — species coverage data
├── density_details.csv     # Already exists — density breakdown per species
└── requirements.txt        # flask only (geopandas already in .venv)
```

**Data flow:** `app.py` reads both CSVs at startup, converts to dicts, passes to Jinja2 template as `species` and `density`. Chart.js receives these values via inline JSON in the template. No database, no dynamic endpoints — one GET `/` route.

**Run command:** `flask run` (or `python app.py`)

---

## Page Structure

### Hero Section
- Full-width dark-green gradient background (`#1a3a1a` → `#2d5a27` → `#4a7c59`)
- Title: "Mapping Invasive Plant Distribution"
- Subtitle: team names + sponsor
- 4 animated stat counters (count up on load):
  - 42.6% — Invasive Coverage
  - 51,284 — Survey Cells (2m×2m)
  - 4 — Invasive Species
  - 26 — Acres Surveyed
- Scroll indicator arrow at bottom

### Sticky Navigation
- Appears after hero scrolls out of view (IntersectionObserver)
- Dark green bar: `Problem | Survey | Findings | Analysis | Action`
- Smooth-scroll anchors to each chapter section

### Chapter 1 — The Problem
- Two-column layout: introduction text (left) + species quick-list card (right)
- Content from poster introduction + arboretum history
- Species list with color-coded threat indicators (red/orange)
- Chapter accent color: `#c0392b` (red — signals threat)

### Chapter 2 — The Survey Method
- Three stat cards in a row: `2m × 2m grid`, `0–3 density scale`, `26 acres`
- Brief explanation of the survey methodology
- Density scale legend: Absent / Low / Moderate / High
- Chapter accent color: `#e67e22` (orange — fieldwork energy)

### Chapter 3 — The Findings
**Overview charts (two side-by-side, interactive Chart.js doughnuts):**
- Left: Species Composition — OB 47.1%, BB 32.8%, JK 14.5%, NM 4.4%, Other 1.2%
- Right: Overall Coverage — With Invasives 42.6%, No Invasives 57.4%
- Hover tooltips showing exact cell counts and percentages

**Per-species cards (4 cards, one per species: OB, BB, JK, NM):**
Each card contains:
- Species name, Latin name, color-coded header bar
- GIS density map image (BBLayout.jpg / JKLayout.jpg / NMLayout.jpg / OBLayout.jpg)
- Interactive Chart.js horizontal bar showing Low / Moderate / High density cell counts
- Coverage % and avg density stats
- Management approach (collapsed by default, expandable)

Species order by threat level (OB first, NM last):
1. Oriental Bittersweet (OB) — 25.1% coverage, avg density 0.54
2. Burning Bush (BB) — 17.5% coverage, avg density 0.38
3. Japanese Knotweed (JK) — 7.7% coverage, avg density 0.20
4. Norway Maple (NM) — 2.4% coverage, avg density 0.05

Chapter accent color: `#4a7c59` (green — nature/findings)

### Chapter 4 — Deeper Insights (New Analysis)
Three new computed analyses not in the original poster:

**1. Species Threat Index**
Composite score per species combining:
- Coverage weight (40%): cells_present / total_cells
- Avg density weight (40%): avg_density / 3 (normalized to 0–1)
- High-density weight (20%): high_cells / total_cells

Formula: `threat_score = ((coverage_pct * 0.4) + (avg_density_normalized * 0.4) + (high_density_pct * 0.2)) * 100`  
All three input components are normalized 0–1 before weighting. Final score is 0–100.  
Expected ranking: OB > BB > JK > NM > Other

**2. Severity Heatmap Table**
An HTML table with color-coded cells:
- Rows: each species
- Columns: Coverage %, Avg Density, High-Density Cells, Moderate Cells, Low Cells
- Cell background color scales from white (low) → light orange → red (high) using CSS inline styles computed in `app.py`
- Makes it instantly scannable which species/metric is most severe

**3. Management Effort Estimator**
Visual horizontal bars representing relative removal effort:
- Effort score = `cells_present × avg_density × difficulty_multiplier`
- Difficulty multipliers (hardcoded, based on poster management notes):
  - OB: 1.4 (vines, needs herbicide, shade strategy)
  - JK: 1.5 (rhizome system, 6–10 years)
  - BB: 1.0 (mechanical removal effective)
  - NM: 0.9 (small saplings pullable)
  - Other: 0.8
- Displayed as a Chart.js horizontal bar, labeled with relative effort tier (Low / Medium / High / Very High)

Chapter accent color: `#8e44ad` (purple — analytical/insight)

### Chapter 5 — Recommendations & Action
- Dark green background (`#1a3a1a`) — matches hero, bookends the page
- Full recommendation text from poster
- Four action bullet points with icons:
  - 🎯 Focus on high-density patches near trails and edges
  - ⚒️ Mechanical removal (hand-pull after rain) for BB and small NM
  - 💧 Herbicide (triclopyr/glyphosate) for dense OB and JK
  - 🌱 Pair removal with native planting + continue 2m×2m monitoring

### Footer
- Background: `#0d1f0d`
- Team names, Clark University, 2024, Prof. John Rogan
- GIS data attribution line (from map sources)

---

## Visual Design System

**Color palette:**
- Primary green: `#2d5a27`
- Light green: `#4a7c59`
- Background: `#f5f7f2`
- White panels: `#ffffff`
- Danger/threat red: `#c0392b`
- Warning orange: `#e67e22`
- Text dark: `#1a2e1a`
- Text muted: `#5a6b5a`

**Typography:**
- Headings: system sans-serif stack (Inter → -apple-system → sans-serif)
- Body: same stack, 16px, 1.6 line-height
- Chapter labels: 11px, 3px letter-spacing, all-caps

**Chapter accent pattern:**
Each chapter has a left border `4px solid [accent-color]` and a small all-caps chapter label above the heading.

**Animations:**
- Hero stat counters: count up from 0 on page load (vanilla JS)
- Sticky nav: fade in via IntersectionObserver on hero exit
- Species cards: fade-in-up on scroll into view (IntersectionObserver + CSS transition)
- Chart.js charts: built-in animation on first render

---

## Data Wiring

`app.py` loads at startup:
```python
# invasive_summary.csv → list of dicts
species = [
  {"Species": "Oriental Bittersweet", "Code": "OB", "Cells Present": 12890,
   "Coverage %": "25.1%", "Avg Density": 0.54, "Max Density": 3},
  ...
]

# density_details.csv → list of dicts  
density = [
  {"Species": "Burning Bush", "Code": "BB", "Avg Density": 0.378,
   "High": 3137, "Moderate": 4152, "Low": 1678, "Absent": 42317},
  ...
]

# Computed in app.py before passing to template
total_cells = 51284
for s in species:
    s["threat_score"] = compute_threat(s, density)
    s["effort_score"] = compute_effort(s, difficulty_multipliers)
```

Template receives: `species`, `density`, `total_cells` as Jinja2 context.  
Chart.js receives: `{{ species | tojson }}` inline in `<script>` tag.

---

## What's NOT in scope

- User authentication or login
- Database (CSVs are the data source)
- Mobile-first responsive design (desktop-first, basic mobile wrapping)
- Shapefile / geopandas live rendering (static map images only)
- Multi-language support
- Deployment configuration (build locally, deploy later)
