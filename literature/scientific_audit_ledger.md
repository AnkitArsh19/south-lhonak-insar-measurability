# Scientific Peer-Review & Audit Ledger

**Project:** Himalayan Glacial Lake Slope Deformation & Early Warning (South Lhonak GLOF Case Study)  
**Document Type:** Internal Scientific Audit & Peer-Review Reconciliation Ledger  
**Audit Date:** 23 October 2026  
**Status:** Phase 1 Exploratory Audit Completed; Ready for AI-Assisted Peer Review Verification  

---

## 1. Executive Summary & Purpose

This ledger documents a rigorous, unsparing peer audit of Phase 1 (Foundation, Exploratory Pilot InSAR, and Optical Baseline). In strict compliance with [`AGENTS.md`](file:///e:/Personal/iirs/AGENTS.md) (Rule #1: Scientific claims must have sources; Rule #5: Never silently discard results; Rule #6: Separation of inference levels), every discrepancy between reported values and physical ground truth is formally recorded with mathematical and physical verification. All numbers in this document are generated directly from [`multi_baseline_audit_metrics.json`](file:///e:/Personal/iirs/results/EXP001/multi_baseline_audit_metrics.json).

---

## 2. Itemized Audit & Resolution Matrix

| # | Domain | Audit Finding / Defect | Physical & Mathematical Reality | Corrective Action in Code / Data |
|---|---|---|---|---|
| **1** | **Lake Area (Pre-Event)** | Chat reported 132.4 ha "deep water core" and claimed it matched NRSC ~160 ha. | **Observational Hypothesis:** Glacial flour / suspended rock silt near the retreating glacier snout raises optical RGB values to 180–190 (milky water). Simple RGB / NDWI thresholding misses this turbid water, giving a ~20% negative bias.<br>**Static Mask vs Empirical SAR:** The HyP3 `water_mask.tif` is a **static external layer (ESA WorldCover 2020/2021 + OSM)** measuring **151.68 ha**, reflecting ~2020 lake extent prior to the ~45% calving expansion documented by Qu et al. (2025) through late 2023. | **Full Sensitivity Curve Committed:** Rather than tuning a single threshold, we report the complete C-band backscatter sensitivity curve for connected water pixels in the basin:<br>- $-12\text{ dB}$: 177.92 ha<br>- $-13\text{ dB}$: 163.84 ha<br>- $-14\text{ dB}$: 158.08 ha<br>- $-15\text{ dB}$: 151.04 ha<br>- $-16\text{ dB}$: 137.60 ha<br>- $-17\text{ dB}$: 116.48 ha<br>**Official NRSC Sensor Provenance:**<br>- 17-Sep-2023: **162.7 ha** (RISAT-1A SAR)<br>- 28-Sep-2023: **167.4 ha** (Sentinel-1A SAR) |
| **2** | **Lake Area (Post-Event)** | Chat reported 0.1 ha, then 77.5 ha, then 65.6 ha via iterative tuning. Earlier `LAKE-POST` polygon extended west to 88.1765°E, placing 24.57 ha outside `LAKE-PRE`. | **NRSC Official Report:** 60.3 ha remaining on 04-Oct-2023 at 06:00 IST (RISAT-1A SAR), with ~105 ha drained (~64% area fraction loss). A post-event residual pool cannot physically lie outside the pre-event lake basin. | **Relabeled & Contained LAKE-POST:** Relabeled `LAKE-POST` as a schematic reference polygon (`Glacial_Lake_Water_Body_Residual_Schematic`, status: `schematic_reference`) approximating the 60.3 ha NRSC benchmark. Adjusted coordinates so it is **100% geometrically contained within `LAKE-PRE`** (0.0 ha difference). Excluded from empirical evidence claims. |
| **3** | **Lake Polygon Elevation** | `data_audit.md` reported lake polygon elevation mean 5,405 m with a range of 5,121 to 5,672 m. | A lake surface is an equipotential surface under gravity. In Copernicus GLO-30 DEM, South Lhonak lake core is flat at **5,162–5,165 m**. High elevations occurred where glacier ice was present when TanDEM-X data was acquired (2011–2015). | Updated lake elevation property to **5,165 masl**. Added automated physical equipotential unit test in `tests/test_vector_features.py` verifying DEM flatness ($\sigma < 15\text{ m}$) across the lake polygon. |
| **4** | **Scarp Target vs Outlet Breach** | Extraction script sampled `MORAINE-BREACH` at `(27.915°N, 88.208°E)`, yielding elevation 5,189 m (lake waterline). | **Geomorphic Disambiguation (External Literature):**<br>1. *Failure Trigger Mass (`LATERAL-MORAINE-SCARP`):* Left/northern lateral moraine ($27.918^\circ - 27.924^\circ\text{N}$, $88.203^\circ - 88.212^\circ\text{E}$, elevation 5,220–5,450 m, area 43.61 ha). Collapsed into the lake triggering impulse waves (Mohanty et al., 2026, *Sci. Rep.*, 16:9741).<br>2. *Outlet Breach (`FRONTAL-DAM-BREACH`):* Terminal moraine dam at eastern outlet ($27.908^\circ - 27.915^\circ\text{N}$, $88.208^\circ - 88.215^\circ\text{E}$, elevation ~5,190–5,205 m, area 25.08 ha) overtopped and deeply incised by the wave. | Separated `LATERAL-MORAINE-SCARP` from `FRONTAL-DAM-BREACH` in `south_lhonak_aoi.geojson`. Samples for InSAR slope deformation are extracted on the lateral moraine failure scarp at 5,295 m (mid-scarp) and 5,374 m (crest). Added disjointness unit test in `tests/test_vector_features.py`. |
| **5** | **InSAR Reference Ambiguity** | Chat claimed "$-35\text{ mm}$ raw LOS displacement proves atmospheric phase screen". | **Exact Metadata Provenance:** Official HyP3 GAMMA metadata XML (`<idAbs>` in `S1AA_..._unw_phase.tif.xml`) confirms that unwrapped phase was referenced to the maximum coherence seed pixel at **28.07152144°N, 88.18960631°E** (17.4 km north). Absolute single-pair LOS numbers are offsets relative to this seed and cannot be interpreted in isolation. Single-pixel differencing against `CTRL-01` (-9.11 mm) was also vulnerable to local ridge-top offset. | Formally record seed pixel coordinates. Implemented both single-pixel (`CTRL-01`) and **ensemble bedrock reference mean** ($\mu_{\text{bedrock}} = -9.97\text{ mm}$ across 119 points) differencing in `src/analysis/generate_three_pair_benchmark.py`. |
| **6** | **Spatial Noise & Dual Nulls** | Single $z$-score ($z=1.36$) under the raw pairwise null ignored the large-scale spatial ramp across the bedrock ridge. If detrended, $z$ reaches ~3.3. | **Geostatistical Reality:** The empirical semivariogram $\gamma(h)$ across the 5.5 km bedrock ridge climbs continuously from $0.22\text{ mm}^2$ to $4.26\text{ mm}^2$, demonstrating a strong spatial trend. Under a planar-detrended null ($\sigma_{\text{detrend}} = 0.78\text{ mm} \implies \sqrt{2}\sigma = 1.10\text{ mm}$), $z \approx 3.3 - 4.1$. However, single interferograms cannot prove whether this ramp extrapolates across the 3 km valley to the lateral moraine. | Report **both nulls side-by-side** in the benchmark report and JSON: Raw pairwise null ($z = 1.36$) vs Planar-detrended null ($z = 3.29$). Softened conclusion: statistical significance is model-dependent and inconclusive on single pairs. |
| **7** | **Positive Control Defect** | Feature `ACT-01` (glacier terminus) showed no excess line-of-sight signal, leaving no working positive control. | Active glacier ice can suffer phase aliasing/decorrelation or flow perpendicular to the radar look vector, suppressing LOS projection. A controlled benchmark must verify pipeline sensitivity. | Added a **synthetic phase injection test** (+15.0 mm localized fringe injected into the scarp ROI). Recovery is verified at **$15.00\text{ mm}$** ($0.00\text{ mm}$ error, status: `PASSED`). |
| **8** | **Pilot Experiment Status** | Pilot pairs were described as part of the pre-registered hindcast. | The pilot pairs were selected knowing the disaster date (5 and 8 days prior to failure). This is an exploratory sample, not a blind pre-registered test. | Formally classify Pilots 1, 2, and 3 as **Phase 1 Exploratory Feasibility**. The true leave-future-out benchmark will freeze all thresholds prior to evaluating the multi-year archive. |
| **9** | **HyP3 Credit Allocation** | Proposed generating 1,200 interferometric pairs on ASF HyP3. | Standard Earthdata HyP3 accounts have monthly credit limits (e.g. 1,000 credits/month, yielding 100 on-demand jobs at 10 credits/job). | Standardized on a targeted small-baseline network of **~100–120 pairs** per track for Phase 2, focusing on dry season and annual coherence bridges. |

---

## 3. Mathematical & Empirical Formulations

### 3.1 Cramér–Rao Bound (Theoretical Lower Bound on Decorrelation Noise)
For an interferogram with multilook factor $L$ and interferometric coherence $\gamma$, the Cramér–Rao lower bound on phase standard deviation is:
$$\sigma_{\phi} = \frac{1}{\sqrt{2L}} \frac{\sqrt{1 - \gamma^2}}{\gamma} \quad [\text{radians}]$$

For our processed Sentinel-1 products (20 range looks $\times$ 4 azimuth looks $\implies L = 80$):
* On the **Bedrock Control (`CTRL-01`)** with $\gamma = 0.985$: $\sigma_{\text{CR}} = \mathbf{0.06\text{ mm}}$
* On the **Mid-Slope Scarp** with $\gamma = 0.969$: $\sigma_{\text{CR}} = \mathbf{0.09\text{ mm}}$
* On the **Lower Moraine Flank** with $\gamma = 0.795$: $\sigma_{\text{CR}} = \mathbf{0.27\text{ mm}}$

> [!IMPORTANT]
> The Cramér–Rao bound is an idealized **lower bound on phase decorrelation noise**, NOT the total InSAR noise floor. In mountainous terrain, spatial phase variance is heavily dominated by turbulent and stratified tropospheric delays.

### 3.2 Dual-Null Hypothesis Framework & Semivariogram Metrics
The table below reports the audited values from [`multi_baseline_audit_metrics.json`](file:///e:/Personal/iirs/results/EXP001/multi_baseline_audit_metrics.json):

| Pilot Pair | Granule ID | Bedrock Pts ($N$) | Bedrock Ensemble Mean ($\mu$) | Raw Spatial $\sigma$ | Detrended $\sigma$ | Raw Null Spread (3.2 km) | Detrended Null Spread ($\sqrt{2}\sigma_{\text{det}}$) | Scarp Diff (vs CTRL01 / vs Ensemble) | Raw Null $z$-score (CTRL01 / Ensemble) | Detrended Null $z$-score (CTRL01 / Ensemble) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Pilot 1 (Desc Sept)** | `..._48B4` | 119 | $-9.97\text{ mm}$ | $1.62\text{ mm}$ | $0.78\text{ mm}$ | $2.66\text{ mm}$ | $1.10\text{ mm}$ | $+3.63\text{ mm}$ / $+4.49\text{ mm}$ | **$1.36$** / **$1.69$** | **$3.29$** / **$4.07$** |
| **Pilot 2 (Asc Sept)** | `..._C8DE` | 116 | $-35.06\text{ mm}$ | $2.65\text{ mm}$ | $1.75\text{ mm}$ | $3.08\text{ mm}$ | $2.47\text{ mm}$ | $+1.42\text{ mm}$ / $+1.08\text{ mm}$ | **$0.46$** / **$0.35$** | **$0.57$** / **$0.44$** |
| **Pilot 3 (Desc May)** | `..._3DA0` | 121 | $+13.93\text{ mm}$ | $1.60\text{ mm}$ | $1.37\text{ mm}$ | $2.31\text{ mm}$ | $1.94\text{ mm}$ | $+3.16\text{ mm}$ / $+2.71\text{ mm}$ | **$1.37$** / **$1.17$** | **$1.63$** / **$1.40$** |

---

## 4. Official Literature Ground-Truth Baseline

All comparisons must cite and validate against these verified primary sources:

1. **National Remote Sensing Centre (NRSC) / ISRO Assessment (October 2023):**
   * *Pre-event lake area (RISAT-1A SAR):* **162.7 ha** (17-Sep-2023).
   * *Pre-event lake area (Sentinel-1A SAR):* **167.4 ha** (28-Sep-2023).
   * *Post-event lake area (RISAT-1A SAR):* **60.3 ha** (04-Oct-2023, 06:00 IST).
   * *Drained lake area:* **107.1 ha** (~64% area fraction loss; volume loss not measured directly).
2. **Mohanty et al. (Scientific Reports, 2026, 16:9741, DOI: 10.1038/s41598-026-35895-7):**
   * *Failure initiation:* Collapse of the left lateral moraine flank above the lake, generating impulse waves that breached the frontal dam.
   * *Volume estimates:* Reports $\sim 38.31\text{ million m}^3$ debris volume plus $\sim 7\text{ million m}^3$ ice calving. (Compared to $\sim 14.7\text{ million m}^3$ in Sattar et al. / Science report).
   * *Geomorphic sanity check:* Over our mapped 43.61 ha lateral moraine failure scarp polygon, these volume estimates imply a mean slab thickness of $\sim 88\text{ m}$ (for $38.3\text{M m}^3$) vs $\sim 34\text{ m}$ (for $14.7\text{M m}^3$).
3. **Qu et al. (2025; cited in EGU 2026 abstract):**
   * *Expansion rate:* Lake expanded by ~45% from ~1.12 km² to 1.63 km² between 2016 and late 2023 due to calving retreat of South Lhonak glacier.
   * *Pre-event InSAR:* Sentinel-1 SBAS time-series detected persistent subsidence along the fringing lateral moraines prior to the 2023 collapse, providing an independent external benchmark for our planned SBAS hindcast.

---

## 5. Independent Geometric & Physical Invariant Unit Tests

All 6 automated unit tests in [`tests/test_vector_features.py`](file:///e:/Personal/iirs/tests/test_vector_features.py) execute and pass independently:
1. `test_lake_post_contained_in_lake_pre`: Proves geometric containment using Shapely in UTM projection (0.00 ha difference area outside pre-event basin).
2. `test_lake_post_schematic_labeling`: Confirms explicit schematic labeling and exclusion from empirical evidence claims.
3. `test_dem_flatness_in_lake_core`: Confirms equipotential surface flatness on Copernicus GLO-30 DEM ($\sigma < 15\text{ m}$, mean ~5171 m).
4. `test_sar_backscatter_water_fraction`: Confirms C-band physical specular reflection ($99.7\%$ of lake pixels with $\sigma^0 < -12\text{ dB}$).
5. `test_scarp_and_breach_separation`: Confirms topological disjointness between lateral moraine trigger scarp and terminal breach.
6. `test_ctrl02_decorrelated_dropped`: Confirms low-coherence control point removed.
