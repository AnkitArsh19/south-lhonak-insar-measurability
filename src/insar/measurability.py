"""
InSAR Measurability Atlas Engine.
Calculates geometric visibility (layover/shadow), sensitivity (R-index), and temporal observability.
"""

from typing import Dict, Any, Tuple
import numpy as np

def compute_r_index(
    incidence_angle_rad: np.ndarray,
    azimuth_angle_rad: np.ndarray,
    slope_rad: np.ndarray,
    aspect_rad: np.ndarray
) -> np.ndarray:
    """
    Computes R-index (geometric sensitivity ratio) for radar imaging.
    R-index relates true ground displacement along slope to LOS displacement.
    R = sin(theta - alpha_app) where alpha_app is the apparent slope in range direction.
    
    When |R| < 0.15, SAR has negligible sensitivity to slope movement.
    """
    alpha_app = np.arctan(np.tan(slope_rad) * np.sin(aspect_rad - azimuth_angle_rad))
    r = np.sin(incidence_angle_rad - alpha_app)
    return r

def classify_measurability(
    is_layover_shadow: np.ndarray,
    mean_coherence: np.ndarray,
    r_index: np.ndarray,
    min_coherence: float = 0.35,
    min_sensitivity: float = 0.20
) -> np.ndarray:
    """
    Classifies terrain into 4 objective InSAR Measurability classes:
    Class 0: Blind (Layover or Shadow)
    Class 1: Low Sensitivity (|R-index| < min_sensitivity)
    Class 2: Decorrelated (Persistent mean coherence < min_coherence)
    Class 3: Fully Measurable (Favorable geometry + sustained coherence)
    """
    measurability = np.full(mean_coherence.shape, 3, dtype=np.int8)
    
    # Decorrelated
    measurability[mean_coherence < min_coherence] = 2
    # Low sensitivity
    measurability[np.abs(r_index) < min_sensitivity] = 1
    # Blind
    measurability[is_layover_shadow] = 0
    
    return measurability
