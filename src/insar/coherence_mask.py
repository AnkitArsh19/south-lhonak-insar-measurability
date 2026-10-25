"""
Coherence masking, decorrelation analysis, and spatial filtering.
"""

from typing import Tuple, Optional
import numpy as np

def create_coherence_mask(
    coherence: np.ndarray,
    threshold: float = 0.35,
    min_connected_pixels: int = 20
) -> np.ndarray:
    """
    Creates a binary mask where interferometric coherence meets reliability criteria.
    Below threshold (decorrelated), phase unwrapping errors dominate.
    
    Parameters:
        coherence: 2D array of temporal or spatial coherence values [0.0, 1.0]
        threshold: Minimum acceptable coherence (typically 0.3-0.4 for C-band SBAS)
        min_connected_pixels: Minimum island size to retain
    """
    valid = (coherence >= threshold) & np.isfinite(coherence)
    
    if min_connected_pixels > 1:
        try:
            from scipy.ndimage import label
            labeled, num_features = label(valid)
            sizes = np.bincount(labeled.ravel())
            mask_sizes = sizes >= min_connected_pixels
            mask_sizes[0] = 0 # background
            valid = mask_sizes[labeled]
        except ImportError:
            pass # fallback to simple threshold
            
    return valid.astype(bool)

def compute_temporal_coherence_loss(
    coherence_stack: np.ndarray,
    dates: list,
    monsoon_months: Tuple[int, ...] = (6, 7, 8, 9)
) -> dict:
    """
    Quantifies the fraction of spatial pixels lost during monsoon / wet-snow seasons.
    Crucial for proving that lack of InSAR signal does not equal slope stability.
    """
    import pandas as pd
    dt = pd.to_datetime(dates)
    is_monsoon = dt.month.isin(monsoon_months)
    
    monsoon_coherence = coherence_stack[is_monsoon, :, :]
    non_monsoon_coherence = coherence_stack[~is_monsoon, :, :]
    
    return {
        "mean_monsoon_coherence": float(np.nanmean(monsoon_coherence)),
        "mean_dry_coherence": float(np.nanmean(non_monsoon_coherence)),
        "monsoon_pixel_loss_percent": float(np.mean(np.nanmean(monsoon_coherence, axis=0) < 0.3) * 100.0)
    }
