"""
Sentinel-1 InSAR Observability & Measurability Engine for South Lhonak Lake (Phase 2 Final)
Evaluates topographic slope, aspect, local incidence angle, signed layover/shadow masks,
and radar geometric sensitivity R = |d_downslope . s_LOS| for both Track 12 (Ascending)
and Track 48 (Descending) using the native 30 m Copernicus GLO-30 DEM.

Methodological Highlights:
  - Correct gradient axis ordering: dz_drow, dz_dcol = np.gradient(dem, dy, dx); p = dz_dcol, q = -dz_drow
  - Full distributions (histograms & percentiles) of slope, aspect (circular mean), signed P_desc and P_asc
  - Signed layover detection: slope facing radar exceeds cot(theta_elev) along look azimuth
  - Local incidence angle threshold (theta_inc <= 70 deg) for Observable class
  - Non-circular validation: binned raw coherence vs local incidence angle
  - Per-pixel and dual-sensitive joint two-track velocity inversion with 95% confidence intervals
  - Threshold sensitivity analysis across R in {0.2, 0.3, 0.5}
  - Exact bearing comparisons: nearest lake shore (177.3 deg), frontal dam breach (142.2 deg), lake centroid (236.7 deg)
  - Explicit labeling: single 12-day pair detection limits, September 2023 snapshot

Outputs:
  - Quantitative JSON: results/measurability_metrics.json
  - Publication Figures:
      results/fig1_radar_geometry_and_sensitivity.png
      results/fig2_four_class_measurability_maps.png
      results/fig3_minimum_detectable_motion_and_plausibility.png
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import json
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import pyproj
from shapely.geometry import shape, Point
from shapely.ops import nearest_points
from scipy.ndimage import map_coordinates

ROOT = Path("e:/Personal/iirs")
SAR_DIR = ROOT / "data" / "sar"
DEM_DIR = ROOT / "data" / "dem"
OUT_DIR = ROOT / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Tracks and directories
p_desc = SAR_DIR / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4"
p_asc  = SAR_DIR / "S1AA_20230913T121407_20230925T121408_VVP012_INT80_G_weF_C8DE"
glo30_path = DEM_DIR / "Copernicus_DSM_COG_10_N27_00_E088_00_DEM.tif"

# Geodetic transformers
t_to_utm = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32645", always_xy=True)
t_to_wgs = pyproj.Transformer.from_crs("EPSG:32645", "EPSG:4326", always_xy=True)

# 1. Load Vector AOI and Feature Polygons
with open(ROOT / "data" / "vector" / "south_lhonak_aoi.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)
feats = {feat["properties"]["id"]: shape(feat["geometry"]) for feat in geojson_data["features"]}
scarp_poly = feats["LATERAL-MORAINE-SCARP"]
lake_pre_poly = feats["LAKE-PRE"]

# 2. Geometric Bearings from Scarp Centroid
scarp_cent = scarp_poly.centroid
nearest_lake_pt = nearest_points(scarp_cent, lake_pre_poly)[1]

bearing_to_nearest_shore = (90.0 - np.rad2deg(np.arctan2(nearest_lake_pt.y - scarp_cent.y, nearest_lake_pt.x - scarp_cent.x))) % 360.0
bearing_to_lake_centroid = (90.0 - np.rad2deg(np.arctan2(lake_pre_poly.centroid.y - scarp_cent.y, lake_pre_poly.centroid.x - scarp_cent.x))) % 360.0

print(f"Bearing from scarp centroid to nearest lake shore: {bearing_to_nearest_shore:.1f} deg")
print(f"Bearing from scarp centroid to lake centroid:     {bearing_to_lake_centroid:.1f} deg")

# 3. Load 30 m Copernicus GLO-30 DEM
im_dem30 = Image.open(glo30_path)
arr_dem30 = np.array(im_dem30)
x0_dem, y0_dem = 88.0, 28.0
d_deg = 1.0 / 3600.0  # 1 arcsecond (~30 m)

lon_min, lon_max = 88.16, 88.24
lat_min, lat_max = 27.88, 27.95
extent = [lon_min, lon_max, lat_min, lat_max]

c_min = int((lon_min - x0_dem) / d_deg)
c_max = int((lon_max - x0_dem) / d_deg)
r_min = int((y0_dem - lat_max) / d_deg)
r_max = int((y0_dem - lat_min) / d_deg)

dem_aoi = arr_dem30[r_min:r_max, c_min:c_max].astype(float)
H, W = dem_aoi.shape

lat_mid = (lat_min + lat_max) / 2.0
dx_m = d_deg * 111412.84 * np.cos(np.deg2rad(lat_mid))  # ~27.35 m
dy_m = d_deg * 111132.954                              # ~30.87 m

# 4. Topographic Gradients with Correct Axis Order
# Axis 0 (rows) increases southward: dy = dy_m
# Axis 1 (cols) increases eastward: dx = dx_m
dz_drow, dz_dcol = np.gradient(dem_aoi, dy_m, dx_m)
p = dz_dcol          # dz/dx (Eastward slope)
q = - dz_drow        # dz/dy (Northward slope)

slope_rad = np.arctan(np.sqrt(p**2 + q**2))
slope_deg = np.rad2deg(slope_rad)
norm_g = np.sqrt(p**2 + q**2)
valid_g = norm_g > 1e-6

aspect_compass = (np.rad2deg(np.arctan2(-p, -q))) % 360.0

# Downslope unit vector d (steepest descent)
d_x = np.zeros_like(p)
d_y = np.zeros_like(p)
d_z = - np.sin(slope_rad)
d_x[valid_g] = - (p[valid_g] / norm_g[valid_g]) * np.cos(slope_rad[valid_g])
d_y[valid_g] = - (q[valid_g] / norm_g[valid_g]) * np.cos(slope_rad[valid_g])

# Surface normal vector n (pointing up)
denom_n = np.sqrt(1.0 + p**2 + q**2)
nx = - p / denom_n
ny = - q / denom_n
nz = 1.0 / denom_n

# 5. Load & Resample SAR Geometry to 30 m Reference Grid
im_c_d = Image.open(p_desc / f"{p_desc.name}_corr.tif")
tp_d = im_c_d.tag_v2.get(33922)
sc_d = im_c_d.tag_v2.get(33550)
x0_d, y0_d = tp_d[3], tp_d[4]
res_xd, res_yd = sc_d[0], sc_d[1]

arr_c_d = np.array(im_c_d)
arr_u_d = np.array(Image.open(p_desc / f"{p_desc.name}_unw_phase.tif"))
arr_phi_d = np.array(Image.open(p_desc / f"{p_desc.name}_lv_phi.tif"))
arr_th_d  = np.array(Image.open(p_desc / f"{p_desc.name}_lv_theta.tif"))

im_c_a = Image.open(p_asc / f"{p_asc.name}_corr.tif")
tp_a = im_c_a.tag_v2.get(33922)
sc_a = im_c_a.tag_v2.get(33550)
x0_a, y0_a = tp_a[3], tp_a[4]
res_xa, res_ya = sc_a[0], sc_a[1]

arr_c_a = np.array(im_c_a)
arr_u_a = np.array(Image.open(p_asc / f"{p_asc.name}_unw_phase.tif"))
arr_phi_a = np.array(Image.open(p_asc / f"{p_asc.name}_lv_phi.tif"))
arr_th_a  = np.array(Image.open(p_asc / f"{p_asc.name}_lv_theta.tif"))

cols_grid = np.arange(c_min, c_max)
rows_grid = np.arange(r_min, r_max)
lons_2d = x0_dem + cols_grid * d_deg
lats_2d = y0_dem - rows_grid * d_deg
mesh_lon, mesh_lat = np.meshgrid(lons_2d, lats_2d)
mesh_x, mesh_y = t_to_utm.transform(mesh_lon, mesh_lat)

col_d = (mesh_x - x0_d) / res_xd
row_d = (y0_d - mesh_y) / res_yd
col_a = (mesh_x - x0_a) / res_xa
row_a = (y0_a - mesh_y) / res_ya

c_d = map_coordinates(arr_c_d, [row_d, col_d], order=1, mode='nearest')
c_a = map_coordinates(arr_c_a, [row_a, col_a], order=1, mode='nearest')
u_d = map_coordinates(arr_u_d, [row_d, col_d], order=0, mode='nearest')
u_a = map_coordinates(arr_u_a, [row_a, col_a], order=0, mode='nearest')
phi_d = map_coordinates(arr_phi_d, [row_d, col_d], order=1, mode='nearest')
th_d  = map_coordinates(arr_th_d,  [row_d, col_d], order=1, mode='nearest')
phi_a = map_coordinates(arr_phi_a, [row_a, col_a], order=1, mode='nearest')
th_a  = map_coordinates(arr_th_a,  [row_a, col_a], order=1, mode='nearest')

# 6. Look Vectors from Ground to Satellite
s_dx = np.cos(th_d) * np.cos(phi_d)
s_dy = np.cos(th_d) * np.sin(phi_d)
s_dz = np.sin(th_d)

s_ax = np.cos(th_a) * np.cos(phi_a)
s_ay = np.cos(th_a) * np.sin(phi_a)
s_az = np.sin(th_a)

# 7. Signed Projections and Geometric Sensitivity R
proj_desc = d_x * s_dx + d_y * s_dy + d_z * s_dz
proj_asc  = d_x * s_ax + d_y * s_ay + d_z * s_az
R_desc = np.abs(proj_desc)
R_asc  = np.abs(proj_asc)

cos_inc_desc = nx * s_dx + ny * s_dy + nz * s_dz
cos_inc_asc  = nx * s_ax + ny * s_ay + nz * s_az
inc_desc = np.rad2deg(np.arccos(np.clip(cos_inc_desc, -1.0, 1.0)))
inc_asc  = np.rad2deg(np.arccos(np.clip(cos_inc_asc, -1.0, 1.0)))

# 8. Signed Layover & Shadow (Blind Geometry)
slope_along_look_d = p * np.cos(phi_d) + q * np.sin(phi_d)
slope_along_look_a = p * np.cos(phi_a) + q * np.sin(phi_a)

layover_d = (-slope_along_look_d) >= (1.0 / np.tan(th_d))
layover_a = (-slope_along_look_a) >= (1.0 / np.tan(th_a))
shadow_d = (cos_inc_desc <= 0.087) | (inc_desc >= 85.0)
shadow_a = (cos_inc_asc  <= 0.087) | (inc_asc  >= 85.0)

blind_d = layover_d | shadow_d
blind_a = layover_a | shadow_a

# 9. Scarp Mask & Detailed Distribution Audits
scarp_mask = np.zeros((H, W), dtype=bool)
for r in range(H):
    lat = y0_dem - (r_min + r) * d_deg
    for c in range(W):
        lon = x0_dem + (c_min + c) * d_deg
        if scarp_poly.contains(Point(lon, lat)):
            scarp_mask[r, c] = True

n_scarp = int(np.sum(scarp_mask))
print(f"Scarp mask pixels on 30 m DEM: {n_scarp}")

slope_scarp = slope_deg[scarp_mask]
aspect_scarp = aspect_compass[scarp_mask]
P_desc_scarp = proj_desc[scarp_mask]
P_asc_scarp  = proj_asc[scarp_mask]
R_desc_scarp = R_desc[scarp_mask]
R_asc_scarp  = R_asc[scarp_mask]

# Circular mean and angular dispersion of scarp aspect
sin_mean = float(np.mean(np.sin(np.deg2rad(aspect_scarp))))
cos_mean = float(np.mean(np.cos(np.deg2rad(aspect_scarp))))
circ_mean_aspect = float((np.rad2deg(np.arctan2(sin_mean, cos_mean))) % 360.0)
circ_dispersion = float(1.0 - np.sqrt(sin_mean**2 + cos_mean**2))

# Slope binning over scarp
slope_bins_summary = {
    "0_15_deg_pct":  float(np.mean((slope_scarp >= 0)  & (slope_scarp < 15)) * 100.0),
    "15_25_deg_pct": float(np.mean((slope_scarp >= 15) & (slope_scarp < 25)) * 100.0),
    "25_35_deg_pct": float(np.mean((slope_scarp >= 25) & (slope_scarp < 35)) * 100.0),
    "35_45_deg_pct": float(np.mean((slope_scarp >= 35) & (slope_scarp < 45)) * 100.0),
}

# Percentiles function
def get_dist_stats(arr):
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "p05": float(np.percentile(arr, 5)),
        "p25": float(np.percentile(arr, 25)),
        "p75": float(np.percentile(arr, 75)),
        "p95": float(np.percentile(arr, 95))
    }

slope_dist = get_dist_stats(slope_scarp)
p_desc_dist = get_dist_stats(P_desc_scarp)
p_asc_dist  = get_dist_stats(P_asc_scarp)

p_desc_dist["positive_count"] = int(np.sum(P_desc_scarp > 0))
p_desc_dist["positive_pct"] = float(np.mean(P_desc_scarp > 0) * 100.0)
p_desc_dist["negative_count"] = int(np.sum(P_desc_scarp < 0))
p_desc_dist["negative_pct"] = float(np.mean(P_desc_scarp < 0) * 100.0)

p_asc_dist["positive_count"] = int(np.sum(P_asc_scarp > 0))
p_asc_dist["positive_pct"] = float(np.mean(P_asc_scarp > 0) * 100.0)
p_asc_dist["negative_count"] = int(np.sum(P_asc_scarp < 0))
p_asc_dist["negative_pct"] = float(np.mean(P_asc_scarp < 0) * 100.0)

# 10. Sensitivity Threshold Analysis for "Observable" Class across R in {0.2, 0.3, 0.5}
threshold_sensitivity = {}
for r_th in [0.2, 0.3, 0.5]:
    obs_d = (~blind_d) & (R_desc >= r_th) & (c_d >= 0.3) & (inc_desc <= 70.0)
    obs_a = (~blind_a) & (R_asc  >= r_th) & (c_a >= 0.3) & (inc_asc  <= 70.0)
    obs_comb = obs_d | obs_a
    threshold_sensitivity[f"R_ge_{r_th}"] = {
        "scarp": {
            "Descending_Observable_pct": float(np.mean(obs_d[scarp_mask]) * 100.0),
            "Ascending_Observable_pct":  float(np.mean(obs_a[scarp_mask]) * 100.0),
            "Combined_Observable_pct":   float(np.mean(obs_comb[scarp_mask]) * 100.0)
        },
        "entire_10km_aoi": {
            "Descending_Observable_pct": float(np.mean(obs_d) * 100.0),
            "Ascending_Observable_pct":  float(np.mean(obs_a) * 100.0),
            "Combined_Observable_pct":   float(np.mean(obs_comb) * 100.0)
        }
    }

# 11. Four-Class Terrain Categorization (at standard R >= 0.3 threshold)
# Classes: 1=Blind, 2=Low Sensitivity (or grazing inc > 70 deg), 3=Decorrelated, 4=Observable
def classify_raster(blind, R, corr, inc, r_thresh=0.3):
    cmap = np.zeros_like(R, dtype=int)
    cmap[blind] = 1
    
    low_sens = (~blind) & (R < r_thresh)
    cmap[low_sens] = 2
    
    decorr = (~blind) & (~low_sens) & (corr < 0.3)
    cmap[decorr] = 3
    
    obs = (~blind) & (R >= r_thresh) & (corr >= 0.3) & (inc <= 70.0)
    cmap[obs] = 4
    
    grazing = (~blind) & (cmap == 0)
    cmap[grazing] = 2
    return cmap

class_desc = classify_raster(blind_d, R_desc, c_d, inc_desc, 0.3)
class_asc  = classify_raster(blind_a, R_asc,  c_a, inc_asc,  0.3)

class_comb = np.zeros_like(class_desc)
for r in range(H):
    for c in range(W):
        cd = class_desc[r, c]
        ca = class_asc[r, c]
        if cd == 4 or ca == 4:
            class_comb[r, c] = 4
        elif cd == 2 or ca == 2:
            class_comb[r, c] = 2
        elif cd == 3 or ca == 3:
            class_comb[r, c] = 3
        else:
            class_comb[r, c] = 1

def get_class_stats(cmap, mask):
    vals = cmap[mask]
    n_tot = len(vals)
    return {
        "Observable_pct": float(np.sum(vals == 4) / n_tot * 100.0),
        "Low_Sensitivity_pct": float(np.sum(vals == 2) / n_tot * 100.0),
        "Decorrelated_pct": float(np.sum(vals == 3) / n_tot * 100.0),
        "Blind_pct": float(np.sum(vals == 1) / n_tot * 100.0)
    }

scarp_stats_desc = get_class_stats(class_desc, scarp_mask)
scarp_stats_asc  = get_class_stats(class_asc,  scarp_mask)
scarp_stats_comb = get_class_stats(class_comb, scarp_mask)

aoi_mask = np.ones((H, W), dtype=bool)
aoi_stats_desc = get_class_stats(class_desc, aoi_mask)
aoi_stats_asc  = get_class_stats(class_asc,  aoi_mask)
aoi_stats_comb = get_class_stats(class_comb, aoi_mask)

# 12. Non-Circular Coherence Validation by Local Incidence Angle
inc_bins = [
    ("0-30 deg", 0.0, 30.0),
    ("30-50 deg", 30.0, 50.0),
    ("50-70 deg", 50.0, 70.0),
    ("70-85 deg (Grazing)", 70.0, 85.0),
    (">85 deg (Shadow/Blind)", 85.0, 180.0)
]

non_circular_validation = {}
for name, inc_map, corr_map, unw_map in [
    ("Descending_Track48", inc_desc, c_d, u_d),
    ("Ascending_Track12", inc_asc, c_a, u_a)
]:
    non_circular_validation[name] = {}
    for b_label, b_min, b_max in inc_bins:
        sel = (inc_map >= b_min) & (inc_map < b_max)
        if np.sum(sel) > 0:
            c_vals = corr_map[sel]
            u_vals = unw_map[sel]
            unw_pct = float(np.mean(np.isfinite(u_vals) & (u_vals != 0)) * 100.0)
            non_circular_validation[name][b_label] = {
                "pixel_count": int(np.sum(sel)),
                "pixel_fraction_pct": float(np.mean(sel) * 100.0),
                "mean_coherence": float(np.mean(c_vals)),
                "median_coherence": float(np.median(c_vals)),
                "unwrapping_success_pct": unw_pct
            }

# 13. Minimum Detectable Slope Velocity Maps (Single 12-day Pair)
# Evaluated across AOI: v_min = 2*sigma / R * (365.25 / 12)
sigma_raw_desc, sigma_raw_asc = 2.66, 3.08
sigma_det_desc, sigma_det_asc = 1.10, 2.47
scale_yr = 365.25 / 12.0

v_min_desc_raw = np.full((H, W), np.nan)
v_min_desc_det = np.full((H, W), np.nan)
v_min_asc_raw  = np.full((H, W), np.nan)
v_min_asc_det  = np.full((H, W), np.nan)

obs_mask_d = (~blind_d) & (c_d >= 0.3) & (inc_desc <= 70.0) & (R_desc > 0.05)
obs_mask_a = (~blind_a) & (c_a >= 0.3) & (inc_asc  <= 70.0) & (R_asc  > 0.05)

v_min_desc_raw[obs_mask_d] = (2.0 * sigma_raw_desc / R_desc[obs_mask_d]) * scale_yr
v_min_desc_det[obs_mask_d] = (2.0 * sigma_det_desc / R_desc[obs_mask_d]) * scale_yr

v_min_asc_raw[obs_mask_a] = (2.0 * sigma_raw_asc / R_asc[obs_mask_a]) * scale_yr
v_min_asc_det[obs_mask_a] = (2.0 * sigma_det_asc / R_asc[obs_mask_a]) * scale_yr

# Combined Best Minimum Detectable Velocity (Detrended Model)
v_min_comb_det = np.fmin(
    np.where(np.isnan(v_min_desc_det), np.inf, v_min_desc_det),
    np.where(np.isnan(v_min_asc_det),  np.inf, v_min_asc_det)
)
v_min_comb_det[np.isinf(v_min_comb_det)] = np.nan

# 14. Joint Two-Track Velocity Inversion on Steep Scarp (slope >= 25 deg)
# The full scarp analysis box (523 pixels) contains both the steep active flank and a flat moraine
# bench (< 15 deg, 39.8% of pixels) where the downslope direction is ill-defined and Descending projections
# cancel out. Masking to slopes >= 25 deg isolates the true steep moraine scarp face (235 pixels,
# equivalent to ~31-33 independent 80 m SAR resolution cells), with mean slope 32.8 deg and aspect 146.8 deg.

steep_scarp_mask = scarp_mask & (slope_deg >= 25.0)
n_steep = int(np.sum(steep_scarp_mask))
approx_sar_pixels = float((n_steep * 30.0 * 30.0) / (80.0 * 80.0))

# Sample LOS displacements from unwrapped phase (d_los = -lambda / (4*pi) * unw_phase * 1000 in mm)
lambda_s1 = 0.055465763
los_d_all = - (lambda_s1 / (4.0 * np.pi)) * u_d * 1000.0
los_a_all = - (lambda_s1 / (4.0 * np.pi)) * u_a * 1000.0

mean_los_desc_steep = float(np.mean(los_d_all[steep_scarp_mask]))
mean_los_asc_steep  = float(np.mean(los_a_all[steep_scarp_mask]))

# Stable Bedrock References from Phase 1 empirical spatial noise analysis:
# 1. Bedrock Ensemble Mean (30 stable bedrock patches around AOI):
#    Descending Track 48: -9.968 mm
#    Ascending Track 12:   -35.056 mm
# 2. CTRL-01 Single Bedrock Patch (27.907 deg N, 88.237 deg E, 5145 m):
#    Descending Track 48: -9.109 mm
#    Ascending Track 12:   -35.390 mm
ref_ens_desc, ref_ens_asc = -9.968, -35.056
ref_ctrl_desc, ref_ctrl_asc = -9.109, -35.390

# Differential LOS offsets (positive = range shortening / movement towards sensor)
y_desc_ens = mean_los_desc_steep - ref_ens_desc
y_asc_ens  = mean_los_asc_steep - ref_ens_asc

y_desc_ctrl = mean_los_desc_steep - ref_ctrl_desc
y_asc_ctrl  = mean_los_asc_steep - ref_ctrl_asc

# Steep scarp polygon-mean signed projections P = d · s
P_desc_steep = float(np.mean(proj_desc[steep_scarp_mask]))
P_asc_steep  = float(np.mean(proj_asc[steep_scarp_mask]))

print(f"Steep scarp (slope >= 25 deg): {n_steep} pixels ({n_steep/n_scarp*100.0:.1f}%), ~{approx_sar_pixels:.1f} SAR cells")
print(f"Mean signed P: Desc = {P_desc_steep:.4f}, Asc = {P_asc_steep:.4f}")
print(f"Offsets vs Ensemble: Desc = {y_desc_ens:+.3f} mm, Asc = {y_asc_ens:+.3f} mm")
print(f"Offsets vs CTRL-01:  Desc = {y_desc_ctrl:+.3f} mm, Asc = {y_asc_ctrl:+.3f} mm")

def solve_joint_inversion(p1, p2, y1, y2, s1, s2):
    w1, w2 = 1.0 / (s1**2), 1.0 / (s2**2)
    denom = (p1**2) * w1 + (p2**2) * w2
    num = (p1 * y1 * w1) + (p2 * y2 * w2)
    v = (num / denom) * scale_yr
    sig = (1.0 / np.sqrt(denom)) * scale_yr
    ci_low = float(v - 1.96 * sig)
    ci_high = float(v + 1.96 * sig)
    return {
        "velocity_mm_yr": float(v),
        "sigma_mm_yr": float(sig),
        "ci95_low_mm_yr": ci_low,
        "ci95_high_mm_yr": ci_high,
        "upper_bound_downslope_creep_mm_yr": float(max(0.0, ci_high)),
        "contains_zero": bool(ci_low <= 0.0 <= ci_high),
        "z_score": float(abs(v) / sig)
    }

# Compute joint inversion for both reference frames under both spatial noise null models
inv_ens_raw  = solve_joint_inversion(P_desc_steep, P_asc_steep, y_desc_ens, y_asc_ens, sigma_raw_desc, sigma_raw_asc)
inv_ens_det  = solve_joint_inversion(P_desc_steep, P_asc_steep, y_desc_ens, y_asc_ens, sigma_det_desc, sigma_det_asc)
inv_ctrl_raw = solve_joint_inversion(P_desc_steep, P_asc_steep, y_desc_ctrl, y_asc_ctrl, sigma_raw_desc, sigma_raw_asc)
inv_ctrl_det = solve_joint_inversion(P_desc_steep, P_asc_steep, y_desc_ctrl, y_asc_ctrl, sigma_det_desc, sigma_det_asc)

# 15. Save Comprehensive JSON Metrics
measurability_results = {
    "project": "Observability & Measurability of Sentinel-1 InSAR for Slope Monitoring Around South Lhonak Lake",
    "dem_source": "Copernicus GLO-30 Digital Elevation Model (30 m native resolution, 1 arcsecond)",
    "temporal_scope": "September 2023 snapshot (single 12-day pairs; monsoon peak and winter snowpack coherence unconstrained)",
    "geometric_bearings": {
        "scarp_centroid_lon_lat": [float(scarp_cent.x), float(scarp_cent.y)],
        "bearing_to_nearest_lake_shore_deg": float(bearing_to_nearest_shore),
        "bearing_to_lake_centroid_deg": float(bearing_to_lake_centroid),
        "scarp_circular_mean_aspect_deg": circ_mean_aspect,
        "scarp_circular_angular_dispersion": circ_dispersion,
        "aspect_shore_bearing_difference_deg": float(abs(circ_mean_aspect - bearing_to_nearest_shore)),
        "aspect_lake_centroid_difference_deg": float(abs(circ_mean_aspect - bearing_to_lake_centroid)),
        "morphological_interpretation": (
            "The failure scarp faces South-Southeast (circular mean aspect 151.1 deg, dispersion 0.05). "
            "This downslope vector faces the lake, aligning within 26.2 deg of the nearest southern lake shore "
            "(bearing 177.3 deg from the static 2020/21 lake mask). It differs from the bearing to the lake centroid "
            "(236.7 deg, WSW), because the elongated glacial lake extends westward toward the glacier snout."
        )
    },
    "scarp_topography_and_slope_distribution": {
        "pixel_count_30m": n_scarp,
        "steep_scarp_pixel_count_30m": n_steep,
        "steep_scarp_fraction_pct": float(n_steep / n_scarp * 100.0),
        "approx_independent_80m_sar_pixels": approx_sar_pixels,
        "elevation_mean_masl": float(np.mean(dem_aoi[scarp_mask])),
        "slope_distribution": slope_dist,
        "slope_bins": slope_bins_summary,
        "topographic_interpretation": (
            "The approximate analysis box (43.6 ha) contains both the steep active moraine flank (35-39 deg, "
            "comprising 28.5% of pixels) and the flatter moraine crest/bench (<15 deg, comprising 39.8% of pixels), "
            "yielding a polygon-wide mean slope of 21.8 deg. Restricting analysis to slopes >= 25 deg isolates "
            "the steep active scarp face (235 pixels, ~31-33 independent 80 m SAR pixels, mean slope 32.8 deg)."
        )
    },
    "scarp_signed_projections_and_distributions": {
        "descending_Track48": p_desc_dist,
        "ascending_Track12": p_asc_dist,
        "steep_scarp_mean_projections": {
            "descending_Track48": P_desc_steep,
            "ascending_Track12": P_asc_steep
        },
        "sign_cancellation_note": (
            "Descending Track 48 exhibits sign-cancelling projections across the full box (38.8% positive, 61.2% "
            "negative; mean P = -0.034, but mean |R| = 0.309) because the flat upper bench curves toward the sensor. "
            "Filtering to the steep scarp (slope >= 25 deg) resolves this ambiguity: mean P_desc becomes consistently "
            "negative (-0.2757) and P_asc remains negative (-0.3658), providing well-posed geometric sensitivity."
        )
    },
    "sensitivity_threshold_analysis": threshold_sensitivity,
    "observability_class_percentages_at_R_0_3": {
        "scarp_analysis_box": {
            "Descending_Track48": scarp_stats_desc,
            "Ascending_Track12": scarp_stats_asc,
            "Combined_Geometry": scarp_stats_comb
        },
        "entire_10km_aoi": {
            "Descending_Track48": aoi_stats_desc,
            "Ascending_Track12": aoi_stats_asc,
            "Combined_Geometry": aoi_stats_comb
        }
    },
    "non_circular_coherence_validation_by_local_incidence": non_circular_validation,
    "joint_two_track_velocity_inversions": {
        "steep_scarp_single_inversion": {
            "sample_size_30m_dem_pixels": n_steep,
            "approx_independent_80m_sar_pixels": approx_sar_pixels,
            "steep_scarp_mean_slope_deg": float(np.mean(slope_deg[steep_scarp_mask])),
            "steep_scarp_mean_aspect_deg": float(circ_mean_aspect),
            "steep_scarp_mean_P_desc": P_desc_steep,
            "steep_scarp_mean_P_asc": P_asc_steep,
            "relative_to_ensemble_reference": {
                "raw_null_model": inv_ens_raw,
                "detrended_null_model": inv_ens_det
            },
            "relative_to_ctrl01_reference": {
                "raw_null_model": inv_ctrl_raw,
                "detrended_null_model": inv_ctrl_det
            }
        },
        "scientific_conclusion": (
            "The steep-scarp joint inversion is model-dependent. Under the conservative raw spatial noise model, "
            "zero motion is contained in the 95% confidence interval (Ensemble: [-651, +106] mm/yr; CTRL-01: [-626, +131] mm/yr). "
            "Under the ramp-removed (detrended) null model, an apparent signal appears at ~3.7-sigma (Ensemble: -390 +/- 105 mm/yr; "
            "CTRL-01: -327 +/- 105 mm/yr). This apparent signal is directed upslope (v < 0), which is physically implausible as "
            "gravitational slope creep and is consistent with residual atmospheric phase delays or reference-pixel drift across "
            "steep alpine relief, but two pilot pairs cannot resolve this. Single pilot pairs cannot detect slope creep below "
            "roughly 0.2 to 0.5 m/yr, and the two pilot pairs constrain slope-parallel creep only to within a few tenths of a metre per year."
        )
    }
}

out_json = OUT_DIR / "measurability_metrics.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(measurability_results, f, indent=2)
print(f"Saved complete metrics JSON to: {out_json}")

# 16. Plot Figure 1: Radar Geometry, Sensitivity & Aspect Alignment
fig1, axs1 = plt.subplots(2, 2, figsize=(14, 12), dpi=150)
plt.subplots_adjust(wspace=0.2, hspace=0.25)

# 1a. Topographic Slope
im0 = axs1[0, 0].imshow(slope_deg, extent=extent, cmap="magma", vmin=0, vmax=50)
axs1[0, 0].set_title("(a) Topographic Slope (Copernicus GLO-30 DEM)", fontsize=11, fontweight="bold")
axs1[0, 0].set_xlabel("Longitude (deg E)")
axs1[0, 0].set_ylabel("Latitude (deg N)")
cb0 = fig1.colorbar(im0, ax=axs1[0, 0], fraction=0.046, pad=0.04)
cb0.set_label("Slope Angle (deg)", fontsize=9)

# 1b. Local Incidence Angle (Descending Track 48)
im1 = axs1[0, 1].imshow(inc_desc, extent=extent, cmap="viridis", vmin=0, vmax=90)
axs1[0, 1].set_title("(b) Descending Track 48: Local Incidence Angle", fontsize=11, fontweight="bold")
axs1[0, 1].set_xlabel("Longitude (deg E)")
axs1[0, 1].set_ylabel("Latitude (deg N)")
cb1 = fig1.colorbar(im1, ax=axs1[0, 1], fraction=0.046, pad=0.04)
cb1.set_label("Local Incidence (deg)", fontsize=9)

# 1c. Sensitivity Index R (Descending Track 48)
im2 = axs1[1, 0].imshow(R_desc, extent=extent, cmap="plasma", vmin=0.0, vmax=1.0)
axs1[1, 0].set_title(f"(c) Descending Track 48: Sensitivity R = |d · s| (Steep mean: {abs(P_desc_steep):.3f})", fontsize=11, fontweight="bold")
axs1[1, 0].set_xlabel("Longitude (deg E)")
axs1[1, 0].set_ylabel("Latitude (deg N)")
cb2 = fig1.colorbar(im2, ax=axs1[1, 0], fraction=0.046, pad=0.04)
cb2.set_label("Sensitivity Index R [0-1]", fontsize=9)

# 1d. Sensitivity Index R (Ascending Track 12)
im3 = axs1[1, 1].imshow(R_asc, extent=extent, cmap="plasma", vmin=0.0, vmax=1.0)
axs1[1, 1].set_title(f"(d) Ascending Track 12: Sensitivity R = |d · s| (Steep mean: {abs(P_asc_steep):.3f})", fontsize=11, fontweight="bold")
axs1[1, 1].set_xlabel("Longitude (deg E)")
axs1[1, 1].set_ylabel("Latitude (deg N)")
cb3 = fig1.colorbar(im3, ax=axs1[1, 1], fraction=0.046, pad=0.04)
cb3.set_label("Sensitivity Index R [0-1]", fontsize=9)

# Overlays: Scarp, Lake Shore
scarp_lons, scarp_lats = scarp_poly.exterior.xy
for ax in axs1.flat:
    ax.plot(scarp_lons, scarp_lats, color="cyan", linewidth=2.0, linestyle="--", label="Scarp Box")
    ax.plot(scarp_cent.x, scarp_cent.y, marker="o", color="cyan", markersize=5)
    ax.plot([scarp_cent.x, nearest_lake_pt.x], [scarp_cent.y, nearest_lake_pt.y], color="lime", linewidth=2.0, label="To Nearest Lake Shore (177°)")
    ax.legend(loc="upper right", fontsize=8.5)

fig1_path = OUT_DIR / "fig1_radar_geometry_and_sensitivity.png"
fig1.savefig(fig1_path, bbox_inches="tight")
plt.close(fig1)
print(f"Saved Figure 1 to: {fig1_path}")

# 17. Plot Figure 2: Four-Class Observability Maps & Minimum Detectable Velocity Map
fig2, axs2 = plt.subplots(1, 3, figsize=(18, 6), dpi=150)
plt.subplots_adjust(wspace=0.15)

from matplotlib.colors import ListedColormap
cmap_4c = ListedColormap(["#222222", "#f39c12", "#e74c3c", "#27ae60"])

# 2a. Descending Observability
axs2[0].imshow(class_desc, extent=extent, cmap=cmap_4c, vmin=0.5, vmax=4.5)
axs2[0].set_title(f"(a) Descending Track 48 (Sept 2023)\n(Scarp Observable: {scarp_stats_desc['Observable_pct']:.1f}%)", fontsize=10.5, fontweight="bold")
axs2[0].set_xlabel("Longitude (deg E)")
axs2[0].set_ylabel("Latitude (deg N)")
axs2[0].plot(scarp_lons, scarp_lats, color="white", linewidth=2.0, linestyle="--")

# 2b. Ascending Observability
axs2[1].imshow(class_asc, extent=extent, cmap=cmap_4c, vmin=0.5, vmax=4.5)
axs2[1].set_title(f"(b) Ascending Track 12 (Sept 2023)\n(Scarp Observable: {scarp_stats_asc['Observable_pct']:.1f}%)", fontsize=10.5, fontweight="bold")
axs2[1].set_xlabel("Longitude (deg E)")
axs2[1].plot(scarp_lons, scarp_lats, color="white", linewidth=2.0, linestyle="--")

# 2c. Minimum Detectable Slope Velocity Map (Detrended Model, Combined Best Geometry)
v_clip = np.clip(v_min_comb_det, 100, 1500)
im2c = axs2[2].imshow(v_clip, extent=extent, cmap="turbo_r", vmin=150, vmax=1000)
axs2[2].set_title("(c) Minimum Detectable Velocity (Single 12-day Pair)\n(Best Combined Geometry, 95% CI: 0.2–0.5 m/yr)", fontsize=10.5, fontweight="bold")
axs2[2].set_xlabel("Longitude (deg E)")
axs2[2].plot(scarp_lons, scarp_lats, color="black", linewidth=2.0, linestyle="--")
cb2c = fig2.colorbar(im2c, ax=axs2[2], fraction=0.046, pad=0.04)
cb2c.set_label("Min Detectable Velocity (mm/yr)", fontsize=9)

import matplotlib.patches as mpatches
legend_patches = [
    mpatches.Patch(color="#27ae60", label="Observable (R >= 0.3, gamma >= 0.3, inc <= 70 deg)"),
    mpatches.Patch(color="#f39c12", label="Low Sensitivity (R < 0.3 or inc > 70 deg)"),
    mpatches.Patch(color="#e74c3c", label="Decorrelated (gamma < 0.3)"),
    mpatches.Patch(color="#222222", label="Blind (Signed Layover / Shadow)"),
    mpatches.Patch(color="white", label="Scarp Box")
]
fig2.legend(handles=legend_patches, loc="lower center", ncol=5, fontsize=8.5, bbox_to_anchor=(0.35, -0.06))

fig2_path = OUT_DIR / "fig2_four_class_measurability_maps.png"
fig2.savefig(fig2_path, bbox_inches="tight")
plt.close(fig2)
print(f"Saved Figure 2 to: {fig2_path}")

# 18. Plot Figure 3: Steep Scarp Projections & Single Joint Inversions
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(15, 5.5), dpi=150)
plt.subplots_adjust(wspace=0.25)

# 3a. Distributions of Signed Projections P across Steep Scarp (slope >= 25 deg)
bins_p = np.linspace(-1.0, 0.2, 25)
ax3a.hist(proj_desc[steep_scarp_mask], bins=bins_p, alpha=0.6, color="#e67e22", label=f"Descending Track 48 (Mean P: {P_desc_steep:.3f})")
ax3a.hist(proj_asc[steep_scarp_mask],  bins=bins_p, alpha=0.6, color="#2980b9", label=f"Ascending Track 12 (Mean P: {P_asc_steep:.3f})")
ax3a.axvline(0, color="black", linestyle="--", linewidth=1.5, label="P = 0 (Perpendicular to Beam)")
ax3a.set_xlabel("Signed Projection P = d · s (Downslope into LOS)", fontsize=10)
ax3a.set_ylabel("Pixel Count (30 m Cells, Slope >= 25°)", fontsize=10)
ax3a.set_title("(a) Steep Scarp Projection Distributions\n[Filtering slope >= 25° resolves sign cancellation: P < 0 on both tracks]", fontsize=10.5, fontweight="bold")
ax3a.grid(True, linestyle="--", alpha=0.5)
ax3a.legend(loc="upper left", fontsize=8.5)

# 3b. Single Steep-Scarp Joint Inversion across Reference and Noise Models
models = [
    "Ensemble Ref\n(Raw Null)",
    "Ensemble Ref\n(Detrended Null)",
    "CTRL-01 Ref\n(Raw Null)",
    "CTRL-01 Ref\n(Detrended Null)"
]
vels = [
    inv_ens_raw["velocity_mm_yr"],
    inv_ens_det["velocity_mm_yr"],
    inv_ctrl_raw["velocity_mm_yr"],
    inv_ctrl_det["velocity_mm_yr"]
]
errs = [
    inv_ens_raw["sigma_mm_yr"] * 1.96,
    inv_ens_det["sigma_mm_yr"] * 1.96,
    inv_ctrl_raw["sigma_mm_yr"] * 1.96,
    inv_ctrl_det["sigma_mm_yr"] * 1.96
]

x_pos = np.arange(len(models))
colors = ["#2980b9", "#34495e", "#16a085", "#2c3e50"]
bars3b = ax3b.bar(x_pos, vels, yerr=errs, capsize=6, color=colors, width=0.45, alpha=0.88)
ax3b.axhline(0, color="red", linestyle="--", linewidth=1.5, label="Zero Motion (Null)")
ax3b.set_xticks(x_pos)
ax3b.set_xticklabels(models, fontsize=8.5, fontweight="bold")
ax3b.set_ylabel("Estimated Slope Velocity (mm/year)", fontsize=10)
ax3b.set_title("(b) Steep Scarp Joint Inversion (slope >= 25°, ~31 SAR pixels, 95% CI)\n[Raw null contains zero; Detrended null shows apparent upslope signal]", fontsize=10.5, fontweight="bold")
ax3b.grid(True, linestyle="--", alpha=0.5, axis="y")
ax3b.legend(loc="lower left", fontsize=9)

for idx, (v, e) in enumerate(zip(vels, errs)):
    ci_status = "Contains 0" if (v - e <= 0 <= v + e) else "Excludes 0"
    ax3b.text(idx, v - e - 55, f"{v:.0f} ± {e:.0f}\n[{ci_status}]", ha="center", fontsize=8, fontweight="bold")

fig3_path = OUT_DIR / "fig3_minimum_detectable_motion_and_plausibility.png"
fig3.savefig(fig3_path, bbox_inches="tight")
plt.close(fig3)
print(f"Saved Figure 3 to: {fig3_path}")

print("\n=== PHASE 2 ENGINE UPDATE COMPLETE ===")

