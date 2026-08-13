import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize

# ==============================
# 1. DATOS DEL CCD (CODIFICADOS)
# ==============================

X_coded = np.array([
    [-1,-1,-1],
    [ 1,-1,-1],
    [-1, 1,-1],
    [ 1, 1,-1],
    [-1,-1, 1],
    [ 1,-1, 1],
    [-1, 1, 1],
    [ 1, 1, 1],
    [ 1, 0, 0],
    [-1, 0, 0],
    [ 0, 1, 0],
    [ 0,-1, 0],
    [ 0, 0, 1],
    [ 0, 0,-1],
    [ 0, 0, 0],
    [ 0, 0, 0],
    [ 0, 0, 0],
    [ 0, 0, 0],
    [ 0, 0, 0],
    [ 0, 0, 0],
])
# Results ==============================


CD = np.array([
    0.97255972,
    1.0137771,
    1.0000866,
    0.97783497,
    0.97429758,
    0.98081865,
    0.97831795,
    0.97785195,
    0.97787442,
    0.97704191,
    0.97429338,
    0.97593080,
    0.97462849
])

CY = np.array([
    0.00542041,
    0.00939375,
    0.00810714,
    0.00399631,
    0.00631185,
    0.00991730,
    0.00433453,
    0.00441803,
    0.00582223,
    0.00435670,
    0.00550246,
    0.00566040,
    0.00417647
])


# Cuadratic regression
poly = PolynomialFeatures(degree=2, include_bias=True)
X_poly = poly.fit_transform(X_coded)

model_CD = LinearRegression().fit(X_poly, CD)
model_CY = LinearRegression().fit(X_poly, CY)

# ==============================
# FUNCIÓN OBJETIVO
# ==============================

w1 = 1.0   # peso drag
w2 = 1.0   # peso side force

def objective(x):
    x = np.array(x).reshape(1, -1)
    x_poly = poly.transform(x)
    
    cd = model_CD.predict(x_poly)[0]
    cy = model_CY.predict(x_poly)[0]
    
    return w1*cd + w2*cy

# ==============================
# 5. OPTIMIZACIÓN
# ==============================

bounds = [(-1,1), (-1,1), (-1,1)]
x0 = [0,0,0]

result = minimize(objective, x0, bounds=bounds, method='SLSQP')

x_opt = result.x

# ==============================
# 6. CONVERTIR A VARIABLES REALES
# ==============================

def coded_to_real(x):
    infx = 43.5 + 43.5*x[0]
    infy = 11   + 11*x[1]
    supx = 30   + 30*x[2]
    return infx, infy, supx

infx_opt, infy_opt, supx_opt = coded_to_real(x_opt)

# ==============================
# 7. RESULTADOS
# ==============================

print("\n===== RESULTADOS =====")
print("Variables óptimas (codificadas):", x_opt)
print("infx (mm):", infx_opt)
print("infy (mm):", infy_opt)
print("supx (mm):", supx_opt)

print("\nValor objetivo:", result.fun)

# Evaluación final
x_poly_opt = poly.transform(np.array(x_opt).reshape(1,-1))
cd_opt = model_CD.predict(x_poly_opt)[0]
cy_opt = model_CY.predict(x_poly_opt)[0]

print("CD estimado:", cd_opt)
print("CY estimado:", cy_opt)

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ==============================
# FUNCIÓN PARA EVALUAR MODELOS
# ==============================

def predict_cd(x):
    x_poly = poly.transform(np.array(x).reshape(1,-1))
    return model_CD.predict(x_poly)[0]

def predict_cy(x):
    x_poly = poly.transform(np.array(x).reshape(1,-1))
    return model_CY.predict(x_poly)[0]

def predict_obj(x):
    return w1*predict_cd(x) + w2*predict_cy(x)

# ==============================
# FUNCIÓN PARA GRAFICAR
# ==============================

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_surface(var1, var2, fixed_index, fixed_value=0):

    grid = np.linspace(-1, 1, 50)
    X, Y = np.meshgrid(grid, grid)

    Z_cd = np.zeros_like(X)
    Z_cy = np.zeros_like(X)
    Z_obj = np.zeros_like(X)

    for i in range(len(grid)):
        for j in range(len(grid)):
            point = [0,0,0]
            point[var1] = X[i,j]
            point[var2] = Y[i,j]
            point[fixed_index] = fixed_value

            Z_cd[i,j] = predict_cd(point)
            Z_cy[i,j] = predict_cy(point)
            Z_obj[i,j] = predict_obj(point)

    labels = ['infx', 'infy', 'supx']
# Figures
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z_cd, cmap='coolwarm')
    ax.scatter(X_coded[:])
    fig.colorbar(surf)
    ax.set_xlabel(labels[var1])
    ax.set_ylabel(labels[var2])
    ax.set_zlabel('CD')
    ax.set_title(f"CD Surface ({labels[var1]} vs {labels[var2]})")
    plt.show()
#=======================
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z_cy, cmap='coolwarm')
    fig.colorbar(surf)
    ax.set_xlabel(labels[var1])
    ax.set_ylabel(labels[var2])
    ax.set_zlabel('CY')
    ax.set_title(f"CY Surface ({labels[var1]} vs {labels[var2]})")
    plt.show()

    # ==========================
    
    # ==========================
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z_obj, cmap='coolwarm')
    fig.colorbar(surf)
    ax.set_xlabel(labels[var1])
    ax.set_ylabel(labels[var2])
    ax.set_zlabel('Objective')
    ax.set_title(f"Objective Surface ({labels[var1]} vs {labels[var2]})")
    plt.show()

    # ==========================

    fig, ax = plt.subplots()

    contour = ax.contourf(X, Y, Z_obj, levels=30, cmap='coolwarm')
    fig.colorbar(contour)

    ax.set_xlabel(labels[var1])
    ax.set_ylabel(labels[var2])
    ax.set_title(f"Objective Heatmap ({labels[var1]} vs {labels[var2]})")

    # marcar mínimo aproximado en la malla
    idx = np.unravel_index(np.argmin(Z_obj), Z_obj.shape)
    ax.plot(X[idx], Y[idx], 'ko')  # punto negro

    plt.show()

#=============================================
#