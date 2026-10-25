import matplotlib.pyplot as plt
import numpy as np
from Hermite import hermit_bl, generate_hermite_paper_fairing
plt.rcParams.update({
    "font.size": 12,
    "font.family": "serif"
})
# f(x) parameters
a = 0.05067808
b = -0.55044524
c = 2.18505828
d = -4.08722944
e = 3.35193831
f = 2.95

# g(x) parameters
m = 0.37
B = 0.85

# Functions
def h(x):
    return a*x**5 + b*x**4 + c*x**3 + d*x**2 + e*x + f

def g(x):
    return m*x + B

L = 3.6

# Mapping coordinates
u = np.linspace(0, 1, 10)
v = np.linspace(0, 1, 10)

U, V = np.meshgrid(u, v)

X = U * L
Y = g(X) + V * (h(X)-g(X))

x = np.linspace(0, L, 100)


normalized_bounds = np.array([
  [-1,-1],
  [1,1],
  [-1,1],
  [1,-1],
  [0,0],
  [-1,0],
  [1,0],
  [0,-1],
  [0, 1]
])

bound = [0,1]
def coded_to_mapped(cx):
    
    t =  (bound[1] + 0)/2  + cx[0]*0.5
    r =  (bound[1] + 0)/2  + cx[1]*0.5
    return [t,r]


def mapped_to_real(MP):
    # MP = [u,v]
    P = MP[0]*L
    Q = g(P) + MP[1] * (h(P)-g(P))
    return P, Q




mapped_values = []
for coded in normalized_bounds:
    t,r = coded_to_mapped(coded)
    mapped_values.append([t,r])



real_values = []
for mapped in mapped_values:
    p,q = mapped_to_real(mapped)
    real_values.append([p,q])


"""
for value in real_values:
    profile = generate_hermite_paper_fairing(value[0], value[1],
                                            nps = 30, export_filename = f"protuberance_coords_{value[0]}_{value[1]}.csv")


    



"""



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
zeta_1 = np.linspace(min_zeta_1, 5,500)
zeta_2 = np.linspace(min_zeta_1, 5,500)

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

X_m = np.linalg.solve(A,B).flatten()

print(X_m)
zetas_2_parabola = X_m[0]*zetas_1**5 + X_m[1]*zetas_1**4 + X_m[2]*zetas_1**3  + X_m[3]*zetas_1**2 +  X_m[4]*zetas_1 + X_m[5] 


print(real_values[:][0], real_values[:][1])
from matplotlib.patches import Patch

xs_1 = [max_zeta_1, max_zeta_1]
ys_1 = [zetas_2[-1], max_zeta_2]
plt.figure(figsize=(5, 5))

plt.contourf(
    Z1, Z2, valid.astype(int),
    levels=[-0.5, 0.5],
    colors=["#BDBDBD"],
    alpha= 0.3
)

plt.contourf(
    Z1, Z2, valid.astype(int),
    levels=[0.5, 1.5],
    colors=["#0072B2"],
    alpha=0.4
)
plt.contour(
    Z1, Z2, valid.astype(int),
    levels=[0.5],
    colors="#1F3552",
    linewidths=1.5
)

real_values = np.array(real_values)
plt.scatter(real_values[:,0], real_values[:,1], color = "#FF0000", label = "CCD points", marker = "v", s = 64, zorder = 5)

from scipy.interpolate import interp1d

for i in range(X.shape[0]):
    x_1_ = X[i, :]
    y_1 =  Y[i, :]
    f = interp1d(x_1_, y_1, kind="quadratic")

    x_new = np.linspace(0, 3.6, 100)
    y_new = f(x_new)

    plt.plot(x_new, y_new,  "--", color="k")
    plt.scatter(x_1_,y_1, color = "k", s =5)

for j in range(X.shape[1]):

    plt.plot(X[:, j], Y[:, j], "--", color="k")
    plt.scatter(X[:, j], Y[:, j], color = "k", s =5)



# desing space plot
plt.plot(zetas_1, zetas_2_parabola, "--", color = "navy", linewidth= 2.5)
plt.plot(zetas_1, zetas_2, "--", color = "navy", label = "Design Space", linewidth= 2.5)
plt.plot([0,0], [0.85,X_m[-1]], "--", color = "navy", linewidth= 2.5)

# ccd points plot


plt.xlabel(r"$\zeta_1$")
plt.ylabel(r"$\zeta_2$")
plt.title("Design space assesment")
regions = [
    Patch(facecolor="#BDBDBD", label="Invalid", edgecolor="#6E6E6E"),
    Patch(facecolor="#0072B2", label="Valid", edgecolor="#1F3552")
]
handles, labels = plt.gca().get_legend_handles_labels()

plt.legend(handles=regions + handles)

#plt.axis("equal")
plt.xlim([min_zeta_1, 5])
plt.tight_layout()
plt.ylim([min_zeta_1, 5])
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



print(real_values)
# left low hermite
xpts_LL, ypts_LL = bounds_hermite(real_values[0][0], real_values[0][1])

# right low hermite
xpts_RL, ypts_RL = bounds_hermite(real_values[1][0], real_values[1][1])

# lft upper hermite
xpts_LU, ypts_LU = bounds_hermite(real_values[2][0], real_values[2][1])

# low_ medium
xpts_LM, ypts_LM = bounds_hermite(real_values[7][0], real_values[7][1])

# upper medium
xpts_UM, ypts_UM = bounds_hermite(real_values[8][0], real_values[8][1])

#MEDIUM MEDIUM
xpts_MM, ypts_MM = bounds_hermite(real_values[4][0], real_values[4][1])

fig, ax = plt.subplots(2, 3, figsize=(12, 4))
ax[0,0].plot(xpts_LL, ypts_LL, marker = "o", color = "tab:blue")
ax[0,0].plot(xpts_LL, ypts_LL, color = "black")
ax[0,0].set_title(f"Left-Lower bound $\zeta_1$ = {real_values[0][0]}; $\zeta_2$ = {real_values[0][1]}")


ax[0,1].plot(xpts_RL, ypts_RL, marker = "o", color = "tab:blue")
ax[0,1].plot(xpts_RL, ypts_RL, color = "black")
ax[0,1].set_title(f"Right-Lower bound $\zeta_1$ = {np.round(real_values[1][0], 2)}; $\zeta_2$ ={np.round(real_values[1][1], 2)}")

ax[0,2].plot(xpts_LU, ypts_LU, marker = "o", color = "tab:blue")
ax[0,2].plot(xpts_LU, ypts_LU, color = "black")
ax[0,2].set_title(f"Left-Upper bound $\zeta_1$ = {np.round(real_values[2][0], 2)}; $\zeta_2$ ={np.round(real_values[2][1], 2)}")

ax[1,0].plot(xpts_LM, ypts_LM, marker = "o", color = "tab:blue")
ax[1,0].plot(xpts_LM, ypts_LM, color = "black")
ax[1,0].set_title(f"Medium-Lower bound $\zeta_1$ = {np.round(real_values[7][0], 2)}; $\zeta_2$ ={np.round(real_values[7][1],2)}")

ax[1,1].plot(xpts_UM, ypts_UM, marker = "o", color = "tab:blue")
ax[1,1].plot(xpts_UM, ypts_UM, color = "black")
ax[1,1].set_title(f"Medium-Upper bound $\zeta_1$ = {np.round(real_values[8][0], 2)}; $\zeta_2$ ={np.round(real_values[8][1], 2)}")

ax[1,2].plot(xpts_MM, ypts_MM, marker = "o", color = "tab:blue")
ax[1,2].plot(xpts_MM, ypts_MM, color = "black")
ax[1,2].set_title(f"Medium-Medium bound $\zeta_1$ = {np.round(real_values[4][0],2)}; $\zeta_2$ ={np.round(real_values[4][1],2)}")

for a in ax.flat:
    a.set_aspect('equal', adjustable='box')

plt.tight_layout()
plt.show()