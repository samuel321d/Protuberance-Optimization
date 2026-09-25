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
        "wall size"        : 1,
        "layer ratio"      : 1.15,
        "layer thickness"  : 5,
        "number of layers" : 15,
        "BOI1"             : 1000,
        "BOI2"             : 300,
        "BOI3"             : 100,
        "global size"      : 2000,
        "L"                : 3000
    }
    
    # Read config
    config = {**default_config, **config}
    L = config["L"]
    
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
    msh = gmsh.model.mesh
    
    # Create the hermite curve from input parameters
    path = Path(__file__).with_name("_.txt")
    hermite = Hermite(a, b, export_filename = str(path))
    path.unlink()
    
    # Extract points of the Hermite
    x_hermite = hermite["x"]
    y_hermite = hermite["y"]
    
    # Points
    # Far-field
    p1 = geom.addPoint(0, 12*L, 0)
    p2 = geom.addPoint(0, 0, 0)
    p3 = geom.addPoint(0, -12*L, 0)
    p4 = geom.addPoint(15*L, -12*L, 0)
    p5 = geom.addPoint(15*L, 12*L, 0)
    
    Hermite
    hermite_tags = []
    for x, y in zip(x_hermite, y_hermite):
        tag = geom.addPoint(x, y, 0)
        hermite_tags.append(tag)
    
    # Rocket
    p6 = geom.addPoint(0, 1000, 0)
    p7 = geom.addPoint(3000, 1000, 0)
    p8 = geom.addPoint(3000, -1000, 0)
    p9 = geom.addPoint(0, -1000, 0)
    
    # Lines
    # Far-field
    l1 = geom.addCircleArc(p1, p2, p3)
    l2 = geom.addLine(p3, p4)
    l3 = geom.addLine(p4, p5)
    l4 = geom.addLine(p5, p1)
    
    # Rocket
    l5 = geom.addLine(p6, p7)
    l6 = geom.addLine(p7, p8)
    l7 = geom.addLine(p8, p9)
    l8 = geom.addLine(p9, p6)
    
    # Rocket curve
    rocket_list = [l5, l6, l7, l8]
    
    # Curve loops
    cl1 = geom.addCurveLoop([l1, l2, l3, l4])
    cl2 = geom.addCurveLoop(rocket_list)
    
    # Surface
    s = geom.addPlaneSurface([cl1, cl2])
    
    geom.synchronize()
    
    # Grupos Physical groups
    gmsh.model.addPhysicalGroup(2, [s], 101)
    gmsh.model.setPhysicalName(2, 101, "Domain")
    
    gmsh.model.addPhysicalGroup(1, [l1, l2, l3, l4], 101)
    gmsh.model.setPhysicalName(1, 101, "Farfield")
    
    gmsh.model.addPhysicalGroup(1, rocket_list, 102)
    gmsh.model.setPhysicalName(1, 102, "Wall")
    
    # ===========================================================
    # Meshing
    # ===========================================================
    gmsh.option.setNumber("Mesh.MeshSizeMax", config["global size"])
    
    # BOIs
    BOI1 = msh.field.add("Box")
    msh.field.setNumber(BOI1, "XMin", -5.5*L)
    msh.field.setNumber(BOI1, "XMax", 8.5*L)
    msh.field.setNumber(BOI1, "YMin", -7*L)
    msh.field.setNumber(BOI1, "YMax", 7*L)
    msh.field.setNumber(BOI1, "VIn", config["BOI1"])
    msh.field.setNumber(BOI1, "Thickness", config["BOI1"])
    
    BOI2 = msh.field.add("Box")
    msh.field.setNumber(BOI2, "XMin", -3.5*L)
    msh.field.setNumber(BOI2, "XMax", 6.5*L)
    msh.field.setNumber(BOI2, "YMin", -5*L)
    msh.field.setNumber(BOI2, "YMax", 5*L)
    msh.field.setNumber(BOI2, "VIn", config["BOI2"])
    msh.field.setNumber(BOI2, "Thickness", config["BOI2"])
    
    BOI3 = msh.field.add("Box")
    msh.field.setNumber(BOI3, "XMin", -1.5*L)
    msh.field.setNumber(BOI3, "XMax", 4.5*L)
    msh.field.setNumber(BOI3, "YMin", -2*L)
    msh.field.setNumber(BOI3, "YMax", 2*L)
    msh.field.setNumber(BOI3, "VIn", config["BOI3"])
    msh.field.setNumber(BOI3, "Thickness", config["BOI3"])
    
    # Combine BOIs
    min = msh.field.add("Min")
    msh.field.setNumbers(min, "FieldsList", [BOI1, BOI2, BOI3])
    msh.field.setAsBackgroundMesh(min)
    
    # Inflation layers field
    BL = msh.field.add("BoundaryLayer")
    
    # Curves to grown on layers
    msh.field.setNumbers(BL, "CurvesList", rocket_list)
    
    # Inflation layers settings
    msh.field.setNumber(BL, "hwall_n", config["wall size"])
    msh.field.setNumber(BL, "ratio", config["layer ratio"])
    msh.field.setNumber(BL, "thickness", config["layer thickness"])
    msh.field.setNumber(BL, "NbLayers", config["number of layers"])
    msh.field.setNumber(BL, "Quads", 1)
    msh.field.setAsBoundaryLayer(BL)
    
    msh.generate(2)
    
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