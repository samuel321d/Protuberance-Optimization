# ===========================================================
# 3D Mesh Generation
# ===========================================================

"""
This file contains the function to generate the 3D mesh of the rocket.

"""

# ===========================================================
# Libraries
# ===========================================================
# 3rd party imports
from pathlib import Path
from math import radians
import gmsh

# ===========================================================
# Function
# ===========================================================


def meshgen_3D(config={}):
    """
    Function to generate a mesh of the rocket.
    Includes the generation of inflation layers.

    Args:
        config: Dictionary containing configuration options

    Returns:
        .format file containing mesh
    """

    # Default configuration
    default_config = {
        "filename": "Mesh.su2",
        "wall size": 1,
        "layer ratio": 1.2,
        "layer thickness": 9.75e-7*1000,
        "number of layers": 40,
        "BOI1": 1000,
        "BOI2": 300,
        "BOI3": 100,
        "global size": 2000,
        "threshold distance": 200,
        "alpha": radians(6),
        "L": 3200
    }

    # Read config
    config = {**default_config, **config}
    L = config["L"]

    # ===========================================================
    # Initialization
    # ===========================================================
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("Rocket")

    # Abreviation
    geom = gmsh.model.geo
    occm = gmsh.model.occ
    msh = gmsh.model.mesh

    # ===========================================================
    # Geometry
    # ===========================================================
    # Import rocket geometry
    rocket_path = Path(__file__).parent / "Rocket.step"
    occm.importShapes(str(rocket_path), highestDimOnly=True)

    occm.synchronize()

    # Extract inflation layer parameters
    N = config["number of layers"]
    r = config["layer ratio"]
    h0 = config["layer thickness"]

    # Calculate layer heights
    heights = [h0]
    for i in range(1, N):
        heights.append(heights[-1] + h0 * r**i)

    # Grow inflation layers
    rocket_surfaces = gmsh.model.getEntities(2)
    #rocket_volumes = gmsh.model.getEntities(3)
    extbl = geom.extrudeBoundaryLayer(rocket_surfaces, [1] * N, heights, True)

    geom.synchronize()

    # Remove rocket
    #occm.remove(rocket_volumes, recursive=False)

    # BL top faces
    top = []
    for i in range(1, len(extbl)):
        if extbl[i][0] == 3:
            top.append(extbl[i-1])

    # Farfield
    # Bounding box
    xmin, xmax = -4, 4
    ymin, ymax = -4, 4
    zmin, zmax = -4, 4

    p1 = geom.addPoint(xmin, ymin, zmin)
    p2 = geom.addPoint(xmax, ymin, zmin)
    p3 = geom.addPoint(xmax, ymax, zmin)
    p4 = geom.addPoint(xmin, ymax, zmin)
    li1 = geom.addLine(p1, p2)
    li2 = geom.addLine(p2, p3)
    li3 = geom.addLine(p3, p4)
    li4 = geom.addLine(p4, p1)
    cli = geom.addCurveLoop([li1, li2, li3, li4])
    si = geom.addPlaneSurface([cli])

    p5 = geom.addPoint(xmin, ymin, zmax)
    p6 = geom.addPoint(xmax, ymin, zmax)
    p7 = geom.addPoint(xmax, ymax, zmax)
    p8 = geom.addPoint(xmin, ymax, zmax)
    ls1 = geom.addLine(p5, p6)
    ls2 = geom.addLine(p6, p7)
    ls3 = geom.addLine(p7, p8)
    ls4 = geom.addLine(p8, p5)
    cls = geom.addCurveLoop([ls1, ls2, ls3, ls4])
    ss = geom.addPlaneSurface([cls])

    lv1 = geom.addLine(p1, p5)
    lv2 = geom.addLine(p2, p6)
    lv3 = geom.addLine(p3, p7)
    lv4 = geom.addLine(p4, p8)
    cll1 = geom.addCurveLoop([li1, lv2, -ls1, -lv1])
    cll2 = geom.addCurveLoop([li2, lv3, -ls2, -lv2])
    cll3 = geom.addCurveLoop([li3, lv4, -ls3, -lv3])
    cll4 = geom.addCurveLoop([li4, lv1, -ls4, -lv4])
    sl1 = geom.addPlaneSurface([cll1])
    sl2 = geom.addPlaneSurface([cll2])
    sl3 = geom.addPlaneSurface([cll3])
    sl4 = geom.addPlaneSurface([cll4])

    # Surface loop
    b = [s[1] for s in top]
    b = []
    b.extend([si, ss, sl1, sl2, sl3, sl4])
    sl = geom.addSurfaceLoop(b)

    # Volume
    v = geom.addVolume([sl])

    geom.synchronize()

    gmsh.fltk.run()

    # Generate mesh
    msh.generate(3)

    # ===========================================================
    # Save results
    # ===========================================================
    # Visualization options
    gmsh.option.setNumber("Geometry.Curves", 1)
    gmsh.option.setNumber("Geometry.Surfaces", 1)
    gmsh.option.setNumber("Mesh.SurfaceFaces", 1)
    gmsh.option.setNumber("Mesh.Points", 1)

    # Read save directory
    path = Path(__file__).parent / config["filename"]
    gmsh.write(str(path))
    gmsh.fltk.run()

    # Finalize
    gmsh.finalize()


# ===========================================================
# Test
# ===========================================================
if __name__ == "__main__":
    config = {
        "filename": "Mesh.su2",
        "wall size": 10,
        "layer thickness": 0.005,
        "total thickness": 10,
        "layer ratio": 1.2,
        "number of layers": 40,
        "BOI1": 2000,
        "BOI2": 5000,
        "BOI3": 100,
        "global size": 4000,
        "alpha": radians(0)
    }

    meshgen_3D(config=config)
