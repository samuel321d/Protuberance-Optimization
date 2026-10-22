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
def meshgen_3D(config = {}):
    """
    Function to generate a mesh of the rocket.
    Includes the generation of inflation layers.

    Args:
        config: Dictionary containing configuration options.

    Returns:
        .format file containing mesh
    """

    # Default configuration
    default_config = {
        "filename"           : "Mesh.su2",
        "wall size"          : 1,
        "layer ratio"        : 1.2,
        "layer thickness"    : 9.75e-7*1000,
        "number of layers"   : 40,
        "BOI1"               : 1000,
        "BOI2"               : 300,
        "BOI3"               : 100,
        "global size"        : 2000,
        "alpha"              : radians(6),
        "L"                  : 3200
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
    # Far-field
    cylinder_ff = occm.addCylinder(0, 0, 0, 20*L, 0, 0, 15*L)
    sphere_ff = occm.addSphere(0, 0, 0, 15*L)

    occm.synchronize()

    # Fusion of elements
    farfield, _ = occm.fuse([(3, cylinder_ff)], [(3, sphere_ff)])

    occm.synchronize()

    # Farfield surfaces
    farfield_boundary = gmsh.model.getBoundary(farfield, combined = False, oriented = False, recursive = False)
    farfield_surfaces = [tag for dim, tag in farfield_boundary if dim == 2]

    # Remove farfield volumes
    occm.remove(farfield, recursive=False)

    occm.synchronize()

    # Import rocket geometry
    rocket_path = Path(__file__).parent / "Rocket.step"
    rocket = occm.importShapes(str(rocket_path), highestDimOnly=True)

    occm.synchronize()

    # Extract inflation layer parameters
    N = config["number of layers"]
    r = config["layer ratio"]
    h0 = config["layer thickness"]

    # Total thickness can be specified instead of layer thickness. If both are specified, total thickness takes precedence.
    total_thickness = config.get("total thickness")
    if total_thickness is not None:
        if total_thickness <= 0:
            raise ValueError("'total thickness' must be greater than 0.")
        h0 = total_thickness / sum(r**i for i in range(N))
    elif h0 <= 0:
        raise ValueError("'layer thickness' must be greater than 0.")

    # Calculate layer heights
    heights = []
    for i in range(N):
        layer_height = h0 * r**i
        heights.append((heights[-1] if heights else 0) + layer_height)



    # Grow inflation layers
    rocket_volumes = [(dim, tag) for dim, tag in rocket if dim == 3]
    rocket_boundary = gmsh.model.getBoundary(rocket_volumes, oriented = True, recursive = False)
    rocket_surfaces = [(dim, abs(tag)) for dim, tag in rocket_boundary if dim == 2]
    inward_surfaces = [(dim, -tag) for dim, tag in rocket_boundary if dim == 2 and tag < 0]

    farfield_points = gmsh.model.getBoundary([(2, tag) for tag in farfield_surfaces], combined = True, oriented = False, recursive = True)
    farfield_size = max(config["global size"] * 10, 1000)
    msh.setSize([(dim, tag) for dim, tag in farfield_points if dim == 0], farfield_size)
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

    # Surface loops
    b_in = [s[1] for s in top]
    s_in = geom.addSurfaceLoop(b_in)
    s_out = geom.addSurfaceLoop(farfield_surfaces)

    # Volume
    v = geom.addVolume([s_out, s_in])

    geom.synchronize()

    # ===========================================================
    # Meshing
    # ===========================================================
    gmsh.option.setNumber("Mesh.Algorithm3D", 4)
    gmsh.option.setNumber("Mesh.MeshSizeMax", config["global size"])
    msh.generate(3)

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
    
    BOI4 = msh.field.add("Box")
    msh.field.setNumber(BOI4, "XMin", -0.5*L)
    msh.field.setNumber(BOI4, "XMax", 2.0*L)
    msh.field.setNumber(BOI4, "YMin", -0.3*L)
    msh.field.setNumber(BOI4, "YMax", 0.6*L)
    msh.field.setNumber(BOI4, "VIn", config["BOI4"])
    msh.field.setNumber(BOI4, "Thickness", config["BOI4"])
    
    BOI5 = msh.field.add("Box")
    msh.field.setNumber(BOI5, "XMin", -0.1*L)
    msh.field.setNumber(BOI5, "XMax", 1.2*L)
    msh.field.setNumber(BOI5, "YMin", -0.25*L)
    msh.field.setNumber(BOI5, "YMax", 0.2*L)
    msh.field.setNumber(BOI5, "VIn", config["BOI5"])
    msh.field.setNumber(BOI5, "Thickness", config["BOI5"])

    # Combine Sizings
    min = msh.field.add("Min")
    msh.field.setNumbers(min, "FieldsList", [BOI1, BOI2, BOI3, BOI4, BOI5])
    msh.field.setAsBackgroundMesh(min)

    # If errors
    _, volume_elements, _ = msh.getElements(3, v)
    if not any(len(elements) for elements in volume_elements):
        raise RuntimeError("Gmsh did not generate 3D elements in the fluid volume.")

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
        "filename"              : "Mesh.msh",
        "wall size"             : 5,
        "layer thickness"       : 1.12e-3,
        "layer ratio"           : 1.21,
        "total thickness"       : 10,
        "number of layers"      : 45,
        "BOI1"                  : 2000,
        "BOI2"                  : 5000,
        "BOI3"                  : 100,
        "global size"           : 100,
        "alpha"                 : radians(0),
        "L"                     : 300
    }

    meshgen_3D(config = config)

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
