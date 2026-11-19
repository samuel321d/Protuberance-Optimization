# ===========================================================================
# SENSIBILITY ANAYSIS FOR CCD OPTIMIZATION

# This Script aims to perform a sensibility analysis for the CCD optimization 
# ===========================================================================

# Libraries
from glob import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import statsmodels.formula.api as smf
import statsmodels.api as sm
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from sklearn.neighbors import NearestNeighbors
import seaborn as sns

# ===========================================================================
# MATPLOTLIB PARAMS
plt.rcParams.update({
    "font.size": 10,
    "font.family": "serif"
})
# ===========================================================================

# ===========================================================================
# Directories where CSV are stored
# ===========================================================================

folder = os.path.dirname(os.path.abspath(__file__))
# calling the csv´s classified by the source
Histories = glob(os.path.join(folder,"Results",  "history_*.csv"))
archivos_ordenados = sorted(
    Histories, 
    key=lambda f: os.path.basename(f).lower()
)
# Dictionaries to store the dataframes
dfs_hist = {
    os.path.splitext(os.path.basename(f))[0]: pd.read_csv(f) 
    for f in archivos_ordenados
}

for key in dfs_hist:
    print(f"File: {key}")

res_cy = []
res_ca = []
res_cm = []
res_cz = []
res_cmz = []
for hist in dfs_hist.values():
    res_cy.append(hist['       "CFy"      '].values[-1]*-1)   
    res_ca.append(hist['       "CFx"      '].values[-1])   
    res_cm.append(hist['       "CMy"      '].values[-1])   
    res_cz.append(hist['       "CFz"      '].values[-1])   
    res_cmz.append(hist['       "CMz"      '].values[-1])   

# ===========================================================================
# CCD POINTS definition and functions to convert
# ===========================================================================

normalized_bounds = np.array([
    [-1,-1],
    #[1,1],
    [-1,1],
    [1,-1],
    [0,0],
    [-1,0],
    #[1,0],
    [0,-1],
    [0, 1],
    # From here are the additional points
    [-0.5, 1.0],
    [0.5, 1.0],
    [-0.5, -1.0],
    [0.5, -1.0],
    [-0.5, 0.0],
    [0.5, 0.0]
])

# Functions describing bounds

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
# ===========================================================================

# ===========================================================================
# Dataframe to store all the data
# ===========================================================================

df_ccd = pd.DataFrame({
    "X1": [x[0] for x in normalized_bounds],
    "X2": [x[1] for x in normalized_bounds],
    "mapped_values_x1": [x[0] for x in mapped_values],
    "mapped_values_x2": [x[1] for x in mapped_values],
    "real_values_x1": [x[0] for x in real_values],
    "real_values_x2": [x[1] for x in real_values],
    "Real_pairs": real_values
})

df_ccd = df_ccd.sort_values(by = "Real_pairs").reset_index(drop=True)  
df_ccd["Cy"] = res_cy
df_ccd["Ca"] = res_ca
df_ccd["Cm"] = res_cm
df_ccd["Cz"] = res_cz
df_ccd["Cmz"] = res_cmz

coefs = ["Cy", "Ca", "Cm", "Cz", "Cmz"]
# ===========================================================================

# ===========================================================================
# Initial Plots: Coefficients vs design variables
# =========================================================================== 
# Put True in case you waant to see the plots
plots = False

if plots:
    fig, axs = plt.subplots(3, 2, figsize=(12, 10))
    axs = axs.flatten()

    for i, coef in enumerate(coefs):
        axs[i].scatter(df_ccd["real_values_x1"], df_ccd[coef], color='blue', label='Data Points')
        axs[i].set_xlabel('Real Values X1')
        axs[i].set_ylabel(coef)
        axs[i].set_title(f'{coef} vs Real Values X1')
        axs[i].legend()
        axs[i].grid()

    plt.tight_layout()
    plt.show()

    fig, axs = plt.subplots(3, 2, figsize=(12, 10))
    axs = axs.flatten()

    for i, coef in enumerate(coefs):
        axs[i].scatter(df_ccd["real_values_x2"], df_ccd[coef], color='green', label='Data Points')
        axs[i].set_xlabel('Real Values X2')
        axs[i].set_ylabel(coef)
        axs[i].set_title(f'{coef} vs Real Values X2')
        axs[i].legend()
        axs[i].grid()
    plt.tight_layout()
    plt.show()


    fig, axs = plt.subplots(3, 2, figsize=(12, 10))
    axs = axs.flatten()

    for i, coef in enumerate(coefs):
        axs[i].plot(df_ccd[coef], color='k', label='Data Points')
        axs[i].set_xlabel('Run')
        axs[i].set_ylabel(coef)
        axs[i].set_title(f'{coef} variation for mapping')
        axs[i].legend()
        axs[i].grid()
    plt.tight_layout()
    plt.show()

# ===========================================================================


# ===========================================================================
# Initial statistical analysis
# ===========================================================================
mean = []
std = []
min = []
max = []
var_coef = []
for coef in coefs:
    mean.append(df_ccd[coef].mean())
    std.append(np.std(df_ccd[coef]))
    min.append(df_ccd[coef].min())
    max.append(df_ccd[coef].max())
    var_coef.append((std[-1]/mean[-1]) * 100)

statistics_df = pd.DataFrame({
    "Coefficient": coefs,
    "Mean": mean,
    "Standard dev": std,
    "Minimum": min,
    "Maximum": max,
    "Variation Coeff (CV)" : var_coef
})

print("\n" + "="*100)
print("General Statistics")
print(statistics_df)
print("\n" + "="*100)

# ===========================================================================
# Pearson correlation
# ===========================================================================
rs_pearson_x1 = []
rs_pearson_x2 = []
for coef in coefs:
    r_pearson_x1 = df_ccd[coef].corr(df_ccd["X1"], method = "pearson")
    r_pearson_x2 = df_ccd[coef].corr(df_ccd["X2"], method = "pearson")
    
    rs_pearson_x1.append(r_pearson_x1)
    rs_pearson_x2.append(r_pearson_x2)

print("\n" + "="*100)
print("Pearson results")
for i, coef in enumerate(coefs):
    print(f"Coefficient: {coef}")
    print("First parameter Pearson correlation:", rs_pearson_x1[i])
    print("Second parameter Pearson correlation:", rs_pearson_x2[i])
    print("\n" + "="*50)

# ===========================================================================
# Analisys of variance ANOVA 
# ===========================================================================

anova_results = {}

for coef in coefs:
    # Wvaluating the most complete model i.e cuadratic
    formula = (
        f"{coef} ~ X1 + X2 + X1:X2 "
        "+ I(X1**2) + I(X2**2)"
    )

    model = smf.ols(formula, data=df_ccd).fit()
    # Type 2 anova will be implemented as it considers the interacion of the 2 variables
    anova_table = sm.stats.anova_lm(model, typ=2)

    anova_results[coef] = anova_table

    print("\n" + "="*100)
    print(f"ANOVA - {coef}")
    print("="*100)

    print(anova_table)

    # Cheking if the addition of the interaction and cuadractic terms improve the model

    model_linear = smf.ols(
        f"{coef} ~ X1 + X2",
        data=df_ccd
    ).fit()

    model_interaction = smf.ols(
        f"{coef} ~ X1 + X2 + X1:X2",
        data=df_ccd
    ).fit()

    model_quadratic = smf.ols(
        f"{coef} ~ X1 + X2 + X1:X2 "
        "+ I(X1**2) + I(X2**2)",
        data=df_ccd
    ).fit()

    # Interaction contribution
    anova_interaction = sm.stats.anova_lm(
        model_linear,
        model_interaction
    )

    # Quadratic contribution
    anova_quadratic = sm.stats.anova_lm(
        model_interaction,
        model_quadratic
    )

    print("\n" + "="*60)
    print(f"Nested ANOVA - {coef}")
    print("="*60)

    print("\nLinear vs Interaction:")
    print(anova_interaction)

    print("\nInteraction vs Quadratic:")
    print(anova_quadratic)


# ===========================================================================
# Normalized sensitivity 
# ===========================================================================


print("\n" + 100*"=")
print("Normalized sensiblity")
print("\n" + 100*"=")

def local_sensitivity(df, response, x1, x2, k=6):

    X = df[[x1, x2]].to_numpy()
    Y = df[response].to_numpy()

    # Characteristic ranges
    ranges = np.ptp(X, axis=0)
    delta_C = np.ptp(Y)

    # Scale variables to comparable ranges
    X_scaled = (X - X.min(axis=0)) / ranges

    # Find nearest neighbors
    nn = NearestNeighbors(n_neighbors=k + 1)
    nn.fit(X_scaled)

    distances, indices = nn.kneighbors(X_scaled)

    results = []

    for i in range(len(df)):

        neighbors = indices[i, 1:]

        # Differences relative to reference point
        dX = X_scaled[neighbors] - X_scaled[i]
        dC = Y[neighbors] - Y[i]

        # Local least-squares gradient
        gradient, _, rank, _ = np.linalg.lstsq(
            dX, dC, rcond=None
        )

        if rank < 2 or delta_C == 0:
            S1 = np.nan
            S2 = np.nan
        else:
            # Range-normalized sensitivities
            S1 = gradient[0] / delta_C
            S2 = gradient[1] / delta_C

        results.append({
            "Point": i,
            f"d{response}X1": gradient[0] / ranges[0],
            f"d{response}X2": gradient[1] / ranges[1],
            "S_X1": S1,
            "S_X2": S2
        })

    return pd.DataFrame(results)

local_sens = {}
for coef in coefs:

    results = local_sensitivity(
    df_ccd,
    response= coef,
    x1="real_values_x1",
    x2="real_values_x2",
    k=6
    )
    local_sens[coef] = results
    print(results)

# ===========================================================================
# Plots
# ===========================================================================

# Variation coeff plot

plt.figure(figsize = (10,6))
bars = plt.bar(statistics_df["Coefficient"], statistics_df["Variation Coeff (CV)"], width = 0.5, align = "center",
        facecolor = "gray", edgecolor = "k")
plt.bar_label(bars, fmt="%.2f", padding=3)
plt.ylabel("Variation Coefficient (CV), %")
plt.ylim(0, statistics_df["Variation Coeff (CV)"].max() * 1.1)
plt.show()

# Pearson correlation

Pearson_co = {
    "X1 P_c" : rs_pearson_x1,
    "X2 P_c" : rs_pearson_x2
}

colores = ["silver", "slategrey"]

fig, ax = plt.subplots(layout='constrained')
ticks = ["Pearson X1", "Pearson X1"]
res = ax.grouped_bar(Pearson_co, tick_labels= coefs, group_spacing=1, colors = colores, edgecolor = "k" )
for container in res.bar_containers:
    ax.bar_label(container,  fmt="%.2f",padding=3)

# Add some text for labels, title, etc.
ax.set_ylabel(r'Pearson correlation coefficient, $r$')
#ax.set_title('Penguin attributes by species')
ax.legend()#(loc='lower right', ncols=3)
ax.set_ylim(-1,1.1)

plt.show()




# ===========================================================================
# Tests for the multiple linear regression models using OLS (Least Sqaures) 
# ===========================================================================

# Models to be tested : Linear, Interaction, Quadratic
formula_ = {
    "Quadratic": (
        "{response} ~ X1 + X2 + X1:X2 "
        "+ I(X1**2) + I(X2**2)"
    ),

    "Linear": (
        "{response} ~ X1 + X2"
    ),

    "Interaction": (
        "{response} ~ X1 + X2 + X1:X2"
    )
}

# Dictionary to store model results
models = {}

# Leave one out Cross validation: consist of iterating all the values but always leaving one out and
# test the models prediction for that one value

loo = LeaveOneOut()

#  Validation list and dictionaries
cv_results = []
cv_predictions = {}


for coef in coefs:

    for model_name, form in formula_.items():

        formula = form.format(response=coef)

        Y_true = []
        Y_pred = []
        full_model = smf.ols(formula, data=df_ccd).fit()

        for train_idx, test_idx in loo.split(df_ccd):
            # Train and test definition
            train = df_ccd.iloc[train_idx]
            test = df_ccd.iloc[test_idx]

            # Fit with 12 obs
            model = smf.ols(formula, data=train).fit()

            # prediction 
            prediction = model.predict(test).iloc[0]

            Y_true.append(test[coef].iloc[0])
            Y_pred.append(prediction)

            
            # Store each model independently
            models[(coef, model_name)] = model


        Y_true = np.array(Y_true)
        Y_pred = np.array(Y_pred)

        # LOOCV metrics

        rmse = np.sqrt(mean_squared_error(Y_true, Y_pred))
        mae = mean_absolute_error(Y_true, Y_pred)
        
        # Sum of error to the pwer of 2
        press = np.sum((Y_true - Y_pred)**2)
        tss = np.sum((Y_true - np.mean(Y_true))**2)
        q2 = 1 - press/tss if tss > 0 else np.nan

        cv_results.append({
            "Coefficient": coef,
            "Model": model_name,
            "LOOCV_RMSE": rmse,
            "LOOCV_MAE": mae,
            "PRESS": press,
            "Q2": q2,
            "R2": full_model.rsquared,
            "Adj_r2": full_model.rsquared_adj
        })
        cv_predictions[(coef, model_name)] = pd.DataFrame({
            "Observed": Y_true,
            "Predicted": Y_pred,
            "Residual": Y_true - Y_pred
        })

        # print("\n" + "="*100)
        # print(f"Coefficient: {coef}")
        # print(f"Model: {model_name}")
        # print("="*100)

        # print(model.summary())

        # print("Design matrix rank:", model.model.rank)
        # print("Number of observations:", model.nobs)
        # print("Residual degrees of freedom:", model.df_resid)

cv_results_df = pd.DataFrame(cv_results)
print("\n" + "="*100)
print("Data frame")
print(df_ccd[["real_values_x1", "real_values_x2", "Cy"]])
print("\n" + "="*100)
print("Models evaluation")
print(cv_results_df)
print("\n" + "="*100)
for (coef, model_name), predictions in cv_predictions.items():

    print(f"\n{'='*70}")
    print(f"Coefficient: {coef} | Model: {model_name}")
    print(f"{'='*70}")

    print(
        predictions.round(6).to_string(index=False)
    )


# metrics

metrics = ["LOOCV_RMSE", "LOOCV_MAE", "Q2", "R2"]  # Sin espacio inicial en LOOCV_RMSE
error_metrics = {"LOOCV_RMSE", "LOOCV_MAE"}

# Orden fijo para mantener consistencia en ejes y colores en los 4 gráficos
#coefs = cv_results_df["Coefficient"].unique().tolist()
modelos = ["Linear", "Interaction", "Quadratic"]
colores = [ "#1f1f1f", "#595959",  "#10253f"]

fig, axes = plt.subplots(2, 2, figsize=(13, 9), layout="constrained")

for ax, metric in zip(axes.flat, metrics):
    # Reestructurar: filas = Coeficientes, columnas = Modelos
    piv = (
        cv_results_df.pivot(index="Coefficient", columns="Model", values=metric)
        .reindex(index=coefs, columns=modelos)
    )
    datos_grupo = piv.to_dict(orient="list")

    res = ax.grouped_bar(
        datos_grupo,
        tick_labels=coefs,
        group_spacing=1,
        colors=colores,
        edgecolor="black",
    )

    # Escala logarítmica y formato de etiquetas según el tipo de métrica
    if metric in error_metrics:
        ax.set_yscale("log")
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ymin, ymax * 2.8)  # Margen superior en escala log para los números
        fmt = "%.4f"
    else:
        ax.set_ylim(0, 1.18)
        fmt = "%.2f"

    for container in res.bar_containers:
        ax.bar_label(container, fmt=fmt, padding=3, rotation=90, fontsize=8)

    ax.set_title(metric, fontweight="bold")
    ax.set_ylabel(f"{metric} (log)" if metric in error_metrics else metric)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    #ax.legend()
# Leyenda única compartida en la parte superior
handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncols=3, bbox_to_anchor=(0.5, 0.99), frameon=False)
fig.get_layout_engine().set(rect=(0, 0, 1, 0.92))
plt.show()



# REsidual plot

import matplotlib.gridspec as gridspec
fig = plt.figure(figsize=(14, 7.5), layout="constrained")
gs = gridspec.GridSpec(2, 6, figure=fig)

# 3 subplots en la fila superior y 2 centrados en la fila inferior
axes = [
    fig.add_subplot(gs[0, 0:2]),
    fig.add_subplot(gs[0, 2:4]),
    fig.add_subplot(gs[0, 4:6]),
    fig.add_subplot(gs[1, 1:3]),
    fig.add_subplot(gs[1, 3:5]),
]

# Estilo oscuro/monocromático y marcadores distintos por modelo
model_styles = {
    "Linear":      {"marker": "s", "color": "#1f1f1f", "ls": "--", "ms": 6},
    "Interaction": {"marker": "^", "color": "#595959", "ls": "-.", "ms": 7},
    "Quadratic":   {"marker": "D", "color": "#10253f", "ls": ":",  "ms": 6},
}
fallback_markers = ["v", "P", "X", "*"]

for ax, coef in zip(axes, coefs):
    # Modelos disponibles para este coeficiente en cv_predictions
    avail_models = [m for (c, m) in cv_predictions.keys() if c == coef]
    first_df = cv_predictions[(coef, avail_models[0])]
    runs = np.arange(1, len(first_df) + 1)

    # 1. Valores observados (CFD EVALUATIONS)
    ax.scatter(
        runs,
        first_df["Observed"],
        label="CFD EVALUATIONS",
        marker="o",
        color="black",
        s=48,
        zorder=5,
    )

    # 2. Predicciones LOOCV de cada modelo
    for idx, model_name in enumerate(avail_models):
        df_m = cv_predictions[(coef, model_name)]
        st = model_styles.get(
            model_name,
            {"marker": fallback_markers[idx % len(fallback_markers)], "color": "#333333", "s": 55},
        )
        ax.plot(
                runs,
                df_m["Predicted"],
                label=f"{model_name} (LOOCV)",
                color=st["color"],           # Color de la línea y del borde del marcador
                linestyle=st["ls"],          # Estilo de línea distinto por modelo (ideal para paper)
                linewidth=1.4,
                marker=st["marker"],
                markersize=st["ms"],         # Equivalente a 's' en plot()
                markerfacecolor="none",      # Equivalente a 'facecolors="none"' (marcador hueco)
                markeredgewidth=1.4,
                zorder=4 - idx * 0.1,
            )
    ax.set_title(coef, fontweight="bold", fontsize=11)
    ax.set_xlabel("Design Point / Run", fontsize=9.5)
    ax.set_ylabel(f"{coef}", fontsize=9.5)
    ax.set_xticks(runs)
    ax.tick_params(direction="in", top=True, right=True, labelsize=8.5)
    ax.grid(True, linestyle=":", color="gray", alpha=0.35)

# Recolectar etiquetas únicas de todos los subplots para la leyenda global
legend_dict = {}
for ax in axes:
    for handle, label in zip(*ax.get_legend_handles_labels()):
        if label not in legend_dict:
            legend_dict[label] = handle

# Reservar espacio superior dentro del lienzo para que plt.show() no corte la leyenda
fig.get_layout_engine().set(rect=(0, 0, 1, 0.92))

fig.legend(
    legend_dict.values(),
    legend_dict.keys(),
    loc="upper center",
    ncols=len(legend_dict),
    bbox_to_anchor=(0.5, 0.99),
    frameon=True,
    edgecolor="black",
    facecolor="white",
    fontsize=9.5,
)

plt.show()

# ===========================================================================
# Correlation matrix
# ===========================================================================

df_coefs = df_ccd[coefs]
cor_matrix = df_coefs.corr()

plt.figure(figsize=(8,6))
sns.heatmap(cor_matrix, annot=True, cmap="turbo", fmt=".2f", linewidths=0.5)
plt.title("Correlation Heatmap")
plt.show()

