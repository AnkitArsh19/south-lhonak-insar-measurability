"""
Extracts LOS displacement profiles from the unwrapped phase across:
  1. The moraine breach scarp
  2. Bedrock control region CTRL-01
  3. Stable control region CTRL-02

Uses corrected lake center coordinates: 27.912 N, 88.197 E

IMPORTANT: This script extracts RAW unwrapped phase converted to LOS displacement.
The values have NOT been corrected for atmospheric delay or orbital errors.
Any patterns must be compared against control slopes before interpretation.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
import math
import json

ROOT = Path(__file__).resolve().parents[2]
SAR_DIR = ROOT / "data" / "sar" / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4"
OUT_DIR = ROOT / "results" / "EXP001"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Constants
SENTINEL1_WAVELENGTH_M = 0.05546576  # C-band ~5.55 cm
RES = 80.0  # meters per pixel
X0, Y0 = 518800.0, 3201360.0  # UTM tiepoint

def latlon_to_utm45n(lat, lon):
    a = 6378137.0
    f = 1 / 298.257223563
    e2 = 2 * f - f * f
    k0 = 0.9996
    lon0 = 87.0
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

def to_pixel(lat, lon):
    x, y = latlon_to_utm45n(lat, lon)
    col = int(round((x - X0) / RES))
    row = int(round((Y0 - y) / RES))
    return col, row

def extract_region_stats(arr_corr, arr_unw, name, lat_center, lon_center, half_size=10):
    """Extract coherence and phase statistics for a rectangular region."""
    col, row = to_pixel(lat_center, lon_center)
    r_min = max(0, row - half_size)
    r_max = min(arr_corr.shape[0], row + half_size)
    c_min = max(0, col - half_size)
    c_max = min(arr_corr.shape[1], col + half_size)
    
    crop_c = arr_corr[r_min:r_max, c_min:c_max]
    crop_p = arr_unw[r_min:r_max, c_min:c_max]
    
    valid_mask = (crop_c > 0) & np.isfinite(crop_p) & (crop_p != 0)
    valid_c = crop_c[valid_mask]
    valid_p = crop_p[valid_mask]
    
    # Convert phase to LOS displacement in mm
    # d_LOS = -(wavelength / 4*pi) * phase
    if len(valid_p) > 0:
        los_mm = -(SENTINEL1_WAVELENGTH_M / (4 * np.pi)) * valid_p * 1000.0
    else:
        los_mm = np.array([])
    
    result = {
        "region": name,
        "center_lat": lat_center,
        "center_lon": lon_center,
        "pixel_col": col,
        "pixel_row": row,
        "valid_pixels": int(len(valid_c)),
        "total_pixels": int(crop_c.size),
    }
    
    if len(valid_c) > 0:
        result.update({
            "coherence_mean": float(np.mean(valid_c)),
            "coherence_median": float(np.median(valid_c)),
            "coherence_std": float(np.std(valid_c)),
            "phase_mean_rad": float(np.mean(valid_p)),
            "phase_std_rad": float(np.std(valid_p)),
            "los_displacement_mean_mm": float(np.mean(los_mm)),
            "los_displacement_std_mm": float(np.std(los_mm)),
            "los_displacement_min_mm": float(np.min(los_mm)),
            "los_displacement_max_mm": float(np.max(los_mm)),
        })
    else:
        result["coherence_mean"] = None
        result["los_displacement_mean_mm"] = None
    
    return result

def main():
    print("Loading InSAR products...")
    f_corr = SAR_DIR / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4_corr.tif"
    f_unw = SAR_DIR / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4_unw_phase.tif"
    f_dem = SAR_DIR / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4_dem.tif"
    
    arr_corr = np.array(Image.open(f_corr))
    arr_unw = np.array(Image.open(f_unw))
    arr_dem = np.array(Image.open(f_dem))
    
    # Define regions using corrected coordinates
    # Lake center verified by user at 27.912, 88.197
    regions = {
        "MORAINE_BREACH": {"lat": 27.916, "lon": 88.197, "desc": "Lateral moraine / breach scarp (north of lake)"},
        "LAKE_SURFACE":   {"lat": 27.912, "lon": 88.197, "desc": "Lake water surface (should be decorrelated)"},
        "CTRL_01":        {"lat": 27.907, "lon": 88.237, "desc": "Bedrock ridge east of lake"},
        "CTRL_02":        {"lat": 27.872, "lon": 88.167, "desc": "Stable valley wall west"},
        "GLACIER_ACT01":  {"lat": 27.932, "lon": 88.177, "desc": "North Lhonak Glacier terminus (known motion)"},
    }
    
    print("\n" + "=" * 80)
    print(f"LOS DISPLACEMENT EXTRACTION: Pilot Pair 1 (2023-09-16 to 2023-09-28)")
    print(f"Conversion: phase (rad) -> d_LOS = -(lambda/4pi) * phase")
    print(f"Wavelength: {SENTINEL1_WAVELENGTH_M*100:.3f} cm (Sentinel-1 C-band)")
    print(f"[WARNING] Values are RAW — not corrected for atmosphere, orbit, or DEM error")
    print("=" * 80)
    
    all_results = []
    
    for rname, rinfo in regions.items():
        stats = extract_region_stats(arr_corr, arr_unw, rname, rinfo["lat"], rinfo["lon"], half_size=10)
        all_results.append(stats)
        
        print(f"\n--- {rname}: {rinfo['desc']} ---")
        print(f"  Center: {rinfo['lat']:.3f}N, {rinfo['lon']:.3f}E -> Pixel ({stats['pixel_col']}, {stats['pixel_row']})")
        print(f"  Valid pixels: {stats['valid_pixels']}/{stats['total_pixels']}")
        
        if stats.get("coherence_mean") is not None:
            print(f"  Coherence: mean={stats['coherence_mean']:.3f}, median={stats['coherence_median']:.3f}, std={stats['coherence_std']:.3f}")
            print(f"  Raw phase: mean={stats['phase_mean_rad']:.3f} +/- {stats['phase_std_rad']:.3f} rad")
            print(f"  Raw LOS displacement: {stats['los_displacement_mean_mm']:.2f} +/- {stats['los_displacement_std_mm']:.2f} mm")
            print(f"  LOS range: [{stats['los_displacement_min_mm']:.2f}, {stats['los_displacement_max_mm']:.2f}] mm")
            
            # DEM elevation at this location
            col, row = stats["pixel_col"], stats["pixel_row"]
            if 0 <= row < arr_dem.shape[0] and 0 <= col < arr_dem.shape[1]:
                elev = arr_dem[row, col]
                print(f"  DEM elevation at pixel: {elev:.0f} m")
        else:
            print(f"  [No valid pixels — likely decorrelated or outside coverage]")
    
    # Key comparison
    print("\n" + "=" * 80)
    print("COMPARATIVE SUMMARY (Target vs Controls)")
    print("=" * 80)
    
    moraine = next((r for r in all_results if r["region"] == "MORAINE_BREACH"), None)
    ctrl01 = next((r for r in all_results if r["region"] == "CTRL_01"), None)
    ctrl02 = next((r for r in all_results if r["region"] == "CTRL_02"), None)
    lake = next((r for r in all_results if r["region"] == "LAKE_SURFACE"), None)
    glacier = next((r for r in all_results if r["region"] == "GLACIER_ACT01"), None)
    
    print(f"\n{'Region':<20} {'Coh Mean':>10} {'LOS (mm)':>10} {'LOS Std':>10} {'Interpretation'}")
    print("-" * 75)
    for r in all_results:
        coh = f"{r['coherence_mean']:.3f}" if r.get('coherence_mean') is not None else "N/A"
        los = f"{r['los_displacement_mean_mm']:.2f}" if r.get('los_displacement_mean_mm') is not None else "N/A"
        los_s = f"{r['los_displacement_std_mm']:.2f}" if r.get('los_displacement_std_mm') is not None else "N/A"
        
        interp = "[OBSERVATION ONLY - no scientific claim]"
        if r["region"] == "LAKE_SURFACE" and r.get("coherence_mean") is not None and r["coherence_mean"] < 0.3:
            interp = "Expected: water decorrelates radar phase"
        
        print(f"{r['region']:<20} {coh:>10} {los:>10} {los_s:>10}  {interp}")
    
    print(f"\n[CRITICAL NOTE] The difference in LOS displacement between MORAINE_BREACH")
    print(f"and CTRL_01 is a RAW OBSERVATION. To determine if it represents real ground")
    print(f"motion, we must: (1) correct for atmospheric delay, (2) verify with the dry")
    print(f"season benchmark pair, (3) check multiple time epochs, (4) account for the")
    print(f"elevation difference between target and control (which causes systematic")
    print(f"tropospheric phase bias at ~5,200 m elevation).")
    
    # Save results
    out_json = OUT_DIR / "pilot1_displacement_extraction.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to: {out_json}")

if __name__ == "__main__":
    main()
