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

# Calculate drag coefficient (alfa = 0 assumption)
Cd = 0
for i in range(0, len(Cp_cfd) - 1):
    dx = x_cfd[i+1] - x_cfd[i] 
    Cd += (Cp_cfd[i] + Cp_cfd[i+1])*dx/2
Cd /= (x_cfd[-1] - x_cfd[0])

# Calculate maximum gradient of Cp
Cp_grad = np.max(np.abs(np.gradient(Cp_cfd, x_cfd)))

# Calculate Cp integral
Cp_int = np.trapz(Cp_cfd, x_cfd)

# Define weights for the metric
w_Cd = 1/3
w_grad = 1
w_int = 1/30

# Calculate metric
metric = w_Cd*Cd + w_grad*Cp_grad + w_int*Cp_int

print(Cd, Cp_int, Cp_grad)

# Plot data
plt.figure(figsize = (10, 5))
plt.plot(x_eq, Cp_eq, label = "Analytical")
plt.plot(x_cfd, Cp_cfd, label = "CFD")
plt.legend()
plt.grid()
plt.savefig("comparison.png")