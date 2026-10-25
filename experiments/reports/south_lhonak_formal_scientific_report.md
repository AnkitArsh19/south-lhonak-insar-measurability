# Geometric Observability and Measurability Limits of Sentinel-1 C-Band InSAR for Periglacial Slope Hazard Monitoring: A Rigorous Post-Disaster Audit of the 2023 South Lhonak Glacial Lake Outburst Flood

**Author:** Research Candidate  
**Institutional Affiliation:** Indian Institute of Remote Sensing (IIRS / ISRO), Dehradun, India  
**Specialization:** Remote Sensing & GIS / Cryospheric Hazard Assessment  
**Date:** October 2026  
**Document Classification:** Formal Technical Monograph & Research Report  
**Associated Repository:** `south-lhonak-insar-measurability`  

---

## Abstract

On the night of 3–4 October 2023, a catastrophic Glacial Lake Outburst Flood (GLOF) originated from South Lhonak Lake in North Sikkim, India, draining approximately 105 hectares of the lake surface, breaching the terminal moraine, and destroying the downstream 1,200 MW Teesta-III hydroelectric project at Chungthang. Following this disaster, widespread claims emerged regarding whether Synthetic Aperture Radar (SAR) Interferometry (InSAR) could have provided operational early warning by detecting pre-collapse slope acceleration from single pre-event satellite passes. 

This monograph establishes an objective, mathematically rigorous assessment of the geometric observability and physical detection limits of Sentinel-1 C-band InSAR across the South Lhonak basin. Using the 30 m Copernicus GLO-30 Digital Elevation Model (DEM) and calibrated 3D radar look-vectors from ASF HyP3, we formulate an analytical forward projection model that maps gravity-driven slope motion onto the radar line-of-sight (LOS) across opposing orbital geometries: Descending Track 048 and Ascending Track 012. Resolving earlier sign-convention discrepancies, we demonstrate that the active failure scarp faces South-Southeast (circular mean aspect $151.1^\circ$, dispersion $0.05$), aligning within $26.2^\circ$ of the nearest southern lake shore. Because the scarp slopes downward while the radar look-vector points upward to the sensor, the geometric projection factor is negative ($P_{\text{desc}} = -0.276$, $P_{\text{asc}} = -0.366$). 

We introduce a four-class terrain categorization scheme (*Blind*, *Low Sensitivity*, *Decorrelated*, *Observable*). Under combined dual-track observation, **87.0%** of the active scarp face is observable at standard geometric sensitivity ($R = |P| \ge 0.3$), rising to **95.0%** at $R \ge 0.2$. However, empirical spatial noise evaluated across 119 stable bedrock reference patches reveals a $2\sigma$ noise floor of $2.20–6.16\text{ mm}$, imposing a single 12-day pair minimum detectable slope velocity of $200–500\text{ mm/yr}$ ($0.2–0.5\text{ m/yr}$). Joint two-track velocity inversion across the steep scarp ($\ge 25^\circ$, 235 DEM pixels, $\sim 31–33$ independent 80 m SAR resolution cells) yields $[-651, +106]\text{ mm/yr}$ (95% CI) under the conservative raw spatial null model, statistically containing zero motion. While a planar-detrended model yields an apparent signal ($-390 \pm 105\text{ mm/yr}$ at $3.7\sigma$), its vector orientation is directed *upslope*, which is physically implausible as gravitational creep and characteristic of unmodelled atmospheric phase screens.

Reconciling our findings with multi-year Persistent Scatterer InSAR (PS-InSAR) literature (Mohanty et al., 2026), which established a true background moraine creep rate of $\sim 22\text{ mm/yr}$, we demonstrate that **true precursory deformation is an order of magnitude smaller than the single-pair InSAR noise floor ($22\text{ mm/yr} \ll 200–500\text{ mm/yr}$)**. Consequently, single interferometric pairs cannot be used for operational early warning. We conclude that robust cryospheric hazard surveillance requires multi-temporal time-series processing (SBAS/PS-InSAR) and multi-frequency integration with L-band radar (NISAR).

**Keywords:** Sentinel-1 InSAR, South Lhonak Lake, Glacial Lake Outburst Flood (GLOF), Slope Measurability, Radar Geometry, Atmospheric Phase Noise, Cryospheric Hazards.

---

## 1. Introduction

High-mountain cryospheric systems across the Himalayas are experiencing accelerated warming, resulting in rapid glacial retreat, permafrost degradation, and the proliferation of unstable proglacial moraine-dammed lakes (Bolch et al., 2012; Nie et al., 2017). South Lhonak Lake, situated at an altitude of ~5,200 m above sea level (asl) in the Mangan district of North Sikkim, represents one of the most prominent examples of rapid lake expansion in the Eastern Himalaya. Between 1962 and 2023, the lake evolved from a small supraglacial pond ($0.11\text{ km}^2$) into a major proglacial water body spanning approximately $1.4\text{ km}^2$—a 12-fold expansion (Remya et al., 2025).

On the night of 3–4 October 2023, an estimated $11.5–38.3\text{ million m}^3$ lateral moraine failure detached from the steep left flank above the lake, generating a massive impulse wave that overtopped and breached the terminal moraine dam (Patlolla et al., 2025; Mohanty et al., 2026). The resulting flood wave propagated down the Lhonak Chu into the Teesta River basin, obliterating the 1,200 MW Teesta-III Chungthang hydroelectric project, washing away critical infrastructure, and resulting in extensive loss of life and property (NDMA, 2024).

```
+-----------------------------------------------------------------------------------+
|                            THE SOUTH LHONAK GLOF CASCADE                          |
|                                                                                   |
|  [Cryospheric Warming & Permafrost Melt]                                          |
|            |                                                                      |
|            v                                                                      |
|  [Slow Lateral Moraine Creep: ~22 mm/yr (Thawing Ice Cores)]                      |
|            |                                                                      |
|            v  (Trigger: Heavy Precipitation / Sudden Detachment)                  |
|  [Catastrophic Mass Detachment: 11.5 - 38.3 MCM Debris + 7.1 MCM Ice Calving]     |
|            |                                                                      |
|            v                                                                      |
|  [Impulse Displacement Wave Overtopping Terminal Moraine]                         |
|            |                                                                      |
|            v                                                                      |
|  [Breach & Evacuation of ~105 Hectares Lake Water (~43 - 54 MCM Total Surge)]     |
|            |                                                                      |
|            v                                                                      |
|  [Downstream Destruction: Teesta-III Hydroelectric Project at Chungthang]         |
+-----------------------------------------------------------------------------------+
```

Following this disaster, multiple retrospective studies were initiated to evaluate whether satellite remote sensing could have detected precursory slope destabilization. Synthetic Aperture Radar Interferometry (InSAR) is widely considered the premier geodetic technique for mapping ground displacement over inaccessible terrain (Bürgmann et al., 2000; Hanssen, 2001). However, the application of InSAR in extreme alpine topography is severely compromised by three physical limitations:
1. **Geometric Distortions:** Steep terrain causes severe foreshortening, layover, and radar shadowing, rendering large portions of mountain flanks geometrically blind.
2. **Temporal and Spatial Decorrelation:** High-altitude weather, snow cover, and loose debris cause rapid loss of interferometric phase coherence ($\gamma < 0.3$).
3. **Atmospheric Phase Screens (APS):** Spatially variable tropospheric water vapor creates synthetic phase ramps that mimic tectonic or gravitational displacement signals on single interferograms (Zebker et al., 1997; Doin et al., 2009).

In the aftermath of the event, conflicting assertions emerged in informal reports and preliminary audits. Some analyses claimed that precursory moraine acceleration was clearly visible in single Sentinel-1 interferograms immediately preceding the disaster, while others cautioned that such signals were indistinguishable from atmospheric noise. 

This monograph resolves this controversy by addressing one fundamental scientific question:
> **Which slopes around South Lhonak Lake can Sentinel-1 InSAR physically measure, and how small a slope movement could it detect?**

Rather than asserting premature conclusions from uncalibrated interferograms, we formulate a forward mathematical model based on 3D vector geometry, characterize empirical spatial noise on stable bedrock, evaluate multi-track observability, and reconcile single-pair sensitivity against long-term multi-year InSAR benchmarks.

---

## 2. Study Area, Multi-Sensor Datasets & Event Chronology

### 2.1 Geographic and Topographic Setting
The South Lhonak basin is situated in the Eastern Himalaya, bounded geographically between $88.15^\circ–88.25^\circ\text{ E}$ and $27.85^\circ–27.95^\circ\text{ N}$ (UTM Zone 45N, EPSG: 32645). The local topography exhibits extreme vertical relief, ranging from 4,800 m asl at the valley floor to over 6,800 m asl along the surrounding glacial ridges. South Lhonak Lake itself occupies an elevation of approximately 5,200 m asl at the terminus of the retreating South Lhonak Glacier.

```
Study Area Coordinates (Bounding Box WGS84):
  North: 27.95° N
  West:  88.15° E  ------ Center: 27.904° N, 88.201° E ------  East:  88.25° E
  South: 27.85° N
Elevation: ~4,800 m to 6,800 m asl (Mean Lake Level: ~5,200 m asl)
```

![Figure 4: Pre- and Post-Event Multi-Sensor Change Detection](file:///e:/Personal/iirs/results/fig4_optical_sar_pilot_alignment.png)  
*Figure 4: Multi-sensor optical and SAR change detection over South Lhonak Lake. (Top Left) Pre-event Sentinel-2 false-color composite showing the intact lake extent. (Top Right) Post-event Sentinel-2 composite following the 3–4 October 2023 outburst. (Bottom Left) Normalized Difference Water Index (NDWI) water mask delineating ~105 ha drained area. (Bottom Right) Aligned Sentinel-1 C-band interferometric coherence ($\gamma$) and differential unwrapped phase across the lateral moraine.*

### 2.2 Event Chronology and Published Volumetric Accounting
Multiple authoritative institutions and research groups have published independent assessments of the flood parameters, lake surface changes, and failure volumes:

| Institutional Source | Primary Sensor(s) | Estimated Debris Volume | Water Volume Loss / Surge | Drained Lake Surface Area |
| :--- | :--- | :---: | :---: | :---: |
| **ISRO / NRSC (2023)** | Sentinel-1A (28 Sep) & RISAT-1A (04 Oct) | — | — | **~105 hectares** (~64% of pre-event area) |
| **Patlolla et al. (2025, JWCC)** | Multi-sensor stereo photogrammetry | **11.50 MCM** | **43.21 MCM** loss / **54.71 MCM** total surge | — |
| **Mohanty et al. (2026, Sci. Rep.)** | Sentinel-1 PS-InSAR + PlanetScope | **38.31 MCM** debris + **7.11 MCM** ice | — | — |
| **Remya et al. (2025, ERC)** | Multi-decadal Landsat / Sentinel-2 | — | — | 12x area growth ($0.11 \to 1.4\text{ km}^2$) |
| **NDMA Sikkim Conclave (2024)** | National multi-agency synthesis | Tens of millions $\text{m}^3$ | Entire upper Teesta basin inundated | Teesta-III dam destroyed |

### 2.3 Satellite Radar & Elevation Datasets
To evaluate radar observability, we analyzed two complementary Sentinel-1 C-band Single Look Complex (SLC) interferometric wide-swath (IW) tracks processed via the Alaska Satellite Facility (ASF) HyP3 framework using Minimum Cost Flow (MCF) phase unwrapping and 30 m pixel posting:
1. **Descending Track 048:** Acquired on descending node (heading $\approx 190.4^\circ$, looking West-Northwest, incidence angle $\theta_{\text{inc}} \approx 34^\circ$). Pre-event pilot pair: 16 September 2023 to 28 September 2023 ($\Delta t = 12\text{ days}$, perpendicular baseline $B_\perp = -18.7\text{ m}$).
2. **Ascending Track 012:** Acquired on ascending node (heading $\approx 349.6^\circ$, looking East-Northeast, incidence angle $\theta_{\text{inc}} \approx 39^\circ$). Pre-event pilot pair: 13 September 2023 to 25 September 2023 ($\Delta t = 12\text{ days}$, perpendicular baseline $B_\perp = +44.1\text{ m}$).
3. **Copernicus GLO-30 DEM:** 30 m native resolution Digital Elevation Model from the Copernicus Data Space, providing topographic elevation ($Z$), slope angle ($\alpha$), and aspect ($\beta$).

---

## 3. Mathematical Framework & Forward Projection Modeling

### 3.1 InSAR Phase Decomposition and Sign Conventions
The measured differential interferometric phase $\Delta\phi_{\text{int}}$ at any ground resolution cell represents the summation of multiple physical and environmental components:
$$\Delta\phi_{\text{int}} = \Delta\phi_{\text{topo}} + \Delta\phi_{\text{disp}} + \Delta\phi_{\text{atm}} + \Delta\phi_{\text{orbit}} + \phi_{\text{noise}}$$

Following topographic phase removal using the Copernicus GLO-30 DEM and orbital baseline refinement, the residual unwrapped phase $\Delta\phi_{\text{unw}}$ is converted to Line-of-Sight (LOS) displacement $d_{\text{LOS}}$. 

Directly adhering to ASF HyP3 technical specifications:
* **Unwrapped Phase (`_unw_phase`):** Positive phase indicates movement *away* from the satellite (range increase / subsidence); negative phase indicates movement *towards* the satellite (range decrease / uplift).
* **LOS Displacement (`_los_disp`):** Defined opposite to phase:
  $$d_{\text{LOS}} = - \frac{\lambda}{4\pi} \Delta\phi_{\text{unw}}$$
  where $\lambda = 0.055465763\text{ m}$ is the radar carrier wavelength for Sentinel-1 C-band ($5.405\text{ GHz}$). Consequently:
  - $d_{\text{LOS}} > 0$: Range shortening (displacement towards the sensor).
  - $d_{\text{LOS}} < 0$: Range lengthening (displacement away from the sensor).

### 3.2 3D Slope Geometry and Steepest Descent Vectors
Assuming periglacial moraine creep is governed by gravity, slope deformation follows the 3D unit vector of steepest descent $\hat{\mathbf{d}} = (d_x, d_y, d_z)$ in the East-North-Up (ENU) coordinate frame. Let the topographic surface be defined by $Z(x, y)$. The local elevation gradients are:
$$p = \frac{\partial Z}{\partial x} = dz\_dcol, \quad q = \frac{\partial Z}{\partial y} = -dz\_drow$$
where $x$ increases Eastward, $y$ increases Northward, and row index increases Southward.

The terrain slope angle $\alpha$ and aspect $\beta$ are defined by:
$$\alpha = \arctan\left(\sqrt{p^2 + q^2}\right), \quad \beta = \text{atan2}(p, q) \pmod{360^\circ}$$

The unit downslope vector $\hat{\mathbf{d}}$ directed down the topographic gradient is:
$$\hat{\mathbf{d}} = \begin{pmatrix} d_x \\ d_y \\ d_z \end{pmatrix} = \begin{pmatrix} -\frac{p}{\sqrt{p^2 + q^2}} \cos\alpha \\ -\frac{q}{\sqrt{p^2 + q^2}} \cos\alpha \\ -\sin\alpha \end{pmatrix} = \begin{pmatrix} -\sin\beta \cos\alpha \\ -\cos\beta \cos\alpha \\ -\sin\alpha \end{pmatrix}$$

```
Topographic Gradient & Downslope Unit Vector (ENU):
       ^ North (y)
       |           . Downslope Vector d = (-sin(beta)*cos(alpha), -cos(beta)*cos(alpha), -sin(alpha))
       |          /
       |         /  Aspect angle beta (clockwise from North)
       |        /
       +-------> East (x)
      /
     v Up (z)   Note: Downslope vector strictly has d_z = -sin(alpha) < 0
```

### 3.3 Calibrated Sensor Look-Vector Geometry
The ground-to-sensor unit look-vector $\hat{\mathbf{s}} = (s_x, s_y, s_z)$ is defined by the radar elevation look angle $\theta$ (measured from the horizontal) and the horizontal orientation azimuth $\phi$ (measured counter-clockwise from East):
$$\hat{\mathbf{s}} = \begin{pmatrix} s_x \\ s_y \\ s_z \end{pmatrix} = \begin{pmatrix} \cos\theta \cos\phi \\ \cos\theta \sin\phi \\ \sin\theta \end{pmatrix}$$

From the ASF HyP3 calibrated geometry metadata over South Lhonak:
* **Descending Track 048:** Ground-to-sensor points East-Southeast ($\phi \approx -10.4^\circ$, $\theta \approx 50.8^\circ$, satellite heading $\approx 190.4^\circ$).
* **Ascending Track 012:** Ground-to-sensor points West-Southwest ($\phi \approx -169.6^\circ$, $\theta \approx 50.9^\circ$, satellite heading $\approx 349.6^\circ$).

### 3.4 Geometric Projection Factor and Sensitivity Index
The projection of 3D slope-parallel deformation velocity $v_{\text{slope}}$ onto the radar line-of-sight is governed by the scalar dot product:
$$P = \hat{\mathbf{d}} \cdot \hat{\mathbf{s}} = d_x s_x + d_y s_y + d_z s_z$$
$$y_{\text{LOS}} = v_{\text{slope}} \cdot P$$

The geometric sensitivity index is defined as the absolute magnitude of this projection:
$$R = |P| = |\hat{\mathbf{d}} \cdot \hat{\mathbf{s}}| \in [0, 1]$$
- When $R = 1$, the slope motion is perfectly collinear with the radar beam (maximum sensitivity).
- When $R = 0$, the slope motion is completely orthogonal to the radar beam (radar blind; zero sensitivity).

![Figure 1: Radar Geometry and Sensitivity Maps](file:///e:/Personal/iirs/results/fig1_radar_geometry_and_sensitivity.png)  
*Figure 1: Topographic slope from Copernicus GLO-30 DEM, local incidence angle ($\theta_{\text{inc}}$), and geometric sensitivity index ($R = |\hat{\mathbf{d}} \cdot \hat{\mathbf{s}}|$) for Descending Track 048 and Ascending Track 012 across the South Lhonak basin. Outlines highlight the lateral moraine failure scarp (cyan box) and the vector pointing to the nearest southern lake shore (lime vector, bearing 177.3°).*

### 3.5 Physical Resolution of the Sign Paradox
A critical insight emerges regarding the algebraic sign of $P$:
Because periglacial moraine scarps slope downward ($\hat{d}_z = -\sin\alpha < 0$) while the ground-to-satellite look-vector points upward ($\hat{s}_z = \sin\theta > 0$), the vertical component of the dot product is always negative ($d_z s_z < 0$). On south/southeast-facing slopes:
$$P_{\text{desc}} = -0.276 < 0, \quad P_{\text{asc}} = -0.366 < 0$$

Under the forward model $y_{\text{LOS}} = v_{\text{slope}} \cdot P$:
1. **Downslope Creep ($v_{\text{slope}} > 0$):** Produces a **negative LOS displacement ($y_{\text{LOS}} < 0$)**, corresponding to range lengthening (motion away from the satellite).
2. **Measured Positive LOS ($y_{\text{LOS}} > 0$):** If an interferogram records range shortening (positive LOS displacement), the inverted velocity $v_{\text{slope}} = y_{\text{LOS}} / P$ is **negative ($v < 0$)**, signifying apparent **upslope motion**.

Any analysis that fails to preserve this sign inversion will misinterpret range-shortening atmospheric artifacts as true downslope acceleration.

---

## 4. Empirical Spatial Noise Characterization & Detection Limits

### 4.1 Selection of Stable Bedrock Ensembles
In alpine environments, spatial phase variance is heavily corrupted by turbulent atmospheric water vapor and elevation-dependent stratification. To establish an empirical null distribution independent of moving periglacial features, we sampled **119 stable crystalline bedrock reference patches** across the South Lhonak basin. Bedrock patches were selected outside glacial tongues, active talus slopes, and alluvium.

```
Bedrock Reference Ensemble:
  - 119 independent patches across crystalline ridge crests
  - Mean elevation: 5,420 m asl
  - Distance from failure scarp: 1.5 km to 5.0 km
  - Standard reference point: CTRL-01 (Solid granitic bedrock spur, 27.915° N, 88.215° E)
```

### 4.2 Raw Pairwise Spatial Dispersion vs. Planar Ramp Detrending
We evaluated two empirical spatial noise null models:
1. **Raw Spatial Null Model:** Direct pairwise dispersion across bedrock patches without parameter fitting. This captures the true operational uncertainty faced by an automated monitoring pipeline.
2. **Planar-Detrended Null Model:** Fitting and removing a first-order spatial plane ($z = a x + b y + c$) across bedrock patches to simulate ideal linear tropospheric ramp correction.

| Sensor Track | Spatial Null Model | Bedrock Spatial Mean | Bedrock Spatial Dispersion ($1\sigma$) | Empirical Noise Floor ($2\sigma$, 95% CI) |
| :--- | :--- | :---: | :---: | :---: |
| **Descending Track 048** | **Raw Spatial Null** | $+0.42\text{ mm}$ | $\mathbf{2.66\text{ mm}}$ | $\mathbf{5.32\text{ mm}}$ |
| | **Planar Detrended** | $0.00\text{ mm}$ | $\mathbf{1.10\text{ mm}}$ | $\mathbf{2.20\text{ mm}}$ |
| **Ascending Track 012** | **Raw Spatial Null** | $-0.18\text{ mm}$ | $\mathbf{3.08\text{ mm}}$ | $\mathbf{6.16\text{ mm}}$ |
| | **Planar Detrended** | $0.00\text{ mm}$ | $\mathbf{2.47\text{ mm}}$ | $\mathbf{4.94\text{ mm}}$ |

### 4.3 Cramér-Rao Lower Bound on Phase Noise
To confirm that empirical dispersion reflects true atmospheric screens rather than radar instrument thermal noise, we computed the theoretical Cramér-Rao lower bound (CRB) on phase standard deviation $\sigma_{\phi}$:
$$\sigma_{\phi} \ge \frac{1}{\sqrt{2 N_L}} \frac{\sqrt{1 - \gamma^2}}{\gamma}$$
where $N_L \approx 40$ is the effective number of looks in the 80 m multilooked cell and $\gamma$ is the interferometric coherence. For high-coherence bedrock ($\gamma = 0.85–0.95$), the CRB yields:
$$\sigma_{\phi} \approx 0.038 - 0.088\text{ rad} \implies \sigma_{\text{inst}} \approx 0.06 - 0.26\text{ mm}$$

Because the observed spatial dispersion ($1\sigma \approx 2.66–3.08\text{ mm}$) is **an order of magnitude larger than the CRB instrument limit**, atmospheric turbulence and topographic stratification represent the overwhelming source of error in single pairs.

### 4.4 Analytical Formulation of Minimum Detectable Velocity ($v_{\text{min\_det}}$)
For a single interferogram spanning temporal baseline $\Delta t$ ($12\text{ days} = 0.03288\text{ yr}$) with geometric sensitivity $R$, the minimum slope velocity detectable at 95% confidence ($2\sigma$) is:
$$v_{\text{min\_det}} = \frac{2 \sigma_{\text{spatial}}}{R \cdot \Delta t}$$

* **Descending Track 048 ($R = 0.309$):**
  $$v_{\text{min\_det}} = \frac{2.20\text{ mm}}{0.309 \times 0.03288\text{ yr}} \approx \mathbf{217\text{ mm/yr}} \text{ (Detrended)} \quad \text{to} \quad \frac{5.32\text{ mm}}{0.309 \times 0.03288\text{ yr}} \approx \mathbf{524\text{ mm/yr}} \text{ (Raw)}$$
* **Ascending Track 012 ($R = 0.449$):**
  $$v_{\text{min\_det}} = \frac{4.94\text{ mm}}{0.449 \times 0.03288\text{ yr}} \approx \mathbf{335\text{ mm/yr}} \text{ (Detrended)} \quad \text{to} \quad \frac{6.16\text{ mm}}{0.449 \times 0.03288\text{ yr}} \approx \mathbf{418\text{ mm/yr}} \text{ (Raw)}$$

**Fundamental Finding:** Single 12-day Sentinel-1 pairs possess an intrinsic velocity detection threshold of **$200–500\text{ mm/yr}$ ($0.2–0.5\text{ m/yr}$)**.

---

## 5. Quantitative Results & Four-Class Observability Mapping

### 5.1 Scarp Topography & Lake-Facing Aspect Validation
The failure scarp analysis polygon spans 523 DEM pixels (43.6 ha) at a mean elevation of 5,350 m asl. Topographic decomposition demonstrates:
* **Circular Mean Aspect:** The downslope vector exhibits a circular mean aspect of **$151.1^\circ$ (SSE)** with an angular dispersion of $0.05$.
* **Lake-Facing Alignment:** This vector directly faces the lake basin, aligning within **$26.2^\circ$** of the nearest southern lake shore (bearing $177.3^\circ$).
* **Slope Bimodal Distribution:** Across the entire polygon, 39.8% of pixels reside on the flatter upper bench ($< 15^\circ$, mean slope $21.8^\circ$). Filtering for steep active slopes ($\ge 25^\circ$) isolates 235 pixels (44.9% of the area; $\sim 31–33$ independent 80 m SAR resolution cells) with a mean slope of **$32.8^\circ$**.

### 5.2 Resolution of Descending Track Sign-Cancellation
Across the unmasked box, Descending Track 048 displays sign cancellation (38.8% positive, 61.2% negative; mean $P = -0.034$) because the rounded upper crest tilts slightly northward toward the descending sensor. Isolating the steep failure face ($\ge 25^\circ$) resolves this ambiguity:
$$P_{\text{desc}} = \mathbf{-0.2757}, \quad P_{\text{asc}} = \mathbf{-0.3658}$$
Both orbital geometries are unambiguously negative, verifying that downslope movement produces line-of-sight range lengthening in both passes.

### 5.3 Four-Class Observability Mapping
Every resolution cell across the 10 km study area was classified into four mutually exclusive operational categories:
1. **Blind (Layover / Shadow):** Terrain slope facing the radar exceeds $\cot\theta_{\text{elev}}$ ($-\frac{\partial Z}{\partial u} \ge \cot\theta_{\text{elev}}$), or local incidence angle enters grazing shadow ($\theta_{\text{inc}} \ge 85^\circ$ or $\cos\theta_{\text{inc}} \le 0.087$).
2. **Low Sensitivity:** Geometric projection is insufficient ($R < 0.3$), or incidence angle is grazing ($70^\circ < \theta_{\text{inc}} < 85^\circ$).
3. **Decorrelated:** Interferometric coherence drops below unwrapping thresholds ($\gamma < 0.3$).
4. **Observable:** Topographically visible, geometrically sensitive, and phase coherent ($R \ge 0.3$, $\gamma \ge 0.3$, $\theta_{\text{inc}} \le 70^\circ$, not blind).

![Figure 2: Four-Class Observability and Minimum Detectable Velocity](file:///e:/Personal/iirs/results/fig2_four_class_measurability_maps.png)  
*Figure 2: (Left & Center) Four-class InSAR observability maps (September 2023 snapshot) for Descending Track 048 and Ascending Track 012. (Right) Combined minimum detectable slope velocity map ($v_{\text{min\_det}}$, 95% CI) showing spatial detection limits across the South Lhonak catchment.*

### 5.4 Sensitivity to Observability Cutoff ($R$ Threshold)
To assess operational margins, we varied the sensitivity threshold $R_{\text{crit}} \in [0.2, 0.5]$:

| Study Zone | Sensitivity Threshold | Descending Track 048 | Ascending Track 012 | Combined Multi-Track Observability |
| :--- | :---: | :---: | :---: | :---: |
| **Moraine Scarp Face** | $R \ge 0.2$ | 78.0% | 89.1% | **95.0%** |
| | **$R \ge 0.3$ (Standard)** | **51.8%** | **76.3%** | **87.0%** |
| | $R \ge 0.5$ | 12.4% | 35.4% | **37.9%** |
| **Entire 10 km Study Basin** | $R \ge 0.2$ | 55.1% | 53.8% | **70.0%** |
| | **$R \ge 0.3$ (Standard)** | **44.8%** | **45.5%** | **63.4%** |
| | $R \ge 0.5$ | 24.3% | 29.5% | **45.8%** |

**Key Takeaway:** Multi-track acquisition is essential. While Descending Track 048 observes only 51.8% of the scarp at $R \ge 0.3$, integrating Ascending Track 012 elevates overall scarp observability to **87.0%**.

---

## 6. Pre-Collapse Velocity Inversion & Plausibility Audit

### 6.1 Multi-Baseline Pilot Dataset Description
We analyzed three independent 12-day Sentinel-1 pilot pairs acquired during key seasonal windows:
* **PILOT-001 (Late Monsoon Descending Track 048, 16–28 Sep 2023):** $B_\perp = -18.7\text{ m}$. Mean scarp coherence $\gamma = 0.969$. Measured differential LOS offset relative to bedrock: $+4.43\text{ mm}$ (Ensemble), $+3.57\text{ mm}$ (CTRL-01).
* **PILOT-002 (Late Monsoon Ascending Track 012, 13–25 Sep 2023):** $B_\perp = +44.1\text{ m}$. Mean scarp coherence $\gamma = 0.941$. Measured differential LOS offset relative to bedrock: $+1.30\text{ mm}$ (Ensemble), $+1.63\text{ mm}$ (CTRL-01).
* **PILOT-003 (Pre-Monsoon Dry Descending Track 048, 07–19 May 2023):** $B_\perp = +8.86\text{ m}$. Mean scarp coherence $\gamma = 0.972$. Measured differential LOS offset relative to bedrock: $+3.16\text{ mm}$ (CTRL-01).

![Figure 5: Multi-Baseline Three-Pair InSAR Benchmark](file:///e:/Personal/iirs/results/fig5_three_pair_interferometric_benchmark.png)  
*Figure 5: Multi-baseline three-pair interferometric benchmark comparison across South Lhonak. (Left Column) Pilot 1 Late-Monsoon Descending Track 048. (Center Column) Pilot 2 Late-Monsoon Ascending Track 012. (Right Column) Pilot 3 Pre-Monsoon Dry Season Descending Track 048. Rows display unwrapped differential phase, LOS displacement, and coherence.*

### 6.2 Joint Ascending-Descending Inversion Formulation
Combining the ascending and descending observations over the steep scarp ($\ge 25^\circ$, 235 DEM pixels), the observation equations are:
$$\mathbf{y} = \mathbf{A} v_{\text{slope}} + \mathbf{e}, \quad \text{where } \mathbf{y} = \begin{pmatrix} y_{\text{desc}} \\ y_{\text{asc}} \end{pmatrix}, \quad \mathbf{A} = \begin{pmatrix} P_{\text{desc}} \cdot \Delta t_{\text{desc}} \\ P_{\text{asc}} \cdot \Delta t_{\text{asc}} \end{pmatrix}$$

Using weighted least squares with covariance matrix $\mathbf{\Sigma} = \text{diag}(\sigma_{\text{desc}}^2, \sigma_{\text{asc}}^2)$:
$$\hat{v}_{\text{slope}} = (\mathbf{A}^T \mathbf{\Sigma}^{-1} \mathbf{A})^{-1} \mathbf{A}^T \mathbf{\Sigma}^{-1} \mathbf{y}, \quad \sigma_v^2 = (\mathbf{A}^T \mathbf{\Sigma}^{-1} \mathbf{A})^{-1}$$

### 6.3 Inversion Results across Reference Frames & Noise Models

| Bedrock Reference Frame | Spatial Noise Null Model | Inverted Slope Velocity ($\hat{v}_{\text{slope}}$) | 95% Confidence Interval | Contains Zero ($v=0$)? | Statistical Interpretation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Bedrock Ensemble (119)** | **Raw Spatial Null** | $\mathbf{-273 \pm 193\text{ mm/yr}}$ | **$[-651, +106]\text{ mm/yr}$** | **Yes** | Consistent with zero motion; upper bound on creep $< 0.11\text{ m/yr}$. |
| | **Planar Detrended** | $\mathbf{-390 \pm 105\text{ mm/yr}}$ | **$[-595, -185]\text{ mm/yr}$** | **No** | Apparent signal at $3.7\sigma$; vector points *upslope*. |
| **CTRL-01 Spur (Single)** | **Raw Spatial Null** | $\mathbf{-248 \pm 193\text{ mm/yr}}$ | **$[-626, +131]\text{ mm/yr}$** | **Yes** | Consistent with zero motion; upper bound on creep $< 0.13\text{ m/yr}$. |
| | **Planar Detrended** | $\mathbf{-327 \pm 105\text{ mm/yr}}$ | **$[-532, -122]\text{ mm/yr}$** | **No** | Apparent signal at $3.1\sigma$; vector points *upslope*. |

![Figure 3: Scarp Projections and Joint Velocity Inversions](file:///e:/Personal/iirs/results/fig3_minimum_detectable_motion_and_plausibility.png)  
*Figure 3: (Left) Frequency distributions of signed projection factors ($P = \hat{\mathbf{d}} \cdot \hat{\mathbf{s}}$) over the steep active scarp ($\ge 25^\circ$) for Descending Track 048 and Ascending Track 012. (Right) Joint ascending-descending slope velocity inversions showing 95% confidence intervals across reference frames and noise models.*

### 6.4 Non-Circular Coherence Validation by Incidence Angle Bins
To confirm that terrain incidence angle thresholds are physically robust and not a circular artifact of coherence masking, we analyzed raw coherence $\gamma$ across incidence angle bins prior to applying any filters:

| Local Incidence Angle ($\theta_{\text{inc}}$) | Pixel Count | Area Fraction | Median Coherence ($\gamma_{\text{desc}}$) | Median Coherence ($\gamma_{\text{asc}}$) | Unwrapping Success Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **$0^\circ–30^\circ$ (Steep Illumination)** | 11,478 | 15.8% | 0.843 | 0.513 | 99.0% |
| **$30^\circ–50^\circ$ (Normal Illumination)** | 40,182 | 55.4% | **0.889** | **0.784** | 93.3% |
| **$50^\circ–70^\circ$ (Oblique Illumination)** | 16,653 | 22.9% | 0.815 | 0.754 | 98.8% |
| **$70^\circ–85^\circ$ (Grazing Angles)** | 3,748 | 5.2% | **0.654** | **0.619** | 99.4% |
| **$> 85^\circ$ (Shadow / Blind)** | 515 | 0.7% | **0.360** | **0.234** | 98.3% |

This confirms that extreme terrain angles independently degrade radar phase coherence, justifying the $\theta_{\text{inc}} \le 70^\circ$ cutoff without circular threshold tuning.

---

## 7. Scientific Reconciliation with Published Literature

### 7.1 Cross-Study Parameter Synthesis
To contextualize our findings within the broader literature, we compare our quantitative results with recent peer-reviewed investigations of South Lhonak Lake:

| Study Citation | InSAR Method & Dataset | Target Feature & Mechanism | Reported Deformation / Failure Parameter | Reconciliation with This Study |
| :--- | :--- | :--- | :--- | :--- |
| **Mohanty et al. (2026)**<br>*Scientific Reports* [16:9741](https://www.nature.com/articles/s41598-026-35895-7) | PS-InSAR stack (64 Sentinel-1 SLC scenes, 2017–2021) | Left lateral moraine; permafrost & buried ice melting | Long-term subsidence rate: **~22 mm/yr** (~2.2 cm/yr); **45.4 MCM** total collapse | Provides the true physical benchmark ($22\text{ mm/yr}$) for pre-event moraine creep. |
| **Yu et al. (2024)**<br>*Remote Sensing* [16(13):2307](https://www.mdpi.com/2072-4292/16/13/2307) | SBAS-InSAR stack (83 asc + 79 desc, 2021–2023) | Lateral moraine slope | Pre-event progressive displacement identified along scarp | Corroborates multi-year deformation, but lacks false-alarm testing or 3D look-vector bounds. |
| **Patlolla et al. (2025)**<br>*J. Water & Climate Change* [16(1):127](https://iwaponline.com/jwcc/article/16/1/127/106444/GLOF-in-the-South-Lhonak-Lake-India) | Multi-sensor single-image photogrammetric DEMs | Landslide scarp differencing | Debris into lake: **11.50 MCM**; Water volume loss: **43.21 MCM** | Verifies that lateral slope collapse displaced ~43 MCM of lake water, creating the GLOF. |
| **Remya et al. (2025)**<br>*Environ. Res. Commun.* [7:115026](https://publications.azimpremjiuniversity.edu.in/6933/1/913.%20S_N_2025_Environ._Res._Commun._7_115026.pdf) | Multi-decadal optical (10 satellite missions) | Glacier-lake-moraine interface | 12x lake growth; calving icebergs weakened lateral moraine | Identifies long-term cryospheric preparation leading to slope detachment. |
| **This Study (2026)**<br>*IIRS Technical Report* | Dual-track Sentinel-1 forward projection + noise audit | Geometric measurability & spatial noise bounds | 95% CI: **$[-651, +106]\text{ mm/yr}$**; Detection limit: **$200–500\text{ mm/yr}$** | Resolves why single pairs cannot detect $22\text{ mm/yr}$ creep and bounds true observability. |

### 7.2 The Resolution of the Paradox: Why Single Pairs Cannot Resolve Precursory Creep
The apparent conflict between studies claiming precursory detection and our finding of no statistically significant single-pair motion is resolved by examining the signal-to-noise ratio:

```
+-----------------------------------------------------------------------------------------+
|                  THE INFERENTIAL GAP: PRECURSORY CREEP VS. NOISE FLOOR                  |
|                                                                                         |
|  True Physical Creep Rate (Mohanty et al., 2026):                                       |
|  [================] ~22 mm/yr (0.022 m/yr)                                             |
|                                                                                         |
|  Single-Pair InSAR Detection Floor (This Study, 95% CI):                                |
|  [===================================================================================]   |
|  200 to 500 mm/yr (0.20 to 0.50 m/yr)                                                    |
|                                                                                         |
|  CONCLUSION: True precursory creep is ~10-25x smaller than single-pair noise floor!     |
|  Single interferometric pairs are physically blind to 22 mm/yr moraine creep.           |
+-----------------------------------------------------------------------------------------+
```

1. **True Precursory Velocity:** Multi-year PS-InSAR stacks (64 scenes over 4 years) achieve millimetric velocity precision ($\sigma_v \approx 2–4\text{ mm/yr}$) through temporal averaging, resolving a true background creep rate of **$\sim 22\text{ mm/yr}$**.
2. **Single-Pair Atmospheric Limits:** A single 12-day Sentinel-1 pair possesses an intrinsic $2\sigma$ spatial noise floor of $2.2–6.2\text{ mm}$. Scaled by sensitivity ($R \approx 0.31–0.45$) and baseline duration ($\Delta t = 12\text{ days}$), the minimum detectable velocity is **$200–500\text{ mm/yr}$**.
3. **Physical Consequence:** Because $22\text{ mm/yr} \ll 200–500\text{ mm/yr}$, pre-collapse moraine creep is completely masked by atmospheric phase delays on individual interferograms.
4. **Critique of Single-Pair "Early Warning" Claims:** Any study claiming to detect pre-collapse moraine acceleration from a single pre-event interferogram has confused turbulent atmospheric delay or reference drift with real ground motion. Under rigorous hypothesis testing, single-pair observations are statistically indistinguishable from zero motion ($[-651, +106]\text{ mm/yr}$).

---

## 8. Operational Recommendations for Early Warning (IIRS & NDMA Mandate)

Following the South Lhonak disaster, the National Disaster Management Authority (NDMA) and the Central Water Commission (CWC) identified **189 high-risk glacial lakes** across the Indian Himalaya requiring urgent early warning systems (NDMA, 2024). Based on our findings, we formulate four operational recommendations for the Indian Institute of Remote Sensing (IIRS) and spaceborne disaster mitigation frameworks:

```
+-----------------------------------------------------------------------------------+
|               OPERATIONAL SURVEILLANCE ARCHITECTURE FOR GLACIAL LAKES             |
|                                                                                   |
|  1. Mandatory Dual-Track Geometry:                                                |
|     Ascending Track (012) + Descending Track (048) -> Eliminates 87% Blindness    |
|                                                                                   |
|  2. Elimination of Single-Pair Triggers:                                          |
|     Automated alarms must require >= 5 consecutive coherent pairs in time-series   |
|                                                                                   |
|  3. Multi-Frequency SAR Integration:                                              |
|     C-band (Sentinel-1) + L-band (NISAR) -> Overcomes Debris Coherence Loss       |
|                                                                                   |
|  4. Transition to Lateral Slope Auditing:                                         |
|     Shift hazard focus from frontal moraine overtopping to 3D lateral stability   |
+-----------------------------------------------------------------------------------+
```

1. **Mandatory Dual-Track Geometry:** Monitoring frameworks must not rely on single orbital geometries. While Descending Track 048 achieves only 51.8% coverage over south-facing scarps due to sign cancellation, dual-track acquisition achieves **87.0% observability** ($R \ge 0.3$) and **95.0%** at $R \ge 0.2$.
2. **Elimination of Single-Pair Alarms:** Operational early warning pipelines must never trigger automated disaster warnings from single interferograms. Because single-pair velocity detection is limited to $\sim 0.2–0.5\text{ m/yr}$, early detection of slow creep requires multi-temporal SBAS or PS-InSAR filtering across at least 5–10 consecutive acquisitions.
3. **Integration of L-Band SAR (NISAR):** C-band radar (~5.6 cm) experiences rapid decorrelation over wet periglacial debris and winter snowpack. The NASA-ISRO SAR (NISAR) mission, operating at L-band (~24 cm wavelength), will maintain phase coherence across rough moraine debris, significantly improving early warning capabilities across the 189 high-risk lakes.
4. **Paradigm Shift in Cryospheric Risk Modeling:** Prior to October 2023, regional hazard assessments focused almost exclusively on frontal moraine dam stability and direct lake overtopping. The South Lhonak event demonstrates that **lateral moraine destabilization and permafrost thawing** represent the primary triggering mechanism. Operational screening must map 3D slope observability across all lateral valley walls.

---

## 9. Methodological Invariants & Code Reproducibility

To guarantee complete scientific reproducibility, all algorithms, vector transformations, and forward projection pipelines were developed under strict unit test enforcement. The test suite comprises **18 automated tests** in `tests/`:

```bash
$ python -m pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1
rootdir: E:\Personal\iirs
collected 18 items

tests/test_data_provenance.py::test_claims_link_to_registered_papers PASSED [  5%]
tests/test_data_provenance.py::test_experiment_registry_has_configs PASSED [ 11%]
tests/test_invariants.py::test_sentinel1_wavelength_conversion PASSED    [ 16%]
tests/test_invariants.py::test_coherence_bounds PASSED                   [ 22%]
tests/test_measurability.py::test_synthetic_east_facing_slope PASSED     [ 27%]
tests/test_measurability.py::test_synthetic_west_facing_slope PASSED     [ 33%]
tests/test_measurability.py::test_horizontal_plane PASSED                [ 38%]
tests/test_measurability.py::test_r_index_bounded PASSED                 [ 44%]
tests/test_measurability.py::test_raster_pipeline_synthetic_ne_rising_grid PASSED [ 50%]
tests/test_measurability.py::test_hyp3_sign_convention_and_forward_model PASSED [ 55%]
tests/test_measurability.py::test_scarp_aspect_faces_lake PASSED         [ 61%]
tests/test_measurability.py::test_metrics_json_integrity PASSED          [ 66%]
tests/test_vector_features.py::test_lake_post_contained_in_lake_pre PASSED [ 72%]
tests/test_vector_features.py::test_lake_post_schematic_labeling PASSED  [ 77%]
tests/test_vector_features.py::test_dem_flatness_in_lake_core PASSED     [ 83%]
tests/test_vector_features.py::test_sar_backscatter_water_fraction PASSED [ 88%]
tests/test_vector_features.py::test_scarp_and_breach_separation PASSED   [ 94%]
tests/test_vector_features.py::test_ctrl02_decorrelated_dropped PASSED   [100%]

============================= 18 passed in 1.58s ==============================
```

* **Physical Invariants Verified:**
  - `test_synthetic_east_facing_slope` & `test_synthetic_west_facing_slope`: Verifies look-vector sensitivity on analytical geometric surfaces.
  - `test_raster_pipeline_synthetic_ne_rising_grid`: Validates that NumPy axis orientation (`axis 0 = -dy`, `axis 1 = +dx`) produces the correct geometric aspect without reflection.
  - `test_hyp3_sign_convention_and_forward_model`: Verifies that positive unwrapped phase represents range lengthening and maps to negative slope velocity.
  - `test_scarp_aspect_faces_lake`: Confirms that the scarp circular mean aspect ($151.1^\circ$) aligns within $26.2^\circ$ of the nearest southern lake shore.
  - `test_dem_flatness_in_lake_core`: Asserts DEM elevation standard deviation $< 3\text{ m}$ over the lake surface, confirming topographic baseline integrity.

---

## 10. Conclusions

1. **Geometric Observability:** Sentinel-1 C-band InSAR is **geometrically observable** across the South Lhonak lateral moraine, achieving **87.0% observability** on the failure scarp face ($R \ge 0.3$) and **95.0%** at $R \ge 0.2$ when combining Ascending (Track 012) and Descending (Track 048) orbits.
2. **Single-Track Insufficiency:** Descending Track 048 alone exhibits lower sensitivity ($R \approx 0.31$) and sign-cancelling projections across curved ridge benches. Dual-track monitoring is mandatory to eliminate geometric blindness.
3. **Single-Pair Noise Floor vs. Precursory Creep:** Single 12-day interferometric pairs possess an empirical spatial noise floor of $2.2–6.2\text{ mm}$, imposing a minimum detectable velocity threshold of **$200–500\text{ mm/yr}$ ($0.2–0.5\text{ m/yr}$)**. Because the true pre-collapse moraine creep rate measured by multi-year PS-InSAR is **$\sim 22\text{ mm/yr}$** (Mohanty et al., 2026), true physical deformation is buried beneath the single-pair noise floor by an order of magnitude.
4. **Scientific Integrity of Pilot Observations:** Pre-disaster pilot observations over the steep scarp ($\ge 25^\circ$) yield a joint slope velocity of **$[-651, +106]\text{ mm/yr}$** (95% CI), which is statistically consistent with zero motion. Any apparent signal under planar detrending points *upslope*, representing unmodelled atmospheric phase screens rather than true slope creep.
5. **Operational Mandate for IIRS & ISRO:** Automated early warning systems for the 189 high-risk Himalayan glacial lakes cannot rely on single-pair thresholding. Robust cryospheric early warning requires multi-temporal time-series processing (SBAS/PS-InSAR) and multi-frequency radar integration with the upcoming NISAR L-band mission.

---

## References

1. **Bolch, T., Kulkarni, A., Kääb, A., Huggel, C., Paul, F., Cogley, J. G., Frey, H., Kargel, J. S., Fujita, K., Scheel, M., Bajracharya, S., & Stoffel, M.** (2012). The state and fate of Himalayan glaciers. *Science*, 336(6079), 310–314. [DOI: 10.1126/science.1215828](https://doi.org/10.1126/science.1215828)
2. **Bürgmann, R., Rosen, P. A., & Fielding, E. J.** (2000). Synthetic aperture radar interferometry to measure Earth's surface topography and its deformation. *Annual Review of Earth and Planetary Sciences*, 28(1), 169–209.
3. **Doin, M. P., Lasserre, C., Peltzer, G., Cavalié, O., & Doubre, C.** (2009). Corrections of stratified tropospheric delays in SAR interferometry: Validation with global atmospheric models. *Journal of Applied Geophysics*, 69(1), 35–50.
4. **Hanssen, R. F.** (2001). *Radar Interferometry: Data Interpretation and Error Analysis*. Kluwer Academic Publishers, Dordrecht.
5. **ISRO / NRSC.** (2023). *Satellite image-based studies of South Lhonak Lake*. National Remote Sensing Centre, Indian Space Research Organisation. [URL: isro.gov.in](https://www.isro.gov.in/Satellite_studies_South_Lhonak_Lake.html)
6. **Mohanty, L. K., Gantayat, P., Dixit, A., Das Adhikari, M., Biswas, R., & Singh, V. K.** (2026). Sequence of events that led to the South Lhonak lake outburst flood in Sikkim, India. *Scientific Reports*, 16, 9741. [DOI: 10.1038/s41598-026-35895-7](https://doi.org/10.1038/s41598-026-35895-7)
7. **NDMA / Sikkim SDMA.** (2024). *South Lhonak Lake Case Study: Session 5 Sikkim Conclave*. National Disaster Management Authority, Ministry of Home Affairs, Government of India. [URL: ndma.gov.in](https://ndma.gov.in/sites/default/files/PDF/Sikkim_Conclave/Session%205/9%20sikkim%20GLOF%20South%20Lhonak%20Lake%20Case%20Study.pdf)
8. **Nie, Y., Sheng, Y., Liu, Q., Yang, X., Liu, S., & Zhang, Y.** (2017). A regional-scale assessment of glacial lake outburst flood susceptibility in the central Himalaya. *Science of The Total Environment*, 583, 102–114.
9. **Patlolla, S. V. R., Suresh Babu, A. V., Sai Bhagheerath, Y. V., & Sreenivas, K.** (2025). GLOF in the South Lhonak Lake, India: photogrammetric analysis and estimation. *Journal of Water and Climate Change*, 16(1), 127–141. [DOI: 10.2166/wcc.2024.512](https://doi.org/10.2166/wcc.2024.512)
10. **Remya, S. N., Nandan, V., Bhattacharya, A., Srinivasalu, P., Mukherjee, K., Govindha Raj, B., Yackel, J., & Bolch, T.** (2025). Glacier calving and moraine collapse triggered the glacial lake outburst flood in South Lhonak Lake, Indian Himalaya. *Environmental Research Communications*, 7(11), 115026. [DOI: 10.1088/2515-7620/ae1936](https://doi.org/10.1088/2515-7620/ae1936)
11. **Yu, Y., Liu, J., Zhao, X., & Zhang, W.** (2024). Retrospective Analysis of Glacial Lake Outburst Flood (GLOF) Using AI Earth InSAR and Optical Images: A Case Study of South Lhonak Lake, Sikkim. *Remote Sensing*, 16(13), 2307. [DOI: 10.3390/rs16132307](https://doi.org/10.3390/rs16132307)
12. **Zebker, H. A., Rosen, P. A., & Hensley, S.** (1997). Atmospheric effects in interferometric synthetic aperture radar surface deformation and topographic maps. *Journal of Geophysical Research: Solid Earth*, 102(B4), 7547–7563.
