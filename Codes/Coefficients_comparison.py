# Libraries
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize
from mpl_toolkits.mplot3d import Axes3D
import itertools
from smt.surrogate_models import KRG
import Values

# Plots config
plt.rcParams.update({
    "text.usetex": False,      # IMPORTANTE
    "font.family": "serif",
    "mathtext.fontset": "cm",  # Computer Modern
    #"font.size": 12,
    "axes.labelsize": 16,
    "axes.titlesize": 18,
    "legend.fontsize": 15,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "lines.linewidth": 2
})


cd_m_09, cy_m_09 = Values.values(0.95)
cd_m_08, cy_m_08 = Values.values(0.8)
cd_m_06, cy_m_06 = Values.values(0.6)

configs = np.linspace(1, 15, 15)

plt.figure(figsize=(10,8))
plt.plot(configs, cd_m_08, linestyle = "--", marker = "s", label = "$C_D$ for $M = 0.8$")
plt.plot(configs, cd_m_06, linestyle = "-.", marker = "^", label = "$C_D$ for $M = 0.6$")
#plt.plot(configs, cd_m_09, linestyle = "-.", marker = "o", label = "$C_D$ for $M = 0.95$")
plt.grid(True, linestyle = "--")
plt.legend()
plt.title("$C_D$ comparison for various Mach numbers and configurations")
plt.xlabel("Configuration")
plt.ylabel("$C_D$")
plt.yticks(np.arange(0.7, 0.78, 0.01))
plt.xticks(np.arange(1, 16, 1))
plt.show()

plt.figure(figsize=(10,8))
plt.plot(configs, cy_m_08, linestyle = "--", marker = "s", label = "$C_Y$ for $M = 0.8$")
plt.plot(configs, cy_m_06, linestyle = "-.", marker = "^", label = "$C_Y$ for $M = 0.6$")
#plt.plot(configs, cy_m_09, linestyle = "-.", marker = "o", label = "$C_Y$ for $M = 0.95$")
plt.grid(True, linestyle = "--")
plt.legend()
plt.title("$C_Y$ comparison for various Mach numbers and configurations")
plt.xlabel("Configuration")
plt.ylabel("$C_Y$")
plt.xticks(np.arange(1, 16, 1))
plt.show()

