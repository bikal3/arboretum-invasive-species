# Mapping Invasive Plant Distribution — Hadwen Arboretum

An interactive web showcase of a GIS-based invasive plant survey conducted at the Hadwen Arboretum, Worcester MA. Built as a portfolio piece presenting the research as a narrative story with interactive charts and new computed analyses.

**Team:** Annan Shrestha · Bikal Shrestha · Nathan Clark  
**Sponsor:** Professor John Rogan · Clark University · 2024

---

## Overview

The Hadwen Arboretum was surveyed using a **51,284-cell (2m × 2m) grid** covering 26 acres. Each cell was scored for the presence and density (0–3 scale) of five invasive species:

| Code | Species |
|------|---------|
| OB | Oriental Bittersweet (*Celastrus orbiculatus*) |
| BB | Burning Bush (*Euonymus alatus*) |
| JK | Japanese Knotweed (*Fallopia japonica*) |
| NM | Norway Maple (*Acer platanoides*) |
| O  | Other Invasives |

**Key finding:** 42.6% of the arboretum contains at least one invasive species.

---

## Features

- **Hero section** with animated stat counters
- **5-chapter narrative** — Problem → Survey → Findings → Analysis → Action
- **Interactive Chart.js charts** — species composition, density distributions, threat index, effort estimator
- **GIS density maps** for each species
- **Species Threat Index** — composite score combining coverage, average density, and high-density cell count
- **Severity Heatmap** — color-coded table (white → dark red) across all metrics
- **Management Effort Estimator** — relative removal effort weighted by species difficulty
- **Analysis notebook** (`analysis.ipynb`) with full data analysis and embedded outputs

---

## Tech Stack

- **Backend:** Python · Flask 3.x · Jinja2
- **Frontend:** Vanilla CSS · Vanilla JS · Chart.js 4.4.4
- **Data:** CSV files (no database)
- **Analysis:** Jupyter Notebook · pandas · matplotlib · seaborn
- **Tests:** pytest (15 tests)

---

## Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/bikal3/arboretum-invasive-species.git
cd arboretum-invasive-species

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
flask run
```

Open **http://127.0.0.1:5000** in your browser.

```bash
# Run tests
pytest tests/test_app.py -v
```

---

## Project Structure

```
arboretum-invasive-species/
├── app.py                  # Flask app — data loading, analysis, route
├── templates/
│   └── index.html          # Single-page Jinja2 template
├── static/
│   ├── css/style.css       # All styles
│   ├── js/charts.js        # Chart.js + animations
│   └── images/             # GIS density map images
├── invasive_summary.csv    # Species coverage data
├── density_details.csv     # Density breakdown per species
├── analysis.ipynb          # Full analysis notebook
├── requirements.txt
└── tests/
    └── test_app.py         # 15 pytest tests
```

---

## Analysis Notebook

`analysis.ipynb` provides a standalone data analysis using only the CSV files — no GIS software required. Outputs are pre-rendered so it displays directly on GitHub.

Sections: Data Overview · Species Coverage · Density Distribution · Coverage Pie Charts · GIS Maps · Threat Index · Severity Heatmap · Management Effort Estimator
