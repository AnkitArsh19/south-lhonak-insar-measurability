"""
==============================================================================
FUTURE WORK / PHASE 4 STUB
This module is part of the future multi-temporal CUSUM early-warning framework.
It is excluded from the frozen single-pair measurability scope of Phase 1-2.
==============================================================================
Control slope evaluation and False Discovery Rate (FDR) accounting.
"""

from typing import Dict, Any, List
from datetime import datetime
import numpy as np
from .detector import detect_cusum_anomaly

def evaluate_control_slopes(
    control_timeseries: Dict[str, Any],
    burn_in_end: datetime,
    threshold_sigma: float = 3.0
) -> Dict[str, Any]:
    """
    Evaluates detector performance across known stable control slopes.
    Any alarm triggered on a stable control slope counts as a False Alarm.
    
    control_timeseries: Dict mapping slope_id -> dict with 'date' and 'disp'
    """
    results = {}
    total_controls = len(control_timeseries)
    false_alarms = 0
    
    for slope_id, data in control_timeseries.items():
        dates = data["date"].tolist() if hasattr(data["date"], "tolist") else list(data["date"])
        disps = data["disp"].values if hasattr(data["disp"], "values") else np.asarray(data["disp"])
        
        det_result = detect_cusum_anomaly(
            dates=dates,
            displacements_mm=disps,
            burn_in_end=burn_in_end,
            threshold_sigma=threshold_sigma
        )
        is_false_alarm = det_result["is_alarm_triggered"]
        if is_false_alarm:
            false_alarms += 1
            
        results[slope_id] = {
            "false_alarm": is_false_alarm,
            "alarm_date": det_result["first_alarm_date"],
            "baseline_sigma": det_result["baseline_sigma_mm"]
        }
        
    false_alarm_rate = false_alarms / total_controls if total_controls > 0 else 0.0
    
    return {
        "total_controls_tested": total_controls,
        "false_alarm_count": false_alarms,
        "false_alarm_rate": false_alarm_rate,
        "per_control_details": results
    }
