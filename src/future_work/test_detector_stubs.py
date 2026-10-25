"""
Phase 4 Future Work Stubs - Detector Tests
Relocated outside active pytest suite until Phase 4 multi-temporal data acquisition.
"""

import numpy as np
from datetime import datetime, timedelta
from src.future_work.detector import detect_cusum_anomaly

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
