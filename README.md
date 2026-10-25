# Observability & Measurability of Sentinel-1 InSAR for Slope Monitoring Around South Lhonak Lake: Geometry, Coherence and Atmospheric Noise

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![SAR Sensor](https://img.shields.io/badge/Sensor-Sentinel--1%20C--band-orange.svg)](#)
[![DEM](https://img.shields.io/badge/DEM-Copernicus%20GLO--30-green.svg)](#)
[![Unit Tests](https://img.shields.io/badge/Tests-19%20Passed%2C%202%20Skipped-brightgreen.svg)](#)

---

## 1. Project Overview & Research Question

On the night of **3–4 October 2023**, a catastrophic Glacial Lake Outburst Flood (GLOF) originated from South Lhonak Lake in Sikkim, India, following a large-scale lateral moraine collapse that triggered displacement waves and breached the terminal moraine dam (Mohanty et al., *Scientific Reports* 16:9741, 2026). Satellite assessments by NRSC/ISRO recorded a post-breach water area decrease of **~107.1 ha** (~64% area fraction drained).

This study addresses one specific, testable remote sensing question:

> **Which slopes around South Lhonak Lake can Sentinel-1 InSAR physically measure, and how small a slope movement could it detect?**

Rather than claiming definitive precursory failure from single interferograms, we evaluate the geometric sensitivity, interferometric coherence, and atmospheric noise limits of Sentinel-1 C-band InSAR across two opposing orbits: **Track 048 (Descending)** and **Track 012 (Ascending)** using the native 30 m Copernicus GLO-30 DEM.

---

## 2. Methodology & Mathematical Invariants

```
   Copernicus GLO-30 DEM (30 m)          HyP3 Look Vectors (lv_theta, lv_phi)
              │                                         │
              ▼                                         ▼
   Topographic Gradient (p, q)                 Satellite LOS Unit Vector (s)
   Slope (alpha) & Aspect (psi)                        │
              │                                         │
              ▼                                         ▼
   Unit Downslope Vector (d) ───────────────► Signed Sensitivity P = d · s
              │                                         │
              └───────────────────┬─────────────────────┘
                                  ▼
                      4-Class Observability Map
          (Blind, Low Sensitivity, Decorrelated, Observable)
                                  │
                                  ▼
       Steep-Scarp Single Joint Velocity Inversion vs Bedrock Null Noise Floor
```

### 1. InSAR Phase & Sign Conventions
Directly from ASF HyP3 InSAR product documentation (`README.md.txt`):
* **Line 117 (`_unw_phase`):** *"Positive values indicate movement away from the sensor (caused by subsidence or lateral movement away from the sensor) and negative values indicate movement towards the sensor (uplift or lateral movement towards the sensor)."*
* **Line 138 (`_los_disp`):** *"Converts the unwrapped differential phase into measurements of ground movement in meters along the look vector (line-of-sight). Positive values indicate movement towards the sensor (such as uplift), while negative values indicate movement away from the sensor (such as subsidence). Note that the sign convention is opposite to that used for the unwrapped phase."*
* **Exact Mathematical Conversion:**
  $$d_{\text{LOS}} = - \frac{\lambda}{4\pi} \Delta\phi_{\text{unw}}$$
  where $\lambda \approx 0.055465763\text{ m}$ (Sentinel-1 C-band).

### 2. Forward Model & Inversion Signs ($y = v_{\text{slope}} \cdot P$)
* **Downslope unit vector $\hat{\mathbf{d}}$:** Computed from DEM gradients (`dz_drow, dz_dcol = np.gradient(dem, dy, dx); p = dz_dcol, q = -dz_drow`). On south/southeast-facing slopes, the downhill vector dips down ($\hat{d}_z = -\sin\alpha < 0$).
* **Look unit vector $\hat{\mathbf{s}}$:** Points from ground to satellite ($\hat{s}_z = \sin\theta > 0$, where $\theta \approx 50.8^\circ$ is look elevation angle).
* **Geometric Sensitivity Projection:** $P = \hat{\mathbf{d}} \cdot \hat{\mathbf{s}}$, and $R = |P| \in [0, 1]$.
  - On the steep scarp ($\ge 25^\circ$), $P_{\text{desc}} = -0.276 < 0$ and $P_{\text{asc}} = -0.366 < 0$. Both are negative.
  - Forward displacement: $y_{\text{LOS}} = v_{\text{slope}} \cdot P$.
  - Downslope creep ($v > 0$) causes range lengthening (movement away from satellite), which requires **negative LOS displacement ($y < 0$)**.
  - Conversely, positive measured differential LOS ($y > 0$, range shortening / movement towards sensor) inverts via least-squares $v = y / P$ to a **negative velocity ($v < 0$, apparent upslope motion)**.

### 3. Four-Class Observability Mapping (September 2023 Snapshot)
* **Observable:** $R \ge 0.3$, $\gamma \ge 0.3$, $\theta_{\text{inc}} \le 70^\circ$, and not blind.
* **Low Sensitivity:** $R < 0.3$ or grazing local incidence $\theta_{\text{inc}} > 70^\circ$.
* **Decorrelated:** Coherence $\gamma < 0.3$.
* **Blind:** Signed layover ($-\frac{\partial z}{\partial u} \ge \cot\theta_{\text{elev}}$ along look azimuth) or shadow ($\cos\theta_{\text{inc}} \le 0.087$ / $\theta_{\text{inc}} \ge 85^\circ$).

### 4. Water Mask Provenance
Directly quoting ASF HyP3 InSAR product documentation (`README.md.txt`, Section 11):
> *"The water mask identifies coastal waters and most inland waterbodies. These areas are assigned a pixel value of 0. All remaining pixels (land, islands, very small inland waterbodies, and landfast Antarctic ice) have a value of 1. All areas between 85 and 90 degrees north latitude are assigned a value of 0, and all areas between 85 and 90 degrees south latitude are assigned a value of 1. The water mask is stored as an 8-bit unsigned integer GeoTIFF file and is always included in the product package.*
>
> *The water mask is generated by ASF using data from OpenStreetMap (https://www.openstreetmap.org/about) and/or ESA WorldCover (https://esa-worldcover.org/en/about/about), depending on location. Areas within Canada, Alaska, and Russia are primarily covered by ESA WorldCover data, while the rest of the world is covered by OpenStreetMaps data. Refer to our InSAR Water Masking Tutorial for more information: https://arcg.is/19aKHj*
>
> *Note that applying the mask after phase unwrapping does not prevent unwrapping errors caused by the inclusion of water pixels as valid data during the phase unwrapping process. When submitting InSAR jobs for processing, there is an option to 'Apply Water Mask'. Selecting this option uses the water mask to adjust the validity mask used for phase unwrapping. This prevents phase unwrapping from occurring over large expanses of water, which can lead to unexpected deformation signals or phase jumps in the unwrapped outputs. This mask was applied during phase unwrapping."*

Note the distinction between:
- **HyP3 Internal Processing Water Mask (`_water_mask.tif`):** The external water mask described above, generated by ASF and applied during phase unwrapping (SNAPHU / MCF) to mask open water;
- **Analysis Feature Polygons (`data/vector/south_lhonak_aoi.geojson`):** The research polygons (`LATERAL-MORAINE-SCARP`, `LAKE-PRE`, `LAKE-POST`, `BREACH-DAM`) digitized from Sentinel-2 MSI multispectral imagery to define our AOI, isolate terrain units, and verify lake-facing geometry.

---

## 3. Key Findings

All reported values trace directly to [`results/measurability_metrics.json`](results/measurability_metrics.json):

### 1. Minimum Detectable Velocity (Single 12-Day Pair Limits on Steep Scarp Face)
Leading detection thresholds evaluated directly on the steep active scarp face by dividing the empirical $2\sigma$ spatial noise floor by steep-face sensitivity $R_{\text{steep}} = |P_{\text{steep}}|$ ($R_{\text{desc}} = 0.276$, $R_{\text{asc}} = 0.366$):

| Sensor Track | Steep Sensitivity ($R_{\text{steep}}$) | Spatial Noise Null Model | Min Detectable LOS Motion ($2\sigma$) | Min Detectable Slope Velocity (Single 12-Day Pair Limit) |
| :--- | :---: | :---: | :---: | :---: |
| **Descending Track 48** | **0.276** (0.2757) | Raw Pairwise Null ($\sigma = 2.66\text{ mm}$) | $5.32\text{ mm}$ | **$\sim 587\text{ mm/yr}$** ($\sim 0.59\text{ m/yr}$) |
| **Descending Track 48** | **0.276** (0.2757) | Planar-Detrended Null ($\sigma = 1.10\text{ mm}$) | $2.20\text{ mm}$ | **$\sim 243\text{ mm/yr}$** ($\sim 0.24\text{ m/yr}$) |
| **Ascending Track 12** | **0.366** (0.3658) | Raw Pairwise Null ($\sigma = 3.08\text{ mm}$) | $6.16\text{ mm}$ | **$\sim 513\text{ mm/yr}$** ($\sim 0.51\text{ m/yr}$) |
| **Ascending Track 12** | **0.366** (0.3658) | Planar-Detrended Null ($\sigma = 2.47\text{ mm}$) | $4.94\text{ mm}$ | **$\sim 411\text{ mm/yr}$** ($\sim 0.41\text{ m/yr}$) |

*Takeaway:* Single 12-day pairs cannot detect slope creep below **$\sim 0.24 - 0.59\text{ m/yr}$** (roughly a few tenths of a metre per year). Detecting slow creep ($< 0.1\text{ m/yr}$) strictly requires multi-temporal time series (SBAS / PS-InSAR) across multi-year stacks.

### 2. Observability Breakdown & Sensitivity to Threshold $R$

| Evaluation Region | Sensitivity Cutoff | Descending Track 48 | Ascending Track 12 | Combined Multi-Track |
| :--- | :---: | :---: | :---: | :---: |
| **Moraine Scarp Box (43.6 ha)** | $R \ge 0.2$ | 78.0% | 89.1% | **95.0%** |
| | **$R \ge 0.3$ (Standard)** | **51.8%** | **76.3%** | **87.0%** |
| | $R \ge 0.5$ | 12.4% | 35.4% | **37.9%** |
| **Steep Scarp Face ($\ge 25^\circ$)** | $R \ge 0.2$ | 81.3% | 96.6% | **100.0%** |
| | **$R \ge 0.3$ (Standard)** | **45.5%** | **77.0%** | **93.6%** |
| | $R \ge 0.5$ | 12.4% | 35.4% | **37.9%** |
| **Entire 10 km AOI** | $R \ge 0.2$ | 55.1% | 53.8% | **70.0%** |
| | **$R \ge 0.3$ (Standard)** | **44.8%** | **45.5%** | **63.4%** |
| | $R \ge 0.5$ | 24.3% | 29.5% | **45.8%** |

*Note: The broad 43.6 ha box contains ~40% flat bench ($< 15^\circ$) where downslope orientation is ill-defined. On the steep active failure face ($\ge 25^\circ$), dual-orbit combined observability reaches **93.6%** at standard sensitivity ($R \ge 0.3$).*

### 3. Scarp Morphology & Aspect Alignment
* **Lake-Facing Aspect:** The lateral moraine scarp full analysis box circular mean aspect is **$151.12^\circ$ (SSE)** with angular dispersion $0.4032$. When restricted to the steep active failure face ($\ge 25^\circ$), the circular mean aspect shifts directly South to **$174.7^\circ$ ($174.67^\circ$)** with an extremely tight angular dispersion of **$0.0338$**. This downslope vector physically faces the lake, aligning within **$2.6^\circ$** of the nearest southern lake shore ($177.3^\circ$ bearing from digitized pre-event lake polygon). (Both differ from the $236.7^\circ$ WSW lake centroid because the glacial lake extends westward toward the glacier snout).
* **Aspect Tolerance Pre-specification:** A loose preliminary quadrant tolerance ($\le 35^\circ$, representing $\pm 1$ compass octant) was pre-specified to confirm that the scarp slopes southward toward the lake rather than northward toward the mountain ridge. Measured alignment is $26.2^\circ$ for the broad analysis box and $2.6^\circ$ for the steep active failure scarp.
* **Slope Bins & Scarp Masking:** The 43.6 ha analysis box contains 523 pixels on the 30 m DEM. However, **39.8% of pixels lie on the flatter moraine crest/bench ($< 15^\circ$)** where downslope direction is ill-defined. Restricting analysis to slopes $\ge 25^\circ$ isolates the steep active failure scarp (235 pixels, 44.9% of scarp area, representing **$\sim 31$ independent 80 m SAR resolution cells** based on native DEM cell area $844.2\text{ m}^2$, or $33.05$ on a nominal $30\times 30\text{ m}$ grid) with mean slope **$34.45^\circ$** ($34.447^\circ$).

### 4. Radar Sensitivity & Sign Cancellation Resolution
* **Full Box Unmasked:** Descending Track 48 exhibits sign cancellation across curved ridge facets (38.8% positive, 61.2% negative; mean $P = -0.034$, mean $|R| = 0.309$).
* **Steep Scarp ($\ge 25^\circ$):** Eliminating the flat crest resolves the sign ambiguity:
  - Descending Track 48: Mean signed $P_{\text{desc}} = \mathbf{-0.2757}$ (all negative, $|P| = 0.2757$).
  - Ascending Track 12: Mean signed $P_{\text{asc}} = \mathbf{-0.3658}$ (all negative, $|P| = 0.3658$).

### 5. Non-Circular Coherence Validation
Evaluating raw coherence against local incidence angle prior to thresholding:
* Descending: median coherence falls from $0.889$ ($30-50^\circ$) to $0.654$ in grazing angles ($70-85^\circ$), and $0.360$ in shadow ($>85^\circ$).
* Ascending: median coherence falls from $0.784$ ($30-50^\circ$) to $0.619$ in grazing angles ($70-85^\circ$), and $0.234$ in shadow ($>85^\circ$).

### 6. Single Steep-Scarp Joint Velocity Inversion
Measured differential LOS offsets across the steep scarp ($\ge 25^\circ$):
- Relative to Bedrock Ensemble: Descending $= +4.429\text{ mm}$, Ascending $= +1.298\text{ mm}$
- Relative to CTRL-01: Descending $= +3.570\text{ mm}$, Ascending $= +1.632\text{ mm}$

Because measured LOS offsets are positive (range shortening) while downslope projections are negative ($P < 0$), joint inversion yields negative velocities:

| Reference Frame | Spatial Noise Null Model | Estimated Velocity ($v_{\text{slope}}$) | 95% Confidence Interval | Contains Zero? |
| :--- | :--- | :---: | :---: | :---: |
| **Bedrock Ensemble** | **Raw Spatial Null** | $\mathbf{-273 \pm 193\text{ mm/yr}}$ | **$[-651, +106]\text{ mm/yr}$** | **Yes** (Upper bound on creep $< 0.11\text{ m/yr}$) |
| **Bedrock Ensemble** | **Detrended Null** | $\mathbf{-390 \pm 105\text{ mm/yr}}$ | **$[-595, -185]\text{ mm/yr}$** | **No** (Apparent upslope signal at $3.7\sigma$) |
| **CTRL-01 Patch** | **Raw Spatial Null** | $\mathbf{-248 \pm 193\text{ mm/yr}}$ | **$[-626, +131]\text{ mm/yr}$** | **Yes** (Upper bound on creep $< 0.13\text{ m/yr}$) |
| **CTRL-01 Patch** | **Detrended Null** | $\mathbf{-327 \pm 105\text{ mm/yr}}$ | **$[-532, -122]\text{ mm/yr}$** | **No** (Apparent upslope signal at $3.1\sigma$) |

### 7. Scientific Conclusion & Cause Attribution
* The inversion result is **model-dependent**.
* Under the conservative raw spatial noise model, zero motion is contained within the 95% confidence intervals ($[-651, +106]\text{ mm/yr}$ and $[-626, +131]\text{ mm/yr}$).
* Under the ramp-removed (detrended) null model, an apparent signal appears at $3.1 - 3.7\sigma$ (Ensemble: $-390 \pm 105\text{ mm/yr}$; CTRL-01: $-327 \pm 105\text{ mm/yr}$). This apparent signal is directed **upslope ($v < 0$)**, which is physically implausible as gravitational creep.
* **Cause is Undetermined:** The offset has the same sign across all three pilot pairs (including the May 2023 dry season baseline), which does not support purely random noise, but three samples are too few to conclude (same-signed offsets occur by chance ~25% of the time, and the September windows share dates). Candidate causes cannot be discriminated from two pilot pairs:
  1. Systematic valley-versus-ridge stratified atmospheric phase delay across steep alpine topography ($5200 - 5300\text{ m}$ masl);
  2. Reference-pixel network drift or phase unwrapping biases;
  3. A null/estimator mismatch: the spatial null is the pairwise spread between point bedrock patches, but it is applied to a polygon mean minus an ensemble mean.
* **Defensible Conclusion:** **Two pilot pairs constrain slope-parallel creep only to within a few tenths of a metre per year.** Single pilot pairs cannot detect slow precursory creep.

---

## 4. Figures & Deliverables

* **Figure 1 (Geometry, Sensitivity & Lake Alignment):** [`results/fig1_radar_geometry_and_sensitivity.png`](results/fig1_radar_geometry_and_sensitivity.png)
* **Figure 2 (Observability & Min Detectable Velocity Map):** [`results/fig2_four_class_measurability_maps.png`](results/fig2_four_class_measurability_maps.png)
* **Figure 3 (Steep Scarp Projections & Single Joint Inversion):** [`results/fig3_minimum_detectable_motion_and_plausibility.png`](results/fig3_minimum_detectable_motion_and_plausibility.png)
* **Full Technical Report:** [`experiments/reports/south_lhonak_insar_measurability_report.md`](experiments/reports/south_lhonak_insar_measurability_report.md)
* **Quantitative JSON Metrics:** [`results/measurability_metrics.json`](results/measurability_metrics.json)

---

## 5. Limitations

1. **Snapshot Sample:** Based on three single 12-day pilot pairs in September and May 2023. Monsoon peak and winter snowpack coherence were not tested.
2. **Spatial Ramp Extrapolation:** Removing a planar ramp from bedrock points reduces apparent noise, but assuming that the plane continues across the 3 km mountain valley is unproven on single pairs.
3. **Analysis Boxes:** Feature polygons (`LATERAL-MORAINE-SCARP`) are digitized approximate analysis boxes, not surveyed ground boundaries.
4. **Single-Pair Detection Floor:** Single 12-day pairs cannot detect slow creep ($< 100\text{ mm/yr}$) due to atmospheric noise floors ($\sim 2 - 5\text{ mm}$). Multi-year time-series methods (SBAS / PS-InSAR) are required for slow deformation monitoring.
5. **Phase 4 Stubs:** Multi-temporal CUSUM anomaly detection and regional hindcasting are relocated to `src/future_work/` outside active pytest collection.

---

## 6. How to Run & Verify

```bash
# 1. Run all 19 automated unit tests (analytic planes, 2D raster grid, HyP3 sign, lake aspect, invariants, sync)
python -m pytest tests/

# 2. Regenerate observability maps, sensitivity indices, joint inversion, and figures
python src/analysis/compute_insar_measurability.py
```

---

## 7. Key References

1. **Mohanty et al. (2026):** Sequence of events that led to the South Lhonak lake outburst flood in Sikkim, India. *Scientific Reports*, 16:9741. DOI: [10.1038/s41598-026-35895-7](https://doi.org/10.1038/s41598-026-35895-7).
2. **National Remote Sensing Centre (NRSC) / ISRO (2023):** Special satellite flood report on South Lhonak Lake disaster mapping.

---

## 8. Data Attribution & License

* **License:** Released under the [MIT License](LICENSE).
* **Copernicus Sentinel Data:** Contains modified Copernicus Sentinel-1 and Sentinel-2 data (2023) processed by ESA and accessed through ASF HyP3.
* **Copernicus DEM (GLO-30):** © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018 provided under Copernicus Programme by EU and ESA.
* **Data Manifest:** See [`data/README.md`](data/README.md) for full scene IDs, perpendicular baselines, and download procedures.

---

## 9. AI Assistance Disclosure

Analysis code, verification test suites, and documentation were developed with AI coding assistants; all scientific derivations, sign conventions, and numerical results were audited and verified by the author.


