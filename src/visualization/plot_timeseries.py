"""
Publication-ready plotting for InSAR displacement time series and pre-event anomaly detection.
"""

from typing import Optional
from pathlib import Path
import pandas as pd
import numpy as np

def plot_hindcast_timeseries(
    df: pd.DataFrame,
    event_date: pd.Timestamp = pd.Timestamp("2023-10-04"),
    burn_in_end: pd.Timestamp = pd.Timestamp("2020-12-31"),
    alarm_date: Optional[pd.Timestamp] = None,
    output_path: Optional[Path] = None,
    title: str = "South Lhonak Moraine Displacement Hindcast (Sentinel-1 C-band)"
):
    """
    Plots LOS displacement time series with burn-in window, event line, and alarm trigger.
    """
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    
    # Plot observations
    ax.scatter(df["date"], df["disp"], color="#1f77b4", s=18, alpha=0.7, label="InSAR LOS Displacement (mm)")
    
    # Detrended or smoothed trend if present
    if "trend" in df.columns:
        ax.plot(df["date"], df["trend"], color="#1f77b4", linewidth=1.5, linestyle="--", label="Fitted Velocity")
        
    # Burn-in window shading
    ax.axvspan(df["date"].min(), burn_in_end, color="gray", alpha=0.15, label="Burn-in Period (Baseline)")
    
    # Failure event vertical line
    ax.axvline(event_date, color="#d62728", linestyle="--", linewidth=2.0, label="GLOF Event (04 Oct 2023)")
    
    # Detection alarm date
    if alarm_date:
        ax.axvline(alarm_date, color="#ff7f0e", linestyle="-.", linewidth=2.0, label=f"First Alarm ({alarm_date.strftime('%Y-%m-%d')})")
        
    ax.set_xlabel("Date", fontsize=11, fontweight="bold")
    ax.set_ylabel("LOS Displacement (mm)", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=12, pad=12, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="lower left", framealpha=0.9)
    
    plt.tight_layout()
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()
    else:
        return fig
