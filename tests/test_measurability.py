"""
Unit tests for Sentinel-1 InSAR Observability and Geometric Sensitivity
Validates slope, aspect, local incidence angle, downslope unit vectors,
sensitivity R = |d_downslope . s_LOS|, 2D raster grid gradient pipeline,
and scarp aspect alignment with nearest lake shore and frontal dam breach.
"""

import numpy as np
import pytest
from pathlib import Path
import json
from PIL import Image
from shapely.geometry import shape, Point
from shapely.ops import nearest_points

def compute_geometry_and_R(dz_dx, dz_dy, lv_phi, lv_theta):
    """
    Computes downslope vector, look vector, sensitivity R, and local incidence angle.
    Convention:
      - dz_dx = dz/dx (East), dz_dy = dz/dy (North)
      - lv_phi: look vector orientation angle (East=0, North=pi/2, South=-pi/2)
      - lv_theta: look vector elevation angle above horizontal (rad)
    """
    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    norm_g = np.sqrt(dz_dx**2 + dz_dy**2)
    
    # Downslope unit vector d (steepest descent)
    if norm_g > 1e-7:
        d_x = - (dz_dx / norm_g) * np.cos(slope_rad)
        d_y = - (dz_dy / norm_g) * np.cos(slope_rad)
        d_z = - np.sin(slope_rad)
    else:
        d_x, d_y, d_z = 0.0, 0.0, -1.0
        
    d = np.array([d_x, d_y, d_z])
    
    # Look vector from ground to satellite s
    s_x = np.cos(lv_theta) * np.cos(lv_phi)
    s_y = np.cos(lv_theta) * np.sin(lv_phi)
    s_z = np.sin(lv_theta)
    s = np.array([s_x, s_y, s_z])
    
    # Sensitivity R = |d . s|
    R = float(abs(np.dot(d, s)))
    
    # Surface normal vector n (pointing up)
    denom = np.sqrt(1.0 + dz_dx**2 + dz_dy**2)
    n = np.array([-dz_dx / denom, -dz_dy / denom, 1.0 / denom])
    cos_inc = float(np.dot(n, s))
    inc_deg = float(np.rad2deg(np.arccos(np.clip(cos_inc, -1.0, 1.0))))
    
    return {
        "slope_deg": float(np.rad2deg(slope_rad)),
        "d_vec": d,
        "s_vec": s,
        "R": R,
        "cos_inc": cos_inc,
        "inc_deg": inc_deg
    }

def test_synthetic_east_facing_slope():
    """
    Analytical Test Case 1: 30 deg East-facing slope.
    Elevation drops towards East: dz/dx = -tan(30 deg), dz/dy = 0.
    1. Ascending sensor looking East (satellite to the West, phi = pi, theta = 45 deg):
       d = (cos(30), 0, -sin(30)) = (sqrt(3)/2, 0, -1/2)
       s = (-cos(45), 0, sin(45)) = (-1/sqrt(2), 0, 1/sqrt(2))
       R = 0.96593
    2. Descending sensor looking West (satellite to the East, phi = 0, theta = 45 deg):
       s = (cos(45), 0, sin(45)) = (1/sqrt(2), 0, 1/sqrt(2))
       R = 0.25882
    """
    dz_dx = - np.tan(np.deg2rad(30.0))
    dz_dy = 0.0
    theta = np.deg2rad(45.0)
    
    res_asc = compute_geometry_and_R(dz_dx, dz_dy, lv_phi=np.pi, lv_theta=theta)
    assert np.isclose(res_asc["slope_deg"], 30.0, atol=1e-4)
    assert np.isclose(res_asc["R"], 0.96593, atol=1e-4)
    
    res_desc = compute_geometry_and_R(dz_dx, dz_dy, lv_phi=0.0, lv_theta=theta)
    assert np.isclose(res_desc["R"], 0.25882, atol=1e-4)
    assert res_asc["R"] > 3.5 * res_desc["R"]

def test_synthetic_west_facing_slope():
    """
    Analytical Test Case 2: 30 deg West-facing slope.
    Elevation drops towards West: dz/dx = tan(30 deg), dz/dy = 0.
    Mirror of Case 1: Descending has high R, Ascending has low R.
    """
    dz_dx = np.tan(np.deg2rad(30.0))
    dz_dy = 0.0
    theta = np.deg2rad(45.0)
    
    res_asc = compute_geometry_and_R(dz_dx, dz_dy, lv_phi=np.pi, lv_theta=theta)
    assert np.isclose(res_asc["R"], 0.25882, atol=1e-4)
    
    res_desc = compute_geometry_and_R(dz_dx, dz_dy, lv_phi=0.0, lv_theta=theta)
    assert np.isclose(res_desc["R"], 0.96593, atol=1e-4)
    assert res_desc["R"] > 3.5 * res_asc["R"]

def test_horizontal_plane():
    """Horizontal plane (zero slope): sensitivity equals sin(theta)."""
    res = compute_geometry_and_R(0.0, 0.0, lv_phi=0.0, lv_theta=np.deg2rad(45.0))
    assert np.isclose(res["slope_deg"], 0.0, atol=1e-4)
    assert np.isclose(res["R"], np.sin(np.deg2rad(45.0)), atol=1e-4)
    assert np.isclose(res["inc_deg"], 45.0, atol=1e-4)

def test_r_index_bounded():
    """R must always lie within [0.0, 1.0]."""
    for dz_dx in [-5.0, -1.0, 0.0, 1.0, 5.0]:
        for dz_dy in [-5.0, -1.0, 0.0, 1.0, 5.0]:
            for phi in [-np.pi, -np.pi/2, 0.0, np.pi/2, np.pi]:
                for theta in [np.deg2rad(30.0), np.deg2rad(45.0), np.deg2rad(60.0)]:
                    res = compute_geometry_and_R(dz_dx, dz_dy, phi, theta)
                    assert 0.0 <= res["R"] <= 1.0 + 1e-6, f"R={res['R']} outside [0, 1]!"

def test_raster_pipeline_synthetic_ne_rising_grid():
    """
    2D Raster Pipeline Test:
    A synthetic 2D DEM grid rising toward the North-East.
    Grid convention:
      - Rows increase Southward (axis 0, spacing dy > 0)
      - Cols increase Eastward (axis 1, spacing dx > 0)
    Topographic slope = 35 deg.
    Because the elevation rises toward the NE, the downslope vector points toward the SW (225 deg).
    """
    dx = 30.0
    dy = 30.0
    rows, cols = np.meshgrid(np.arange(12), np.arange(12), indexing="ij")
    
    slope_target = np.tan(np.deg2rad(35.0))
    dem_ne_rising = (11.0 - rows) * dy * (slope_target / np.sqrt(2.0)) + cols * dx * (slope_target / np.sqrt(2.0))
    
    dz_drow, dz_dcol = np.gradient(dem_ne_rising, dy, dx)
    p = dz_dcol
    q = - dz_drow
    
    slope_deg = np.rad2deg(np.arctan(np.sqrt(p**2 + q**2)))
    aspect_deg = (np.rad2deg(np.arctan2(-p, -q))) % 360.0
    
    interior_slope = slope_deg[2:-2, 2:-2]
    interior_aspect = aspect_deg[2:-2, 2:-2]
    
    assert np.allclose(interior_slope, 35.0, atol=1e-3), f"Expected slope 35 deg, got {np.mean(interior_slope)}"
    assert np.allclose(interior_aspect, 225.0, atol=1e-3), f"Expected aspect 225 deg (SW), got {np.mean(interior_aspect)}"

def test_scarp_aspect_points_toward_lake_and_breach():
    """
    Verifies that the moraine scarp circular mean aspect computed on the native 30 m GLO-30 DEM
    physically points toward the nearest southern lake shore (177.3 deg) and frontal breach (142.2 deg).
    Explicit tolerance: circular mean aspect must be within 30 deg of both nearest shore and breach.
    """
    glo30_path = Path("e:/Personal/iirs/data/dem/Copernicus_DSM_COG_10_N27_00_E088_00_DEM.tif")
    assert glo30_path.exists(), "Copernicus GLO-30 DEM missing!"
    
    im_dem = Image.open(glo30_path)
    arr_dem = np.array(im_dem)
    
    with open("e:/Personal/iirs/data/vector/south_lhonak_aoi.geojson", "r", encoding="utf-8") as f:
        gj = json.load(f)
    feats = {feat["properties"]["id"]: shape(feat["geometry"]) for feat in gj["features"]}
    scarp = feats["LATERAL-MORAINE-SCARP"]
    lake = feats["LAKE-PRE"]
    breach = feats["FRONTAL-DAM-BREACH"]
    
    scarp_cent = scarp.centroid
    nearest_shore_pt = nearest_points(scarp_cent, lake)[1]
    
    bearing_nearest_shore = (90.0 - np.rad2deg(np.arctan2(nearest_shore_pt.y - scarp_cent.y, nearest_shore_pt.x - scarp_cent.x))) % 360.0
    bearing_breach = (90.0 - np.rad2deg(np.arctan2(breach.centroid.y - scarp_cent.y, breach.centroid.x - scarp_cent.x))) % 360.0
    
    # Assert bearing bounds
    assert 170.0 <= bearing_nearest_shore <= 185.0, f"Bearing to nearest shore {bearing_nearest_shore:.1f} out of range"
    assert 135.0 <= bearing_breach <= 150.0, f"Bearing to breach {bearing_breach:.1f} out of range"
    
    # Crop DEM around scarp
    x0, y0 = 88.0, 28.0
    d_deg = 1.0 / 3600.0
    minx, miny, maxx, maxy = scarp.bounds
    margin = 0.005
    c_min = int((minx - margin - x0) / d_deg)
    c_max = int((maxx + margin - x0) / d_deg) + 1
    r_min = int((y0 - (maxy + margin)) / d_deg)
    r_max = int((y0 - (miny - margin)) / d_deg) + 1
    
    dem_sub = arr_dem[r_min:r_max, c_min:c_max].astype(float)
    lat_mid = (miny + maxy) / 2.0
    dx_m = d_deg * 111412.84 * np.cos(np.deg2rad(lat_mid))
    dy_m = d_deg * 111132.954
    
    dz_drow, dz_dcol = np.gradient(dem_sub, dy_m, dx_m)
    p = dz_dcol
    q = - dz_drow
    aspect_deg = (np.rad2deg(np.arctan2(-p, -q))) % 360.0
    
    scarp_mask = np.zeros(dem_sub.shape, dtype=bool)
    for r in range(dem_sub.shape[0]):
        lat = y0 - (r_min + r) * d_deg
        for c in range(dem_sub.shape[1]):
            lon = x0 + (c_min + c) * d_deg
            if scarp.contains(Point(lon, lat)):
                scarp_mask[r, c] = True
                
    aspect_scarp = aspect_deg[scarp_mask]
    sin_mean = float(np.mean(np.sin(np.deg2rad(aspect_scarp))))
    cos_mean = float(np.mean(np.cos(np.deg2rad(aspect_scarp))))
    circ_mean_aspect = float((np.rad2deg(np.arctan2(sin_mean, cos_mean))) % 360.0)
    
    # Check that circular mean aspect aligns within 30 deg of nearest shore and breach
    diff_shore = abs(circ_mean_aspect - bearing_nearest_shore)
    diff_breach = abs(circ_mean_aspect - bearing_breach)
    
    assert diff_shore <= 30.0, f"Scarp aspect {circ_mean_aspect:.1f} deg deviates >30 deg from nearest shore ({diff_shore:.1f} deg)"
    assert diff_breach <= 30.0, f"Scarp aspect {circ_mean_aspect:.1f} deg deviates >30 deg from frontal breach ({diff_breach:.1f} deg)"

def test_metrics_json_integrity():
    """Verify measurability_metrics.json exists and contains complete required keys and valid numbers."""
    json_path = Path("e:/Personal/iirs/results/measurability_metrics.json")
    assert json_path.exists(), "measurability_metrics.json missing!"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "geometric_bearings" in data
    assert "scarp_topography_and_slope_distribution" in data
    assert "scarp_signed_projections_and_distributions" in data
    assert "sensitivity_threshold_analysis" in data
    assert "observability_class_percentages_at_R_0_3" in data
    assert "non_circular_coherence_validation_by_local_incidence" in data
    assert "joint_two_track_velocity_inversions" in data
    
    # Assert Descending sign cancellation is recorded
    p_desc = data["scarp_signed_projections_and_distributions"]["descending_Track48"]
    assert p_desc["positive_pct"] > 30.0 and p_desc["negative_pct"] > 50.0
    
    # Assert Dual-sensitive subset fraction
    dual = data["joint_two_track_velocity_inversions"]["dual_sensitive_pixels_subset"]
    assert dual["scarp_fraction_pct"] > 60.0
    
    # Assert 95% CI contains zero in joint inversion
    lumped = data["joint_two_track_velocity_inversions"]["lumped_scarp_mean_inversion"]["raw_null_model"]
    assert lumped["ci95_low_mm_yr"] < 0.0 < lumped["ci95_high_mm_yr"]

if __name__ == "__main__":
    test_synthetic_east_facing_slope()
    test_synthetic_west_facing_slope()
    test_horizontal_plane()
    test_r_index_bounded()
    test_raster_pipeline_synthetic_ne_rising_grid()
    test_scarp_aspect_points_toward_lake_and_breach()
    test_metrics_json_integrity()
    print("\nALL 7 MEASURABILITY & OBSERVABILITY UNIT TESTS PASSED SUCCESSFULLY!")
