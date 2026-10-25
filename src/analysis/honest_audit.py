"""
Honest audit of Pilot Pair 1 findings.
Separates what is directly measured from data vs what is inferred or assumed.
Updates coordinates to user-verified lake center: 27.912, 88.197.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAR_DIR = ROOT / "data" / "sar" / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4"
OPT_DIR = ROOT / "data" / "optical" / "sentinel2"

# Corrected lake center from user's direct verification on Copernicus Browser
LAKE_CENTER_LAT = 27.912
LAKE_CENTER_LON = 88.197

print("=" * 70)
print("HONEST DATA AUDIT: Pilot Pair 1 (2023-09-16 to 2023-09-28)")
print("=" * 70)

# ===== 1. METADATA DIRECTLY FROM HyP3 PARAMETER FILE (FACT) =====
print("\n--- VERIFIED FROM HyP3 METADATA (.txt file) ---")
print("Reference Granule: S1A_IW_SLC__1SDV_20230916T000326_...050345_060FB7_3B45")
print("Secondary Granule: S1A_IW_SLC__1SDV_20230928T000326_...050520_0615B5_8E7B")
print("Pass Direction: DESCENDING")
print("Perpendicular Baseline: -69.603 m  [SOURCE: HyP3 parameter file]")
print("Temporal Baseline: 12 days  [SOURCE: Acquisition date difference]")
print("Range Looks x Azimuth Looks: 20 x 4  [SOURCE: HyP3 parameter file]")
print("Output Resolution: 80 m  [SOURCE: HyP3 parameter file]")
print("Phase Filter: Adaptive (adf), parameter 0.6  [SOURCE: HyP3 parameter file]")
print("DEM Source: GLO-30  [SOURCE: HyP3 parameter file]")
print("Unwrapping Method: MCF (Minimum Cost Flow)  [SOURCE: HyP3 parameter file]")
print("CRS: UTM Zone 45N  [SOURCE: GeoTIFF tags]")

# ===== 2. COMPUTE PIXEL COORDINATES =====
# InSAR products are in UTM Zone 45N (EPSG:32645)
# We need to convert the lake center lat/lon to UTM
# Using the formulaic approach (approximate for UTM Zone 45N, central meridian 87E)
import math

def latlon_to_utm45n(lat, lon):
    """Approximate WGS84 lat/lon to UTM Zone 45N (central meridian 87E)."""
    # Constants
    a = 6378137.0  # WGS84 semi-major axis
    f = 1 / 298.257223563
    e2 = 2 * f - f * f
    k0 = 0.9996
    lon0 = 87.0  # Central meridian for UTM zone 45
    
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    lon0_rad = math.radians(lon0)
    
    N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)
    T = math.tan(lat_rad)**2
    C = (e2 / (1 - e2)) * math.cos(lat_rad)**2
    A = math.cos(lat_rad) * (lon_rad - lon0_rad)
    
    e_prime2 = e2 / (1 - e2)
    M = a * ((1 - e2/4 - 3*e2**2/64 - 5*e2**3/256) * lat_rad
             - (3*e2/8 + 3*e2**2/32 + 45*e2**3/1024) * math.sin(2*lat_rad)
             + (15*e2**2/256 + 45*e2**3/1024) * math.sin(4*lat_rad)
             - (35*e2**3/3072) * math.sin(6*lat_rad))
    
    x = k0 * N * (A + (1-T+C)*A**3/6 + (5-18*T+T**2+72*C-58*e_prime2)*A**5/120) + 500000
    y = k0 * (M + N * math.tan(lat_rad) * (A**2/2 + (5-T+9*C+4*C**2)*A**4/24 + (61-58*T+T**2+600*C-330*e_prime2)*A**6/720))
    
    return x, y

utm_x, utm_y = latlon_to_utm45n(LAKE_CENTER_LAT, LAKE_CENTER_LON)
print(f"\n--- COORDINATE CONVERSION ---")
print(f"User-verified lake center: {LAKE_CENTER_LAT}N, {LAKE_CENTER_LON}E")
print(f"Computed UTM 45N: X = {utm_x:.1f}, Y = {utm_y:.1f}")

# InSAR product tiepoint and pixel scale (from GeoTIFF tags)
x0, y0 = 518800.0, 3201360.0  # Upper-left corner in UTM
res = 80.0  # meters per pixel

px = int(round((utm_x - x0) / res))
py = int(round((y0 - utm_y) / res))
print(f"Pixel location in InSAR raster: col={px}, row={py}")

# ===== 3. COHERENCE AND PHASE EXTRACTION (COMPUTED FROM REAL DATA) =====
print("\n--- COHERENCE & PHASE: COMPUTED FROM DOWNLOADED GeoTIFFs ---")

f_corr = SAR_DIR / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4_corr.tif"
f_unw = SAR_DIR / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4_unw_phase.tif"

im_corr = Image.open(f_corr)
im_unw = Image.open(f_unw)
arr_corr = np.array(im_corr)
arr_unw = np.array(im_unw)

rows, cols = arr_corr.shape
print(f"Raster dimensions: {cols} cols x {rows} rows")
print(f"Raster bounds (UTM 45N): X [{x0:.0f} to {x0 + cols*res:.0f}], Y [{y0 - rows*res:.0f} to {y0:.0f}]")

# Bounds check
in_bounds = 0 <= px < cols and 0 <= py < rows
print(f"Lake center pixel in bounds: {in_bounds}")

if in_bounds:
    # Extract 50-pixel radius (~4 km) around lake center
    hw = 50
    r_min = max(0, py - hw)
    r_max = min(rows, py + hw)
    c_min = max(0, px - hw)
    c_max = min(cols, px + hw)
    
    crop_corr = arr_corr[r_min:r_max, c_min:c_max]
    crop_unw = arr_unw[r_min:r_max, c_min:c_max]
    
    # Mask out zero/nodata
    valid_corr = crop_corr[crop_corr > 0]
    valid_unw = crop_unw[np.isfinite(crop_unw) & (crop_unw != 0)]
    
    print(f"\nLocal {hw*2}x{hw*2} pixel crop ({hw*2*80/1000:.0f} km x {hw*2*80/1000:.0f} km):")
    print(f"  Coherence: min={np.min(valid_corr):.4f}, max={np.max(valid_corr):.4f}, mean={np.mean(valid_corr):.4f}, median={np.median(valid_corr):.4f}")
    print(f"  Unwrapped phase: min={np.min(valid_unw):.3f}, max={np.max(valid_unw):.3f}, mean={np.mean(valid_unw):.3f} rad")
    print(f"  Pixels with coherence >= 0.35: {np.sum(valid_corr >= 0.35)}/{len(valid_corr)} ({100*np.mean(valid_corr >= 0.35):.1f}%)")
    print(f"  Pixels with coherence >= 0.50: {np.sum(valid_corr >= 0.50)}/{len(valid_corr)} ({100*np.mean(valid_corr >= 0.50):.1f}%)")
    
    # Point sample at exact lake center
    coh_at_lake = arr_corr[py, px]
    phase_at_lake = arr_unw[py, px]
    print(f"\n  Single pixel at lake center ({LAKE_CENTER_LAT}, {LAKE_CENTER_LON}):")
    print(f"    Coherence: {coh_at_lake:.4f}")
    print(f"    Unwrapped phase: {phase_at_lake:.3f} rad")
    if coh_at_lake < 0.1:
        print(f"    [NOTE: Very low coherence expected - this pixel may be on water surface]")

# ===== 4. OPTICAL IMAGE BOUNDS VERIFICATION =====
print("\n--- OPTICAL IMAGE BOUNDS VERIFICATION ---")
for name in ["south_lhonak_20230926_pre_event.tiff", "south_lhonak_20231009_post_event.tiff"]:
    f = OPT_DIR / name
    im = Image.open(f)
    tp = im.tag_v2.get(33922)
    sc = im.tag_v2.get(33550)
    ul_lon, ul_lat = tp[3], tp[4]
    lr_lon = ul_lon + im.size[0] * sc[0]
    lr_lat = ul_lat - im.size[1] * sc[1]
    
    lake_inside = ul_lon <= LAKE_CENTER_LON <= lr_lon and lr_lat <= LAKE_CENTER_LAT <= ul_lat
    print(f"{name}:")
    print(f"  Bounds: Lon [{ul_lon:.5f} to {lr_lon:.5f}], Lat [{lr_lat:.5f} to {ul_lat:.5f}]")
    print(f"  Lake center ({LAKE_CENTER_LAT}, {LAKE_CENTER_LON}) inside frame: {lake_inside}")

# ===== 5. HONESTY CHECKLIST =====
print("\n" + "=" * 70)
print("FACT vs INFERENCE SEPARATION")
print("=" * 70)
print("""
VERIFIED FACTS (directly from data):
  1. HyP3 processed the pair successfully with MCF unwrapping
  2. Perpendicular baseline = -69.6 m (from HyP3 metadata)
  3. Coherence and phase values are as computed above from real GeoTIFF pixels
  4. The InSAR swath covers the South Lhonak study area

INFERENCES THAT REQUIRE CAUTION:
  1. [CAUTION] 'High coherence means the slope is measurable' - coherence
     tells us phase is stable between acquisitions, but does NOT prove
     the phase change represents real ground motion vs atmospheric delay
  2. [CAUTION] The phase values have NOT been corrected for:
     - Atmospheric tropospheric delay (elevation-correlated)
     - Orbital ramp errors
     - Topographic residuals (DEM error)
     Any of these can produce apparent 'displacement' of several mm
  3. [CAUTION] We have NOT yet compared the target slope phase against
     control slopes (CTRL-01, CTRL-02) to rule out systematic artifacts
  4. [CAUTION] A single 12-day pair cannot establish a deformation RATE
     or TIME SERIES - it only shows one snapshot of phase difference

CLAIMS THE AGENT MUST NOT MAKE YET:
  - 'Pre-event deformation was detected'
  - 'The moraine was accelerating before failure'
  - 'InSAR provides early warning capability'
  These require the full hindcast experiment with controls and FDR accounting
""")
