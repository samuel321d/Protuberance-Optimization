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
        config: Dictionary containing configuration options. If "total
            thickness" is set, it determines the cumulative boundary-layer
            height and overrides "layer thickness".

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
    rocket = occm.importShapes(str(rocket_path), highestDimOnly=True)

    occm.synchronize()

    # Extract inflation layer parameters
    N = config["number of layers"]
    r = config["layer ratio"]
    h0 = config["layer thickness"]

    # Calculate layer heights
    if N < 1:
        raise ValueError("'number of layers' must be at least 1.")
    if r <= 0:
        raise ValueError("'layer ratio' must be greater than 0.")

    total_thickness = config.get("total thickness")
    if total_thickness is not None:
        if total_thickness <= 0:
            raise ValueError("'total thickness' must be greater than 0.")
        h0 = total_thickness / sum(r**i for i in range(N))
    elif h0 <= 0:
        raise ValueError("'layer thickness' must be greater than 0.")

    heights = []
    for i in range(N):
        layer_height = h0 * r**i
        heights.append((heights[-1] if heights else 0) + layer_height)

    # Grow inflation layers
    rocket_surfaces = gmsh.model.getEntities(2)
    rocket_volumes = gmsh.model.getEntities(3)
    boundary = gmsh.model.getBoundary(
        rocket_volumes, oriented=True, recursive=False
    )
    inward_surfaces = [
        (dim, -tag)
        for dim, tag in boundary
        if dim == 2 and tag < 0
    ]
    msh.generate(2)
    if inward_surfaces:
        msh.reverse(inward_surfaces)

    extbl = geom.extrudeBoundaryLayer(rocket_surfaces, [1] * N, heights, True)

    geom.synchronize()

    # Remove rocket
    occm.remove(rocket, recursive = True)

    occm.synchronize()

    # BL top faces
    top = []
    for i in range(1, len(extbl)):
        if extbl[i][0] == 3:
            top.append(extbl[i-1])

    # Farfield
    # Bounding box
    xmin, xmax = -4000, 500
    ymin, ymax = -500, 500
    zmin, zmax = -500, 500

    cylinder2 = gmsh.model.occ.addCylinder(0, 0, 0, 20*L, 0, 0, 15*L)
    circle = gmsh.model.occ.addSphere(0, 0, 0, 15*L)

    gmsh.model.occ.synchronize()

    total, __ = gmsh.model.occ.fuse([(3, cylinder2)], [(3, circle)])

    gmsh.model.occ.synchronize()

    surfaces = gmsh.model.getBoundary(total, combined=False, oriented=False, recursive=False)
    surface_tags = [tag for dim, tag in surfaces if dim == 2]

    gmsh.model.occ.remove(total, recursive=False)

    gmsh.model.occ.synchronize()

    # p1 = geom.addPoint(xmin, ymin, zmin)
    # p2 = geom.addPoint(xmax, ymin, zmin)
    # p3 = geom.addPoint(xmax, ymax, zmin)
    # p4 = geom.addPoint(xmin, ymax, zmin)
    # li1 = geom.addLine(p1, p2)
    # li2 = geom.addLine(p2, p3)
    # li3 = geom.addLine(p3, p4)
    # li4 = geom.addLine(p4, p1)
    # cli = geom.addCurveLoop([li1, li2, li3, li4])
    # si = geom.addPlaneSurface([cli])

    # p5 = geom.addPoint(xmin, ymin, zmax)
    # p6 = geom.addPoint(xmax, ymin, zmax)
    # p7 = geom.addPoint(xmax, ymax, zmax)
    # p8 = geom.addPoint(xmin, ymax, zmax)
    # ls1 = geom.addLine(p5, p6)
    # ls2 = geom.addLine(p6, p7)
    # ls3 = geom.addLine(p7, p8)
    # ls4 = geom.addLine(p8, p5)
    # cls = geom.addCurveLoop([ls1, ls2, ls3, ls4])
    # ss = geom.addPlaneSurface([cls])

    # lv1 = geom.addLine(p1, p5)
    # lv2 = geom.addLine(p2, p6)
    # lv3 = geom.addLine(p3, p7)
    # lv4 = geom.addLine(p4, p8)
    # cll1 = geom.addCurveLoop([li1, lv2, -ls1, -lv1])
    # cll2 = geom.addCurveLoop([li2, lv3, -ls2, -lv2])
    # cll3 = geom.addCurveLoop([li3, lv4, -ls3, -lv3])
    # cll4 = geom.addCurveLoop([li4, lv1, -ls4, -lv4])
    # sl1 = geom.addPlaneSurface([cll1])
    # sl2 = geom.addPlaneSurface([cll2])
    # sl3 = geom.addPlaneSurface([cll3])
    # sl4 = geom.addPlaneSurface([cll4])



    # The fluid volume is bounded by the farfield shell and the layer's top.
    b_in = [s[1] for s in top]
    #b_out = [si, ss, sl1, sl2, sl3, sl4]
    s_out = geom.addSurfaceLoop(surface_tags)
    s_in = geom.addSurfaceLoop(b_in)

    # Volume
    v = geom.addVolume([s_out, s_in])

    geom.synchronize()

    # Generate mesh
    gmsh.option.setNumber("Mesh.Algorithm3D", 4)
    gmsh.option.setNumber("Mesh.MeshSizeMax", config["global size"])
    msh.generate(3)
    _, volume_elements, _ = msh.getElements(3, v)
    if not any(len(elements) for elements in volume_elements):
        raise RuntimeError(
            "Gmsh did not generate 3D elements in the fluid volume."
        )

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
        "filename": "Mesh.msh",
        "wall size": 10,
        "layer thickness": 0.005,
        "total thickness": 10,
        "layer ratio": 1.2,
        "number of layers": 40,
        "BOI1": 2000,
        "BOI2": 5000,
        "BOI3": 100,
        "global size": 100,
        "alpha": radians(0),
        "L": 300
    }

    meshgen_3D(config=config)

    import meshio
    import shutil
    import subprocess

    # Convert to VTU
    mesh = meshio.read(Path(__file__).parent / config["filename"])
    mesh.cell_sets.clear()
    vtu_path = Path(Path(__file__).parent / "Mesh.vtu").resolve()
    meshio.write(vtu_path, mesh)

    # Open in Paraview
    paraview = shutil.which("paraview") or shutil.which("paraview.exe")
    if paraview is None:
        paraview = r"C:\Program Files\ParaView 6.2.0\bin\paraview.exe"
        if not Path(paraview).is_file():
            raise FileNotFoundError(
                "ParaView was not found. Add paraview.exe to PATH or update its path in BL.py."
            )

    subprocess.Popen([paraview, str(vtu_path)])
