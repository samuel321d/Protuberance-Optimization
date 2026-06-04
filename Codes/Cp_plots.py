import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams.update({
    "text.usetex": False,     
    "font.family": "serif",
    "mathtext.fontset": "cm", 
    #"font.size": 12,
    "axes.labelsize": 16,
    "axes.titlesize": 18,
    "legend.fontsize": 12,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "lines.linewidth": 2
})




route_cam8 = "Datos_sim cam 8"

files = {}

for file in os.listdir(route_cam8):
    if file.endswith(".csv"):
        data = pd.read_csv(os.path.join(route_cam8, file), skiprows=4)
        files[file] = data
print(files.keys())

print(files["cp_1000_z.csv"].head())
def z_t_theta(data_z, data_y):
    """
    Function taht receives the Z values from a dataframe and returns the azimutal angle theta in rad

    """
    r = 0.174 # radius in m
    z = data_z
    y = data_y
    #z_min = np.min(z)
    #z_max = np.max(z)
    angle = 6 # deg

    #z_normalized = (z - z_min) / (z_max - z_min) * r
    
    theta = np.arcsin(z / r)
    data["theta"] = theta


plt.figure(figsize=(10, 6))

"""    
z_t_theta(files["cp_1000_z.csv"])

plt.figure(figsize=(10, 6))
plt.plot(files["cp_1000_z.csv"]["theta"] * 180 / np.pi, files["cp_1000_z.csv"]["Pressure Coefficient"], label="Cp cam 8")
plt.xlabel("Theta (deg)")
plt.ylabel("Pressure Coefficient (Cp)")
plt.xticks(np.arange(0,91, 10))
plt.grid()
plt.show()
"""