"""
Downloads the 30-meter Copernicus GLO-30 DEM tile covering South Lhonak (N27 E088).
Source: AWS Open Data / OpenTopography public S3 mirrors.
"""

from pathlib import Path
import requests

DEM_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "dem"

URLS = [
    "https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N27_00_E088_00_DEM/Copernicus_DSM_COG_10_N27_00_E088_00_DEM.tif",
    "https://opentopography.s3.sdsc.edu/raster/COP30/COP30_hh/Copernicus_DSM_COG_10_N27_00_E088_00_DEM.tif"
]

def download_glo30_dem(target_filename: str = "Copernicus_DSM_COG_10_N27_00_E088_00_DEM.tif") -> Path:
    DEM_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DEM_DIR / target_filename
    
    if out_file.exists() and out_file.stat().st_size > 1000000:
        print(f"DEM tile already exists: {out_file} ({out_file.stat().st_size / (1024*1024):.2f} MB)")
        return out_file
        
    print(f"Attempting download of Copernicus GLO-30 DEM tile N27_E088...")
    success = False
    
    for url in URLS:
        try:
            print(f"Connecting to: {url}...")
            resp = requests.get(url, stream=True, timeout=30)
            if resp.status_code == 200:
                total_size = int(resp.headers.get("content-length", 0))
                print(f"Downloading {total_size / (1024*1024):.2f} MB...")
                downloaded = 0
                with open(out_file, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                print(f"Download complete: {out_file} ({out_file.stat().st_size / (1024*1024):.2f} MB)")
                success = True
                break
            else:
                print(f"Mirror returned HTTP {resp.status_code}, trying next...")
        except Exception as e:
            print(f"Failed with error: {e}")
            
    if not success:
        print("\nCould not download automatically from open mirrors.")
        print(f"Manual download URL: https://dataspace.copernicus.eu/ or OpenTopography")
        print(f"Place tile in: {DEM_DIR}")
        
    return out_file

if __name__ == "__main__":
    download_glo30_dem()
