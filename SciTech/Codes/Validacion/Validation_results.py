import matplotlib.pyplot as plt
import numpy as np

CA = [0.7265864362, 0.7243008244, 0.7127830205, 0.7219930788]

CY = [-0.2912849533, -0.2965115216, -0.3007896347,-0.2974963103]

CA = [0.7300965245, 0.7219930788, 0.7131660903, 0.7162179869]

CY = [-0.2926888112, -0.2974963103, -0.3007376488, -0.2952700236]

fig, [ax1, ax2] = plt.subplots(2, 1, figsize = (8, 6))

ax1.plot([1, 2, 3, 4], CA, marker = "o", label = "CFD Results")
ax1.hlines(0.7543307086614179, 1, 4, color = "black", linestyle = "--", label = "K. Kawauchi et al. (2019)")
ax1.set_ylabel(r"$C_A$")
ax1.set_xlabel("Mesh Type")
ax1.set_xticks([1, 2, 3, 4])
ax1.set_xticklabels(["Coarse", "Medium", "Fine", "Extra Fine"])
ax1.legend()
ax1.grid()

ax2.plot([1, 2, 3, 4], CY, marker = "o", label = "CFD Results")
ax2.hlines(-0.30381679389313, 1, 4, color = "black", linestyle = "--", label = "K. Kawauchi et al. (2019)")
ax2.set_ylabel(r"$C_Y$")
ax2.set_xlabel("Mesh Type")
ax2.set_xticks([1, 2, 3, 4])
ax2.set_xticklabels(["Coarse", "Medium", "Fine", "Extra Fine"])
ax2.legend()
ax2.grid()

plt.tight_layout()
plt.show()