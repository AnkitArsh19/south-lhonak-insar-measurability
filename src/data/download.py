"""
Data discovery and acquisition utilities for SAR and optical products.
"""

from typing import List, Dict, Any, Optional
import os
from pathlib import Path
from datetime import datetime

# Study area defaults: South Lhonak Glacial Lake, Sikkim
DEFAULT_BBOX = [88.15, 27.85, 88.25, 27.95] # [W, S, E, N]

def search_sentinel1_asf(
    bbox: Optional[List[float]] = None,
    start_date: str = "2017-01-01",
    end_date: str = "2023-10-04",
    flight_direction: Optional[str] = None, # 'ASCENDING' or 'DESCENDING'
    relative_orbit: Optional[int] = None,
    beam_mode: str = "IW",
    processing_level: str = "SLC"
) -> List[Dict[str, Any]]:
    """
    Queries Alaska Satellite Facility (ASF) via asf_search for Sentinel-1 acquisitions.
    Returns metadata list without downloading.
    """
    bbox = bbox or DEFAULT_BBOX
    w, s, e, n = bbox
    wkt_polygon = f"POLYGON(({w} {s}, {e} {s}, {e} {n}, {w} {n}, {w} {s}))"
    
    try:
        import asf_search as asf
    except ImportError:
        raise ImportError("asf_search is required. Install via: pip install asf_search")
        
    opts = {
        "platform": asf.PLATFORM.SENTINEL1,
        "processingLevel": processing_level,
        "beamMode": beam_mode,
        "start": start_date,
        "end": end_date,
        "intersectsWith": wkt_polygon,
    }
    if flight_direction:
        opts["flightDirection"] = flight_direction.upper()
    if relative_orbit:
        opts["relativeOrbit"] = relative_orbit
        
    results = asf.search(**opts)
    
    scenes = []
    for r in results:
        meta = r.properties
        scenes.append({
            "scene_name": meta.get("sceneName"),
            "flight_direction": meta.get("flightDirection"),
            "path_number": meta.get("pathNumber"),
            "frame_number": meta.get("frameNumber"),
            "start_time": meta.get("startTime"),
            "polarization": meta.get("polarization"),
            "url": meta.get("url"),
            "bytes": meta.get("bytes")
        })
    return scenes

def summarize_scene_coverage(scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generates temporal and track statistics for acquired scenes."""
    tracks = {}
    for s in scenes:
        p = s["path_number"]
        tracks[p] = tracks.get(p, 0) + 1
        
    return {
        "total_scenes": len(scenes),
        "tracks_summary": tracks,
        "earliest": min(s["start_time"] for s in scenes) if scenes else None,
        "latest": max(s["start_time"] for s in scenes) if scenes else None
    }
