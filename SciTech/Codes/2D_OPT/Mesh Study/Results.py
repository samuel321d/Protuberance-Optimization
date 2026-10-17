import numpy as np
import matplotlib.pyplot as plt

fig, [ax1, ax2] = plt.subplots(2, 1, figsize = (10, 6))
ax1.plot([0.5, 1, 3, 5], [0.083036, 0.080218, 0.080956, 0.082878], label = "Non-Converged")
ax1.scatter([0.5, 1], [0.083693, 0.081281], label = "Converged")
ax1.set_xlabel("Sizing")
ax1.set_ylabel("CD")
ax1.grid()

ax2.plot([0.5, 1, 3, 5], [0.399130, 0.395684, 0.392535, 0.396353], label = "Non-Converged")
ax2.scatter([0.5, 1], [0.401166, 0.398616], label = "Converged")
ax2.set_xlabel("Sizing")
ax2.set_ylabel("CL")
ax2.grid()

plt.tight_layout()

fig2, [ax1, ax2] = plt.subplots(2, 1, figsize = (10, 6))
ax1.plot([0.5, 1, 3, 5], [5.7997, 7.71576, 9.18479, 9.22516], label = "Non-Converged")
ax1.scatter([0.5, 1], [7.67977, 9.41724], label = "Converged")
ax1.set_xlabel("Sizing")
ax1.set_ylabel("Cp_Int")
ax1.grid()

ax2.plot([0.5, 1, 3, 5], [0.032192, 0.0345111111111108, 0.03225051194539179, 0.025063934426228944], label = "Non-Converged")
ax2.scatter([0.5, 1], [0.03314400000000001, 0.03584343434343403], label = "Converged")
ax2.set_xlabel("Sizing")
ax2.set_ylabel("Cp_Grad")
ax2.grid()

plt.tight_layout()
plt.show()
