# ===========================================================
# Objective Function for the Optimization
# ===========================================================

"""
This file defines an objective function, used for the curve optimization process.
Function definition:

    f(curve) = w_Cd*Cd + w_grad*Cp_grad + w_int*Cp_int

- Cd: Drag coefficient from Cp integration
- Cp_grad: Maximum gradient of the Cp distribution
- Cp_int: Integral of Cp along the curve

"""

# ==========================================================
# Libraries
# ==========================================================
# 3rd party imports
import numpy as np
from pathlib import Path

# Personal imports
from Cp_linearized_equation import Cp_linearized_distribution
from Hermite import generate_hermite_paper_fairing as Hermite

# ===========================================================
# Function
# ===========================================================
def objfun(parameters, M_infty):
    """
    Objective function for the optimization.
    Args:
        parameters: Parameters for the Hermite curve
        M_infty: Freestream Mach number
    
    Returns:
        metric: Calculated metric based on Cp distribution
    
    """
    
    # Unpack parameters of the Hermite curve
    a, b = parameters
    
    # Create the hermite curve from input parameters
    path = Path(__file__).with_name("protuberance_coords.txt")
    Hermite(a, b, export_filename = str(path))
    
    # Calculate the linearized pressure Cp distribution
    x, Cp = Cp_linearized_distribution(M_infty, config = {"path" : path, "delimiter" : "\t"})
    
    # Calculate drag coefficient (alfa = 0 assumption)
    Cd = 0
    for i in range(0, len(Cp) - 1):
        dx = x[i+1] - x[i] 
        Cd += (Cp[i] + Cp[i+1])*dx/2
    Cd /= (x[-1] - x[0])
    
    # Calculate maximum gradient of Cp
    Cp_grad = np.max(np.abs(np.gradient(Cp, x)))
    
    # Calculate Cp integral
    Cp_int = np.trapz(Cp, x)
    
    # Define weights for the metric
    w_Cd = 1/3
    w_grad = 1
    w_int = 1/30
    
    # Calculate metric
    metric = w_Cd*Cd + w_grad*Cp_grad + w_int*Cp_int
    
    return metric