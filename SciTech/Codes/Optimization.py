######################################
# Main optimization code
######################################

# Libraries
from scipy.optimize import minimize
import numpy as np
import matplotlib.pyplot as plt

# Personal functions
from Cp_linearized_equation import Cp_linearized_distribution
from Hermite import Hermite

# Define objective function
def objective_function(parameters, M_infty):
    """
    Objective function for optimization
    
    Args:
        parameters: Parameters for the Hermite curve
        M_infty: Freestream Mach number
    
    Returns:
        metric: Calculated metric based on Cp distribution and drag coefficient
    """
    
    # Unpack parameters
    a, b = parameters
    
    # Create the hermite curve from input parameters
    path = Hermite(a, b)
    
    # Calculate the linearized pressure Cp distribution
    x, Cp = Cp_linearized_distribution(M_infty, config = {"path" : path})
    
    # Calculate drag coefficient (alfa = 0)
    Cd = 0
    for i in range(0, len(Cp) - 1):
        dx = x[i+1] - x[i] 
        Cd += (Cp[i] + Cp[i+1])*dx/2
    Cd /= (x[-1] - x[0])
    
    # Calculate maximum gradient of Cp
    Cp_grad = np.max(np.abs(np.gradient(Cp, x)))
    
    # Calculate Cp integral
    Cp_int = np.trapezoid(Cp, x)
    
    # Define weights for the metric
    w_Cd = 1
    w_grad = 1
    w_int = 1
    
    # Calculate metric
    metric = w_Cd*Cd + w_grad*Cp_grad + w_int*Cp_int
    
    return metric

# Find minimum
x0 = np.array([0, 1]) # Initial values
bounds = "no se xd" # Bounds
M_infty = 1.4 # Freestream Mach number

optim = minimize(objective_function, x0, args = (M_infty), method = "Nelder-Mead", bounds = bounds, options={'xatol': 1e-5, 'disp': False, 'maxiter':10000})

# Verify success
if not optim.success:
    print("Traste", optim.message)

# Extract optimum value
a = optim.x[0]
b = optim.x[1]

# Create optimum Hermite curve
path = Hermite(a, b)

# Optimum Cp dsitribution
_, _ = Cp_linearized_distribution(M_infty, config = {"path" : path, "save_data" : True, "name_data" : "Optimum_Cp.txt", "save_plot" : True, "name_plot" : "Optimum_Cp.png"})