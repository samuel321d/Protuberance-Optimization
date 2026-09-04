######################################
# Cp from linearized supersonic theory
######################################

# Libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Freestream condition
M_infty = 1.4

# # Generate curve
# x = np.arange(0, np.pi, 0.01)
# curve = 0.1 * np.sin(x)

# # Save curve as a .txt
# x = x.reshape(-1, 1)
# curve = curve.reshape(-1, 1)
# data = np.hstack((x, curve))
# np.savetxt('Curve.txt', data, delimiter = ',', header = 'x, curve')

# Read curve from .txt
data = np.loadtxt('Curve.txt', delimiter = ',', skiprows = 1)
x = data[:, 0]
curve = data[:, 1]

# Calculate the local angle of the curve
slope = np.gradient(curve, x)
theta = np.arctan(slope)

# Calculate Cp distribution using linearized supersonic theory
gamma = np.sqrt(M_infty**2 - 1)
Cp = 2 * theta / gamma

# # Save data
# data = np.hstack((x.reshape(-1, 1), curve.reshape(-1, 1), Cp.reshape(-1, 1)))
# np.savetxt('Cp_distribution.txt', data, delimiter = ',', header = 'x, curve, Cp')

# Plot Cp distribution
plt.figure(figsize = (10, 5))
plt.plot(x, Cp, label = "Cp", linestyle = "-", color = "blue", marker = "o")
plt.plot(x, curve, label = "Curve", color = "black")
plt.xlabel("x")
plt.ylabel("Cp(x) / h(x)")
plt.title("Cp distribution along the curve")
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig('grafica.png')