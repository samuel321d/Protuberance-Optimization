# Cp from linearized supersonic theory

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Generate curve
x = np.arange(0, np.pi, 0.01)
curve = 0.1 * np.sin(x)

# Derivative
slope = np.gradient(curve, x)
theta = np.arctan(slope)

M_infty = 1.4

gamma = np.sqrt(M_infty**2 - 1)

cp = 2 * theta / gamma

plt.figure(figsize = (10, 5))
plt.plot(x, curve)
plt.plot(x, cp)
plt.grid()
plt.savefig('grafica.png')