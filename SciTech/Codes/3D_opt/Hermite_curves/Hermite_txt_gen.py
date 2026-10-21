import pandas as pd
import numpy as np
from Hermite import hermit_bl, generate_hermite_paper_fairing


# CCD Hermite generation Script
n = 2 # NUmber of parameters
bounds = ([0.5, 3.0], [0.5, 3.0])
normalized_bounds = np.array([
  [-1,-1],
  [1,1],
  [-1,1],
  [1,-1],
  [0,0],
  [-1,0],
  [1,0],
  [0,-1],
  [0, 1]
])
def coded_to_real(x):
    a = np.sum(bounds[0])/2 +  (bounds[0][1] - bounds[0][0])*0.5*x[0]
    b = np.sum(bounds[1])/2 +  (bounds[1][1] - bounds[1][0])*0.5*x[1]
    
    return a,b

real_values = []

for coded in normalized_bounds:
    a,b = coded_to_real(coded)
    real_values.append([a,b])

for value in real_values:
    profile = generate_hermite_paper_fairing(value[0], value[1], nps = 30, export_filename = f"protuberance_coords_{value[0]}_{value[1]}.csv")