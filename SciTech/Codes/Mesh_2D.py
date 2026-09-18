# ===========================================================
# 2D Mesh Generation
# ===========================================================

"""
This file contains the function to generate the 2D mesh of the Hermite Curve on the rocket.

"""

# ===========================================================
# Libraries
# ===========================================================
# 3rd party imports
from pathlib import Path
import gmsh

# Personal imports
from Hermite import generate_hermite_paper_fairing as Hermite

# ===========================================================
# Function
# ===========================================================
def meshgen_2D(a, b, config = {}):
    """
    Function to generate a mesh of the Hermite curve mounted on the rocket.
    Includes the generation of inflation layers.
    
    Args:
        a: Parameter 1 of the Hermite curve (zeta1)
        b: Parameter 2 of the Hermite curve (zeta2)
        config: Dictionary containing configuration options
    
    Returns:
        .su2 file containing mesh
    """
    
    # Default configuration
    default_config = {
        "filename"         : "Mesh.su2",
        "wall size"        : 0.005,
        "layer ratio"      : 1.15,
        "layer thickness"  : 0.05,
        "number of layers" : 15
    }
    
    # Read config
    config = {**default_config, **config}
    
    # ===========================================================
    # Initialization
    # ===========================================================
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("Hermite")
    
    # ===========================================================
    # Geometry
    # ===========================================================
    # Abreviation
    geom = gmsh.model.geo
    
    # Create the hermite curve from input parameters
    path = Path(__file__).with_name("_.txt")
    hermite = Hermite(a, b, export_filename = str(path))
    path.unlink()
    
    # Extract points of the Hermite
    x_hermite = hermite["x"]
    y_hermite = hermite["y"]
    
    # Points
    p1 = geom.addPoint(-500, 0, 0)
    p2 = geom.addPoint(x_hermite[-1], 0, 0)
    p3 = geom.addPoint(500, 0, 0)
    p4 = geom.addPoint(500, 100, 0)
    p5 = geom.addPoint(-500, 100, 0)
    
    # Hermite points
    hermite_tags = []
    for x, y in zip(x_hermite, y_hermite):
        tag = geom.addPoint(x, y, 0)
        hermite_tags.append(tag)
    
    # Lines
    l1 = geom.addLine(p1, hermite_tags[0])
    lH = geom.addSpline(hermite_tags)
    l2 = geom.addLine(hermite_tags[-1], p2)
    l3 = geom.addLine(p2, p3)
    l4 = geom.addLine(p3, p4)
    l5 = geom.addLine(p4, p5)
    l6 = geom.addLine(p5, p1)
    
    # Curve loop
    cl = geom.addCurveLoop([l1, lH, l2, l3, l4, l5, l6])
    
    # Surface
    s = geom.addPlaneSurface([cl])
    
    geom.synchronize()
    
    # Grupos Physical groups
    gmsh.model.addPhysicalGroup(2, [s], 101)
    gmsh.model.setPhysicalName(2, 101, "Domain")

    gmsh.model.addPhysicalGroup(1, [l4, l5, l6], 101)
    gmsh.model.setPhysicalName(1, 101, "Farfield")
    
    gmsh.model.addPhysicalGroup(1, [l1, lH, l2, l3], 102)
    gmsh.model.setPhysicalName(1, 102, "Wall")
    
    # ===========================================================
    # Meshing
    # ===========================================================
    # Inflation layers field
    BL = gmsh.model.mesh.field.add("BoundaryLayer")
    
    # Curves to grown on layers
    gmsh.model.mesh.field.setNumbers(BL, "CurvesList", [l1, lH, l2, l3])
    
    # Inflation layers settings
    gmsh.model.mesh.field.setNumber(BL, "hwall_n", config["wall size"])
    gmsh.model.mesh.field.setNumber(BL, "ratio", config["layer ratio"])
    gmsh.model.mesh.field.setNumber(BL, "thickness", config["layer thickness"])
    gmsh.model.mesh.field.setNumber(BL, "NbLayers", config["number of layers"])
    gmsh.model.mesh.field.setNumber(BL, "Quads", 1)
    gmsh.model.mesh.field.setAsBoundaryLayer(BL)
    
    gmsh.model.mesh.generate(2)
    
    # ===========================================================
    # Save results
    # ===========================================================
    # Visualization options
    gmsh.option.setNumber("Mesh.SurfaceFaces", 1)
    gmsh.option.setNumber("Mesh.Points", 1)
    
    # Read save directory
    path = Path(__file__).parent / config["filename"]
    gmsh.write(str(path))
    
    # Finalize
    gmsh.finalize()

# ===========================================================
# Test
# ===========================================================
if __name__ == "__main__":
    meshgen_2D(1, 1, config = {"filename" : "Mesh.msh"})

if False:
    # Sizing
    D = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(D, "CurvesList", [l1, l2, l3])  # en 3D usas SurfacesList

    T = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(T, "InField", D)
    gmsh.model.mesh.field.setNumber(T, "SizeMin", 0.01)   # tamaño cerca de la superficie
    gmsh.model.mesh.field.setNumber(T, "SizeMax", 0.02)   # tamaño lejos
    gmsh.model.mesh.field.setNumber(T, "DistMin", 0.05)   # hasta dónde aplica SizeMin
    gmsh.model.mesh.field.setNumber(T, "DistMax", 0.30)   # a partir de dónde aplica SizeMax

    gmsh.model.mesh.field.setAsBackgroundMesh(T)
