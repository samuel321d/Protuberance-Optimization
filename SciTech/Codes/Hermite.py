import numpy as np

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

zeta1_input = 
zeta2_input = 

profile = generate_hermite_paper_fairing(zeta1_input, zeta2_input, nps=30)
