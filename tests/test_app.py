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
