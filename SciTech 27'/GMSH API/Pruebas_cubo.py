import gmsh
import math
import os
import sys

gmsh.initialize()

gmsh.model.add("Cubo")


# Geometry generation

Cube = gmsh.model.occ.addBox(0,0,0, 10, 10, 10)

gmsh.model.occ.synchronize()

Domain = gmsh.model.getEntities(3)

Boundaries = gmsh.model.getBoundary(Domain, combined = False, oriented=False, recursive=False)

print(f"BD",Boundaries)

print("Volúmenes:", Domain)
print("Número de volúmenes:", len(Domain))
print("Límites:", Boundaries)
Walls = []
bottom_tag = None
for dim, tag in Boundaries:
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.occ.getBoundingBox(dim, tag)
    if abs(zmin) < 1e-6 and abs(zmax) < 1e-6:
        bottom_tag = tag
        break


print("Bottom tag", bottom_tag)



# ---------------------------------------------------------
# 1. CREACIÓN DE LA CAPA LÍMITE (CAPAS PRISMÁTICAS)
# ---------------------------------------------------------
field_bl = gmsh.model.mesh.field.add("BoundaryLayer")

gmsh.model.mesh.field.setNumbers(field_bl, "FacesList", [bottom_tag])
gmsh.model.mesh.field.setNumber(field_bl, "Size", 0.05)       # Altura del primer prisma (h_wall)
gmsh.model.mesh.field.setNumber(field_bl, "Ratio", 1.2)       # Factor de crecimiento entre capas
gmsh.model.mesh.field.setNumber(field_bl, "Thickness", 1.0)   # Espesor total de las capas prismáticas

# IMPORTANTE: Asignar explícitamente este campo como Capa Límite
gmsh.model.mesh.field.setAsBoundaryLayer(field_bl)

# =========================================================
# Control de tamaño de celdas en el cubo
# =========================================================
# Field creation
field_distance = gmsh.model.mesh.field.add("Distance")

# Calc of distance from each point to given entities (walls)
gmsh.model.mesh.field.setNumbers(
    field_distance,
    "FacesList",
    [bottom_tag]
)

# Threshold tag creation
field_threshold = gmsh.model.mesh.field.add("Threshold")

gmsh.model.mesh.field.setNumber(
    field_threshold,
    "InField",
    field_distance
)

# Sizes definition
gmsh.model.mesh.field.setNumber(
    field_threshold,
    "SizeMin",
    0.1
)

gmsh.model.mesh.field.setNumber(
    field_threshold,
    "SizeMax",
    1
)

gmsh.model.mesh.field.setNumber(
    field_threshold,
    "DistMin",
    1
)

gmsh.model.mesh.field.setNumber(
    field_threshold,
    "DistMax",
    10
)


gmsh.model.mesh.field.setAsBackgroundMesh(field_threshold)
# MEsh generation
gmsh.model.mesh.generate(3)  # Generate 3D mesh

# Visualization options
gmsh.option.setNumber("Mesh.SurfaceFaces", 1) # display faces of the mesh elements
gmsh.option.setNumber("Mesh.Points", 1) # display points of the mesh elements
# Launch the GUI to see the results:
gmsh.fltk.run()





gmsh.finalize()
