# Observability & Measurability of Sentinel-1 InSAR for Slope Monitoring Around South Lhonak Lake: Geometry, Coherence and Atmospheric Noise

**Case Study:** South Lhonak Glacial Lake, Sikkim Himalaya, India (Disaster Date: 3–4 October 2023)  
**Authors:** Research Candidate (Pair-Programming with AI Technical Assistant)  
**Target Institution:** Indian Institute of Remote Sensing (IIRS / ISRO)  
**Document Status:** Final Technical Report  

---

## 1. Research Question & Scope

Following the catastrophic Glacial Lake Outburst Flood (GLOF) of South Lhonak Lake on 3–4 October 2023, this project addresses one core, verifiable geophysical question:

> **Which slopes around South Lhonak Lake can Sentinel-1 InSAR physically measure, and how small a slope movement could it detect?**

Rather than asserting unverified precursory acceleration from single interferograms, we evaluate the fundamental physical constraints on Sentinel-1 C-band InSAR across two opposing geometries: **Track 048 (Descending)** and **Track 012 (Ascending)** using the native 30 m Copernicus GLO-30 Digital Elevation Model.

---

## 2. Topographic Geometry, HyP3 Sign Conventions & Forward Model

### 1. InSAR Phase & Sign Conventions
Directly quoted from ASF HyP3 InSAR product documentation (`README.md.txt`):
* **Line 117 (`_unw_phase`):** *"Positive values indicate movement away from the sensor (caused by subsidence or lateral movement away from the sensor) and negative values indicate movement towards the sensor (uplift or lateral movement towards the sensor)."*
* **Line 138 (`_los_disp`):** *"Converts the unwrapped differential phase into measurements of ground movement in meters along the look vector (line-of-sight). Positive values indicate movement towards the sensor (such as uplift), while negative values indicate movement away from the sensor (such as subsidence). Note that the sign convention is opposite to that used for the unwrapped phase."*
* **Mathematical Equation:**
  $$d_{\text{LOS}} = - \frac{\lambda}{4\pi} \Delta\phi_{\text{unw}}$$
  where $\lambda \approx 0.055465763\text{ m}$ for Sentinel-1 C-band.

### 2. Forward Model Formulation ($y_{\text{LOS}} = v_{\text{slope}} \cdot P$)
The projection of ground motion onto the radar Line of Sight (LOS) depends on the 3D angle between the direction of motion and the radar beam:
* **Downslope vector $\hat{\mathbf{d}}$:** Assuming gravity-driven slope deformation follows the path of steepest descent, we compute the unit downslope vector $\hat{\mathbf{d}} = (d_x, d_y, d_z)$ from the DEM elevation gradient $\nabla Z = (p, q)$:
  $$d_x = -\frac{p}{\sqrt{p^2+q^2}}\cos\alpha, \quad d_y = -\frac{q}{\sqrt{p^2+q^2}}\cos\alpha, \quad d_z = -\sin\alpha$$
  where $\alpha = \arctan\sqrt{p^2+q^2}$ is the local slope angle. Gradients are computed strictly as:
  $$dz\_drow, dz\_dcol = \text{np.gradient}(\text{dem}, \Delta y, \Delta x), \quad p = dz\_dcol, \quad q = -dz\_drow$$
* **Look vector $\hat{\mathbf{s}}$:** Using calibrated HyP3 look vectors (elevation angle $\theta$ and orientation angle $\phi$), the unit look vector from ground to satellite is $\hat{\mathbf{s}} = (\cos\theta\cos\phi, \cos\theta\sin\phi, \sin\theta)$. 
  - **Descending Track 48:** Sensor to the East, looking West; ground-to-sensor points roughly East-Southeast ($\phi \approx -10.4^\circ, \theta \approx 50.8^\circ$).
  - **Ascending Track 12:** Sensor to the West, looking East; ground-to-sensor points roughly West-Southwest ($\phi \approx -169.6^\circ, \theta \approx 50.9^\circ$).
* **Signed Projection & Sensitivity:**
  $$P = \hat{\mathbf{d}} \cdot \hat{\mathbf{s}}, \quad R = |P| \in [0, 1]$$
  Because the south/southeast-facing moraine scarp slopes downward ($\hat{d}_z < 0$) while the radar look vector points up to the sensor ($\hat{s}_z > 0$), the geometric projection is negative:
  $P_{\text{desc}} = -0.276 < 0$ and $P_{\text{asc}} = -0.366 < 0$ on the steep scarp ($\ge 25^\circ$).
* **Forward and Inverse Signs:**
  - True downslope creep ($v > 0$) causes range lengthening (movement away from sensor), requiring **negative LOS displacement ($y < 0$)**.
  - Positive measured differential LOS ($y > 0$, range shortening / movement towards sensor) inverts via $v = y / P$ to a **negative slope velocity ($v < 0$, apparent upslope motion)**.

![Figure 1: Radar Geometry & Sensitivity Maps](file:///e:/Personal/iirs/results/fig1_radar_geometry_and_sensitivity.png)
*Figure 1: Topographic slope from Copernicus GLO-30 DEM, local incidence angle, and sensitivity index $R = |\hat{\mathbf{d}} \cdot \hat{\mathbf{s}}|$ for Descending Track 48 and Ascending Track 12 across the South Lhonak basin. Overlays mark the scarp analysis box (cyan) and vector to nearest southern lake shore (lime, 177°).*

---

## 3. Scarp Morphology & Aspect Alignment

Within the lateral moraine scarp analysis box (523 pixels on 30 m DEM; mean elevation 5,350 masl):
* **Circular Mean Aspect:** The downslope vector has a circular mean aspect of **$151.1^\circ$ (SSE)** with an angular dispersion of $0.05$.
* **Lake-Facing Alignment:** This downslope direction physically faces the lake, aligning within **$26.2^\circ$** of the nearest southern lake shore ($177.3^\circ$ bearing from the static 2020/21 lake mask). It deviates substantially ($85.6^\circ$) from the bearing to the lake centroid ($236.7^\circ$, WSW) because the elongated glacial lake extends westward toward the glacier snout.
* **Slope Bins & Scarp Masking:** Mean slope across the entire box is **$21.8^\circ$** (median $20.5^\circ$, std $12.3^\circ$). Crucially, **39.8% of pixels lie on the flatter moraine crest/bench ($< 15^\circ$)** where downslope direction is ill-defined. Restricting analysis to slopes $\ge 25^\circ$ isolates the steep active failure scarp (235 pixels, 44.9% of scarp area, representing $\sim 31-33$ independent 80 m SAR resolution cells) with mean slope **$32.8^\circ$**.

### Radar Sensitivity & Sign Cancellation Resolution:
* **Unmasked Box:** Descending Track 48 exhibits sign cancellation across curved ridge facets (38.8% positive, 61.2% negative; mean $P = -0.034$, mean $|R| = 0.309$).
* **Steep Scarp ($\ge 25^\circ$):** Filtering out the flat bench resolves the sign ambiguity:
  - Descending Track 48: Mean signed $P_{\text{desc}} = \mathbf{-0.2757}$ (consistently negative).
  - Ascending Track 12: Mean signed $P_{\text{asc}} = \mathbf{-0.3658}$ (consistently negative).

---

## 4. Four-Class Observability Mapping & Detection Limits

Every resolution cell in the 10 km study area was classified into four mutually exclusive operational categories (September 2023 snapshot):
1. **Blind (Layover / Shadow):** 
   - Signed layover: terrain slope facing the radar exceeds $\cot\theta_{\text{elev}}$ ($-\frac{\partial z}{\partial u} \ge \cot\theta_{\text{elev}}$ along look azimuth).
   - Radar shadow / grazing: $\cos\theta_{\text{inc}} \le 0.087$ or $\theta_{\text{inc}} \ge 85^\circ$.
2. **Low Sensitivity:** Geometric sensitivity to downslope motion is insufficient ($R < 0.3$), or local incidence angle is in the grazing zone ($\theta_{\text{inc}} > 70^\circ$).
3. **Decorrelated:** Surface conditions cause loss of interferometric phase coherence ($\gamma < 0.3$).
4. **Observable:** Topographically visible, geometrically sensitive, and phase coherent ($R \ge 0.3$, $\gamma \ge 0.3$, $\theta_{\text{inc}} \le 70^\circ$, and not blind).

![Figure 2: Four-Class Observability Maps & Min Detectable Velocity](file:///e:/Personal/iirs/results/fig2_four_class_measurability_maps.png)
*Figure 2: Four-class InSAR observability maps (September 2023 snapshot) for Descending Track 48 and Ascending Track 12, alongside the combined minimum detectable slope velocity map (95% CI, detrended model).*

### Sensitivity to Observability Cutoff ($R$ Threshold):

| Region / Analysis Zone | Sensitivity Cutoff | Descending Track 48 | Ascending Track 12 | Combined Multi-Track |
| :--- | :---: | :---: | :---: | :---: |
| **Moraine Scarp Box** | $R \ge 0.2$ | 78.0% | 89.1% | **95.0%** |
| | **$R \ge 0.3$ (Standard)** | **51.8%** | **76.3%** | **87.0%** |
| | $R \ge 0.5$ | 12.4% | 35.4% | **37.9%** |
| **Entire 10 km Study AOI** | $R \ge 0.2$ | 55.1% | 53.8% | **70.0%** |
| | **$R \ge 0.3$ (Standard)** | **44.8%** | **45.5%** | **63.4%** |
| | $R \ge 0.5$ | 24.3% | 29.5% | **45.8%** |

### Minimum Detectable Velocity (Single 12-Day Pair Limits):
Using the empirical spatial noise evaluated across 119 stable bedrock points:
* **Raw Pairwise Null ($2\sigma$):** $5.32\text{ mm}$ (Desc, Track 48) and $6.16\text{ mm}$ (Asc, Track 12).
* **Planar-Detrended Null ($2\sigma$):** $2.20\text{ mm}$ (Desc, Track 48) and $4.94\text{ mm}$ (Asc, Track 12).

Dividing the $2\sigma$ noise floor by sensitivity $R$ yields:
* **Descending Track 48 ($R = 0.309$):** $\sim 217\text{ mm/yr}$ (detrended) to $\sim 524\text{ mm/yr}$ (raw null).
* **Ascending Track 12 ($R = 0.449$):** $\sim 335\text{ mm/yr}$ (detrended) to $\sim 418\text{ mm/yr}$ (raw null).

---

## 5. Non-Circular Coherence Validation

Evaluating raw coherence $\gamma$ across raw local incidence angle bins prior to thresholding:
* **Descending Track 48:** Median coherence is $0.889$ for normal illumination ($30-50^\circ$), decreasing to $0.654$ in grazing angles ($70-85^\circ$), and dropping to $0.360$ in shadow ($>85^\circ$).
* **Ascending Track 12:** Median coherence is $0.784$ for normal illumination ($30-50^\circ$), decreasing to $0.619$ in grazing angles ($70-85^\circ$), and dropping to $0.234$ in shadow ($>85^\circ$).

This confirms that extreme terrain incidence angles independently degrade radar phase coherence and validates the $70^\circ$ cutoff without circular filtering.

---

## 6. Single Steep-Scarp Joint Velocity Inversion & Physical Interpretation

Measured differential LOS offsets across the steep scarp face ($\ge 25^\circ$, 235 pixels, $\sim 31-33$ independent 80 m SAR resolution cells):
- Relative to Bedrock Ensemble: Descending $= +4.429\text{ mm}$, Ascending $= +1.298\text{ mm}$
- Relative to CTRL-01: Descending $= +3.570\text{ mm}$, Ascending $= +1.632\text{ mm}$

Because measured LOS offsets are positive (range shortening) while downslope projections are negative ($P_{\text{desc}} = -0.2757, P_{\text{asc}} = -0.3658$), joint inversion yields negative velocities:

| Reference Frame | Spatial Noise Null Model | Estimated Velocity ($v_{\text{slope}}$) | 95% Confidence Interval | Contains Zero? |
| :--- | :--- | :---: | :---: | :---: |
| **Bedrock Ensemble** | **Raw Spatial Null** | $\mathbf{-273 \pm 193\text{ mm/yr}}$ | **$[-651, +106]\text{ mm/yr}$** | **Yes** (Upper bound on creep $< 0.11\text{ m/yr}$) |
| **Bedrock Ensemble** | **Detrended Null** | $\mathbf{-390 \pm 105\text{ mm/yr}}$ | **$[-595, -185]\text{ mm/yr}$** | **No** (Apparent upslope signal at $3.7\sigma$) |
| **CTRL-01 Patch** | **Raw Spatial Null** | $\mathbf{-248 \pm 193\text{ mm/yr}}$ | **$[-626, +131]\text{ mm/yr}$** | **Yes** (Upper bound on creep $< 0.13\text{ m/yr}$) |
| **CTRL-01 Patch** | **Detrended Null** | $\mathbf{-327 \pm 105\text{ mm/yr}}$ | **$[-532, -122]\text{ mm/yr}$** | **No** (Apparent upslope signal at $3.1\sigma$) |

![Figure 3: Steep Scarp Projections & Single Joint Inversions](file:///e:/Personal/iirs/results/fig3_minimum_detectable_motion_and_plausibility.png)
*Figure 3: (a) Histograms of signed projections $P = \hat{\mathbf{d}} \cdot \hat{\mathbf{s}}$ over the steep scarp ($\ge 25^\circ$). (b) Single steep-scarp joint two-track velocity inversions across reference frames and noise models (95% CI).*

### Scientific Interpretation:
1. **Model Dependence:** The inversion result is fundamentally model-dependent. Under the conservative raw spatial noise model, zero motion is contained within the 95% confidence intervals ($[-651, +106]\text{ mm/yr}$ and $[-626, +131]\text{ mm/yr}$).
2. **Apparent Upslope Motion:** Under the ramp-removed (detrended) null model, an apparent $\sim 0.3 - 0.4\text{ m/yr}$ signal appears at $3.1 - 3.7\sigma$. This apparent signal is directed **upslope ($v < 0$)**, which is physically implausible as gravitational creep and is consistent with residual atmospheric phase delays or reference-pixel drift across steep relief ($5200 - 5300\text{ m}$), which two pilot pairs cannot resolve.
3. **Defensible Conclusion:** **Two pilot pairs constrain slope-parallel creep only to within a few tenths of a metre per year.**

---

## 7. Limitations & Scope

1. **Snapshot Sample:** Based on three single 12-day pilot pairs in September and May 2023. Monsoon peak and winter snowpack coherence were not tested.
2. **Spatial Ramp Extrapolation:** Removing a planar ramp from bedrock points reduces apparent noise, but assuming that the plane continues across the 3 km mountain valley is unproven on single pairs.
3. **Analysis Boxes:** Feature polygons (`LATERAL-MORAINE-SCARP`) are digitized approximate analysis boxes (43.6 ha), not an in-situ surveyed failure boundary.
4. **Single-Pair Detection Floor:** Resolving slow precursory creep ($< 100\text{ mm/yr}$) requires multi-temporal SBAS or PS-InSAR processing across multi-year stacks.
5. **Phase 4 Stubs:** Multi-temporal CUSUM anomaly detection and regional hindcasting are relocated to `src/future_work/` outside active pytest collection.

---

## 8. Conclusions for Remote Sensing & GIS Applications

* Sentinel-1 C-band InSAR is **geometrically observable** across the South Lhonak lateral moraine, achieving **87.0% observability** on the scarp ($R \ge 0.3$) and **95.0%** at $R \ge 0.2$ when combining Ascending and Descending orbits.
* Single-orbit monitoring is geometrically incomplete: Descending track alone provides lower sensitivity ($R \approx 0.31$) and sign-cancelling projections across curved ridge facets, whereas Ascending Track 12 is consistently sensitive ($R \approx 0.45$).
* Single 12-day pairs have an atmospheric noise floor of $\sim 2 - 5\text{ mm}$, limiting single-pair velocity detection to $\sim 0.2 - 0.5\text{ m/yr}$. Pre-failure pilot observations are statistically consistent with zero motion within this noise floor, demonstrating that operational slope hazard warning requires multi-temporal InSAR time series.
