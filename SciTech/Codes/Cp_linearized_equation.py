# ===========================================================
# Cp Calculation (Potential Flow Theory)
# ===========================================================

"""
This file contains a function that generates the Cp distribution over a surface (contained in a .txt).
This is done by using the linearized perturbed potential flow theory.

"""

# ==========================================================
# Libraries
# ==========================================================
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# ==========================================================
# Function
# ==========================================================
def Cp_linearized_distribution(M_infty, config = {}):
    """"
    Calculates the Cp distribution along a curve using the linearized supersonic potential theory.
    
    Args:
        M_infty: Freestream Mach number
        config: Dictionary containing configuration options
    
    Returns:
        x: x-coordinates of the curve
        Cp: Calculated Cp distribution along the curve
    """
    
    # default configuration
    default_config = {
        "save_data" : False,
        "name_data" : "Cp_distribution.txt",
        "save_plot" : False,
        "name_plot" : "graphics.png",
        "path"      : "curve.txt",
        "delimiter" : "\t",
        "skip_rows" : 1
    }
    
    # Read config
    config = {**default_config, **config}
    
    # Resolve relative paths next to this module while preserving absolute paths.
    configured_path = Path(config["path"])
    path = configured_path if configured_path.is_absolute() else Path(__file__).with_name(configured_path)
    
    # Read curve from path
    data = np.loadtxt(path, delimiter = config["delimiter"], skiprows = config["skip_rows"])
    
    # Extract curve
    x = data[:, 0]
    curve = data[:, 1]
    
    # Calculate the local angle of the curve
    slope = np.gradient(curve, x)
    theta = np.arctan(slope)
    
    # Calculate Cp distribution
    gamma = np.sqrt(M_infty**2 - 1)
    Cp = 2 * theta / gamma
    
    # Save data
    if config["save_data"]:
        data = np.hstack((x.reshape(-1, 1), curve.reshape(-1, 1), Cp.reshape(-1, 1)))
        np.savetxt(config["name_data"], data, delimiter = ',', header = 'x, Curve, Cp')
    
    # Save Cp distribution plot
    if config["save_plot"]:
        plt.figure(figsize = (10, 5))
        plt.plot(x, Cp, label = "Cp(x)", linestyle = "-", color = "blue", marker = "o")
        plt.plot(x, curve, label = "Curve", color = "black")
        plt.xlabel("x")
        plt.ylabel("Value")
        plt.title("Cp distribution along the curve")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig(config["name_plot"])
    
    return x, Cp