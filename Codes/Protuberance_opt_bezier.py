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

# Plots config
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

#==================================================================================

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


def polynomial_regression(CD, CY, w_cd, w_cy, deg, mode):
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

    poly = PolynomialFeatures(degree=deg, include_bias=False)
    X_poly = poly.fit_transform(X_coded)

    model_CD = LinearRegression().fit(X_poly, CD)
    model_CY = LinearRegression().fit(X_poly, CY)


    r2_CD = model_CD.score(X_poly, CD)
    r2_CY = model_CY.score(X_poly, CY)



    # optimización
    bounds = [(-1,1), (-1,1), (-1,1)]
    x0 = [0,0,0]

    result = minimize(objective, x0,args = (model_CD, model_CY, w_cd, w_cy, poly),
                        bounds=bounds, method='SLSQP')

    x_opt = result.x
    infx_opt, infy_opt, supx_opt = coded_to_real(x_opt)
    if mode == True:
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
    else:
        return model_CD, model_CY, x_opt, poly


    

# Function caller: polynomial_regression(CD, CY, 0, 1)

# Variables globales para los labels
labels = ["INF_X", "INF_Y", "SUP_X"]

def plot_surfaces(model_type, model, target_name, x_fixed, ccd_points, y_true, poly_transformer=None, resolution=100):
    """
    Inputs:
    - model_type: str, "poly" para Regresión Polinomial, "kriging" para Surrogate Kriging.
    - model: objeto del modelo entrenado (ej. model_CD de sklearn o un modelo Kriging).
    - target_name: str, "cd" o "cy" para colocar el nombre correcto en las etiquetas.
    - x_fixed: list/array, los valores de [x1, x2, x3] donde se fijarán los planos.
    - ccd_points: array, los puntos reales (codificados) usados en los experimentos.
    - y_true: array, los valores de respuesta real de CD o CY.
    - poly_transformer: objeto PolynomialFeatures (solo necesario si model_type == "poly").
    - resolution: int, cantidad de puntos en la malla.
    """
    
    # Asignar la etiqueta matemática correspondiente
    if target_name.lower() == "cd":
        bar_label = "$C_D$"
    else:
        bar_label = "$C_Y$"

    vars_idx = [0, 1, 2]

    # Combinaciones posibles de 2 variables (para los ejes X e Y del gráfico 3D)
    combinations = list(itertools.combinations(vars_idx, 2))

    for var1, var2 in combinations:
        # Identificar qué variable se queda fija
        fixed_var = list(set(vars_idx) - set([var1, var2]))[0]

        # Crear el grid
        grid = np.linspace(-1, 1, resolution)
        A, B = np.meshgrid(grid, grid)

        # Preparar la matriz de puntos con la variable fija y las variables iteradas
        points = np.zeros((A.size, 3))
        points[:, fixed_var] = x_fixed[fixed_var]
        points[:, var1] = A.ravel()
        points[:, var2] = B.ravel()
        
        # =====================================
        # PREDICCIÓN DE Z SEGÚN EL MODELO
        # =====================================
        if model_type.lower() == "poly":
            if poly_transformer is None:
                raise ValueError("Provide 'poly_transformer' to execute the polinomial function.")
            points_poly = poly_transformer.transform(points)
            Z_flat = model.predict(points_poly)
            
        elif model_type.lower() == "kriging":
            # Asumimos la sintaxis típica de Kriging (ej. SMT Surrogate Modeling Toolbox)
            Z_flat = model.predict_values(points)
            
        else:
            raise ValueError("El model_type debe ser 'poly' o 'kriging'.")

        # Asegurarnos de que Z tenga la forma geométrica del grid (resolution x resolution)
        Z = Z_flat.flatten().reshape(A.shape)

        # =====================================
        # GRÁFICO (3D SURFACE Y CONTOUR)
        # =====================================
        fig = plt.figure(figsize=(9, 7))
        ax = fig.add_subplot(111, projection='3d')

        # Superficie principal
        surf = ax.plot_surface(A, B, Z, cmap='jet', alpha=0.8)

        # Determinar la altura (offset) donde se dibujará la base (contorno)
        z_min = np.min(Z)
        z_max = np.max(Z)
        # Ligeramente debajo del mínimo de Z
        offset_val = z_min - (z_max - z_min) * 0.05 

        # Proyectar las líneas de contorno en la base
        ax.contour(A, B, Z, zdir='z', offset=offset_val, cmap='jet', linewidths=1.2, levels=15)
        ax.set_zlim(bottom=offset_val, top=z_max)

        # =====================================
        # PUNTOS EXPERIMENTALES (CCD)
        # =====================================
        tol = 1e-6
        # Filtrar puntos experimentales que están en el mismo plano de la variable fija
        mask = np.isclose(ccd_points[:, fixed_var], x_fixed[fixed_var], atol=tol)
        ccd_slice = ccd_points[mask]
        y_slice = y_true[mask]

        if len(ccd_slice) > 0:
            ax.scatter(
                ccd_slice[:, var1],
                ccd_slice[:, var2],
                y_slice,
                color='k',
                s=50,
                label='Puntos Experimentales'
            )
            ax.legend()

        # Etiquetas, Títulos y Colorbar
        fig.colorbar(surf, label=bar_label)
        ax.set_xlabel(labels[var1])
        ax.set_ylabel(labels[var2])
        ax.set_zlabel(bar_label)

        ax.set_title(
            f"{labels[var1]} vs {labels[var2]}\n"
            f"{labels[fixed_var]} fixed = {x_fixed[fixed_var]:.3f}"
        )

        plt.show()

#polynomial_regression(CD, CY, 0.2, 0.8, 4, mode = True)
#model_CD, model_CY, x_opt, poly = polynomial_regression(CD, CY, 0, 1, 4, mode = False)
#poly = PolynomialFeatures(degree=4, include_bias=False)
#plot_surfaces("poly", model_CD, "cd", x_opt, X_coded, CD,poly_transformer= poly)


#===================================================================================




def objective_kriging(x,CDs, CYs, w_cd, w_cy, model_cd, model_cy):
    """ Function aimed to opmitize an objective funcion pondered by cd and cy for the kriging surrogate"
        Inputs:
        - x: vector to evaluate
        - CDs: List that contains the min a max values from the original CD array
        - CYs: List that contains the min a max values from the original CY array
        - w_cd: weigh of CD
        - W_cy: weight of CY
        - Kriging surrogate models    
    """
    CD_min, CD_max = CDs
    CY_min, CY_max = CYs

    x = np.array(x).reshape(1,-1)

    cd = model_cd.predict_values(x)[0,0]
    cy = model_cy.predict_values(x)[0,0]

    # normalizacion
    cd_norm = (cd - CD_min)/(CD_max - CD_min)
    cy_norm = (cy - CY_min)/(CY_max - CY_min)

    return w_cd*cd_norm + w_cy*cy_norm



def kriging(CD, CY, w_cd, w_cy):

    CD_reshaped = CD.reshape(-1, 1)
    CY_reshaped = CY.reshape(-1, 1)

    # ==============================
    # MOdelo kriging

    # Modelo CD
    sm_cd = KRG(theta0=[1e-2]*3, print_global=False)
    sm_cd.set_training_values(X_coded, CD_reshaped)
    sm_cd.train()

    # Modelo Cy
    sm_cy = KRG(theta0=[1e-2]*3, print_global=False)
    sm_cy.set_training_values(X_coded, CY_reshaped)
    sm_cy.train()

    # Models evaluation
    x_eval = np.array([[0.8,0.8,0.8]]) # We evaluate the at a random point out of the dataset
    Cd_pred = sm_cd.predict_values(x_eval)

    Cy_pred = sm_cy.predict_values(x_eval)

    # Variance and model performance
    Cd_var = sm_cd.predict_variances(x_eval)
    Cy_var = sm_cy.predict_variances(x_eval)

    print("="*50)
    print("Model performance Prediction:")
    print("="*50)
    print(f"Predicción de CD: {Cd_pred}")
    print(f"Varianza de CD: {Cd_var}")
    print("="*30)
    print(f"Predicción de CY: {Cy_pred}")

    print(f"Varianza de CY: {Cy_var}")

    # Minimization
    x0 = [0,0,0]
    bounds = [(-1,1), (-1,1), (-1,1)]
    
    CDs = [CD.min(), CD.max()]
    CYs = [CY.min(), CY.max()]

    minimization = minimize(
    objective_kriging,
    x0,
    args=(CDs, CYs, w_cd, w_cy, sm_cd, sm_cy,),
    bounds = bounds,
    method='SLSQP'
    )

    x_opt = minimization.x
    print("="*50)
    print("="*50)    
    print("Optimization Results:")
    print("="*50)
    print(f"X optimum for obetive fun: {w_cd} Cd + {w_cy} CY : {x_opt}")
    print(f"Real parameter values:")
    print(coded_to_real(x_opt))
    return sm_cd, sm_cy, x_opt


sm_cd, sm_cy, x_opt = kriging(CD, CY, 0, 1)

#plot_surfaces("kriging", sm_cy, "cy", x_opt, X_coded, CY)


cd_M06 = np.array([
    0.71847113,
    0.71870199,
    0.71900538,
    0.71880551,
    0.72066854,
    0.71846812,
    0.71918084,
    0.71693225,
    0.71829,
    0.7182505,
    0.71757527,
    0.71797325,
    0.71814265,
    0.71777072,
    0.71884376,
])
cy_M06 = np.array([
    0.017183182,
    0.016057047,
    0.016013796,
    0.016918182,
    0.017112903,
    0.01619539,
    0.016316143,
    0.018736481,
    0.01741,
    0.01802637,
    0.01745053,
    0.01765875,
    0.017155085,
    0.01817863,
    0.015968937,
])

polynomial_regression(cd_M06, cy_M06, 0, 1, 4, mode = True)
model_CD, model_CY, x_opt_06, poly = polynomial_regression(cd_M06, cy_M06, 0, 1, 4, mode = False)

plot_surfaces("poly", model_CY, "cy", x_opt_06, X_coded, cy_M06,poly_transformer= poly)