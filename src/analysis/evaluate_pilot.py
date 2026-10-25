"""
Evaluates Pilot Pair 1 InSAR (2023-09-16 to 2023-09-28) and
optical Sentinel-2 pre- vs post-event captures over South Lhonak.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SAR_DIR = ROOT / "data" / "sar" / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4"
OPT_DIR = ROOT / "data" / "optical" / "sentinel2"
OUT_DIR = ROOT / "results" / "EXP001"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_optical_comparison():
    print("Generating optical comparison figure...")
    f_pre = OPT_DIR / "south_lhonak_20230926_pre_event.tiff"
    f_post = OPT_DIR / "south_lhonak_20231009_post_event.tiff"
    
    im_pre = Image.open(f_pre)
    im_post = Image.open(f_post)
    
    w, h = im_pre.size
    combined = Image.new("RGB", (w, h * 2 + 100), (25, 25, 30))
    
    cdraw = ImageDraw.Draw(combined)
    cdraw.text((20, 15), "South Lhonak Glacial Lake Outburst Flood — Optical Verification (Sentinel-2 L2A)", fill=(255, 255, 255))
    cdraw.text((20, 35), "Pre-Event: 26 September 2023 (Intact Lake ~168 ha) vs Post-Event: 09 October 2023 (Drained Lake & Moraine Breach)", fill=(180, 220, 255))
    
    # Pre-event
    combined.paste(im_pre, (0, 60))
    cdraw.text((15, 65), "PRE-EVENT: 2023-09-26 (Full Lake Level)", fill=(255, 255, 0))
    
    # Post-event
    combined.paste(im_post, (0, 60 + h + 20))
    cdraw.text((15, 60 + h + 25), "POST-EVENT: 2023-10-09 (Moraine Breach & Catastrophic Drainage)", fill=(255, 80, 80))
    
    out_path = OUT_DIR / "optical_pre_vs_post_comparison.png"
    combined.save(out_path)
    print(f"Optical comparison saved to: {out_path}")
    return out_path

def inspect_insar_products():
    print("\nAuditing InSAR Coherence and Unwrapped Phase...")
    f_corr = SAR_DIR / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4_corr.tif"
    f_unw = SAR_DIR / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4_unw_phase.tif"
    
    im_corr = Image.open(f_corr)
    im_unw = Image.open(f_unw)
    
    arr_corr = np.array(im_corr)
    arr_unw = np.array(im_unw)
    
    # UTM Zone 45N bounds
    # Tiepoint: (518800.0, 3201360.0), pixel scale 80m
    x0, y0 = 518800.0, 3201360.0
    res = 80.0
    
    # South Lhonak approximate UTM 45N coordinates:
    # Lon ~ 88.201, Lat ~ 27.904 -> X ~ 618300, Y ~ 3087300
    target_x = 618300.0
    target_y = 3087300.0
    
    px = int(round((target_x - x0) / res))
    py = int(round((y0 - target_y) / res))
    
    print(f"Full swath shape: {arr_corr.shape} (cols={arr_corr.shape[1]}, rows={arr_corr.shape[0]})")
    print(f"Target South Lhonak pixel in swath: col={px}, row={py}")
    
    # Crop 100x100 pixels (~8 km x 8 km) around the lake
    hw = 50
    crop_corr = arr_corr[py-hw:py+hw, px-hw:px+hw]
    crop_unw = arr_unw[py-hw:py+hw, px-hw:px+hw]
    
    print(f"Local 8km crop coherence: min={np.nanmin(crop_corr):.3f}, max={np.nanmax(crop_corr):.3f}, mean={np.nanmean(crop_corr):.3f}")
    print(f"Local 8km crop unwrapped phase: min={np.nanmin(crop_unw):.2f}, max={np.nanmax(crop_unw):.2f}, mean={np.nanmean(crop_unw):.2f} rad")
    
    # Check coherence threshold: fraction of pixels with gamma >= 0.35
    valid_fraction = float(np.mean(crop_corr >= 0.35)) * 100.0
    print(f"Fraction of pixels with coherence >= 0.35 in immediate 8km basin: {valid_fraction:.1f}%")
    
    # Render quicklook of local coherence and phase
    # Normalize coherence to 0-255
    corr_vis = (np.clip(crop_corr, 0, 1.0) * 255).astype(np.uint8)
    img_corr = Image.fromarray(corr_vis).resize((400, 400), Image.Resampling.NEAREST)
    
    # Normalize unwrapped phase
    unw_valid = crop_unw[np.isfinite(crop_unw)]
    p_min, p_max = np.percentile(unw_valid, 2), np.percentile(unw_valid, 98)
    unw_vis = np.clip((crop_unw - p_min) / (p_max - p_min + 1e-6) * 255, 0, 255).astype(np.uint8)
    img_unw = Image.fromarray(unw_vis).resize((400, 400), Image.Resampling.NEAREST)
    
    # Combine into report figure
    comb_sar = Image.new("RGB", (840, 480), (20, 20, 25))
    sdraw = ImageDraw.Draw(comb_sar)
    sdraw.text((20, 15), "Sentinel-1 InSAR Pilot Pair (2023-09-16 to 2023-09-28) — South Lhonak Basin", fill=(255, 255, 255))
    sdraw.text((20, 35), f"Track 48 Descending | B_perp = -69.6 m | dt = 12 days | Local Coherence Mean = {np.nanmean(crop_corr):.2f}", fill=(180, 220, 255))
    
    comb_sar.paste(img_corr.convert("RGB"), (20, 60))
    sdraw.text((30, 65), "Coherence Map (0.0 to 1.0)", fill=(255, 255, 0))
    
    comb_sar.paste(img_unw.convert("RGB"), (430, 60))
    sdraw.text((440, 65), "Unwrapped Phase (radians)", fill=(0, 255, 255))
    
    out_sar = OUT_DIR / "insar_pilot_coherence_and_phase.png"
    comb_sar.save(out_sar)
    print(f"InSAR evaluation figure saved to: {out_sar}")
    
    return {
        "mean_coherence": float(np.nanmean(crop_corr)),
        "coherent_fraction_pct": valid_fraction,
        "phase_min": float(np.nanmin(crop_unw)),
        "phase_max": float(np.nanmax(crop_unw))
    }

if __name__ == "__main__":
    generate_optical_comparison()
    inspect_insar_products()
