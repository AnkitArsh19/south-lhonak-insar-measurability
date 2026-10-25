"""
Publication-ready plotting for InSAR Measurability Atlas.
"""

from typing import Optional
from pathlib import Path
import numpy as np

def plot_measurability_map(
    measurability_grid: np.ndarray,
    extent: list, # [lon_min, lon_max, lat_min, lat_max]
    output_path: Optional[Path] = None,
    lake_poly_coords: Optional[list] = None
):
    """
    Renders discrete 4-class measurability map:
    0: Blind (Layover/Shadow)
    1: Low Sensitivity (|R| < 0.2)
    2: Decorrelated (Mean coherence < 0.35)
    3: Measurable
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    
    cmap = ListedColormap(["#2b2b2b", "#d95f02", "#7570b3", "#1b9e77"])
    classes = ["Blind (Layover/Shadow)", "Low Sensitivity", "Decorrelated", "Measurable"]
    
    fig, ax = plt.subplots(figsize=(8, 7), dpi=300)
    im = ax.imshow(measurability_grid, cmap=cmap, vmin=0, vmax=3, extent=extent, origin="upper")
    
    if lake_poly_coords:
        ax.plot(*zip(*lake_poly_coords), color="cyan", linewidth=1.5, label="Lake Perimeter")
        
    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2, 3], fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels(classes)
    
    ax.set_title("InSAR Measurability Atlas — South Lhonak Basin", fontsize=12, fontweight="bold")
    ax.set_xlabel("Longitude (°E)", fontsize=10)
    ax.set_ylabel("Latitude (°N)", fontsize=10)
    
    plt.tight_layout()
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()
    else:
        return fig
