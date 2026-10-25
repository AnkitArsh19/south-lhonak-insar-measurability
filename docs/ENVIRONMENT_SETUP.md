# Environment Setup Guide

This guide describes how to configure the Python and InSAR processing environment for the IIRS South Lhonak Research Project.

---

## 1. Prerequisites

- **OS:** Windows 10/11 (with optional Windows Subsystem for Linux - WSL2 Ubuntu for native ISCE2/MintPy compilation, or Conda-forge on Windows).
- **Package Manager:** [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Mambaforge](https://github.com/conda-forge/miniforge) (recommended for fast dependency resolution).
- **Disk Space:** At least 50 GB free for temporary InSAR interferogram processing.

---

## 2. Conda Environment Creation

Create the dedicated conda environment from [environment.yml](file:///e:/Personal/iirs/environment.yml):

```bash
cd e:\Personal\iirs
conda env create -f environment.yml
conda activate iirs-insar
```

Alternatively, with `mamba` (faster):
```bash
mamba env create -f environment.yml
mamba activate iirs-insar
```

---

## 3. API Credentials Setup

To automate satellite and meteorological data queries, configure your API keys:

### A. NASA Earthdata (for ASF, Sentinel-1, NISAR, DEM)
Create a `.netrc` file in your user home directory (`~/.netrc` or `%USERPROFILE%\_netrc` on Windows):

```text
machine urs.earthdata.nasa.gov
    login YOUR_EARTHDATA_USERNAME
    password YOUR_EARTHDATA_PASSWORD
```

### B. Copernicus Data Space Ecosystem (CDSE)
Export environment variables or place in `.env`:
```bash
CDSE_CLIENT_ID="your_client_id"
CDSE_CLIENT_SECRET="your_client_secret"
```

### C. ECMWF Climate Data Store (CDS API for ERA5 Tropospheric Correction)
Create a `.cdsapirc` file in `%USERPROFILE%\.cdsapirc`:
```text
url: https://cds.climate.copernicus.eu/api
key: YOUR_CDS_API_KEY
```

---

## 4. Verification

Run the test suite to verify physical invariants and integrity:

```bash
pytest tests/ -v
```
