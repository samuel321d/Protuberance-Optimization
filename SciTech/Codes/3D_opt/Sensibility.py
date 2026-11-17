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
# ===========================================================================
# MATPLOTLIB PARAMS
plt.rcParams.update({
    "font.size": 12,
    "font.family": "serif"
})
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
print("Files readed: ", len(dfs_hist))

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

# CCD POINTS
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

plots = True

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

models = {}

for coef in coefs:

    for model_name, form in formula_.items():

        formula = form.format(response=coef)

        model = smf.ols(formula, data=df_ccd).fit()

        # Store each model independently
        models[(coef, model_name)] = model

        print("\n" + "="*60)
        print(f"Coefficient: {coef}")
        print(f"Model: {model_name}")
        print("="*60)

        print(model.summary())

        print("Design matrix rank:", model.model.rank)
        print("Number of observations:", model.nobs)
        print("Residual degrees of freedom:", model.df_resid)


print(df_ccd[["real_values_x1", "real_values_x2", "Cy"]])