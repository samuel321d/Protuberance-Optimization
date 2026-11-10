import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from glob import glob
from matplotlib.ticker import MaxNLocator 
# MATPLOTLIB PARAMS
plt.rcParams.update({
    "font.size": 12,
    "font.family": "serif"
})
folder = os.path.dirname(os.path.abspath(__file__))
# calling the csv´s classified by the source
Histories = glob(os.path.join(folder, "history*.csv"))
CFDS = glob(os.path.join(folder, "CFD*.csv"))
WTS = glob(os.path.join(folder, "WT*.csv"))

# Dictionaries to store the dataframes
dfs_hist = {os.path.splitext(os.path.basename(f))[0]: pd.read_csv(f) for f in sorted(Histories)}
dfs_cfd = {os.path.splitext(os.path.basename(f))[0]: pd.read_csv(f, names = ["AoA", "Coeff"]) for f in sorted(CFDS)}
dfs_wt = {os.path.splitext(os.path.basename(f))[0]: pd.read_csv(f, names = ["AoA", "Coeff"]) for f in sorted(WTS)}


angles = [1, 2, 4, 5, 8, 10, 12, 15]
own_res_cy = []
own_res_ca = []
own_res_cm = []
own_res_cz = []
for hist in dfs_hist.values():
    own_res_cy.append(hist['       "CFy"      '].values[-1]*-1)   
    own_res_ca.append(hist['       "CFx"      '].values[-1])   
    own_res_cm.append(hist['       "CMy"      '].values[-1])   
    own_res_cz.append(hist['       "CFz"      '].values[-1])   

for key in dfs_wt:
    dfs_wt[key] = (
        dfs_wt[key]
        .sort_values('AoA')
        .reset_index(drop=True)
    )

for key in dfs_cfd:
    dfs_cfd[key] = (
        dfs_cfd[key]
        .sort_values('AoA')
        .reset_index(drop=True)
    )
# pOtiching moment coefficient correction
reference_length = 0.368
CoM_offset = 0.78 * reference_length
Cm_own = np.array(own_res_cm) - (CoM_offset / reference_length) * np.array(own_res_cz)
# Plots
xticks_angles = np.arange(0, 16, 1)
plt.figure(figsize=(7, 5))
plt.plot(angles, own_res_cy, 'o-', label='Present CFD', color='black', alpha = 0.75)
plt.plot(dfs_cfd['CFDCY']['AoA'], dfs_cfd['CFDCY']['Coeff'], marker = 's', linestyle = '--', label='Kawauchi et al. CFD', color='black', alpha=0.5)
plt.scatter(dfs_wt['WTCY']['AoA'], dfs_wt['WTCY']['Coeff'], label='Kawauchi et al. WT', color='black', marker='v')
plt.xlabel(r"Angle of Attack $\alpha$, deg")
plt.ylabel(r"Side Force Coefficient $C_y$")
plt.legend()
plt.grid()
plt.xticks(xticks_angles)
plt.show()

plt.figure(figsize=(7, 5))
# plot Ca
plt.plot(angles, own_res_ca, 'o-', label='Present CFD - $C_A$', color='black', alpha = 0.75)
plt.plot(dfs_cfd['CFDCA']['AoA'], dfs_cfd['CFDCA']['Coeff'], marker = 'o', linestyle = '--', label='Kawauchi et al. CFD - $C_A$', color='black', alpha=0.5)
plt.scatter(dfs_wt['WTCA']['AoA'], dfs_wt['WTCA']['Coeff'], label='Kawauchi et al. WT - $C_A$', color='black', marker='o')
# plot Cm
plt.plot(angles, Cm_own, 's-', label='Present CFD - $C_m$', color='black', alpha = 0.75)
plt.plot(dfs_cfd['CFDCM']['AoA'], dfs_cfd['CFDCM']['Coeff'], marker = 's', linestyle = '--', label='Kawauchi et al. CFD - $C_m$', color='black', alpha=0.5)
plt.scatter(dfs_wt['WTCM']['AoA'], dfs_wt['WTCM']['Coeff'], label='Kawauchi et al. WT - $C_m$', color='black', marker='s')
plt.xlabel(r"Angle of Attack $\alpha$, deg")
plt.ylabel(r"Axial Force Coefficient $C_A$ and Moment Coefficient $C_m$")
plt.legend()
plt.grid()
plt.xticks(xticks_angles)
plt.show()

print(own_res_ca)
# Errors calculation

# Interpolation of Wind tunnel data
WDCY_interp = np.interp(angles[:-1], dfs_wt['WTCY']['AoA'], dfs_wt['WTCY']['Coeff'])
WDCA_interp = np.interp(angles[:-1], dfs_wt['WTCA']['AoA'], dfs_wt['WTCA']['Coeff'])
WDCM_interp = np.interp(angles[:-1], dfs_wt['WTCM']['AoA'], dfs_wt['WTCM']['Coeff'])
print("Interpolated Wind Tunnel Data:")
print(f"Side Force Coefficient (C_y): {WDCY_interp}")
print(f"Axial Force Coefficient (C_a): {WDCA_interp}")
print(f"Moment Coefficient (C_m): {WDCM_interp}")
Errors_Cy = np.abs((np.array(own_res_cy[:-1]) - WDCY_interp) / (WDCY_interp.max() - WDCY_interp.min())) * 100
Errors_Ca = np.abs((np.array(own_res_ca[:-1]) - WDCA_interp) /WDCA_interp) * 100   #(WDCA_interp.max() - WDCA_interp.min())) * 100
Errors_Cm = np.abs((Cm_own[:-1] - WDCM_interp) / (WDCM_interp.max() - WDCM_interp.min())) * 100

Errors_Cy2 = np.abs((np.array(own_res_cy[:-1]) - WDCY_interp) / (WDCY_interp)) * 100
Errors_Ca2 = np.abs((np.array(own_res_ca[:-1]) - WDCA_interp) / (WDCA_interp)) * 100
Errors_Cm2 = np.abs((Cm_own[:-1] - WDCM_interp) / (WDCM_interp)) * 100

print("="*50)
print("Validation Errors (%):")
print(f"Side Force Coefficient (C_y)")
for angle, error in zip(angles[:-1], Errors_Cy):
    print(f"Angle: {angle} deg, Error: {error:.2f}%")


print(f"Axial Force Coefficient (C_a)")    
for angle, error in zip(angles[:-1], Errors_Ca):
    print(f"Angle: {angle} deg, Error: {error:.2f}%")

print(f"Moment Coefficient (C_m)")    
for angle, error in zip(angles[:-1], Errors_Cm):
    print(f"Angle: {angle} deg, Error: {error:.2f}%")
print("="*50)


plt.figure(figsize=(7, 5))
plt.plot(angles[:-1], Errors_Cy, 'o-', label='Side Force Coefficient $C_y$', color='black')
plt.plot(angles[:-1], Errors_Ca, 's-', label='Axial Force Coefficient $C_a$', color='black')
plt.plot(angles[:-1], Errors_Cm, '^-', label='Moment Coefficient $C_m$', color='black')
plt.xlabel(r"Angle of Attack $\alpha$, deg")
plt.ylabel(r"Error, %")
plt.legend()
plt.grid()
plt.xticks(xticks_angles)
plt.show()