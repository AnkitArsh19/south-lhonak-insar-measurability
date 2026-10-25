"""
==============================================================================
FUTURE WORK / PHASE 4 STUB
This module is part of the future multi-temporal CUSUM early-warning framework.
It is excluded from the frozen single-pair measurability scope of Phase 1-2.
==============================================================================
Leave-future-out hindcast evaluation protocol runner.
"""

from typing import Dict, Any, List
from datetime import datetime
import numpy as np
from .detector import detect_cusum_anomaly
from .control_slopes import evaluate_control_slopes

def run_hindcast_evaluation(
    target_timeseries: Any,
    control_timeseries: Dict[str, Any],
    event_date: datetime = datetime(2023, 10, 4),
    burn_in_end: datetime = datetime(2020, 12, 31),
    threshold_sigma: float = 3.0
) -> Dict[str, Any]:
    """
    Executes the strict hindcast evaluation protocol:
    1. Evaluates target slope (South Lhonak lateral moraine)
    2. Evaluates control slopes
    3. Calculates early warning lead time before event_date
    """
    target_dates = target_timeseries["date"].tolist() if hasattr(target_timeseries["date"], "tolist") else list(target_timeseries["date"])
    target_disps = target_timeseries["disp"].values if hasattr(target_timeseries["disp"], "values") else np.asarray(target_timeseries["disp"])
    
    target_result = detect_cusum_anomaly(
        dates=target_dates,
        displacements_mm=target_disps,
        burn_in_end=burn_in_end,
        threshold_sigma=threshold_sigma
    )
    
    control_result = evaluate_control_slopes(
        control_timeseries=control_timeseries,
        burn_in_end=burn_in_end,
        threshold_sigma=threshold_sigma
    )
    
    lead_time_days = None
    if target_result["is_alarm_triggered"]:
        alarm_date = target_result["first_alarm_date"]
        lead_time_days = (event_date - alarm_date).days
        
    return {
        "event_date": str(event_date.date()) if hasattr(event_date, "date") else str(event_date),
        "target_detected": target_result["is_alarm_triggered"],
        "first_alarm_date": str(target_result["first_alarm_date"].date()) if (target_result["first_alarm_date"] and hasattr(target_result["first_alarm_date"], "date")) else str(target_result["first_alarm_date"]),
        "lead_time_days": lead_time_days,
        "control_false_alarm_rate": control_result["false_alarm_rate"],
        "control_false_alarm_count": control_result["false_alarm_count"],
        "is_valid_scientific_detection": target_result["is_alarm_triggered"] and (control_result["false_alarm_rate"] < 0.20)
    }
