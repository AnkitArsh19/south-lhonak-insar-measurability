"""
Fetches Sentinel-1 acquisition catalogs from Alaska Satellite Facility (ASF) REST API.
Does not require heavy external dependencies (uses standard requests & csv).
"""

import sys
import csv
from pathlib import Path
import requests

DEFAULT_AOI = "POLYGON((88.15 27.85, 88.25 27.85, 88.25 27.95, 88.15 27.95, 88.15 27.85))"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "catalogs"

def fetch_asf_s1_catalog(
    polygon_wkt: str = DEFAULT_AOI,
    start_date: str = "2017-01-01T00:00:00Z",
    end_date: str = "2023-10-04T23:59:59Z",
    output_filename: str = "sentinel1_south_lhonak_catalog.csv"
) -> Path:
    """
    Queries ASF Vertex API directly for all Sentinel-1 SLC granules over South Lhonak.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / output_filename
    
    url = "https://api.daac.asf.alaska.edu/services/search/param"
    params = {
        "platform": "SENTINEL-1",
        "processingLevel": "SLC",
        "beamMode": "IW",
        "intersectsWith": polygon_wkt,
        "start": start_date,
        "end": end_date,
        "output": "csv"
    }
    
    print(f"Querying ASF Search API for Sentinel-1 scenes ({start_date[:10]} to {end_date[:10]})...")
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    
    # Save the raw CSV response
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(resp.text)
        
    # Analyze the catalog
    lines = resp.text.strip().splitlines()
    header = lines[0].split(",") if lines else []
    num_records = len(lines) - 1 if len(lines) > 1 else 0
    
    print(f"Successfully fetched catalog: {num_records} granules found.")
    print(f"Saved to: {out_path}")
    return out_path

if __name__ == "__main__":
    fetch_asf_s1_catalog()
