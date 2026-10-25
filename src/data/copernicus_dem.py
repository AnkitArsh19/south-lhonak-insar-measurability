"""
Copernicus GLO-30 DEM tile handler for high-relief Himalayan terrain.
"""

from typing import List, Tuple
from pathlib import Path
import math

def get_glo30_tile_names(bbox: List[float]) -> List[str]:
    """
    Computes required Copernicus GLO-30 1x1 degree tile names for a given bounding box.
    Format: Copernicus_DSM_COG_10_N27_00_E088_00_DEM
    
    bbox: [west, south, east, north]
    """
    w, s, e, n = bbox
    min_lat = math.floor(s)
    max_lat = math.floor(n)
    min_lon = math.floor(w)
    max_lon = math.floor(e)
    
    tiles = []
    for lat in range(min_lat, max_lat + 1):
        lat_prefix = f"N{abs(lat):02d}" if lat >= 0 else f"S{abs(lat):02d}"
        for lon in range(min_lon, max_lon + 1):
            lon_prefix = f"E{abs(lon):03d}" if lon >= 0 else f"W{abs(lon):03d}"
            tile_id = f"Copernicus_DSM_COG_10_{lat_prefix}_00_{lon_prefix}_00_DEM"
            tiles.append(tile_id)
            
    return tiles

def generate_dem_vrt(dem_files: List[Path], output_vrt: Path) -> Path:
    """Combines multiple DEM GeoTIFF tiles into a single virtual raster."""
    try:
        from osgeo import gdal
    except ImportError:
        raise ImportError("GDAL Python bindings are required.")
        
    gdal.BuildVRT(str(output_vrt), [str(f) for f in dem_files])
    return output_vrt
