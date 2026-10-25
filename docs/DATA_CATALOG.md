# South Lhonak Research Data Catalog

This catalog outlines all satellite, elevation, meteorological, and in-situ datasets required for the project, including spatial/temporal extents, data providers, and access pathways.

---

## 1. Study Area Bounds

- **Bounding Box (WGS84):**
  - West: `88.15° E`
  - South: `27.85° N`
  - East: `88.25° E`
  - North: `27.95° N`
- **Center Coordinates:** `27.904° N, 88.201° E`
- **Elevation Range:** ~4,800 m to 6,800 m asl (Lake level ~5,200 m asl)
- **UTM Zone:** UTM Zone 45N (EPSG: 32645)

---

## 2. SAR Data (Synthetic Aperture Radar)

### A. Sentinel-1 C-band (Primary Hindcast Stack)
- **Sensor:** Sentinel-1A / Sentinel-1B
- **Wavelength:** C-band (~5.6 cm, 5.405 GHz)
- **Mode:** Interferometric Wide Swath (IW), Single Look Complex (SLC)
- **Polarization:** VV + VH (VV prioritized for co-polar phase stability)
- **Temporal Window:** 01 January 2017 to 03 October 2023 (Hindcast), plus immediate post-event scenes (04–15 October 2023)
- **Coverage Geometry:**
  - **Ascending Track:** Path/Relative Orbit **012** (Incidence angle ~39° over South Lhonak)
  - **Descending Track:** Path/Relative Orbit **048** (Incidence angle ~34° over South Lhonak)
- **Access:** Alaska Satellite Facility (ASF) DAAC via `asf_search` or Copernicus Data Space Ecosystem (CDSE) API.
- **Audited Catalog Granules:** 205 Ascending (Track 012), 191 Descending (Track 048) scenes (2017–2023).

### B. NISAR L-band & S-band (Future & Operational Framework)
- **Sensor:** NASA-ISRO SAR Mission
- **Wavelength:** L-band (~24 cm, 1.25 GHz) & S-band (~9.3 cm, 3.2 GHz)
- **Advantage:** Penetrates snowpack and rough periglacial debris; dramatically reduces temporal decorrelation in high-mountain terrain.
- **Access:** ASF DAAC (L-band products) / ISRO SAC / Bhuvan portal.
- **Proxy Dataset (for historical comparison):** ALOS-2 PALSAR-2 (L-band Fine Beam / ScanSAR) acquired over Sikkim.

---

## 3. Digital Elevation Models (DEM)

| Product | Resolution | Vertical Accuracy | Source | Application |
|---|---|---|---|---|
| **Copernicus DEM (GLO-30)** | 30 m | < 4 m | Copernicus Data Space | Primary topographic phase removal & geocoding |
| **AW3D30 (ALOS PRISM)** | 30 m | ~5 m | JAXA EORC | Baseline validation & terrain morphometry |
| **NASADEM** | 30 m | ~6 m | NASA LP DAAC | Reprocessed SRTM with improved void filling |
| **HMA DEM (Shean et al.)** | 8 m | ~2–3 m | NSIDC | High-resolution slope angle and aspect validation |

---

## 4. Optical Imagery (Extent & Feature Tracking)

### A. Sentinel-2 MSI (Level-2A BOA Surface Reflectance)
- **Bands:** B02 (Blue), B03 (Green), B04 (Red), B08 (NIR), B11/B12 (SWIR)
- **Temporal Window:** 2017–2024 (cloud-free pre-monsoon and post-monsoon images)
- **Application:** Lake surface area tracking (NDWI), moraine scarp mapping, cross-correlation feature tracking using `autoRIFT` or `scikit-image`.

### B. PlanetScope / SkySat (High Resolution)
- **Resolution:** 3 m (PlanetScope) / 0.5 m (SkySat)
- **Key Scenes:** Late September 2023 (pre-event), 04 October 2023 (post-event)
- **Application:** Exact boundary of lateral moraine breach, ice-cored slump extent, and downstream deposition.

---

## 5. Meteorological & Atmospheric Datasets

### A. ERA5 / ERA5-Land Reanalysis
- **Provider:** ECMWF via Copernicus Climate Data Store (CDS API)
- **Variables:** Surface temperature, 2m dewpoint, total column water vapor, geopotential height at pressure levels (1000–300 hPa).
- **Application:** Atmospheric Phase Screen (APS) estimation in MintPy (`PyAPS`) to decouple elevation-correlated tropospheric delay from true slope subsidence.

### B. GPM IMERG (Integrated Multi-satellitE Retrievals for GPM)
- **Product:** IMERG Final Run (0.1° x 0.1°, half-hourly)
- **Application:** Precipitation triggers during 01–04 October 2023 Sikkim extreme rainfall event.

---

## 6. Lake Outburst & Downstream Data

- **Lake Bathymetry / Volume:** Published estimates in Mohanty et al. (2026), Sattar et al. (~65 million m³ pre-event).
- **Breach Geometry:** Post-event field & optical surveys (~100m wide moraine breach).
- **Downstream Cross-Sections:** Chungthang Dam (Teesta-III, ~60–68 km downstream), Dikchu, Singtam.
