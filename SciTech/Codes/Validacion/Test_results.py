import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

history = pd.read_csv("history_C.csv")

print(history.head(5))

print(history[ '    "rms[Rho]"    '])



plt.figure(1)
plt.plot(history["Inner_Iter"],history[ '    "rms[Rho]"    '], label = "Continuity")
plt.plot(history["Inner_Iter"],history[ '    "rms[RhoU]"   '], label = "U-velocity")
plt.plot(history["Inner_Iter"],history[ '    "rms[RhoV]"   '], label = "V-velocity")
plt.plot(history["Inner_Iter"],history[ '    "rms[RhoE]"   '], label = "Energy")
plt.plot(history["Inner_Iter"],history[ '     "rms[nu]"    '], label = "Nu_tilda")
plt.xlabel("Iteration")
plt.ylabel("RMS residual")
plt.legend()
plt.grid()
plt.ylim(-6.5,1)
plt.title("RMS Residuals")
plt.show()

plt.figure(2)
plt.plot(history["Inner_Iter"], history['       "CFx"      '])
plt.grid()
plt.xlabel("Iteration")
plt.ylabel("CA")
plt.title("CA convergence plot")
plt.show()

plt.figure(3)
plt.plot(history["Inner_Iter"], history['       "CFy"      '])
plt.grid()
plt.xlabel("Iteration")
plt.ylabel("CFy")
plt.title("Cy convergence plot")
plt.show()