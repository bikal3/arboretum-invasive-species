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
