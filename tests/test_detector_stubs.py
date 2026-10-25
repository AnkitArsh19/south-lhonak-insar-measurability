"""
Detector invariant test stubs preserved from Phase 1 baseline.
These tests verify CUSUM anomaly detector stubs when moving to Phase 4
(multi-temporal anomaly detection and Regional Hindcasting).
Marked as skipped in active Phase 2 suite.
"""

from datetime import datetime, timedelta
import sys
from pathlib import Path
import numpy as np
import pytest

# Ensure project root is in sys.path for IDE linter and test runners
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.future_work.detector import detect_cusum_anomaly  # type: ignore
except ImportError:
    from iirs.src.future_work.detector import detect_cusum_anomaly  # type: ignore

@pytest.mark.skip(reason="Phase 4 anomaly detector stub; preserved for CUSUM implementation")
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

@pytest.mark.skip(reason="Phase 4 anomaly detector stub; preserved for CUSUM implementation")
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
            
    # Call detect_cusum_anomaly (stub imported at module level)
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
