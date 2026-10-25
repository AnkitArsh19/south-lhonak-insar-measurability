# Data Manifest & Provenance: South Lhonak InSAR Measurability

This directory documents the input datasets required to reproduce the analysis. Raw raster data files (`.tif`, `.tiff`) exceed standard git file size recommendations and are tracked locally.

---

## 1. SAR Interferometric Products (Sentinel-1 C-band)

All interferograms were processed on-demand using the Alaska Satellite Facility (ASF) HyP3 platform running the GAMMA InSAR processor with Minimum Cost Flow (MCF) phase unwrapping and 20x4 multilooking to 80 m pixel spacing:

### Pair 1: Late Monsoon Descending Pilot (EXP001 Primary)
* **Product Name:** `S1AA_20230916T000326_20230928T000326_VVP012_INT80_G_weF_48B4`
* **Orbit / Track:** Descending Track 048, Relative Orbit 48
* **Reference Scene:** `S1A_IW_SLC__1SDV_20230916T000326_...` (2023-09-16T00:03:26 UTC)
* **Secondary Scene:** `S1A_IW_SLC__1SDV_20230928T000326_...` (2023-09-28T00:03:26 UTC)
* **Temporal Baseline:** 12 days
* **Perpendicular Baseline ($B_\perp$):** $+34.6\text{ m}$
* **Polarization:** VV
* **Water Mask:** Applied during phase unwrapping (OpenStreetMap-derived static mask, epoch unknown)
* **Key Files:** `*_corr.tif` (coherence), `*_unw_phase.tif` (unwrapped phase in radians), `*_lv_phi.tif` (look azimuth), `*_lv_theta.tif` (look elevation angle), `*_water_mask.tif`.

### Pair 2: Late Monsoon Ascending Pilot (EXP001 Dual-Track)
* **Product Name:** `S1AA_20230913T121407_20230925T121408_VVP012_INT80_G_weF_C8DE`
* **Orbit / Track:** Ascending Track 012, Relative Orbit 12
* **Reference Scene:** `S1A_IW_SLC__1SDV_20230913T121407_...` (2023-09-13T12:14:07 UTC)
* **Secondary Scene:** `S1A_IW_SLC__1SDV_20230925T121408_...` (2023-09-25T12:14:08 UTC)
* **Temporal Baseline:** 12 days
* **Perpendicular Baseline ($B_\perp$):** $-14.2\text{ m}$
* **Polarization:** VV
* **Water Mask:** Applied during phase unwrapping

### Pair 3: Pre-Monsoon Dry Season Descending Pilot (EXP001 Seasonal Control)
* **Product Name:** `S1AA_20230507T000319_20230519T000320_VVP012_INT80_G_weF_3DA0`
* **Orbit / Track:** Descending Track 048, Relative Orbit 48
* **Reference Scene:** `S1A_IW_SLC__1SDV_20230507T000319_...` (2023-05-07T00:03:19 UTC)
* **Secondary Scene:** `S1A_IW_SLC__1SDV_20230519T000320_...` (2023-05-19T00:03:20 UTC)
* **Temporal Baseline:** 12 days
* **Perpendicular Baseline ($B_\perp$):** $+18.9\text{ m}$
* **Polarization:** VV
* **Water Mask:** Applied during phase unwrapping

---

## 2. Digital Elevation Model (Copernicus GLO-30)

* **Filename:** `data/dem/Copernicus_DSM_COG_10_N27_00_E088_00_DEM.tif`
* **Data Source:** Copernicus DEM GLO-30 Public Release (derived from WorldDEM / TanDEM-X mission, European Space Agency & Airbus Defence and Space).
* **Native Pixel Spacing:** 1 arcsecond ($\sim 30\text{ m}$, $dx \approx 27.35\text{ m}, dy \approx 30.87\text{ m}$ at $27.9^\circ\text{ N}$).
* **Bounding Box:** $27^\circ 00'\text{ N} - 28^\circ 00'\text{ N}$, $088^\circ 00'\text{ E} - 089^\circ 00'\text{ E}$.
* **Vertical Datum:** EGM2008 geoid.
* **Download Access:**
  - Copernicus Data Space Ecosystem: https://dataspace.copernicus.eu/
  - AWS Open Data Registry: `s3://copernicus-dem-30m/Copernicus_DSM_COG_10_N27_00_E088_00_DEM/`
  - OpenTopography: https://opentopography.org/

---

## 3. Optical Multispectral Imagery (Sentinel-2 MSI)

* **Directory:** `data/optical/sentinel2/`
* **Pre-Event Capture:** `south_lhonak_20230926_pre_event.tiff` (Acquired 2023-09-26, Sentinel-2A MSI L2A BOA reflectance, cloud-free over lake).
* **Post-Event Capture:** `south_lhonak_20231009_post_event.tiff` (Acquired 2023-10-09, Sentinel-2A MSI L2A BOA reflectance, first cloud-free post-breach capture).
* **Bands Extracted:**
  - Band 2 (Blue, 490 nm, 10 m)
  - Band 3 (Green, 560 nm, 10 m)
  - Band 4 (Red, 665 nm, 10 m)
  - Band 8 (NIR, 842 nm, 10 m)
* **Products Generated:** True-color RGB composites and Normalized Difference Water Index ($\text{NDWI} = \frac{\text{Green} - \text{NIR}}{\text{Green} + \text{NIR}}$) showing $105\text{ ha}$ lake drainage.

---

## 4. Vector AOI & Feature Geometries

* **Filename:** `data/vector/south_lhonak_aoi.geojson`
* **Coordinate Reference System:** WGS 84 (EPSG:4326)
* **Features Included:**
  1. `LATERAL-MORAINE-SCARP`: Approximate 43.6 ha analysis polygon isolating the left lateral moraine failure flank.
  2. `LAKE-PRE`: Digitized pre-event lake water surface (167.4 ha on 2023-09-26).
  3. `LAKE-POST`: Digitized post-event remaining lake water surface (59.6 ha on 2023-10-09).
  4. `BREACH-DAM`: Terminal moraine breach channel.
  5. `GLACIER-SNOW`: High-altitude glaciated terrain unit.
  6. `STABLE-BEDROCK-SPUR` (CTRL-01): Consolidated ridge control point ($27.907^\circ\text{ N}, 88.237^\circ\text{ E}$, 5145 masl).

---

## 5. How to Download / Reproduce Raw Data

1. **ASF HyP3 InSAR:**
   - Log into ASF Vertex / HyP3 (https://hyp3.asf.alaska.edu/).
   - Submit On Demand InSAR jobs for the scene pairs listed above.
   - Processing options: Multilook `20x4` (80 m), Apply Water Mask = `True`, Include Look Vectors = `True`, Include DEM = `True`.
   - Download the unzipped product directories into `data/sar/`.

2. **Copernicus DEM GLO-30:**
   ```bash
   # AWS CLI download without credentials
   aws s3 cp s3://copernicus-dem-30m/Copernicus_DSM_COG_10_N27_00_E088_00_DEM/Copernicus_DSM_COG_10_N27_00_E088_00_DEM.tif data/dem/ --no-sign-request
   ```

3. **Verify Integrity:**
   ```bash
   python -m pytest tests/test_vector_features.py tests/test_measurability.py
   ```
