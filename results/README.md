# Results Directory

All outputs produced by scripts in `src/` or `experiments/` are stored here in structured folders.

## Directory Structure

```
results/
├── README.md
├── figures/              # Publication-ready plots (.png, .pdf)
├── tables/               # Formatted summaries and metrics (.csv, .tex)
├── timeseries/           # Extracted displacement time series (.csv, .h5)
├── interferograms/       # Processed unwrapped phase and coherence products
└── EXP001/               # Experiment-specific run bundle (configs, logs, outputs)
```

## Storage Rules

1. Intermediates (>100MB) such as raw SLC granules or full unwrapped radar rasters must NOT be committed to git (see `.gitignore`).
2. Final metrics, CSV tables, and vector figures are tracked in version control.
3. Every plot generated in `figures/` must be paired with the script and commit hash that generated it.
