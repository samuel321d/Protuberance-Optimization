import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

eq = np.loadtxt("Cp_distribution.txt", delimiter = ",", skiprows = 1)
cfd = np.loadtxt("CFD.txt", delimiter = ",", skiprows = 1)
indx = cfd[:, 8].argsort()
cfd = cfd[indx]

# Linerized equation data
x_eq = eq[:, 0]
Cp_eq = eq[:, 2]

# CFD data
x_cfd = cfd[:, 8]
Cp_cfd = cfd[:, 13]

# Plot data
plt.figure(figsize = (10, 5))
plt.plot(x_eq, Cp_eq, label = "Analytical")
plt.plot(x_cfd, Cp_cfd, label = "CFD")
plt.legend()
plt.grid()
plt.savefig("comparison.png")

print(np.rad2deg(max(eq[:, 3])))