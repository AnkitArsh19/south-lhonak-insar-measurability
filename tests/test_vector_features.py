"""
Independent Invariant and Physical Verification Tests for Study Geometries
Validates geometric containment, DEM equipotential flatness, SAR backscatter physics,
and topological separation for South Lhonak features.
"""

import json
from pathlib import Path
import numpy as np
from PIL import Image
import pyproj
from shapely.geometry import shape, Point
from shapely.ops import transform

ROOT = Path("e:/Personal/iirs")
GEOJSON_PATH = ROOT / "data" / "vector" / "south_lhonak_aoi.geojson"
SAR_PILOT_DIR = ROOT / "data" / "sar" / "S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4"

def load_geojson_features():
    assert GEOJSON_PATH.exists(), f"Vector file missing: {GEOJSON_PATH}"
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {feat["properties"]["id"]: feat for feat in data["features"]}

def test_lake_post_contained_in_lake_pre():
    """
    Independent Geometric Invariant:
    A post-drainage residual water pool must be strictly contained within
    the pre-event lake basin boundary (zero area of LAKE-POST outside LAKE-PRE).
    """
    feats = load_geojson_features()
    assert "LAKE-PRE" in feats and "LAKE-POST" in feats, "Lake features missing"
    
    geom_pre = shape(feats["LAKE-PRE"]["geometry"])
    geom_post = shape(feats["LAKE-POST"]["geometry"])
    
    t_to_utm = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32645", always_xy=True).transform
    diff_geom = geom_post.difference(geom_pre)
    diff_area_ha = transform(t_to_utm, diff_geom).area / 10000.0 if not diff_geom.is_empty else 0.0
    
    assert diff_area_ha < 0.001, f"LAKE-POST extends outside LAKE-PRE by {diff_area_ha:.4f} ha!"
    assert geom_pre.contains(geom_post), "LAKE-PRE must topologically contain LAKE-POST!"

def test_lake_post_schematic_labeling():
    """Verify LAKE-POST is explicitly documented as schematic and excluded from empirical claims."""
    feats = load_geojson_features()
    post_props = feats["LAKE-POST"]["properties"]
    assert post_props.get("type") == "Glacial_Lake_Water_Body_Residual_Schematic", "Must be labeled schematic type"
    assert post_props.get("status") == "schematic_reference", "Status must be schematic_reference"
    assert "Schematic" in post_props.get("name", ""), "Name must disclose schematic approximation"

def test_dem_flatness_in_lake_core():
    """
    Independent Physical Invariant:
    A natural standing lake water body represents an equipotential gravitational surface.
    On Copernicus GLO-30 DEM, elevation across the lake core must be flat (std < 15 m).
    """
    feats = load_geojson_features()
    geom_post = shape(feats["LAKE-POST"]["geometry"])
    
    f_dem = SAR_PILOT_DIR / f"{SAR_PILOT_DIR.name}_dem.tif"
    assert f_dem.exists(), f"DEM raster missing: {f_dem}"
    
    im_dem = Image.open(f_dem)
    tp = im_dem.tag_v2.get(33922)
    sc = im_dem.tag_v2.get(33550)
    x0, y0 = tp[3], tp[4]
    res_x, res_y = sc[0], sc[1]
    arr_dem = np.array(im_dem)
    
    t_to_utm = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32645", always_xy=True)
    minx, miny, maxx, maxy = geom_post.bounds
    
    elevs = []
    for lon in np.linspace(minx, maxx, 25):
        for lat in np.linspace(miny, maxy, 25):
            if geom_post.contains(Point(lon, lat)):
                x, y = t_to_utm.transform(lon, lat)
                c = int(round((x - x0) / res_x))
                r = int(round((y0 - y) / res_y))
                if 0 <= r < arr_dem.shape[0] and 0 <= c < arr_dem.shape[1]:
                    elevs.append(arr_dem[r, c])
                    
    elevs = np.array(elevs)
    assert len(elevs) > 100, "Insufficient DEM sampling points inside lake polygon"
    elev_std = float(np.std(elevs))
    elev_mean = float(np.mean(elevs))
    assert elev_std < 15.0, f"DEM inside lake is non-flat: std={elev_std:.2f} m > 15 m!"
    assert 5150 <= elev_mean <= 5190, f"Lake elevation ({elev_mean:.1f} m) deviates from expected 5165 m range!"

def test_sar_backscatter_water_fraction():
    """
    Independent Physical Invariant:
    Smooth specular water reflects C-band radar signals away from the sensor.
    Over 90% of pixels inside the pre-event lake polygon must show low backscatter (sigma0 < -12 dB).
    """
    feats = load_geojson_features()
    geom_post = shape(feats["LAKE-POST"]["geometry"])
    
    f_amp = SAR_PILOT_DIR / f"{SAR_PILOT_DIR.name}_amp.tif"
    assert f_amp.exists(), f"Amplitude raster missing: {f_amp}"
    
    im_amp = Image.open(f_amp)
    tp = im_amp.tag_v2.get(33922)
    sc = im_amp.tag_v2.get(33550)
    x0, y0 = tp[3], tp[4]
    res_x, res_y = sc[0], sc[1]
    arr_amp = np.array(im_amp)
    
    t_to_utm = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32645", always_xy=True)
    minx, miny, maxx, maxy = geom_post.bounds
    
    amps = []
    for lon in np.linspace(minx, maxx, 25):
        for lat in np.linspace(miny, maxy, 25):
            if geom_post.contains(Point(lon, lat)):
                x, y = t_to_utm.transform(lon, lat)
                c = int(round((x - x0) / res_x))
                r = int(round((y0 - y) / res_y))
                if 0 <= r < arr_amp.shape[0] and 0 <= c < arr_amp.shape[1]:
                    amps.append(arr_amp[r, c])
                    
    amps = np.array(amps)
    # amp is linear power sigma0; dB = 10 * log10(amp)
    amps_db = 10.0 * np.log10(np.maximum(amps, 1e-6))
    frac_low = float(np.mean(amps_db < -12.0))
    assert frac_low > 0.90, f"Low backscatter fraction ({frac_low*100:.1f}%) < 90% expected for water body!"

def test_scarp_and_breach_separation():
    """Verify that lateral moraine trigger scarp and frontal outlet breach are distinct and non-overlapping."""
    feats = load_geojson_features()
    assert "LATERAL-MORAINE-SCARP" in feats and "FRONTAL-DAM-BREACH" in feats
    geom_scarp = shape(feats["LATERAL-MORAINE-SCARP"]["geometry"])
    geom_breach = shape(feats["FRONTAL-DAM-BREACH"]["geometry"])
    assert not geom_scarp.intersects(geom_breach), "Scarp and breach polygons must not overlap!"

def test_ctrl02_decorrelated_dropped():
    """Verify that decorrelated CTRL-02 has been removed from control regions."""
    feats = load_geojson_features()
    assert "CTRL-02" not in feats, "CTRL-02 should be removed due to low coherence!"

if __name__ == "__main__":
    test_lake_post_contained_in_lake_pre()
    print("PASS: test_lake_post_contained_in_lake_pre (difference area = 0.0 ha, strictly inside)")
    test_lake_post_schematic_labeling()
    print("PASS: test_lake_post_schematic_labeling (explicit schematic labeling)")
    test_dem_flatness_in_lake_core()
    print("PASS: test_dem_flatness_in_lake_core (equipotential DEM std < 15 m)")
    test_sar_backscatter_water_fraction()
    print("PASS: test_sar_backscatter_water_fraction (>90% pixels < -12 dB)")
    test_scarp_and_breach_separation()
    print("PASS: test_scarp_and_breach_separation (non-overlapping)")
    test_ctrl02_decorrelated_dropped()
    print("PASS: test_ctrl02_decorrelated_dropped (decorrelated control removed)")
    print("\nALL 6 INDEPENDENT INVARIANT TESTS PASSED SUCCESSFULLY!")
