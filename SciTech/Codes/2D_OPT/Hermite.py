# ===========================================================
# Hermite Curve Generation
# ===========================================================

"""
This file contains the Hermite generation functions, using the two defined parameters (zeta 1,2).

"""

# ===========================================================
# Libraries
# ===========================================================
import numpy as np
import matplotlib.pyplot as plt 
# ===========================================================
# Functions
# ===========================================================
def hermit_bl(X0, X1, X0p, X1p, nps=30, clustering=True):
    if clustering:
        beta = np.linspace(0, np.pi, nps)
        t = 0.5 * (1 - np.cos(beta))
    else:
        t = np.linspace(0, 1, nps)
    
    af =  2*t**3 - 3*t**2 + 1
    bf =    t**3 - 2*t**2 + t
    cf = -2*t**3 + 3*t**2
    df =    t**3 -   t**2
    
    xt = af*X0 + bf*X0p + cf*X1 + df*X1p
    
    daf =  6*t**2 - 6*t
    dbf =  3*t**2 - 4*t + 1
    dcf = -6*t**2 + 6*t
    ddf =  3*t**2 - 2*t
    
    xdt = daf*X0 + dbf*X0p + dcf*X1 + ddf*X1p
    
    return xt, xdt

def generate_hermite_paper_fairing(zeta1, zeta2, nps=30, export_filename="protuberance_coords.txt"):
    x0 = 0.0
    x1 = 87.0
    y0 = 0.0
    y1 = 22.0
    
    delta_x = x1 - x0
    
    x0p = zeta1 * delta_x
    x1p = zeta2 * delta_x
    
    y0p = 0.0
    y1p = 0.0
    
    xpts, _ = hermit_bl(x0, x1, x0p, x1p, nps=nps, clustering=True)
    ypts, _ = hermit_bl(y0, y1, y0p, y1p, nps=nps, clustering=True)
    
    data_out = np.column_stack((xpts, ypts))
    np.savetxt(export_filename, data_out, fmt='%.6f', delimiter='\t', header="X_mm\tY_mm")
    
    return {'x': xpts, 'y': ypts, 'zeta1': zeta1, 'zeta2': zeta2}

param_bounds = {
    'zeta1': [0.5, 3.0],
    'zeta2': [0.5, 3.0]
}

# ===========================================================
# Test
# ===========================================================
if __name__ == "__main__":
    zeta1_input = 1
    zeta2_input = 1
    
    profile = generate_hermite_paper_fairing(zeta1_input, zeta2_input, nps=30)

def find_param_bounds(zeta1, zeta2, nps=30):
    x0, x1 = 0.0, 87.0
    y0, y1 = 0.0, 22.0

    delta_x = x1 - x0
    x0p = zeta1 * delta_x
    x1p = zeta2 * delta_x

    y0p = y1p = 0.0
    x_cr, y_cr = 62.0, 19.0

    xpts, _ = hermit_bl(
        x0, x1, x0p, x1p, nps=nps, clustering=True
    )
    ypts, _ = hermit_bl(
        y0, y1, y0p, y1p, nps=nps, clustering=True
    )
    valid =True

    for x, y in zip(xpts, ypts):
        
        if x > x_cr and y < y_cr:
            valid = False
            return valid

    for i in range(1, len(xpts)):
        if xpts[i] - xpts[i-1] < 0:
            valid = False
            return valid

    return valid    
min_zeta_1 = 0.0
zeta_1 = np.linspace(min_zeta_1, 5,100)
zeta_2 = np.linspace(min_zeta_1, 5,100)

Z1, Z2 = np.meshgrid(zeta_1, zeta_2)

valid_params = []
invalid_params = []

for z1, z2 in zip(Z1.ravel(), Z2.ravel()):
    if find_param_bounds(z1, z2):
        valid_params.append((z1, z2))
    else:
        invalid_params.append((z1, z2))

print("Válidos:", len(valid_params))
print("Inválidos:", len(invalid_params))



valid = np.zeros(Z1.shape, dtype=bool)

for i, z2 in enumerate(zeta_2):
    for j, z1 in enumerate(zeta_1):
        valid[i, j] = find_param_bounds(z1, z2)


max_zeta_1 = 3.6
max_zeta_2 = 2.7

zetas_1 = np.linspace(min_zeta_1,max_zeta_1,50)
zetas_2 = 0.37*zetas_1 + 0.85

print(zetas_2[-1])

A = np.array([[0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1],
            [2**5,2**4, 2**3, 2**2, 2,1],
            [max_zeta_1**5, max_zeta_1**4,max_zeta_1**3, max_zeta_1**2, max_zeta_1, 1],
            [0.36**5,0.36**4,0.36**3, 0.36**2, 0.36, 1],
            [2.85**5,2.85**4, 2.85**3, 2.85**2, 2.85, 1]
            ])

B = np.array([[2.95], [3.9] , [3.6], [zetas_2[-1]], [3.72], [3.10]])

X = np.linalg.solve(A,B).flatten()

print(X)
zetas_2_parabola = X[0]*zetas_1**5 + X[1]*zetas_1**4 + X[2]*zetas_1**3  + X[3]*zetas_1**2 +  X[4]*zetas_1 + X[5] 

from matplotlib.patches import Patch

xs_1 = [max_zeta_1,max_zeta_1]
ys_1 = [zetas_2[-1], max_zeta_2]
plt.figure(figsize=(5, 5))

plt.contourf(
    Z1, Z2, valid.astype(int),
    levels=[-0.5, 0.5, 1.5],
    colors=["red", "green"],
    labels = ["invalid", "valid"]
)
plt.plot(zetas_1, zetas_2_parabola, "--", color = "blue")
plt.plot(zetas_1, zetas_2, "--", color = "blue", label = "design_space")
plt.xlabel(r"$\zeta_1$")
plt.ylabel(r"$\zeta_2$")
plt.title("Design space assesment")
regions = [
    Patch(facecolor="red", label="Invalid"),
    Patch(facecolor="green", label="Valid")
]
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles=regions + handles)
plt.grid()
plt.axis("equal")
plt.xlim([min_zeta_1,5])
plt.ylim([min_zeta_1,5])
plt.show()



# Hermites
def bounds_hermite(zeta1, zeta2, nps=30):
    x0, x1 = 0.0, 87.0
    y0, y1 = 0.0, 22.0

    delta_x = x1 - x0
    x0p = zeta1 * delta_x
    x1p = zeta2 * delta_x

    y0p = y1p = 0.0
    x_cr, y_cr = 62.0, 19.0

    xpts, _ = hermit_bl(
        x0, x1, x0p, x1p, nps=nps, clustering=True
    )
    ypts, _ = hermit_bl(
        y0, y1, y0p, y1p, nps=nps, clustering=True
    )
    return xpts, ypts


# left low hermite
xpts_LL, ypts_LL = bounds_hermite(min_zeta_1, 0.85)

# right low hermite
xpts_RL, ypts_RL = bounds_hermite(max_zeta_1, zetas_2[-1])

# right upper hermite
xpts_RU, ypts_RU = bounds_hermite(max_zeta_1, max_zeta_2)

# left upper

xpts_LU, ypts_LU = bounds_hermite(min_zeta_1, max_zeta_2)


fig, ax = plt.subplots(2, 2, figsize=(10, 8))
ax[0,0].plot(xpts_LL, ypts_LL, marker = "o", color = "tab:blue")
ax[0,0].plot(xpts_LL, ypts_LL, color = "black")
ax[0,0].set_title(f"Left-Lower bound $\zeta_1$ = {min_zeta_1}; $\zeta_2$ = 0.85")


ax[0,1].plot(xpts_RL, ypts_RL, marker = "o", color = "tab:blue")
ax[0,1].plot(xpts_RL, ypts_RL, color = "black")
ax[0,1].set_title(f"Right-Lower bound $\zeta_1$ = {max_zeta_1}; $\zeta_2$ ={zetas_2[-1]}")

ax[1,0].plot(xpts_RU, ypts_RU, marker = "o", color = "tab:blue")
ax[1,0].plot(xpts_RU, ypts_RU, color = "black")
ax[1,0].set_title(f"Right-Upper bound $\zeta_1$ = {max_zeta_1}; $\zeta_2$ ={max_zeta_2}")

ax[1,1].plot(xpts_LU, ypts_LU, marker = "o", color = "tab:blue")
ax[1,1].plot(xpts_LU, ypts_LU, color = "black")
ax[1,1].set_title(f"Left-Upper bound $\zeta_1$ = {min_zeta_1}; $\zeta_2$ ={max_zeta_2}")
for a in ax.flat:
    a.set_aspect('equal', adjustable='box')

plt.tight_layout()
plt.show()

