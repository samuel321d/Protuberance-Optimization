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


def generate_hermite_protuberance(params, bounds, nps=30, export_filename="protuberance_coords.txt"):

    p_clamped = {}
    for key, val in params.items():
        if key in bounds:
            min_val, max_val = bounds[key]
            p_clamped[key] = np.clip(val, min_val, max_val)
            if val != p_clamped[key]:
                print(f"[WARN] El parámetro {key}={val} superó los límites. Ajustado a {p_clamped[key]}")
        else:
            p_clamped[key] = val

    xpts, xdpts = hermit_bl(p_clamped['x0'], p_clamped['xe'], p_clamped['x0p'], p_clamped['xep'], nps, clustering=True)
    ypts, ydpts = hermit_bl(p_clamped['y0'], p_clamped['ye'], p_clamped['y0p'], p_clamped['yep'], nps, clustering=True)

    data_out = np.column_stack((xpts, ypts))
    header_str = "X_m\tY_m"

    np.savetxt(export_filename, data_out, fmt='%.6f', delimiter='\t', header=header_str)
    print(f"[INFO] Coordenadas exportadas a: {export_filename}")

    def y_func(x_query):
        return np.interp(x_query, xpts, ypts)

    return {
        'x': xpts,
        'y': ypts,
        'y_func': y_func,
        'params_used': p_clamped
    }


param_bounds = {
    'x0':  [0.0, 0.0],
    'xe':  [0.5, 2.0],
    'y0':  [0.0, 0.0],
    'ye':  [0.1, 1.5],
    'x0p': [0.1, 3.0],
    'y0p': [0.0, 2.0],
    'xep': [0.1, 3.0],
    'yep': [-2.0, 2.0]
}

input_params = {
    'x0':  ,
    'xe':  ,
    'y0':  ,
    'ye':  ,
    'x0p': ,
    'y0p': ,
    'xep': ,
    'yep': 
}

nps = 30
profile = generate_hermite_protuberance(input_params, param_bounds, nps=nps, export_filename="protuberance_coords.txt")