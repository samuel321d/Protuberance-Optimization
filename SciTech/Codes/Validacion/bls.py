import numpy as np
from scipy.optimize import fsolve

h0 = 9.65e-4 # FL THCKNSS
r = 1.21 # groth rato
h_t = 0.625 # max hght/total

# h_t = ho*(1-r**N)/(1-r)

def serie(N):
    return h_t - h0*(1-r**N)/(1-r)

root = fsolve(serie, 20)
print(root)
