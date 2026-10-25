"""
Geospatial projection and geometry utilities.
"""

from typing import Tuple, List
import numpy as np

def compute_los_displacement(phase: np.ndarray, wavelength_m: float) -> np.ndarray:
    """
    Convert unwrapped interferometric phase (radians) to Line-Of-Sight (LOS) displacement (meters).
    
    Convention: Positive phase corresponds to motion towards the satellite (uplift/advance),
    Negative phase corresponds to motion away from the satellite (subsidence/slope retreat).
    Equation: d_LOS = -(lambda / (4 * pi)) * delta_phi
    
    Parameters:
        phase: Unwrapped phase in radians
        wavelength_m: Radar wavelength in meters (e.g. 0.0554657 m for Sentinel-1 C-band,
                      0.24 m for NISAR L-band)
    
    Returns:
        d_los in meters
    """
    return -(wavelength_m / (4.0 * np.pi)) * phase

def project_los_to_slope(
    d_los: np.ndarray,
    incidence_angle_deg: float,
    heading_angle_deg: float,
    slope_deg: float,
    aspect_deg: float
) -> np.ndarray:
    """
    Projects 1D LOS displacement along the direction of maximum slope gradient.
    
    Geometric Sensitivity Coefficient:
        C = -sin(theta) * sin(alpha) * cos(phi - psi) + cos(theta) * cos(alpha)
        where:
        theta = incidence angle
        phi = SAR azimuth / line of sight direction
        alpha = slope angle
        psi = slope aspect
    """
    theta = np.deg2rad(incidence_angle_deg)
    alpha = np.deg2rad(slope_deg)
    phi = np.deg2rad(heading_angle_deg - 90.0) # Radar look direction
    psi = np.deg2rad(aspect_deg)
    
    c = -np.sin(theta) * np.sin(alpha) * np.cos(phi - psi) + np.cos(theta) * np.cos(alpha)
    
    # Avoid division by zero or near-zero sensitivity
    with np.errstate(divide='ignore', invalid='ignore'):
        d_slope = np.where(np.abs(c) > 0.15, d_los / c, np.nan)
        
    return d_slope
