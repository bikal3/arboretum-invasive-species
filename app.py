import csv
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
