import gmsh
import math
import os
import sys

gmsh.initialize()

gmsh.model.add("Onera")

# Load a STEP file (using `importShapes' instead of `merge' can directly
# retrieve the tags of the highest dimensional imported entities):
path = os.path.dirname(os.path.abspath(__file__))
v = gmsh.model.occ.importShapes(os.path.join(path, os.pardir, 'ONERAM6_WING.stp'))
# Synchronize the CAD kernel with the Gmsh model (OCC)
gmsh.model.occ.synchronize()

# Domain generation
geom = gmsh.model.geo
# Center point creation
center_point = geom.addPoint(0, 0, 0, 101)


# Radio
R = 1000 * 10 # mm
sphere = gmsh.model.occ.addSphere(0, 0, 0, R)


# Get the bounding box of the volume:
#xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.occ.getBoundingBox(
#    sphere[0][0], sphere[0][1])

# Creating a cutting plane

s = []                                  
s.append((2, gmsh.model.occ.addRectangle(-R, -R, 0, 2*R, 2*R)))
gmsh.model.occ.rotate([s[0]], 0, 0, 0, 1, 0, 0, -math.pi/2)


gmsh.model.occ.synchronize()
# Boolean to remove wing from the sphere
fluid, fragments = gmsh.model.occ.cut(
    [(3,sphere)],
    v
)

# Fragment (i.e. intersect) the volume with  the cutting plane:
gmsh.model.occ.fragment([(3,sphere)], s)


gmsh.model.occ.remove([(3,2)], True)
gmsh.model.occ.remove(gmsh.model.occ.getEntities(2), True)
gmsh.model.occ.synchronize()


#=====================================================================================================


Domain = gmsh.model.getEntities(3)

Boundaries_FluidD = gmsh.model.getBoundary(Domain, combined = False, oriented=False, recursive=False)

print(f"BD",Boundaries_FluidD)

print("Volúmenes:", Domain)
print("Número de volúmenes:", len(Domain))
print("Límites:", Boundaries_FluidD)
Walls = []
for dim, tag in Boundaries_FluidD:
    #print("Dimensión:", dim, "Tag:", tag)
    # Get the bounding box of the surface:
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.occ.getBoundingBox(dim, tag)
    #print("xmin, ymin, zmin, xmax, ymax, zmax")

    #print("Bounding box:", xmin, ymin, zmin, xmax, ymax, zmax)


Walls = [tag for dim, tag in Boundaries_FluidD[2:]]
# Physical groups creation

# Boundaries
Farfield_surface = Boundaries_FluidD[0] # dim, tag
Symmetry_p_surface = Boundaries_FluidD[1]

# WING GEOMETRIC SURFACES
Intrados = Boundaries_FluidD[2]
Extrados = Boundaries_FluidD[3]

TE_extrados = Boundaries_FluidD[4]
TE_intrados = Boundaries_FluidD[5]

round_tip_intrados = Boundaries_FluidD[6]
tip_intrados = Boundaries_FluidD[7]
round_tip_extrados = Boundaries_FluidD[8]
tip_extrados = Boundaries_FluidD[9]

TE_tip_intrados = Boundaries_FluidD[10]
TE_tip_extrados = Boundaries_FluidD[11]

#Walls = Boundaries_FluidD[2:]

print("Walls:", Walls)

# ==========================================================================================
# --------------------------------------------------
# Boundary layer

#Walls sin TE
Walls_TE = Walls[:2]
Walls_TE = Walls_TE + Walls[4:8]
print(Walls_TE)
# First layer thickness [mm]
h1 = 2.38e-3

# Growth ratio
ratio = 1.22

# Number of layers
N = 35

# Thickness of each layer
layer_thicknesses = [
    h1 * ratio**i
    for i in range(N)
]

# Cumulative height of each layer interface
heights = []

total_height = 0.0

for h in layer_thicknesses:
    total_height += h
    heights.append(total_height)

print("First layer:", layer_thicknesses[0], "mm")
print("Last layer :", layer_thicknesses[-1], "mm")
print("Total BL   :", heights[-1], "mm")

# ============================================================
# Extrude Boundary Layer
# ============================================================
out = gmsh.model.geo.extrudeBoundaryLayer(
    [(2, s) for s in Walls],
    numElements=[1] * N,
    heights=heights,
    recombine=True # Recombine option to generate prism ñayers
)

gmsh.model.geo.synchronize()







# ===============================================================================================
# ==========================================================================================
# Mesh from wing to farfield
# ==========================================================================================

# Field creation
field_distance = gmsh.model.mesh.field.add("Distance")

# Calc of distance from each point to given entities (walls)
gmsh.model.mesh.field.setNumbers(
    field_distance,
    "FacesList",
    Walls
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
    10.0
)

gmsh.model.mesh.field.setNumber(
    field_threshold,
    "SizeMax",
    500.0
)

gmsh.model.mesh.field.setNumber(
    field_threshold,
    "DistMin",
    5
)

gmsh.model.mesh.field.setNumber(
    field_threshold,
    "DistMax",
    1000
)

# Set where the mesh is goint to be generated
#gmsh.model.mesh.field.setAsBackgroundMesh(
#    field_threshold)
# ===========================================================================================
# ============================================================================================
curve_tags = []

for surface_tag in Walls:

    curves = gmsh.model.getBoundary(
        [(2, surface_tag)],
        combined=False,
        oriented=False,
        recursive=False
    )

    for dim, tag in curves:
        if dim == 1:
            curve_tags.append(tag)

# Eliminar duplicados
curve_tags = list(set(curve_tags))


# ==========================================================================================
# mesh on wing curves
# ==========================================================================================

field_curves_Wing = gmsh.model.mesh.field.add("Distance")

gmsh.model.mesh.field.setNumbers(
    field_curves_Wing,
    "CurvesList",
    curve_tags
)
Curve_threshold = gmsh.model.mesh.field.add("Threshold")

gmsh.model.mesh.field.setNumber(
    Curve_threshold,
    "InField",
    field_curves_Wing
)

gmsh.model.mesh.field.setNumber(
    Curve_threshold,
    "SizeMin",
    5.0
)

gmsh.model.mesh.field.setNumber(
    Curve_threshold,
    "SizeMax",
    1e6
)

gmsh.model.mesh.field.setNumber(
    Curve_threshold,
    "DistMin",
    10
)

gmsh.model.mesh.field.setNumber(
    Curve_threshold,
    "DistMax",
    100
    )



#Minimum background for mesh generation
min_field = gmsh.model.mesh.field.add("Min")

gmsh.model.mesh.field.setNumbers(
    min_field,
    "FieldsList",
    [
        field_threshold,
        Curve_threshold
    ]
)

gmsh.model.mesh.field.setAsBackgroundMesh(
    min_field
)
# ===========================================================================================



# MEsh generation
gmsh.model.mesh.generate(3)  # Generate 3D mesh

# Visualization options
gmsh.option.setNumber("Mesh.SurfaceFaces", 1) # display faces of the mesh elements
gmsh.option.setNumber("Mesh.Points", 1) # display points of the mesh elements



# Launch the GUI to see the results:
gmsh.fltk.run()





gmsh.finalize()
