"""
Pytest configuration and synthetic fixtures for scientific validation tests.
"""

import pytest
import numpy as np

@pytest.fixture
def synthetic_flat_dem():
    """Generates a synthetic flat DEM raster for testing."""
    return np.full((10, 10), 5200.0, dtype=float)
