import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import load_species_data, load_density_data, compute_threat_score, compute_effort_score, severity_color


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
    assert round(score, 1) == 9690.7


def test_severity_color_max():
    assert severity_color(100, 100) == '#c0392b'


def test_severity_color_zero():
    assert severity_color(0, 100) == '#ffffff'


def test_severity_color_half():
    # ratio=0.5: r=223(0xdf), g=156(0x9c), b=149(0x95)
    assert severity_color(50, 100) == '#df9c95'


def test_severity_color_zero_max():
    assert severity_color(0, 0) == '#ffffff'


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
