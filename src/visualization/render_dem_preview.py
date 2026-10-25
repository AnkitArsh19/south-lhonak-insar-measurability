"""
Audits DEM elevations under each GeoJSON feature and generates
a publication-quality Hillshade + Vector overlay preview.
Uses numpy + Pillow + standard library (no matplotlib required).
"""

import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
DEM_PATH = ROOT / "data" / "dem" / "Copernicus_DSM_COG_10_N27_00_E088_00_DEM.tif"
GEOJSON_PATH = ROOT / "data" / "vector" / "south_lhonak_aoi.geojson"
OUTPUT_IMG = ROOT / "experiments" / "reports" / "aoi_dem_preview.png"

def compute_hillshade(elevation, azimuth=315.0, altitude=45.0, cell_size_m=30.0):
    """Computes shaded relief array from 2D elevation grid."""
    az_rad = np.radians(azimuth)
    alt_rad = np.radians(altitude)
    
    # Gradient in y and x
    dy, dx = np.gradient(elevation, cell_size_m, cell_size_m)
    
    slope = np.arctan(np.sqrt(dx**2 + dy**2))
    aspect = np.arctan2(-dx, dy)
    
    shaded = np.sin(alt_rad) * np.cos(slope) + np.cos(alt_rad) * np.sin(slope) * np.cos(az_rad - aspect)
    # Scale to 0-255
    shaded = 255 * (shaded + 1) / 2.0
    return np.clip(shaded, 0, 255).astype(np.uint8)

def main():
    OUTPUT_IMG.parent.mkdir(parents=True, exist_ok=True)
    
    # Load DEM
    print("Loading Copernicus DEM...")
    im = Image.open(DEM_PATH)
    dem_full = np.array(im)
    
    # DEM metadata
    # Tiepoint: (0, 0) is (Lon 88.0, Lat 28.0)
    # Scale: 1/3600 deg per pixel (~0.00027777778)
    origin_lon = 88.0
    origin_lat = 28.0
    res = 1.0 / 3600.0
    
    # Load GeoJSON
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geo = json.load(f)
        
    # Crop to study area with 0.02 deg margin
    crop_w = 88.14
    crop_e = 88.26
    crop_s = 27.84
    crop_n = 27.96
    
    col_min = int(round((crop_w - origin_lon) / res))
    col_max = int(round((crop_e - origin_lon) / res))
    row_min = int(round((origin_lat - crop_n) / res))
    row_max = int(round((origin_lat - crop_s) / res))
    
    dem_crop = dem_full[row_min:row_max, col_min:col_max]
    h, w = dem_crop.shape
    print(f"Cropped DEM shape: {w} x {h} pixels (~{w*30/1000:.1f} km x {h*30/1000:.1f} km)")
    
    # Check elevations under features
    print("\n--- Feature Elevation Audit ---")
    feature_stats = {}
    for feat in geo["features"]:
        fid = feat["properties"]["id"]
        coords = feat["geometry"]["coordinates"][0] # outer ring
        
        # Convert coords to pixel indices
        pix_cols = [int(round((lon - crop_w) / res)) for lon, lat in coords]
        pix_rows = [int(round((crop_n - lat) / res)) for lon, lat in coords]
        
        # Bounding box of polygon in crop
        c_min, c_max = max(0, min(pix_cols)), min(w - 1, max(pix_cols))
        r_min, r_max = max(0, min(pix_rows)), min(h - 1, max(pix_rows))
        
        poly_elev = dem_crop[r_min:r_max+1, c_min:c_max+1]
        mean_e = float(np.mean(poly_elev))
        min_e = float(np.min(poly_elev))
        max_e = float(np.max(poly_elev))
        feature_stats[fid] = {"mean": mean_e, "min": min_e, "max": max_e}
        print(f"Feature {fid} ({feat['properties']['name']}): Min={min_e:.1f}m, Max={max_e:.1f}m, Mean={mean_e:.1f}m")
        
    # Compute hillshade
    print("\nGenerating shaded relief...")
    hillshade = compute_hillshade(dem_crop)
    
    # Blend with elevation tint
    elev_norm = (dem_crop - np.min(dem_crop)) / (np.max(dem_crop) - np.min(dem_crop) + 1e-6)
    # Simple terrain colormap (rgb)
    r = (0.25 * hillshade + 0.75 * (180 + 75 * elev_norm)).clip(0, 255).astype(np.uint8)
    g = (0.25 * hillshade + 0.75 * (190 + 50 * elev_norm)).clip(0, 255).astype(np.uint8)
    b = (0.25 * hillshade + 0.75 * (160 + 95 * elev_norm)).clip(0, 255).astype(np.uint8)
    rgb = np.stack([r, g, b], axis=-1)
    
    # Scale up by 2x for crisp plotting
    img = Image.fromarray(rgb).resize((w * 2, h * 2), Image.Resampling.BILINEAR)
    draw = ImageDraw.Draw(img)
    scale = 2.0
    
    # Feature styling
    colors = {
        "AOI-01": (255, 255, 0),         # Yellow
        "LAKE-PRE": (0, 180, 255),       # Cyan / Blue
        "MORAINE-BREACH": (255, 40, 40), # Red
        "CTRL-01": (0, 220, 0),          # Green
        "CTRL-02": (50, 205, 50),        # Lime Green
        "ACT-01": (255, 140, 0)          # Orange
    }
    
    # Draw vector features
    for feat in geo["features"]:
        fid = feat["properties"]["id"]
        coords = feat["geometry"]["coordinates"][0]
        pts = []
        for lon, lat in coords:
            px = (lon - crop_w) / res * scale
            py = (crop_n - lat) / res * scale
            pts.append((px, py))
            
        color = colors.get(fid, (255, 255, 255))
        # Draw boundary line
        draw.line(pts + [pts[0]], fill=color, width=3)
        
        # Draw label
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        draw.text((cx - 20, cy - 8), fid, fill=(255, 255, 255))
        
    # Draw title and legend bar at top
    header_img = Image.new("RGB", (img.width, 90), (30, 30, 35))
    hdraw = ImageDraw.Draw(header_img)
    hdraw.text((20, 15), "Copernicus GLO-30 DEM Hillshade & Study Area Vector Audit", fill=(255, 255, 255))
    hdraw.text((20, 38), "AOI (Yellow) | Lake (Cyan) | Breach Scarp (Red) | Bedrock CTRL-01 (Green) | CTRL-02 (Lime) | ACT-01 (Orange)", fill=(200, 200, 200))
    hdraw.text((20, 60), f"Bounds: {crop_w:.2f}°E to {crop_e:.2f}°E, {crop_s:.2f}°N to {crop_n:.2f}°N | Lake Elevation ~5,200 m asl", fill=(160, 220, 255))
    
    # Stack header on top
    final_img = Image.new("RGB", (img.width, img.height + 90))
    final_img.paste(header_img, (0, 0))
    final_img.paste(img, (0, 90))
    
    final_img.save(OUTPUT_IMG)
    print(f"\nPreview saved successfully: {OUTPUT_IMG}")
    
    # Save machine-readable stats
    with open(ROOT / "experiments" / "reports" / "elevation_audit.json", "w", encoding="utf-8") as f:
        json.dump(feature_stats, f, indent=2)

if __name__ == "__main__":
    main()
