# ADR-001: InSAR Processing Pipeline and Time-Series Framework Selection

- **Status:** Accepted
- **Date:** 2026-10-22
- **Deciders:** IIRS Research Team
- **Consulted:** [important_data.md](file:///e:/Personal/iirs/important_data.md), [project_outline.md](file:///e:/Personal/iirs/project_outline.md), Yunjun et al. (2019)

## Context and Problem Statement
South Lhonak Lake sits at ~5,200 m asl in steep, glaciated Himalayan terrain subject to seasonal snow cover, steep topography, and high tropospheric stratification. We need an InSAR processing workflow that can handle multi-year Sentinel-1 SLC stacks (2017–2023) and future NISAR products, perform robust phase unwrapping error detection, apply atmospheric phase screen (APS) correction via weather models (ERA5), and provide full reproducibility.

## Decision Drivers
1. **Steep mountain topography capability:** Must handle layover/shadow masking and severe elevation-dependent tropospheric delay.
2. **Phase unwrapping error management:** Unwrapping bridging or network closure checks to avoid misinterpreting 2pi phase jumps as sudden slope failure.
3. **Reproducibility & Scriptability:** Pure CLI/Python execution without reliance on proprietary GUI software.
4. **Compatibility with NISAR:** Ability to ingest future NISAR HDF5 products alongside Sentinel-1.

## Considered Options
1. **ESA SNAP (Desktop GUI + GPT):** Good for individual pair interferograms, but cumbersome for multi-year SBAS network analysis and error modeling.
2. **ISCE2/ISCE3 + MintPy (Small Baseline App):** Standard open-source stack (NASA/JPL + Univ. of Miami); native support for Sentinel-1 and NISAR; automated unwrapping error correction (closure loop), PyAPS integration with ERA5.
3. **PyGMTSAR (Python + GMTSAR):** Fast GPU-accelerated interferogram creation, but smaller community for high-relief complex tropospheric inversion.
4. **Cloud On-Demand (ASF HyP3 + MintPy):** InSAR pairs processed via ASF HyP3 cloud service; interferograms ingested directly into local MintPy for time series.

## Decision Outcome
Chosen option: **Hybrid ASF HyP3 / ISCE2 stack with MintPy for time-series analysis**.
- HyP3 handles cloud generation of unwrapped interferograms and coherence rasters using Gamma / ISCE kernels.
- MintPy conducts local network inversion, ERA5 atmospheric correction, topographic residual correction, and displacement extraction.

### Positive Consequences
- Avoids requiring hundreds of gigabytes of local raw SLC storage on Windows workstation.
- Highly reproducible: full MintPy configuration is stored in version control (`experiments/configs/`).
- Seamless path to NISAR L-band processing via MintPy's native HDF5 loaders.

### Negative Consequences / Trade-offs
- Requires ASF Earthdata credentials and HyP3 quota management.
- Local fallback requires conda Linux or WSL environment for native ISCE2 execution if customized coregistration is needed.
