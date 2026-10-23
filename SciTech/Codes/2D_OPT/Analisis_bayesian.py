import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import griddata
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel
from sklearn.preprocessing import MinMaxScaler

# History data reading

data_bayesian = pd.read_csv("optimization_history_bayesian.csv")

param_a = data_bayesian["Parameter_1"]
param_b = data_bayesian["Parameter_2"]




# Analisis of results

# General statistics

def statistics(performance_param):

    min = data_bayesian[performance_param].min()
    max = data_bayesian[performance_param].max()
    mean = data_bayesian[performance_param].mean()
    std = np.std(data_bayesian[performance_param])
    print(50*"=")    
    print(f"{performance_param} Statistics")
    print(f"Minimum {performance_param} : {min}")
    print(f"Maximum {performance_param} : {max}")

print(50*"=")
print("CD STATISTICS")






A, B = np.meshgrid(np.linspace(param_a.min(), param_a.max(), 100 ),
                   np.linspace(param_b.min(), param_b.max(), 100 )
                   )

# interpolation of points
J_grid = griddata(
    (param_a, param_b), data_bayesian["Objective"],
    (A,B),
    method = "linear"
)

Cd_grid = griddata(
    (param_a, param_b), data_bayesian["Cd"],
    (A,B), method = "linear"
)


Cp_int_grid = griddata(
    (param_a, param_b), data_bayesian["Cp_integral"],
    (A,B), method = "linear"
)

Cp_grad_grid = griddata(
    (param_a, param_b), data_bayesian["Cp_gradient"],
    (A,B), method = "linear"
)

fig = plt.figure(1)
ax = fig.add_subplot(111, projection = "3d")
ax.plot_surface(A, B, J_grid, cmap = "jet")

ax.scatter(param_a, param_b, data_bayesian["Objective"], s = 35, label = "CFD evaluations")
ax.set_xlabel("Parameter A")
ax.set_ylabel("Parameter B")
ax.set_zlabel("Objective Function")
ax.legend()
ax.set_title(f"Objective function evaluations")
plt.show()





fig = plt.figure(2)
ax = fig.add_subplot(111, projection = "3d")
ax.plot_surface(A, B, Cp_int_grid, cmap = "jet")

ax.scatter(param_a, param_b, data_bayesian["Cp_integral"], s = 35, label = "CFD evaluations")
ax.set_xlabel("Parameter A")
ax.set_ylabel("Parameter B")
ax.set_zlabel("Cp integral")
ax.legend()
ax.set_title(f"Cp integral results")
plt.show()



fig = plt.figure(3)
ax = fig.add_subplot(111, projection = "3d")
ax.plot_surface(A, B, Cp_grad_grid, cmap = "jet")

ax.scatter(param_a, param_b, data_bayesian["Cp_gradient"], s = 35, label = "CFD evaluations")
ax.set_xlabel("Parameter A")
ax.set_ylabel("Parameter B")
ax.set_zlabel("Cp gradient")
ax.legend()
ax.set_title(f"Cp grdient results")
plt.show()


fig = plt.figure(4)
ax = fig.add_subplot(111, projection = "3d")
ax.plot_surface(A, B, Cd_grid, cmap = "jet")

ax.scatter(param_a, param_b, data_bayesian["Cd"], s = 35, label = "CFD evaluations")
ax.set_xlabel("Parameter A")
ax.set_ylabel("Parameter B")
ax.set_zlabel("Cd ")
ax.legend()
ax.set_title(f"Cd Results")
plt.show()











"""
# Matriz de parámetros
X = np.column_stack((param_a, param_b))
J = np.asarray(data_bayesian["Objective"])

scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X)

kernel = ConstantKernel(1.0) * Matern(
    length_scale=[0.2, 0.2],
    length_scale_bounds=(0.01, 10.0),
    nu=2.5
)

gp = GaussianProcessRegressor(
    kernel=kernel,
    normalize_y=True,
    n_restarts_optimizer=10,
    random_state=42
)

gp.fit(X, J)

# Malla de predicción
A, B = np.meshgrid(
    np.linspace(X[:, 0].min(), X[:, 0].max(), 100),
    np.linspace(X[:, 1].min(), X[:, 1].max(), 100)
)

X_grid = np.column_stack((A.ravel(), B.ravel()))

J_pred, J_std = gp.predict(X_grid, return_std=True)
J_pred = J_pred.reshape(A.shape)

# Superficie predictiva y puntos CFD
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

ax.plot_surface(A, B, J_pred, cmap="coolwarm", alpha=0.8)
ax.scatter(X[:, 0], X[:, 1], J, color="k", s=35)

ax.set_xlabel("Parameter A")
ax.set_ylabel("Parameter B")
ax.set_zlabel("Predicted objective")

plt.show()
print(gp.kernel_)
print("Límites:", gp.kernel_.bounds)
#print(data_bayesian.head())
"""