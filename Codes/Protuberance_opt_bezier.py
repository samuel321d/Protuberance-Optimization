# Libraries
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize

# DATA FROM SIMULATIONS ==================================================================================
CD = np.array([
    0.97255972,
    0.97236026,
    0.97336911,
    0.97783497,
    0.97429758,
    0.98081865,
    0.97831795,
    0.97453492,
    0.97785195,
    0.97787442,
    0.97208514,
    0.97704191,
    0.97429338,
    0.97593080,
    0.97462849
])

CY = np.array([
    0.00542041,
    0.00599532,
    0.00575979,
    0.00399631,
    0.00631185,
    0.00991730,
    0.00433453,
    0.00436945,
    0.00441803,
    0.00582223,
    0.00625490,
    0.00435670,
    0.00550246,
    0.00566040,
    0.00417647
])

#==================================================================================


import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize

def objective(x, model_CD, model_CY, w_cd, w_cy, poly):
    x = np.array(x).reshape(1, -1)
    x_poly = poly.transform(x)

    cd = model_CD.predict(x_poly)[0]
    cy = model_CY.predict(x_poly)[0]

    return w_cd*cd + w_cy*cy

# desnormalizar
def coded_to_real(x):
    infx = 43.5 + 43.5*x[0]
    infy = 11   + 11*x[1]
    supx = 30   + 30*x[2]
    return infx, infy, supx


def polynomial_regression(CD, CY, w_cd, w_cy):
    # Normalizado
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
    ])

    poly = PolynomialFeatures(degree=3, include_bias=False)
    X_poly = poly.fit_transform(X_coded)

    model_CD = LinearRegression().fit(X_poly, CD)
    model_CY = LinearRegression().fit(X_poly, CY)


    r2_CD = model_CD.score(X_poly, CD)
    r2_CY = model_CY.score(X_poly, CY)

    # RESULTS 
    print("R2 CD:", r2_CD)
    print("R2 CY:", r2_CY)

    feature_names = poly.get_feature_names_out(['x1', 'x2', 'x3'])

    # Print mathematical Model for CD
    print("\n--- Equation Coefficients for CD ---")
    print(f"Intercept (Beta_0): {model_CD.intercept_:.6f}")
    for name, coef in zip(feature_names, model_CD.coef_):
        print(f"{name}: {coef:.6f}")

    # Print the Mathematical Model for CY
    print("\n--- Equation Coefficients for CY ---")
    print(f"Intercept (Beta_0): {model_CY.intercept_:.6f}")
    for name, coef in zip(feature_names, model_CY.coef_):
        print(f"{name}: {coef:.6f}")

    # optimización
    bounds = [(-1,1), (-1,1), (-1,1)]
    x0 = [0,0,0]

    result = minimize(objective, x0,args = (model_CD, model_CY, w_cd, w_cy, poly),
                        bounds=bounds, method='SLSQP')

    x_opt = result.x
    infx_opt, infy_opt, supx_opt = coded_to_real(x_opt)
    # resultados
    print("\n===== RESULTADOS =====")
    print("Variables óptimas (codificadas):", x_opt)
    print("infx (mm):", infx_opt)
    print("infy (mm):", infy_opt)
    print("supx (mm):", supx_opt)

    print("\nValor objetivo:", result.fun)

    x_poly_opt = poly.transform(np.array(x_opt).reshape(1,-1))
    cd_opt = model_CD.predict(x_poly_opt)[0]
    cy_opt = model_CY.predict(x_poly_opt)[0]

    print("CD estimado:", cd_opt)
    print("CY estimado:", cy_opt)



polynomial_regression(CD, CY, 0, 1)

import itertools
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

labels = ["INF_X", "INF_Y", "SUP_X"]

def plot_surfaces(model, x_fixed, ccd_points, y_true,resolution=100):

    if model == "cd":
        bar_label = "$C_D$"
    else:
        bar_label = "$C_Y$"

    vars_idx = [0,1,2]

    # combinaciones de variables
    combinations = list(itertools.combinations(vars_idx, 2))

    for var1, var2 in combinations:

        # variable fija
        fixed_var = list(set(vars_idx) - set([var1, var2]))[0]

        grid = np.linspace(-1, 1, resolution)

        A, B = np.meshgrid(grid, grid)

        points = np.zeros((A.size, 3))

        points[:, fixed_var] = x_fixed[fixed_var]
        points[:, var1] = A.ravel()
        points[:, var2] = B.ravel()

        #Z = model.

        # =====================================
        # CONTOUR
        # =====================================
# =====================================
        # 3D SURFACE
        # =====================================

        fig = plt.figure(figsize=(9, 7))
        ax = fig.add_subplot(111, projection='3d')

        surf = ax.plot_surface(A, B, Z, cmap='jet', alpha=0.9)

        # 2. Determinar la altura (offset) donde se dibujará la base
        z_min = np.min(Z)
        z_max = np.max(Z)
        offset_val = z_min - (z_max - z_min) * 0.05 # Ligeramente debajo del mínimo de Z

        # 3. Proyectar las líneas de contorno en la base
        ax.contour(A, B, Z, zdir='z', offset=offset_val, cmap='jet', linewidths=1.2, levels=15)

        # 4. Forzar el límite inferior del eje Z para que el contorno sea visible
        ax.set_zlim(bottom=offset_val, top=z_max)

        tol = 1e-6
        mask = np.isclose(ccd_points[:, fixed_var], x_fixed[fixed_var], atol=tol)
        ccd_slice = ccd_points[mask]
        y_slice = y_true[mask]

        if len(ccd_slice) > 0:
            z_ccd = model.predict_values(ccd_slice)
            ax.scatter(
                ccd_slice[:, var1],
                ccd_slice[:, var2],
                y_slice,
                color='k',
                s=50,
                label='CCD Points'
            )

        fig.colorbar(surf, label = bar_label)

        # Etiquetas
        ax.set_xlabel(labels[var1])
        ax.set_ylabel(labels[var2])
        ax.set_zlabel(bar_label)

        # Corrección menor: usar 'f' en lugar de 'r' para que las variables se impriman correctamente
        ax.set_title(
            f"{labels[var1]} vs {labels[var2]}\n"
            f"{labels[fixed_var]} fixed = "
            f"{x_fixed[fixed_var]:.3f}"
        )

        plt.show()