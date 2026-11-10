# ==================================================
#  Meshes generation Script
# ==================================================
# This script automates the mesh generation for the CADS geomtries located on the "CADS" folder. 
# It uses the "Mesh_3D.py" script to create meshes for each geometry and saves them in the "Meshes" folder.

from Mesh_3D import meshgen_3D
import os
import glob
import numpy as np


# cads file names

cads_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CADS")
cads_routes = glob.glob(os.path.join(cads_folder, "*.step"))
names = [os.path.splitext(os.path.basename(ruta))[0] for ruta in cads_routes]
print(names)

def config(path, mesh_name):
    config_CAT = { 
        "filename"              : f"{mesh_name}.su2",
        "layer thickness"       : 9.58e-7,
        "layer ratio"           : 1.19,
        "total thickness"       : 0.001,
        "number of layers"      : 20,
        "BOIC1"                 : 0.2*8.8,
        "BOIC2"                 : 0.1*8.8,
        "BOIC3"                 : 0.05*8.8,
        "BOIC4"                 : 0.02*8.8,
        "BOIC5"                 : 0.007*8.8,
        "BOIC6"                 : 0.003*8.8,
        "BOIF1"                 : 0.008*8.8,
        "BOIF2"                 : 0.004*8.8,
        "BOIS1"                 : 0.004*8.8,
        "BOIS2"                 : 0.0015*8.8,
        "BOIS3"                 : 0.0005*8.8,
        "global size"           : 0.4*8.8,
        "L"                     : 3.24,
        "prot_loc"              : 0.62,
        "BOIP1"                 : 0.0006*8.8,
        "BOIP2"                 : 0.0015*8.8,
        "R_radius"              : 0.087,
        "cone"                  : 0.003*8.8,
        "cone2"                 : 0.007*8.8,
        "cone3"                 : 0.003*8.8,
        "wall size"             : 0.0013*8.8,
        "BOICELDA"              : 1,
        "rocket_path"           : path
    }
    return config_CAT

mesh_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Meshes")
# mesh gen
for i in range(len(cads_routes)):
    mesh_gen = meshgen_3D(mesh_folder, config(cads_routes[i], names[i]))
    