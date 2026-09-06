######################################
# Cp from linearized supersonic theory
######################################

# Libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Function definition
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
        "skip_rows" : 1
    }
    
    # Read config
    config = {**default_config, **config}
    
    # Read curve from path
    data = np.loadtxt(config["path"], delimiter = ',', skiprows = config["skip_rows"])
    x = data[:, 0]
    curve = data[:, 1]
    
    # Calculate the local angle of the curve
    slope = np.gradient(curve, x)
    theta = np.arctan(slope)
    
    # Calculate Cp distribution using linearized supersonic theory
    gamma = np.sqrt(M_infty**2 - 1)
    Cp = 2 * theta / gamma
    
    # Save data
    if config["save_data"]:
        data = np.hstack((x.reshape(-1, 1), curve.reshape(-1, 1), Cp.reshape(-1, 1)))
        np.savetxt(config["name_data"], data, delimiter = ',', header = 'x, Curve, Cp')
    
    # Save Cp distribution plot
    if config["save_plot"]:
        plt.figure(figsize = (10, 5))
        plt.plot(x, Cp, label = "Cp", linestyle = "-", color = "blue", marker = "o")
        plt.plot(x, curve, label = "Curve", color = "black")
        plt.xlabel("x")
        plt.ylabel("Cp(x) / h(x)")
        plt.title("Cp distribution along the curve")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig(config["name_plot"])
    
    return x, Cp