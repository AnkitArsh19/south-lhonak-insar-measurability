# Research Data Directory

This directory houses all raw, intermediate, and processed datasets for the South Lhonak GLOF research project.

## Directory Structure

```
data/
├── README.md               # This file
├── vector/                 # AOI boundaries, lake polygons, moraine scarps, control slopes (.geojson, .shp)
├── dem/                    # Digital Elevation Models (Copernicus GLO-30, NASADEM) (.tif, .vrt)
├── catalogs/               # Satellite scene catalogs, query results, baseline tables (.csv)
├── sar/                    # Sentinel-1 SLCs or processed HyP3 interferograms (.zip, .nc, .tif)
├── meteo/                  # ERA5 weather reanalysis and GPM IMERG rainfall (.nc, .grib, .csv)
└── optical/                # Sentinel-2 Level-2A and PlanetScope optical imagery (.tif, .jp2)
```

## Storage & Git Rules
- Large raster datasets (>50 MB) and raw satellite archives must **NOT** be committed to git (already configured in `.gitignore`).
- Vector files (`.geojson`, `.kml`), catalogs (`.csv`), and config files are tracked in git.
