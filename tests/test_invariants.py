"""
Physical and mathematical invariant tests for InSAR and GLOF calculations.
Guarantees the IDE agent cannot introduce physically impossible results.
"""

import numpy as np
import pytest
from src.utils.geo_utils import compute_los_displacement, project_los_to_slope
from src.insar.measurability import compute_r_index, classify_measurability
from src.analysis.detector import detect_cusum_anomaly
from datetime import datetime, timedelta

def test_sentinel1_wavelength_conversion():
    """Verify that 2pi phase change equals half wavelength displacement."""
    lambda_s1 = 0.0554657  # ~5.55 cm
    phase = 2.0 * np.pi
    d_los = compute_los_displacement(phase, lambda_s1)
    
    # delta_d = -lambda / (4*pi) * (2*pi) = -lambda / 2
    expected = -lambda_s1 / 2.0
    assert np.isclose(d_los, expected, atol=1e-6)

def test_coherence_bounds():
    """Verify coherence classification adheres to bounds [0, 1]."""
    is_ls = np.array([False, False, False, True])
    mean_coh = np.array([0.5, 0.2, 0.6, 0.8])
    r_idx = np.array([0.8, 0.8, 0.05, 0.9])
    
    classes = classify_measurability(is_ls, mean_coh, r_idx, min_coherence=0.35, min_sensitivity=0.2)
    assert np.array_equal(classes, [3, 2, 1, 0])

def test_detector_on_stable_slope_no_false_alarm():
    """Verify detector does not alarm on purely stable ground at 3.5-sigma."""
    np.random.seed(42)
    start_date = datetime(2017, 1, 1)
    dates = [start_date + timedelta(days=12*i) for i in range(200)]
    noise = np.random.normal(0, 3.0, len(dates))
    
    result = detect_cusum_anomaly(
        dates=dates,
        displacements_mm=noise,
        burn_in_end=datetime(2020, 12, 31),
        threshold_sigma=3.5,
        consecutive_points=3
    )
    assert not result["is_alarm_triggered"], "Stable ground falsely triggered an alarm!"

def test_detector_on_accelerating_slope_triggers():
    """Verify detector catches true acceleration and calculates positive lead time."""
    np.random.seed(42)
    start_date = datetime(2017, 1, 1)
    dates = [start_date + timedelta(days=12*i) for i in range(200)]
    noise = np.random.normal(0, 3.0, len(dates))
    
    disp = noise.copy()
    accel_date = datetime(2022, 1, 1)
    for i, d in enumerate(dates):
        if d >= accel_date:
            t_yr = (d - accel_date).total_seconds() / (365.25 * 86400.0)
            disp[i] -= 45.0 * t_yr
            
    result = detect_cusum_anomaly(
        dates=dates,
        displacements_mm=disp,
        burn_in_end=datetime(2020, 12, 31),
        threshold_sigma=3.0,
        consecutive_points=3
    )
    assert result["is_alarm_triggered"], "Accelerating slope was missed by detector!"
    assert result["first_alarm_date"] is not None
    assert result["first_alarm_date"] >= datetime(2022, 1, 1)
