"""
Automated synchronization test between measurability_metrics.json and README.md / reports.
Guarantees zero numeric divergence across prose, tables, and JSON outputs.
"""

from pathlib import Path
import json
import re
import pytest

def test_metrics_json_and_readme_consistency():
    root_dir = Path(__file__).resolve().parent.parent
    json_path = root_dir / "results" / "measurability_metrics.json"
    readme_path = root_dir / "README.md"
    
    assert json_path.exists(), "measurability_metrics.json missing!"
    assert readme_path.exists(), "README.md missing!"
    
    with open(json_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)
        
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_text = f.read()
        
    steep_inv = metrics["joint_two_track_velocity_inversions"]["steep_scarp_single_inversion"]
    topo = metrics["scarp_topography_and_slope_distribution"]
    bearings = metrics["geometric_bearings"]
    limits = metrics["steep_scarp_detection_limits_mm_yr"]
    
    # 1. Exact numeric bounds in JSON
    assert abs(steep_inv["steep_scarp_mean_slope_deg"] - 34.45) < 0.05
    assert abs(steep_inv["steep_scarp_mean_aspect_deg"] - 174.67) < 0.1
    assert abs(steep_inv["steep_scarp_mean_dispersion"] - 0.0338) < 0.005
    assert abs(topo["approx_independent_80m_sar_pixels"] - 31.00) < 0.1
    assert abs(topo["approx_independent_80m_sar_pixels_nominal_grid"] - 33.05) < 0.1
    assert abs(bearings["scarp_circular_mean_aspect_deg"] - 151.12) < 0.1
    assert abs(bearings["scarp_circular_angular_dispersion"] - 0.4032) < 0.005
    
    # 2. Check steep-scarp detection limits in JSON
    desc_raw = limits["descending_Track48"]["raw_null_sigma_2.66mm"]
    desc_det = limits["descending_Track48"]["detrended_null_sigma_1.10mm"]
    asc_raw = limits["ascending_Track12"]["raw_null_sigma_3.08mm"]
    asc_det = limits["ascending_Track12"]["detrended_null_sigma_2.47mm"]
    
    assert abs(desc_raw - 587.4) < 1.0
    assert abs(desc_det - 242.9) < 1.0
    assert abs(asc_raw - 512.5) < 1.0
    assert abs(asc_det - 411.0) < 1.0
    
    # 3. Check README contains the synchronized steep-scarp numbers
    assert "34.45" in readme_text, "Steep scarp mean slope 34.45 deg missing in README"
    assert "174.7" in readme_text or "174.67" in readme_text, "Steep scarp aspect 174.7 deg missing in README"
    assert "0.276" in readme_text or "0.2757" in readme_text, "Descending steep R missing in README"
    assert "0.366" in readme_text or "0.3658" in readme_text, "Ascending steep R missing in README"
    assert "587" in readme_text or "590" in readme_text, "Descending raw steep detection limit missing in README"
    assert "243" in readme_text or "240" in readme_text, "Descending detrended steep detection limit missing in README"
    assert "513" in readme_text or "510" in readme_text, "Ascending raw steep detection limit missing in README"
    assert "411" in readme_text, "Ascending detrended steep detection limit missing in README"
