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
from math import radians
import gmsh
import ezdxf
import numpy as np

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
        h_bc: List with hermite curve boundary points
        .su2 file containing mesh
    """
    
    # Default configuration
    default_config = {
        "filename"              : "Mesh.su2",
        "wall size"             : 1,
        "layer ratio"           : 1.15,
        "layer thickness"       : 5,
        "number of layers"      : 15,
        "use boundary layer"    : True,
        "BOI1"                  : 1000,
        "BOI2"                  : 300,
        "BOI3"                  : 100,
        "global size"           : 2000,
        "protuberance location" : 1000,
        "alpha"                 : radians(0),
        "r"                     : 174,
        "L"                     : 3000
    }
    
    # Read config
    config = {**default_config, **config}
    L = config["L"]
    r = config["r"]
    
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
    geom = gmsh.model.occ
    msh = gmsh.model.mesh
    
    # Create the hermite curve from input parameters
    path = Path(__file__).with_name("_.txt")
    hermite = Hermite(a, b, export_filename = str(path))
    path.unlink()
    
    # Read rocket surface
    path = Path(__file__).with_name("Rocket_points.dxf")
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    
    points = []
    print(msp)
    for entity in msp:
        
        # ----------------
        # LINE 
        # ----------------
        if entity.dxftype() == "LINE":
            
            p1 = entity.dxf.start
            p2 = entity.dxf.end
            
            points.append((p1.x, p1.y))
            points.append((p2.x, p2.y))
            
        # ----------------
        # ARC
        # ----------------
        elif entity.dxftype() == "ARC":
            
            center = entity.dxf.center
            radius = entity.dxf.radius
            
            theta1 = np.deg2rad(entity.dxf.start_angle)
            theta2 = np.deg2rad(entity.dxf.end_angle)
            
            theta = np.linspace(theta1, theta2, 50)
            
            for t in theta:
                x = center.x + radius * np.cos(t)
                y = center.y + radius * np.sin(t)
                
                points.append((x, y))
                
        # ----------------
        # SPLINE
        # ----------------
        elif entity.dxftype() == "SPLINE":
            
            spline_points = entity.flattening(0.01)
            
            for p in spline_points:
                points.append((p.x, p.y))
    rocket_coords = np.array(points)
    
    x_rocket = rocket_coords[:, 0]
    y_rocket = rocket_coords[:, 1]
    
    # Extract points of the Hermite
    x_hermite = hermite["x"]
    y_hermite = hermite["y"]
    
    # Points
    # Far-field
    p1 = geom.addPoint(0, -12*L, 0)
    p2 = geom.addPoint(0, 0, 0)
    p3 = geom.addPoint(0, 12*L, 0)
    p4 = geom.addPoint(15*L, 12*L, 0)
    p5 = geom.addPoint(15*L, -12*L, 0)
    
    # Rocket 
    rocket_tags = []
    for x, y in zip(x_rocket, y_rocket):
        tag = geom.addPoint(x + 3200, y, 0)
        rocket_tags.append(tag)
    
    # Hermite 
    hermite_tags = []
    for x, y in zip(x_hermite, y_hermite):
        tag = geom.addPoint(x + config["protuberance location"], y + max(y_rocket), 0)
        hermite_tags.append(tag)
    p6 = geom.addPoint(x_hermite[-1] + config["protuberance location"], y_hermite[0] + max(y_rocket), 0)
    
    # Lines
    # Far-field
    l1 = geom.addCircleArc(p1, p2, p3)
    l2 = geom.addLine(p3, p4)
    l3 = geom.addLine(p4, p5)
    l4 = geom.addLine(p5, p1)
    
    # Rocket
    lr = geom.addBSpline(rocket_tags)
    lf = geom.addLine(rocket_tags[-1], rocket_tags[0])
    
    # Hermite
    lh = geom.addBSpline(hermite_tags)
    l5 = geom.addLine(hermite_tags[-1], p6)
    l6 = geom.addLine(p6, hermite_tags[0])
    
    # Rocket curve
    rocket_list = [lr, lf]
    
    rotate_list = [lr, lf, lh, l5, l6]
    
    # Rotate rocket
    dim_tags_rocket = [(1, tag) for tag in rotate_list]
    geom.rotate(dim_tags_rocket, 0, 0, 0, 0, 0, 1, config["alpha"])
    
    # Curve loops
    cl1 = geom.addCurveLoop([l1, l2, l3, l4])
    cl2 = geom.addCurveLoop(rocket_list)
    cl3 = geom.addCurveLoop([lh, l5, l6])
    
    # Surface
    s = geom.addPlaneSurface([cl1])
    s_rocket = geom.addPlaneSurface([cl2])
    # s_hermite = geom.addPlaneSurface([cl3])
    
    # fusion, _ = geom.fuse([(2, s_rocket)], [(2, s_hermite)])
    # rocket_surfaces = [(dim, tag) for dim, tag in fusion if dim == 2]
    
    geom.synchronize()
    
    # cut_surfaces, _ = geom.cut([(2, s)], rocket_surfaces)
    cut_surfaces, _ = geom.cut([(2, s)], [(2, s_rocket)])
    domain_surfaces = [(dim, tag) for dim, tag in cut_surfaces if dim == 2]
    
    geom.synchronize()
    
    all_boundary = [c[1] for surface in domain_surfaces for c in gmsh.model.getBoundary([surface], combined=False, oriented=False)]
    farfield_curves = [l1, l2, l3, l4]
    wall_curves = [curve for curve in all_boundary if curve not in farfield_curves]
    
    # Physical groups
    gmsh.model.addPhysicalGroup(2, [tag for _, tag in domain_surfaces], 101)
    gmsh.model.setPhysicalName(2, 101, "Domain")
    
    gmsh.model.addPhysicalGroup(1, farfield_curves, 101)
    gmsh.model.setPhysicalName(1, 101, "Farfield")
    
    gmsh.model.addPhysicalGroup(1, wall_curves, 102)
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
    use_boundary_layer = bool(config.get("use boundary layer", False))
    if use_boundary_layer:
        BL = msh.field.add("BoundaryLayer")
        
        # Curves to grown on layers
        msh.field.setNumbers(BL, "CurvesList", wall_curves)
        
        # Inflation layers settings
        msh.field.setNumber(BL, "hwall_n", config["wall size"])
        msh.field.setNumber(BL, "ratio", config["layer ratio"])
        msh.field.setNumber(BL, "thickness", config["layer thickness"])
        msh.field.setNumber(BL, "NbLayers", config["number of layers"])
        msh.field.setNumber(BL, "Quads", 1)
        msh.field.setAsBoundaryLayer(BL)
    else:
        print("Info: Boundary layer disabled (use boundary layer = True to enable it). This geometry is stable without inflation layers in Gmsh.")
    
    # Generate mesh
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