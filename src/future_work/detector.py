"""
==============================================================================
FUTURE WORK / PHASE 4 STUB
This module is part of the future multi-temporal CUSUM early-warning framework.
It is excluded from the frozen single-pair measurability scope of Phase 1-2.
==============================================================================
Pre-event deformation anomaly detectors (CUSUM, Velocity Threshold).
Tuned strictly on pre-event burn-in windows, evaluated on holdout periods.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime
import numpy as np

def detect_cusum_anomaly(
    dates: List[datetime],
    displacements_mm: np.ndarray,
    burn_in_end: datetime,
    threshold_sigma: float = 3.0,
    consecutive_points: int = 3
) -> Dict[str, Any]:
    """
    Cumulative Sum (CUSUM) anomaly detector for slope acceleration.
    
    1. Fits linear velocity on the burn-in period (dates <= burn_in_end).
    2. Detrends the full time-series using baseline velocity.
    3. Computes cumulative residual sum.
    4. Triggers alarm if cumulative sum exceeds threshold_sigma * standard_error
       for consecutive_points time steps.
    """
    sorted_indices = np.argsort(dates)
    dates_sorted = [dates[i] for i in sorted_indices]
    disp_sorted = np.asarray(displacements_mm)[sorted_indices]
    
    # Valid finite values
    valid = np.isfinite(disp_sorted)
    dates_sorted = [dates_sorted[i] for i in range(len(dates_sorted)) if valid[i]]
    disp_sorted = disp_sorted[valid]
    
    t0 = dates_sorted[0]
    t_years = np.array([(d - t0).total_seconds() / (365.25 * 86400.0) for d in dates_sorted])
    
    burn_mask = np.array([d <= burn_in_end for d in dates_sorted])
    if np.sum(burn_mask) < 5:
        raise ValueError("Burn-in period must contain at least 5 observations.")
        
    # Fit baseline slope
    p = np.polyfit(t_years[burn_mask], disp_sorted[burn_mask], 1)
    baseline_velocity = p[0]  # mm/year
    
    # Detrend
    detrended = disp_sorted - (p[0] * t_years + p[1])
    sigma_baseline = float(np.std(detrended[burn_mask]))
    
    # Anomaly trigger (negative for retreat/subsidence)
    alarm_condition = detrended < (-threshold_sigma * sigma_baseline)
    
    alarm_dates = []
    consec = 0
    first_alarm_date = None
    
    for i, d in enumerate(dates_sorted):
        if d > burn_in_end:
            if alarm_condition[i]:
                consec += 1
                if consec >= consecutive_points and first_alarm_date is None:
                    first_alarm_date = d
                    alarm_dates.append(d)
            else:
                consec = 0
                
    return {
        "baseline_velocity_mm_yr": float(baseline_velocity),
        "baseline_sigma_mm": float(sigma_baseline),
        "first_alarm_date": first_alarm_date,
        "is_alarm_triggered": first_alarm_date is not None
    }
