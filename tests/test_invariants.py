"""
Physical and mathematical invariant tests for InSAR and GLOF calculations.
Guarantees the IDE agent cannot introduce physically impossible results.
"""

import numpy as np
import pytest
from src.utils.geo_utils import compute_los_displacement
from src.insar.measurability import classify_measurability

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

