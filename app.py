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
