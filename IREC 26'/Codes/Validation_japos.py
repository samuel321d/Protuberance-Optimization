import numpy as np
# Atm conditions
M = 1.5
Re = 1.38E7
L = 0.368 # l ref
p_inf = 53000
T_0 = 294 #[K]
P0 = 196.1E3 #[Pa]
gamma = 1.4
R = 287.05
T_inf = T_0 / (1 + (gamma - 1) / 2 * M**2)
a_inf = np.sqrt(gamma * R * T_inf)
u_inf = M * a_inf
rho_inf = p_inf / (R * T_inf)
mu_inf = 1.716E-5 * (T_inf / 273.15)**(3/2) * (273.15 + 110.4) / (T_inf + 110.4)
nu_inf = mu_inf / rho_inf


print("="*50)
print("Atm conditions: ")
print("="*50)
print(f"T_inf = {T_inf:.2f} K")
print(f"Reynolds number: Re = {Re:.2e}")
print(f"p_inf = {p_inf:.2f} Pa")
print(f"T_inf = {T_inf:.2f} K")
print(f"T_0 = {T_0:.2f} K")
print(f"rho_inf = {rho_inf:.4f} kg/m^3")
print(f"a_inf = {a_inf:.2f} m/s")
print(f"u_inf = {u_inf:.2f} m/s")
print(f"mu_inf = {mu_inf:.2e} kg/(m*s)")
print(f"nu_inf = {nu_inf:.2e} m^2/s")
print(f"modified_turb_visc = {3*nu_inf:.4e} m^2/s")

# Coefficients calcs

alpha = 5 * np.pi / 180
Cd = 0.87
cy = 0.03834
cl = 0.4715

A = np.zeros((2,2))

A[0,0] = np.cos(alpha)
A[0,1] = np.sin(alpha)
A[1,0] = -np.sin(alpha)
A[1,1] = np.cos(alpha) 

B = np.array([[Cd], [cl]])

coeffs = np.linalg.solve(A, B)
C_A = coeffs[0,0]
C_N = coeffs[1,0]

# Malla calida dmedia (4M)

Ca_4_first = [0.7738]
Cy_4_first = [0.0357]

Ca_4_second = [0.6581, 0.6679, 0.676, 0.6825]
Cy_4_second = [0.00969 ,0.01923, 0.03412, 0.0527]



print("="*50)
print("Coefficients:")
print("="*50)
print(f"C_A = {coeffs[0,0]:.4f}")
print(f"C_N = {coeffs[1,0]:.4f}")

# Data from Studies ===========================================================================================================================
import pandas as pd 
import matplotlib.pyplot as plt
# DATA _CY for comparison
Data_wt_cy = pd.read_csv("c:/Users/Julian Samuel/Downloads/Cy_wt.csv")
Data_japos_cy = pd.read_csv("c:/Users/Julian Samuel/Downloads/Cy_CFD_japos.csv")

headers_CY = ["alpha", "Cy"]
Data_wt_cy.columns = headers_CY
Data_japos_cy.columns = headers_CY
Data_japos_cy = Data_japos_cy[:4]


# DATA C_A for comparison
Data_wt_ca = pd.read_csv("c:/Users/Julian Samuel/Downloads/C_A_WT.csv")
Data_japos_ca = pd.read_csv("c:/Users/Julian Samuel/Downloads/C_A_CFD_japos.csv")
headers_CA = ["alpha", "C_A"]
Data_wt_ca.columns = headers_CA
Data_japos_ca.columns = headers_CA
Data_japos_ca = Data_japos_ca[:4]

print("Data from Studies:")
print(f"WT CY Data Points: {Data_wt_cy['Cy']}")
print(f"WT CA Data Points: {Data_wt_ca['C_A']}")
print(f"Japos CA Data Points: {Data_japos_ca['C_A']}")

# Plots ===========================================================================================================================

# Configuración estilo paper


plt.rcParams.update({
    "text.usetex": False,      # IMPORTANTE
    "font.family": "serif",
    "mathtext.fontset": "cm",  # Computer Modern
    #"font.size": 12,
    "axes.labelsize": 16,
    "axes.titlesize": 18,
    "legend.fontsize": 12,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "lines.linewidth": 2
})

alphas = [2,3,4,5]
plt.figure(figsize=(10,6))
plt.scatter(Data_wt_cy["alpha"], Data_wt_cy["Cy"], label=r"Experimental Kawauchi et.al", marker='o', zorder=1, color = "black")
plt.plot(Data_japos_cy["alpha"], Data_japos_cy["Cy"], label=r"CFD Kawauchi et.al", marker='x', zorder=2, color = "dimgray")
#plt.scatter(alpha * 180 / np.pi, cy, color='firebrick', label=r"Own CFD 1st order, $2\times10^6$ grid", zorder=3, marker = "D")
#plt.scatter(alpha * 180 / np.pi, Cy_4_first[0], color='darkgreen', label=r"Own CFD 1st order, $4\times10^6$ grid", zorder=4, marker="^")
plt.plot(alphas, Cy_4_second, color='navy', label=r"Own CFD 2nd order, $4\times10^6$ grid", zorder=4, marker = 's'  )
plt.xlabel(r"Angle of Attack $\alpha$ [°]")
plt.ylabel(r"Side Force Coefficient $C_Y$")
plt.grid()
plt.legend()
plt.title(r"C_Y vs Alpha")
plt.xlim(0,7)
plt.show()

plt.figure(figsize=(10,6))
plt.scatter(Data_wt_ca["alpha"], Data_wt_ca["C_A"], label=r"Experimental Kawauchi et.al", marker='o', color = "black")
plt.plot(Data_japos_ca["alpha"], Data_japos_ca["C_A"], label=r"CFD Kawauchi et.al", marker='x', color = "dimgray")
#plt.scatter(alpha * 180 / np.pi, C_A, color='firebrick', label=r"Own CFD 1st order, $2\times10^6$ grid", zorder=3, marker = "D")
#plt.scatter(alpha * 180 / np.pi, Ca_4_first[0], color='darkgreen', label=r"Own CFD 1st order, $4\times10^6$ grid", zorder=4, marker = "^")
plt.plot(alphas, Ca_4_second, color='navy', label=r"Own CFD 2nd order, $4\times10^6$ grid", zorder=4, marker = 's')
plt.xlabel(r"Angle of Attack $\alpha$ [°]")
plt.ylabel(r"Axial Force Coefficient $C_A$")
plt.grid()
plt.legend()
plt.title(r"C_A vs Alpha")
plt.xlim(0,7)
plt.ylim(0.55,0.8)
plt.show()





print("="*50)
print("Error Analysis:")
# Errores
Cy_8m = 0.052
Ca_8m = 0.6897
Ca_list = [
    C_A,            # 2M 1st
    Ca_4_first[0],  # 4M 1st
    Ca_4_second[2], # 4M 2nd alpha=5
    Ca_8m           # 8M 2nd
]

Cy_list = [
    cy,
    Cy_4_first[0],
    Cy_4_second[2],
    Cy_8m
]

labels = [
    r"1st order $2\times10^6$",
    r"1st order $4\times10^6$",
    r"2nd order $4\times10^6$",
    r"2nd order $8\times10^6$"
]

Ca_experimentals = [Data_wt_ca["C_A"][3], Data_wt_ca["C_A"][4]]
Cy_experimentals = [Data_wt_cy["Cy"][3], Data_wt_cy["Cy"][4]]

alpha_experimentals = [Data_wt_ca["alpha"][3], Data_wt_ca["alpha"][4]]

m_cy = (Cy_experimentals[1] - Cy_experimentals[0]) / (alpha_experimentals[1] - alpha_experimentals[0])
b_cy = Cy_experimentals[0] - m_cy * alpha_experimentals[0]
Cy_experimental_at_5 = m_cy * 5 + b_cy

m_ca = (Ca_experimentals[1] - Ca_experimentals[0]) / (alpha_experimentals[1] - alpha_experimentals[0])
b_ca = Ca_experimentals[0] - m_ca * alpha_experimentals[0]
Ca_experimental_at_5 = m_ca * 5 + b_ca

print(f"Experimental C_A at alpha=5°: {Ca_experimental_at_5:.4f}")
print(f"Experimental C_y at alpha=5°: {Cy_experimental_at_5:.4f}")



errors_ca = []
errors_cy = []

for ca, cy_val, label in zip(Ca_list, Cy_list, labels):

    error_Ca = abs(ca - Ca_experimental_at_5)/abs(Ca_experimental_at_5)*100
    error_Cy = abs(cy_val - Cy_experimental_at_5)/abs(Cy_experimental_at_5)*100

    errors_ca.append(error_Ca)
    errors_cy.append(error_Cy)
    print(f"{label}")
    print(f"C_A error = {error_Ca:.2f}%")
    print(f"C_y error = {error_Cy:.2f}%")
    print()


CA_error = [15.07, 4.88, 3.87]
CY_error = [21.71, 7.61, 5.12]

grids = [2,4,8]
plt.figure(figsize=(10,6))
plt.plot(grids, CA_error, color  = "k", marker = 'o')
#plt.scatter(alpha * 180 / np.pi, C_A, color='firebrick', label=r"Own CFD 1st order, $2\times10^6$ grid", zorder=3, marker = "D")
#plt.scatter(alpha * 180 / np.pi, Ca_4_first[0], color='darkgreen', label=r"Own CFD 1st order, $4\times10^6$ grid", zorder=4, marker = "^")
#plt.plot(alphas, Ca_4_second, color='navy', label=r"Own CFD 2nd order, $4\times10^6$ grid", zorder=4, marker = 's')
plt.xlabel(r"Cell count [$\times10^6$]")
plt.ylabel(r"Axial Force Coefficient $C_A$ Error [%]")
plt.grid()
plt.legend()
plt.title(r"C_A error vs Cell Count")
#plt.xlim(0,9)
#plt.ylim(0.0,0.1)
plt.show()



plt.figure(figsize=(10,6))
plt.plot(grids, CY_error, color  = "k", marker = 'o')
#plt.scatter(alpha * 180 / np.pi, C_A, color='firebrick', label=r"Own CFD 1st order, $2\times10^6$ grid", zorder=3, marker = "D")
#plt.scatter(alpha * 180 / np.pi, Ca_4_first[0], color='darkgreen', label=r"Own CFD 1st order, $4\times10^6$ grid", zorder=4, marker = "^")
#plt.plot(alphas, Ca_4_second, color='navy', label=r"Own CFD 2nd order, $4\times10^6$ grid", zorder=4, marker = 's')
plt.xlabel(r"Cell count [$\times10^6$]")
plt.ylabel(r"Side Force Coefficient $C_Y$ Error [%]")
plt.grid()
plt.legend()
plt.title(r"C_Y error vs Cell Count")
#plt.xlim(0,9)
#plt.ylim(0.0,0.1)
plt.show()
