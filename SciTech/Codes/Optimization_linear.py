# ===========================================================
# Curve Optimization (Potential Flow Theory)
# ===========================================================

"""
This file does an optimization of a curve using linearized perturbed potential flow theory.
This in done by optimizing the weighted objective function in Objective_function.py

"""

# ==========================================================
# Libraries
# ==========================================================
# 3rd party imports
from scipy.optimize import minimize
from pathlib import Path
import numpy as np

# Personal imports
from Objective_function import objfun
from Cp_linearized_equation import Cp_linearized_distribution
from Hermite import generate_hermite_paper_fairing as Hermite

# Configuration of optimization
x0 = np.array([1, 1])               # Initial values
bounds = ([0.5, 3.0], [0.5, 3.0])   # Bounds
M_infty = 1.4                       # Freestream Mach number

# Optimization
optim = minimize(objfun, x0, args = (M_infty,), method = "Nelder-Mead", bounds = bounds, options={'xatol': 1e-5, 'disp': True, 'maxiter':10000})

# Verify results
if not optim.success:
    # Verify optimization success
    print("The optimization failed", optim.message)
else:
    # Extract optimum value
    a = optim.x[0]
    b = optim.x[1]
    
    # Create optimum Hermite curve
    path = Path(__file__).with_name("protuberance_coords.txt")
    Hermite(a, b, export_filename=str(path))
    
    # Save results in a directory next to this script
    results_dir = Path(__file__).parent / "Optimization Results"
    results_dir.mkdir(parents = True, exist_ok = True)
    plot_path = results_dir / "Optimum_Cp_(Linear).png"
    data_path = results_dir / "Optimum_Cp_(Linear).txt"
    
    # Calculate & save optimum Cp distribution
    _, _ = Cp_linearized_distribution(M_infty, config = {"path" : path, "delimiter" : "\t", "save_data" : True, "name_data" : data_path, "save_plot" : True, "name_plot" : plot_path})

# Remove temporary geometry file after the optimization
if "path" in locals() and path.exists():
    path.unlink()