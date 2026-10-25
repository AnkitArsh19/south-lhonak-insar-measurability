# Experiments Directory

This directory manages all computational experiments for the South Lhonak GLOF InSAR deformation monitoring project.
It strictly follows the protocol specified in [experiment-workflow skill](file:///e:/Personal/iirs/.agents/skills/experiment-workflow/SKILL.md) and [AGENTS.md](file:///e:/Personal/iirs/AGENTS.md).

## Experiment Standards

1. **Pre-registration:** Every experiment MUST be registered in `experiments_registry.csv` before running, with an explicit hypothesis and defined success/failure metrics.
2. **Configuration as Code:** Every experiment has a reproducible YAML config in `configs/`.
3. **No Metric-Peeking:** The detector threshold must be tuned strictly on pre-2022 data or synthetic/control slopes, never on the 2023 pre-event window.
4. **Control Slopes Mandatory:** No deformation claim on the South Lhonak lateral moraine is valid without running identical processing on at least two stable control slopes and one known active slope in the Teesta basin.
5. **Output Isolation:** Results are saved to `../results/EXPxxx/` with full provenance logs, parameters, git commit hash, and input data manifests.

## Structure

```
experiments/
├── README.md                   # This file
├── experiments_registry.csv    # Central ledger of all experiments
├── configs/                    # YAML configuration files
│   ├── EXP001_sbas_hindcast_baseline.yaml
│   └── ...
└── scripts/                    # Experiment execution runners
    ├── run_hindcast.py
    └── evaluate_detector.py
```
