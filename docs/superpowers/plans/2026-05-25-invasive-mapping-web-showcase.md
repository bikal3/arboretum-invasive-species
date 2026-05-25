# Invasive Mapping Web Showcase — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page Flask web app showcasing the Hadwen Arboretum invasive plant mapping project as an interactive portfolio piece with hero, narrative chapters, Chart.js visualizations, and three new computed analyses.

**Architecture:** Python Flask serves one GET `/` route via a Jinja2 template. Data is loaded from existing CSVs at startup; computed analyses (threat index, effort scores, severity heatmap colors) are computed in Python and passed as JSON to Chart.js in the browser. All GIS map images are static files.

**Tech Stack:** Python Flask 3.x, Jinja2, Chart.js 4.x (CDN), vanilla CSS, vanilla JS, pytest

---

## File Map

| File | Responsibility |
|------|----------------|
| `app.py` | Flask factory, CSV loading, data merging, analysis computation, one GET `/` route |
| `templates/index.html` | Complete single-page Jinja2 template — hero, sticky nav, all 5 chapters, footer |
| `static/css/style.css` | All styles — color system, layout, hero, chapter styles, cards, heatmap table, responsive |
| `static/js/charts.js` | Chart.js chart configs, stat counter animation, sticky nav observer, scroll fade-in |
| `static/images/` | BBLayout.jpg, JKLayout.jpg, NMLayout.jpg, OBLayout.jpg (copied from project root) |
| `tests/test_app.py` | Unit tests for data/analysis functions + Flask route integration tests |
| `requirements.txt` | `flask>=3.0` and `pytest>=8.0` |

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `templates/`, `static/css/`, `static/js/`, `static/images/`, `tests/` directories

- [ ] **Step 1: Create requirements.txt**

```
flask>=3.0
pytest>=8.0
```

- [ ] **Step 2: Create directory structure and init tests package**

```bash
mkdir -p templates static/css static/js static/images tests
touch tests/__init__.py
```

- [ ] **Step 3: Copy map images to static/images/**

```bash
cp BBLayout.jpg JKLayout.jpg NMLayout.jpg OBLayout.jpg static/images/
```

- [ ] **Step 4: Install dependencies into existing .venv**

```bash
.venv/bin/pip install flask pytest
```

Expected output ends with:
```
Successfully installed flask-3.x.x ...
```

- [ ] **Step 5: Verify install**

```bash
.venv/bin/python -c "import flask, pytest; print('OK')"
```
Expected: `OK`

- [ ] **Step 6: Init git and commit**

```bash
git init
git add requirements.txt tests/__init__.py
git commit -m "chore: project setup for Flask web showcase"
```

---

### Task 2: Data Loading Functions

**Files:**
- Create: `app.py` (data functions only — route added in Task 4)
- Create: `tests/test_app.py` (data loading tests)

- [ ] **Step 1: Write failing tests**

Create `tests/test_app.py`:

```python
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import load_species_data, load_density_data


def test_load_species_data_returns_five_rows():
    rows = load_species_data()
    assert len(rows) == 5


def test_load_species_data_ob_fields():
    rows = load_species_data()
    ob = next(r for r in rows if r['code'] == 'OB')
    assert ob['name'] == 'Oriental Bittersweet'
    assert ob['cells_present'] == 12890
    assert abs(ob['coverage_pct'] - 25.1) < 0.1
    assert abs(ob['avg_density'] - 0.537) < 0.01


def test_load_density_data_returns_five_rows():
    rows = load_density_data()
    assert len(rows) == 5


def test_load_density_data_ob_fields():
    rows = load_density_data()
    ob = next(r for r in rows if r['code'] == 'OB')
    assert ob['high'] == 4417
    assert ob['moderate'] == 5812
    assert ob['low'] == 2661
    assert ob['absent'] == 38394
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
.venv/bin/pytest tests/test_app.py -v 2>&1 | head -20
```
Expected: `ImportError` or `ModuleNotFoundError` (app.py doesn't exist yet)

- [ ] **Step 3: Create app.py with data loading functions**

Create `app.py`:

```python
import csv
import json
from pathlib import Path
from flask import Flask, render_template

BASE_DIR = Path(__file__).parent


def load_species_data():
    rows = []
    with open(BASE_DIR / 'invasive_summary.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                'code': row['Code'].strip(),
                'name': row['Species'].strip(),
                'cells_present': int(row['Cells Present']),
                'coverage_pct': float(row['Coverage %'].replace('%', '')),
                'avg_density': float(row['Avg Density']),
                'max_density': int(row['Max Density']),
            })
    return rows


def load_density_data():
    rows = []
    with open(BASE_DIR / 'density_details.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                'code': row['Code'].strip(),
                'name': row['Species'].strip(),
                'avg_density': float(row['Avg Density']),
                'high': int(row['High']),
                'moderate': int(row['Moderate']),
                'low': int(row['Low']),
                'absent': int(row['Absent']),
            })
    return rows
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
.venv/bin/pytest tests/test_app.py -v
```
Expected:
```
PASSED tests/test_app.py::test_load_species_data_returns_five_rows
PASSED tests/test_app.py::test_load_species_data_ob_fields
PASSED tests/test_app.py::test_load_density_data_returns_five_rows
PASSED tests/test_app.py::test_load_density_data_ob_fields
```

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: data loading functions for species and density CSVs"
```

---

### Task 3: Analysis Computation Functions

**Files:**
- Modify: `app.py` (add 3 functions after `load_density_data`)
- Modify: `tests/test_app.py` (add analysis tests)

- [ ] **Step 1: Write failing tests**

Add to the bottom of `tests/test_app.py`:

```python
from app import compute_threat_score, compute_effort_score, severity_color


def test_compute_threat_score_ob():
    species_row = {'cells_present': 12890, 'avg_density': 0.537}
    density_row = {'high': 4417}
    score = compute_threat_score(species_row, density_row, total_cells=51284)
    assert round(score, 1) == 18.9


def test_compute_threat_score_ob_beats_nm():
    ob_s = {'cells_present': 12890, 'avg_density': 0.537}
    ob_d = {'high': 4417}
    nm_s = {'cells_present': 1216, 'avg_density': 0.046}
    nm_d = {'high': 227}
    assert compute_threat_score(ob_s, ob_d, 51284) > compute_threat_score(nm_s, nm_d, 51284)


def test_compute_effort_score():
    species_row = {'cells_present': 12890, 'avg_density': 0.537}
    score = compute_effort_score(species_row, difficulty=1.4)
    assert round(score, 1) == round(12890 * 0.537 * 1.4, 1)


def test_severity_color_max():
    assert severity_color(100, 100) == '#c0392b'


def test_severity_color_zero():
    assert severity_color(0, 100) == '#ffffff'


def test_severity_color_half():
    # ratio=0.5: r=223(0xdf), g=156(0x9c), b=149(0x95)
    assert severity_color(50, 100) == '#df9c95'


def test_severity_color_zero_max():
    assert severity_color(0, 0) == '#ffffff'
```

- [ ] **Step 2: Run new tests — verify they fail**

```bash
.venv/bin/pytest tests/test_app.py -v -k "threat or effort or severity"
```
Expected: `ImportError` (functions not yet in app.py)

- [ ] **Step 3: Add three analysis functions to app.py**

Add after `load_density_data()` in `app.py`:

```python
DIFFICULTY = {'OB': 1.4, 'JK': 1.5, 'BB': 1.0, 'NM': 0.9, 'O': 0.8}


def compute_threat_score(species_row, density_row, total_cells):
    coverage = species_row['cells_present'] / total_cells
    avg_den = species_row['avg_density'] / 3
    high = density_row['high'] / total_cells
    return ((coverage * 0.4) + (avg_den * 0.4) + (high * 0.2)) * 100


def compute_effort_score(species_row, difficulty):
    return species_row['cells_present'] * species_row['avg_density'] * difficulty


def severity_color(value, max_value):
    if max_value == 0:
        return '#ffffff'
    ratio = min(value / max_value, 1.0)
    r = int(255 - ratio * (255 - 192))
    g = int(255 - ratio * (255 - 57))
    b = int(255 - ratio * (255 - 43))
    return f'#{r:02x}{g:02x}{b:02x}'
```

- [ ] **Step 4: Run all tests — verify all 11 pass**

```bash
.venv/bin/pytest tests/test_app.py -v
```
Expected: 11 tests `PASSED`, 0 failures

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: analysis functions — threat score, effort score, severity color"
```

---

### Task 4: Flask Route

**Files:**
- Modify: `app.py` (add `SPECIES_META`, `TOTAL_CELLS` constants, `assemble_data`, `create_app`, route)
- Modify: `tests/test_app.py` (add route tests)

- [ ] **Step 1: Write failing route tests**

Add to the bottom of `tests/test_app.py`:

```python
from app import create_app


def test_index_returns_200():
    client = create_app().test_client()
    assert client.get('/').status_code == 200


def test_index_contains_title():
    client = create_app().test_client()
    assert b'Mapping Invasive Plant Distribution' in client.get('/').data


def test_index_contains_all_species_codes():
    client = create_app().test_client()
    data = client.get('/').data
    for code in [b'OB', b'BB', b'JK', b'NM']:
        assert code in data


def test_index_contains_chart_data():
    client = create_app().test_client()
    data = client.get('/').data
    assert b'speciesData' in data
    assert b'statsData' in data
```

- [ ] **Step 2: Run new tests — verify they fail**

```bash
.venv/bin/pytest tests/test_app.py -v -k "index"
```
Expected: `ImportError` (`create_app` not yet defined)

- [ ] **Step 3: Replace app.py with the complete version**

```python
import csv
from pathlib import Path
from flask import Flask, render_template

BASE_DIR = Path(__file__).parent

DIFFICULTY = {'OB': 1.4, 'JK': 1.5, 'BB': 1.0, 'NM': 0.9, 'O': 0.8}

SPECIES_META = {
    'OB': {
        'name': 'Oriental Bittersweet',
        'latin': 'Celastrus orbiculatus',
        'color': '#c0392b',
        'map_image': 'OBLayout.jpg',
        'management': (
            'Shade is one of the most powerful non-chemical tools. Promoting or planting '
            'large shade trees can suppress bittersweet by reducing the high-light conditions '
            'it needs to thrive, especially along edges and openings. In heavily infested '
            'patches, mechanical control alone may be insufficient, and targeted herbicide '
            'treatments (often using triclopyr in late summer) are sometimes recommended as '
            'part of an integrated strategy.'
        ),
    },
    'BB': {
        'name': 'Burning Bush',
        'latin': 'Euonymus alatus',
        'color': '#e74c3c',
        'map_image': 'BBLayout.jpg',
        'management': (
            'Mechanical removal is usually the preferred control method. Seedlings and small '
            'shrubs can often be pulled or dug out by hand, especially when the soil is moist, '
            'which makes it easier to remove most of the root system and reduce resprouting. '
            'For larger plants, tools such as a weed wrench or spading fork can be used to '
            'lever out the roots, and there is often little need for herbicide if the shrubs '
            'can be fully removed, particularly when done before they produce a heavy seed crop.'
        ),
    },
    'JK': {
        'name': 'Japanese Knotweed',
        'latin': 'Fallopia japonica',
        'color': '#e67e22',
        'map_image': 'JKLayout.jpg',
        'management': (
            'Effective control requires long-term persistence. Mowing or cutting patches every '
            '2-3 weeks over a period of 6-10 years can gradually exhaust the plant\'s '
            'underground rhizome system. The best time of year for a major cut is typically '
            'June, and control can be jump-started by an application of glyphosate in late '
            'summer (August-September), when systemic herbicides are most readily translocated '
            'to the roots.'
        ),
    },
    'NM': {
        'name': 'Norway Maple',
        'latin': 'Acer platanoides',
        'color': '#f39c12',
        'map_image': 'NMLayout.jpg',
        'management': (
            'Small seedlings and saplings are good candidates for mechanical control. Young '
            'trees with shallow roots can be pulled or dug when the soil is wet, taking care '
            'to remove the root crown so that the plant does not resprout. In areas where many '
            'seedlings are present, repeated hand-pulling after rain events can gradually '
            'deplete the seed bank.'
        ),
    },
    'O': {
        'name': 'Other Invasives',
        'latin': '',
        'color': '#95a5a6',
        'map_image': None,
        'management': 'Monitor and remove as identified using species-appropriate methods.',
    },
}

TOTAL_CELLS = 51284
INVASIVE_CELLS = 21847   # 42.6% of 51284 — from shapefile INVAS column
INVASIVE_PCT = 42.6
NON_INVASIVE_PCT = 57.4


def load_species_data():
    rows = []
    with open(BASE_DIR / 'invasive_summary.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                'code': row['Code'].strip(),
                'name': row['Species'].strip(),
                'cells_present': int(row['Cells Present']),
                'coverage_pct': float(row['Coverage %'].replace('%', '')),
                'avg_density': float(row['Avg Density']),
                'max_density': int(row['Max Density']),
            })
    return rows


def load_density_data():
    rows = []
    with open(BASE_DIR / 'density_details.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                'code': row['Code'].strip(),
                'name': row['Species'].strip(),
                'avg_density': float(row['Avg Density']),
                'high': int(row['High']),
                'moderate': int(row['Moderate']),
                'low': int(row['Low']),
                'absent': int(row['Absent']),
            })
    return rows


def compute_threat_score(species_row, density_row, total_cells):
    coverage = species_row['cells_present'] / total_cells
    avg_den = species_row['avg_density'] / 3
    high = density_row['high'] / total_cells
    return ((coverage * 0.4) + (avg_den * 0.4) + (high * 0.2)) * 100


def compute_effort_score(species_row, difficulty):
    return species_row['cells_present'] * species_row['avg_density'] * difficulty


def severity_color(value, max_value):
    if max_value == 0:
        return '#ffffff'
    ratio = min(value / max_value, 1.0)
    r = int(255 - ratio * (255 - 192))
    g = int(255 - ratio * (255 - 57))
    b = int(255 - ratio * (255 - 43))
    return f'#{r:02x}{g:02x}{b:02x}'


def assemble_data():
    species_rows = load_species_data()
    density_rows = load_density_data()
    density_by_code = {d['code']: d for d in density_rows}

    effort_scores = {
        s['code']: compute_effort_score(s, DIFFICULTY.get(s['code'], 1.0))
        for s in species_rows
    }
    max_effort = max(effort_scores.values())

    def effort_tier(pct):
        for threshold, label in [(75, 'Very High'), (40, 'High'), (15, 'Medium')]:
            if pct >= threshold:
                return label
        return 'Low'

    total_species_cells = sum(s['cells_present'] for s in species_rows)
    max_coverage = max(s['coverage_pct'] for s in species_rows)
    max_avg_density = max(s['avg_density'] for s in species_rows)
    max_high = max(density_by_code[s['code']]['high'] for s in species_rows)
    max_moderate = max(density_by_code[s['code']]['moderate'] for s in species_rows)
    max_low = max(density_by_code[s['code']]['low'] for s in species_rows)

    species = []
    for s in species_rows:
        code = s['code']
        d = density_by_code[code]
        meta = SPECIES_META[code]
        raw_effort = effort_scores[code]
        effort_pct = (raw_effort / max_effort) * 100

        species.append({
            **s,
            **meta,
            'high': d['high'],
            'moderate': d['moderate'],
            'low': d['low'],
            'absent': d['absent'],
            'composition_pct': round(s['cells_present'] / total_species_cells * 100, 1),
            'threat_score': round(compute_threat_score(s, d, TOTAL_CELLS), 1),
            'effort_pct': round(effort_pct, 1),
            'effort_tier': effort_tier(effort_pct),
            'sev_color_coverage': severity_color(s['coverage_pct'], max_coverage),
            'sev_color_avg_density': severity_color(s['avg_density'], max_avg_density),
            'sev_color_high': severity_color(d['high'], max_high),
            'sev_color_moderate': severity_color(d['moderate'], max_moderate),
            'sev_color_low': severity_color(d['low'], max_low),
        })

    species.sort(key=lambda x: x['threat_score'], reverse=True)

    stats = {
        'total_cells': TOTAL_CELLS,
        'invasive_cells': INVASIVE_CELLS,
        'invasive_pct': INVASIVE_PCT,
        'non_invasive_pct': NON_INVASIVE_PCT,
    }
    return species, stats


def create_app():
    flask_app = Flask(__name__)

    @flask_app.route('/')
    def index():
        species, stats = assemble_data()
        card_species = [s for s in species if s['code'] != 'O']
        return render_template('index.html',
                               species=species,
                               card_species=card_species,
                               stats=stats)

    return flask_app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

- [ ] **Step 4: Run all tests — verify all 15 pass**

```bash
.venv/bin/pytest tests/test_app.py -v
```
Expected: 15 tests `PASSED`, 0 failures

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: Flask route with full assembled species and analysis data"
```

---

### Task 5: HTML Template

**Files:**
- Create: `templates/index.html`

- [ ] **Step 1: Create templates/index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mapping Invasive Plants — Hadwen Arboretum</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
</head>
<body>

  <!-- HERO -->
  <section class="hero" id="hero">
    <div class="hero-inner">
      <p class="hero-kicker">Clark University &middot; Hadwen Arboretum &middot; 2024</p>
      <h1 class="hero-title">Mapping Invasive Plant<br>Distribution</h1>
      <p class="hero-authors">Annan Shrestha &middot; Bikal Shrestha &middot; Nathan Clark</p>
      <p class="hero-sponsor">Sponsor: Professor John Rogan</p>
      <div class="hero-stats">
        <div class="stat-card">
          <span class="stat-number" data-target="42.6" data-suffix="%">0%</span>
          <span class="stat-label">Invasive Coverage</span>
        </div>
        <div class="stat-card">
          <span class="stat-number" data-target="51284" data-suffix="">0</span>
          <span class="stat-label">Survey Cells (2m&times;2m)</span>
        </div>
        <div class="stat-card">
          <span class="stat-number" data-target="4" data-suffix="">0</span>
          <span class="stat-label">Invasive Species</span>
        </div>
        <div class="stat-card">
          <span class="stat-number" data-target="26" data-suffix="">0</span>
          <span class="stat-label">Acres Surveyed</span>
        </div>
      </div>
      <div class="hero-scroll-hint">&#x25BC; scroll to explore</div>
    </div>
  </section>

  <!-- STICKY NAV -->
  <nav class="sticky-nav" id="sticky-nav">
    <span class="nav-brand">Hadwen Invasive Map</span>
    <div class="nav-links">
      <a href="#problem">Problem</a>
      <a href="#survey">Survey</a>
      <a href="#findings">Findings</a>
      <a href="#analysis">Analysis</a>
      <a href="#action">Action</a>
    </div>
  </nav>

  <!-- CH 1: THE PROBLEM -->
  <section class="chapter" id="problem">
    <div class="chapter-label" style="color:#c0392b;">Chapter 1</div>
    <h2 class="chapter-title" style="border-left-color:#c0392b;">The Problem</h2>
    <div class="two-col">
      <div class="prose">
        <p>The Hadwen Arboretum is a 26-acre urban forest owned by Clark University that provides
        important habitat, teaching space, and recreation for the surrounding community. Like many
        New England woodlands, it is increasingly impacted by invasive plants that outcompete
        native species and alter ecosystem processes.</p>
        <p>This project mapped the fine-scale distribution and density of these invasives using a
        2m &times; 2m survey grid to identify hotspots and support targeted management and
        restoration planning.</p>
        <p>The land was originally part of Obadiah Hadwen's Magnolia Farm, bequeathed to Clark
        University in 1907 to be preserved as an arboretum and outdoor classroom. Recent
        student- and faculty-led efforts have sought to restore the arboretum's educational
        mission while improving ecological health.</p>
      </div>
      <div class="species-list-card">
        <h3>Invasive Species Tracked</h3>
        <ul>
          {% for s in card_species %}
          <li>
            <span class="species-dot" style="background:{{ s.color }};"></span>
            <div>
              <span class="species-item-name">{{ s.name }}</span>
              <span class="species-item-latin">{{ s.latin }}</span>
            </div>
          </li>
          {% endfor %}
        </ul>
      </div>
    </div>
  </section>

  <!-- CH 2: THE SURVEY -->
  <section class="chapter chapter-alt" id="survey">
    <div class="chapter-label" style="color:#e67e22;">Chapter 2</div>
    <h2 class="chapter-title" style="border-left-color:#e67e22;">The Survey Method</h2>
    <div class="survey-stats">
      <div class="survey-stat">
        <span class="survey-stat-value">2m &times; 2m</span>
        <span class="survey-stat-label">Grid cell size</span>
      </div>
      <div class="survey-stat">
        <span class="survey-stat-value">51,284</span>
        <span class="survey-stat-label">Total cells surveyed</span>
      </div>
      <div class="survey-stat">
        <span class="survey-stat-value">0 &ndash; 3</span>
        <span class="survey-stat-label">Density scale</span>
      </div>
      <div class="survey-stat">
        <span class="survey-stat-value">26 ac</span>
        <span class="survey-stat-label">Full arboretum</span>
      </div>
    </div>
    <div class="density-legend">
      <h3>Density Scale</h3>
      <div class="legend-items">
        <div class="legend-item">
          <span class="legend-swatch" style="background:#ffffff;border:1px solid #ccc;"></span>
          <span>0 &mdash; Absent</span>
        </div>
        <div class="legend-item">
          <span class="legend-swatch" style="background:#ffb3b3;"></span>
          <span>1 &mdash; Low</span>
        </div>
        <div class="legend-item">
          <span class="legend-swatch" style="background:#ff6666;"></span>
          <span>2 &mdash; Moderate</span>
        </div>
        <div class="legend-item">
          <span class="legend-swatch" style="background:#c0392b;"></span>
          <span>3 &mdash; High / Dominant</span>
        </div>
      </div>
    </div>
  </section>

  <!-- CH 3: FINDINGS -->
  <section class="chapter" id="findings">
    <div class="chapter-label" style="color:#4a7c59;">Chapter 3</div>
    <h2 class="chapter-title" style="border-left-color:#4a7c59;">The Findings</h2>

    <div class="charts-overview">
      <div class="chart-wrapper">
        <h3>Species Composition</h3>
        <p class="chart-sub">Share of invasive area by species</p>
        <canvas id="speciesCompositionChart"></canvas>
      </div>
      <div class="chart-wrapper">
        <h3>Overall Coverage</h3>
        <p class="chart-sub">{{ stats.invasive_pct }}% of the arboretum has invasives</p>
        <canvas id="overallCoverageChart"></canvas>
      </div>
    </div>

    <h3 class="section-subheading">Per-Species Breakdown</h3>
    <div class="species-cards">
      {% for s in card_species %}
      <div class="species-card fade-in-up">
        <div class="species-card-header" style="background:{{ s.color }};">
          <div>
            <span class="species-card-code">{{ s.code }}</span>
            <span class="species-card-name">{{ s.name }}</span>
          </div>
          <span class="species-card-latin">{{ s.latin }}</span>
        </div>
        <div class="species-card-body">
          <img src="{{ url_for('static', filename='images/' + s.map_image) }}"
               alt="{{ s.name }} density map" class="species-map-img">
          <div class="species-stats-row">
            <div class="species-stat">
              <span class="species-stat-val">{{ s.coverage_pct }}%</span>
              <span class="species-stat-lbl">Coverage</span>
            </div>
            <div class="species-stat">
              <span class="species-stat-val">{{ s.avg_density }}</span>
              <span class="species-stat-lbl">Avg Density</span>
            </div>
            <div class="species-stat">
              <span class="species-stat-val">{{ "{:,}".format(s.cells_present) }}</span>
              <span class="species-stat-lbl">Cells Present</span>
            </div>
          </div>
          <div class="density-bar-wrapper">
            <canvas id="densityBar_{{ s.code }}" height="80"></canvas>
          </div>
          <details class="management-details">
            <summary>Management Approach</summary>
            <p class="management-text">{{ s.management }}</p>
          </details>
        </div>
      </div>
      {% endfor %}
    </div>
  </section>

  <!-- CH 4: ANALYSIS -->
  <section class="chapter chapter-alt" id="analysis">
    <div class="chapter-label" style="color:#8e44ad;">Chapter 4 &middot; New Analysis</div>
    <h2 class="chapter-title" style="border-left-color:#8e44ad;">Deeper Insights</h2>

    <div class="analysis-block fade-in-up">
      <h3>&#127919; Species Threat Index</h3>
      <p>A composite 0&ndash;100 score combining coverage (40%), average density (40%), and
      high-density cell count (20%). Higher score = greater ecological threat to the arboretum.</p>
      <div class="chart-wrapper-wide">
        <canvas id="threatIndexChart" height="120"></canvas>
      </div>
    </div>

    <div class="analysis-block fade-in-up">
      <h3>&#127777;&#65039; Severity Heatmap</h3>
      <p>Color intensity scales from white (low) to dark red (high) within each column.</p>
      <div class="table-scroll">
        <table class="heatmap-table">
          <thead>
            <tr>
              <th>Species</th>
              <th>Coverage %</th>
              <th>Avg Density</th>
              <th>High-Density Cells</th>
              <th>Moderate Cells</th>
              <th>Low Cells</th>
            </tr>
          </thead>
          <tbody>
            {% for s in species %}
            <tr>
              <td class="species-name-cell">
                <span class="dot" style="background:{{ s.color }};"></span>{{ s.name }}
              </td>
              <td style="background:{{ s.sev_color_coverage }};">{{ s.coverage_pct }}%</td>
              <td style="background:{{ s.sev_color_avg_density }};">{{ s.avg_density }}</td>
              <td style="background:{{ s.sev_color_high }};">{{ "{:,}".format(s.high) }}</td>
              <td style="background:{{ s.sev_color_moderate }};">{{ "{:,}".format(s.moderate) }}</td>
              <td style="background:{{ s.sev_color_low }};">{{ "{:,}".format(s.low) }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </div>

    <div class="analysis-block fade-in-up">
      <h3>&#9874;&#65039; Management Effort Estimator</h3>
      <p>Relative removal effort: cells present &times; average density &times; difficulty
      multiplier (JK=1.5 rhizome system, OB=1.4 vine regrowth, BB=1.0, NM=0.9, Other=0.8).
      Normalized to the highest-effort species.</p>
      <div class="chart-wrapper-wide">
        <canvas id="effortChart" height="120"></canvas>
      </div>
    </div>
  </section>

  <!-- CH 5: ACTION -->
  <section class="chapter chapter-dark" id="action">
    <div class="chapter-label" style="color:#a8d5a2;">Chapter 5</div>
    <h2 class="chapter-title" style="border-left-color:#a8d5a2; color:white;">
      Recommendations &amp; Action
    </h2>
    <p class="chapter-body-text" style="color:#d4edda;">
      Focus management on high-density patches of oriental bittersweet, burning bush, knotweed,
      and Norway maple, especially along edges, trails, and disturbed areas.
    </p>
    <ul class="action-list">
      <li>&#127919; Focus on high-density patches near trails and edges first</li>
      <li>&#9874;&#65039; Use mechanical removal (hand-pull after rain) for burning bush and small Norway maple</li>
      <li>&#128167; Apply herbicide (triclopyr / glyphosate) for dense oriental bittersweet and knotweed stands</li>
      <li>&#127807; Pair removal with native tree and understory planting to suppress regrowth</li>
      <li>&#128269; Continue 2m &times; 2m grid monitoring to track treatment success and detect new invasions</li>
    </ul>
  </section>

  <!-- FOOTER -->
  <footer class="site-footer">
    <p>Annan Shrestha &middot; Bikal Shrestha &middot; Nathan Clark &middot; Clark University 2024</p>
    <p>Sponsor: Professor John Rogan</p>
    <p class="attribution">Map data: Esri, Vantor, Airbus DS, USGS, NGA, NASA, CGIAR,
    N Robinson, NCEAS, NLS, OS, NMA, Geodatastyrelsen, Rijkswaterstaat, GSA, Geoland,
    FEMA, Intermap, and the GIS user community</p>
  </footer>

  <script>
    window.speciesData = {{ species | tojson }};
    window.cardSpeciesData = {{ card_species | tojson }};
    window.statsData = {{ stats | tojson }};
  </script>
  <script src="{{ url_for('static', filename='js/charts.js') }}"></script>
</body>
</html>
```

- [ ] **Step 2: Start Flask and verify the page loads with no 500 errors**

```bash
FLASK_APP=app.py .venv/bin/flask run
```
Open `http://127.0.0.1:5000` — HTML structure should be visible in browser (no CSS/JS yet).
Terminal must show `GET / 200`.

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat: complete Jinja2 template with all 5 chapters"
```

---

### Task 6: CSS

**Files:**
- Create: `static/css/style.css`

- [ ] **Step 1: Create static/css/style.css**

```css
/* Reset & Base */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: #1a2e1a;
  background: #f5f7f2;
}
img { max-width: 100%; display: block; }
a { color: inherit; text-decoration: none; }

/* Hero */
.hero {
  background: linear-gradient(160deg, #1a3a1a 0%, #2d5a27 50%, #4a7c59 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 60px 24px;
}
.hero-inner { max-width: 800px; }
.hero-kicker {
  font-size: 11px;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: #a8d5a2;
  margin-bottom: 16px;
}
.hero-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  color: #ffffff;
  line-height: 1.15;
  margin-bottom: 16px;
}
.hero-authors { font-size: 1rem; color: #d4edda; margin-bottom: 4px; }
.hero-sponsor { font-size: 0.85rem; color: rgba(212,237,218,0.7); margin-bottom: 40px; }
.hero-stats {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 40px;
}
.stat-card {
  background: rgba(255,255,255,0.12);
  backdrop-filter: blur(6px);
  border-radius: 12px;
  padding: 16px 24px;
  min-width: 130px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.stat-number { font-size: 2rem; font-weight: 800; color: #ffffff; }
.stat-label { font-size: 0.75rem; color: #a8d5a2; line-height: 1.3; }
.hero-scroll-hint { font-size: 0.8rem; color: #a8d5a2; animation: bounce 2s infinite; }
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(6px); }
}

/* Sticky Nav */
.sticky-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #2d5a27;
  display: flex;
  align-items: center;
  padding: 10px 32px;
  gap: 24px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.sticky-nav.visible { opacity: 1; pointer-events: all; }
.nav-brand { font-weight: 700; color: #ffffff; font-size: 0.9rem; flex: 1; }
.nav-links { display: flex; gap: 20px; }
.nav-links a { color: #a8d5a2; font-size: 0.85rem; transition: color 0.2s; }
.nav-links a:hover { color: #ffffff; }

/* Chapters */
.chapter { padding: 64px 32px; max-width: 1100px; margin: 0 auto; }
.chapter-alt { background: #ffffff; max-width: 100%; padding: 64px 32px; }
.chapter-alt > * { max-width: 1100px; margin-left: auto; margin-right: auto; }
.chapter-dark { background: #1a3a1a; max-width: 100%; padding: 64px 32px; }
.chapter-dark > * { max-width: 1100px; margin-left: auto; margin-right: auto; }
.chapter-label {
  font-size: 11px;
  letter-spacing: 3px;
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 6px;
}
.chapter-title {
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  font-weight: 800;
  border-left: 5px solid;
  padding-left: 16px;
  margin-bottom: 32px;
  line-height: 1.2;
}
.chapter-body-text { font-size: 1.05rem; margin-bottom: 28px; max-width: 750px; }

/* Chapter 1 */
.two-col { display: grid; grid-template-columns: 1fr 340px; gap: 32px; align-items: start; }
.prose p { margin-bottom: 16px; color: #3a4a3a; }
.species-list-card { background: #e8f0e4; border-radius: 12px; padding: 24px; }
.species-list-card h3 { font-size: 1rem; margin-bottom: 16px; color: #2d5a27; }
.species-list-card ul { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.species-list-card li { display: flex; align-items: flex-start; gap: 10px; }
.species-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.species-item-name { font-weight: 600; font-size: 0.9rem; display: block; }
.species-item-latin { font-style: italic; font-size: 0.78rem; color: #5a6b5a; display: block; }

/* Chapter 2 */
.survey-stats { display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 32px; }
.survey-stat {
  background: #fff8f0;
  border: 1px solid #ffd6a0;
  border-radius: 10px;
  padding: 20px 28px;
  flex: 1;
  min-width: 160px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.survey-stat-value { font-size: 1.6rem; font-weight: 800; color: #e67e22; }
.survey-stat-label { font-size: 0.8rem; color: #7a5a2a; }
.density-legend h3 { font-size: 1rem; margin-bottom: 12px; color: #2d5a27; }
.legend-items { display: flex; gap: 20px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; }
.legend-swatch { width: 20px; height: 20px; border-radius: 4px; flex-shrink: 0; }

/* Chapter 3 Charts */
.charts-overview { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-bottom: 48px; }
.chart-wrapper { background: #ffffff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.chart-wrapper h3 { font-size: 1rem; margin-bottom: 4px; }
.chart-sub { font-size: 0.8rem; color: #5a6b5a; margin-bottom: 16px; }
.chart-wrapper-wide { background: #ffffff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.section-subheading { font-size: 1.1rem; font-weight: 700; color: #2d5a27; margin-bottom: 20px; }

/* Species Cards */
.species-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(480px, 1fr)); gap: 24px; }
.species-card { background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.species-card-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}
.species-card-code { font-size: 1.4rem; font-weight: 800; color: rgba(255,255,255,0.9); margin-right: 10px; }
.species-card-name { font-size: 1.1rem; font-weight: 700; color: #ffffff; }
.species-card-latin { font-style: italic; font-size: 0.8rem; color: rgba(255,255,255,0.75); }
.species-card-body { padding: 20px; }
.species-map-img { width: 100%; border-radius: 8px; margin-bottom: 16px; border: 1px solid #e0e8dc; }
.species-stats-row { display: flex; gap: 16px; margin-bottom: 16px; }
.species-stat {
  flex: 1;
  background: #f5f7f2;
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.species-stat-val { font-size: 1.2rem; font-weight: 700; color: #2d5a27; }
.species-stat-lbl { font-size: 0.72rem; color: #5a6b5a; }
.density-bar-wrapper { margin-bottom: 16px; }
.management-details summary {
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  color: #4a7c59;
  padding: 8px 0;
  border-top: 1px solid #e0e8dc;
}
.management-details[open] summary { color: #2d5a27; }
.management-text { margin-top: 10px; font-size: 0.88rem; color: #3a4a3a; line-height: 1.6; }

/* Chapter 4 Analysis */
.analysis-block { margin-bottom: 48px; }
.analysis-block h3 { font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; color: #1a2e1a; }
.analysis-block > p { font-size: 0.9rem; color: #5a6b5a; margin-bottom: 16px; max-width: 700px; }
.table-scroll { overflow-x: auto; }
.heatmap-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
  background: #ffffff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.heatmap-table th {
  background: #2d5a27;
  color: #ffffff;
  padding: 12px 16px;
  text-align: left;
  font-size: 0.8rem;
  font-weight: 600;
}
.heatmap-table td { padding: 10px 16px; border-bottom: 1px solid #e8f0e4; font-weight: 500; }
.heatmap-table tbody tr:last-child td { border-bottom: none; }
.heatmap-table tbody tr:hover { filter: brightness(0.97); }
.species-name-cell { display: flex; align-items: center; gap: 8px; background: #ffffff !important; }
.dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* Chapter 5 */
.action-list { list-style: none; display: flex; flex-direction: column; gap: 14px; margin-top: 8px; }
.action-list li {
  font-size: 1rem;
  color: #d4edda;
  padding: 8px 12px;
  border-left: 3px solid #4a7c59;
  background: rgba(255,255,255,0.05);
  border-radius: 0 6px 6px 0;
}

/* Footer */
.site-footer { background: #0d1f0d; padding: 32px; text-align: center; color: #4a7c59; font-size: 0.85rem; line-height: 2; }
.attribution { font-size: 0.72rem; color: #2d5a27; margin-top: 8px; }

/* Scroll animation */
.fade-in-up { opacity: 0; transform: translateY(24px); transition: opacity 0.5s ease, transform 0.5s ease; }
.fade-in-up.visible { opacity: 1; transform: translateY(0); }

/* Responsive */
@media (max-width: 768px) {
  .two-col { grid-template-columns: 1fr; }
  .charts-overview { grid-template-columns: 1fr; }
  .species-cards { grid-template-columns: 1fr; }
  .hero-stats { gap: 10px; }
  .stat-card { min-width: 110px; padding: 12px 16px; }
  .stat-number { font-size: 1.5rem; }
  .chapter, .chapter-alt, .chapter-dark { padding: 40px 16px; }
}
```

- [ ] **Step 2: Restart Flask and verify styles load**

```bash
FLASK_APP=app.py .venv/bin/flask run
```
Open `http://127.0.0.1:5000`. Verify:
- Dark green hero fills the viewport
- Stat cards appear inside the hero
- Chapter sections have colored left-border accent
- No unstyled text visible

- [ ] **Step 3: Commit**

```bash
git add static/css/style.css
git commit -m "feat: complete CSS — nature/clean theme, all chapters, responsive"
```

---

### Task 7: Charts and Animations

**Files:**
- Create: `static/js/charts.js`

- [ ] **Step 1: Create static/js/charts.js**

```javascript
/* Stat counter animation */
function animateCounter(el) {
  const target = parseFloat(el.dataset.target);
  const suffix = el.dataset.suffix || '';
  const isDecimal = target % 1 !== 0;
  const duration = 1800;
  const start = performance.now();

  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = target * eased;
    el.textContent = (isDecimal
      ? current.toFixed(1)
      : Math.floor(current).toLocaleString()) + suffix;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

window.addEventListener('load', () => {
  document.querySelectorAll('.stat-number').forEach(animateCounter);
});

/* Sticky nav via IntersectionObserver */
const nav = document.getElementById('sticky-nav');
const hero = document.getElementById('hero');
if (nav && hero) {
  new IntersectionObserver(
    ([entry]) => nav.classList.toggle('visible', !entry.isIntersecting),
    { threshold: 0 }
  ).observe(hero);
}

/* Scroll fade-in for .fade-in-up elements */
const fadeObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      fadeObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });
document.querySelectorAll('.fade-in-up').forEach(el => fadeObs.observe(el));

/* Chart.js global defaults */
Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
Chart.defaults.plugins.legend.labels.boxWidth = 14;
Chart.defaults.plugins.legend.labels.padding = 16;

/* Overview doughnut charts */
(function () {
  const species = window.speciesData || [];
  const stats = window.statsData || {};

  new Chart(document.getElementById('speciesCompositionChart'), {
    type: 'doughnut',
    data: {
      labels: species.map(s => s.name),
      datasets: [{
        data: species.map(s => s.composition_pct),
        backgroundColor: species.map(s => s.color),
        borderWidth: 2,
        borderColor: '#f5f7f2',
      }],
    },
    options: {
      plugins: {
        tooltip: {
          callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed.toFixed(1)}%` },
        },
      },
    },
  });

  new Chart(document.getElementById('overallCoverageChart'), {
    type: 'doughnut',
    data: {
      labels: ['With Invasives', 'No Invasives'],
      datasets: [{
        data: [stats.invasive_pct, stats.non_invasive_pct],
        backgroundColor: ['#c0392b', '#a8d5a2'],
        borderWidth: 2,
        borderColor: '#f5f7f2',
      }],
    },
    options: {
      plugins: {
        tooltip: {
          callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed.toFixed(1)}%` },
        },
      },
    },
  });
})();

/* Per-species density bar charts */
(function () {
  (window.cardSpeciesData || []).forEach(s => {
    const canvas = document.getElementById(`densityBar_${s.code}`);
    if (!canvas) return;
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: ['Low', 'Moderate', 'High'],
        datasets: [{
          data: [s.low, s.moderate, s.high],
          backgroundColor: ['#90ee90', '#ffd700', s.color],
          borderWidth: 1,
          borderColor: 'rgba(0,0,0,0.08)',
        }],
      },
      options: {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 11 } } },
          y: { ticks: { font: { size: 11 } } },
        },
      },
    });
  });
})();

/* Threat Index horizontal bar */
(function () {
  const sorted = [...(window.speciesData || [])].sort((a, b) => b.threat_score - a.threat_score);
  new Chart(document.getElementById('threatIndexChart'), {
    type: 'bar',
    data: {
      labels: sorted.map(s => s.name),
      datasets: [{
        label: 'Threat Index (0–100)',
        data: sorted.map(s => s.threat_score),
        backgroundColor: sorted.map(s => s.color),
        borderWidth: 1,
        borderColor: 'rgba(0,0,0,0.1)',
      }],
    },
    options: {
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` Score: ${ctx.parsed.x.toFixed(1)}` } },
      },
      scales: {
        x: { max: 25, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 11 } } },
        y: { ticks: { font: { size: 12 } } },
      },
    },
  });
})();

/* Management Effort horizontal bar */
(function () {
  const sorted = [...(window.speciesData || [])].sort((a, b) => b.effort_pct - a.effort_pct);
  new Chart(document.getElementById('effortChart'), {
    type: 'bar',
    data: {
      labels: sorted.map(s => `${s.name} (${s.effort_tier})`),
      datasets: [{
        label: 'Relative Effort (%)',
        data: sorted.map(s => s.effort_pct),
        backgroundColor: sorted.map(s => s.color),
        borderWidth: 1,
        borderColor: 'rgba(0,0,0,0.1)',
      }],
    },
    options: {
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` Effort: ${ctx.parsed.x.toFixed(1)}%` } },
      },
      scales: {
        x: { max: 100, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 11 } } },
        y: { ticks: { font: { size: 11 } } },
      },
    },
  });
})();
```

- [ ] **Step 2: Restart Flask and verify all charts render**

```bash
FLASK_APP=app.py .venv/bin/flask run
```

Open `http://127.0.0.1:5000` and confirm each item:

| Item | Expected |
|------|----------|
| Stat counters | Animate 0 → target on page load |
| Sticky nav | Hidden at top, fades in after scrolling past hero |
| Species Composition doughnut | Renders with 5 segments, hover shows % |
| Overall Coverage doughnut | Renders red/green, hover shows % |
| OB density bar | Horizontal bars: Low/Moderate/High cell counts |
| BB density bar | Same as above |
| JK density bar | Same as above |
| NM density bar | Same as above |
| Threat Index bar | OB scores highest, horizontal bars |
| Effort Estimator bar | OB and JK highest, tier labels in axis |
| Severity Heatmap | Color-coded cells, OB row darkest |
| Fade-in-up | Species cards and analysis blocks animate on scroll |

- [ ] **Step 3: Commit**

```bash
git add static/js/charts.js
git commit -m "feat: Chart.js charts, stat counters, sticky nav, scroll animations"
```

---

### Task 8: Final Test Run and Smoke Check

**Files:** No new files — verification only

- [ ] **Step 1: Run the full test suite**

```bash
.venv/bin/pytest tests/test_app.py -v
```
Expected output:
```
PASSED tests/test_app.py::test_load_species_data_returns_five_rows
PASSED tests/test_app.py::test_load_species_data_ob_fields
PASSED tests/test_app.py::test_load_density_data_returns_five_rows
PASSED tests/test_app.py::test_load_density_data_ob_fields
PASSED tests/test_app.py::test_compute_threat_score_ob
PASSED tests/test_app.py::test_compute_threat_score_ob_beats_nm
PASSED tests/test_app.py::test_compute_effort_score
PASSED tests/test_app.py::test_severity_color_max
PASSED tests/test_app.py::test_severity_color_zero
PASSED tests/test_app.py::test_severity_color_half
PASSED tests/test_app.py::test_severity_color_zero_max
PASSED tests/test_app.py::test_index_returns_200
PASSED tests/test_app.py::test_index_contains_title
PASSED tests/test_app.py::test_index_contains_all_species_codes
PASSED tests/test_app.py::test_index_contains_chart_data

15 passed in x.xxs
```

- [ ] **Step 2: Start Flask for final walkthrough**

```bash
FLASK_APP=app.py .venv/bin/flask run
```

Manually verify at `http://127.0.0.1:5000`:

| Section | Check |
|---------|-------|
| Hero | Dark green gradient, title, team names, 4 animated stat counters |
| Sticky nav | Appears on scroll, all 5 chapter links work |
| Ch 1 | Two-column: intro text left, species list card right, colored dots |
| Ch 2 | 4 survey stat cards, density scale legend |
| Ch 3 | Two doughnut charts with hover tooltips |
| Ch 3 | 4 species cards — each has map image, 3 stats, density bar, expandable management |
| Ch 4 | Threat Index chart — OB highest score |
| Ch 4 | Severity heatmap — OB row darkest red |
| Ch 4 | Effort chart — OB and JK highest bars |
| Ch 5 | Dark green bg, 5 action items |
| Footer | Team names + attribution |
| Mobile (375px width) | Cards stack, hero stats wrap |

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: invasive mapping web showcase — complete"
```
