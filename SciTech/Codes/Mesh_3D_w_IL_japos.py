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
import shutil
import subprocess
import tempfile
import gmsh
import numpy as np
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
        "layer ratio"        : 1.2,
        "layer thickness"    : 9.75e-7*1000,
        "number of layers"   : 40,
        "BOIC1"              : 1000,
        "BOIC2"              : 500,
        "BOIC3"              : 400,
        "BOIC4"              : 200,
        "BOIC5"              : 100,
        "BOIF1"              : 50,
        "BOIF2"              : 20,
        "BOIS1"              : 300, 
        "BOIS2"              : 100,
        "global size"        : 2000,
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
    cylinder_ff = occm.addCylinder(0, 0, 0, 15*L, 0, 0, 12*L)
    sphere_ff = occm.addSphere(0, 0, 0, 12*L)

    occm.synchronize()

    # Fusion of elements
    farfield, _ = occm.fuse([(3, cylinder_ff)], [(3, sphere_ff)])

    occm.synchronize()

    # Farfield surfaces
    farfield_boundary = gmsh.model.getBoundary(farfield, combined = False, oriented = False, recursive = False)
    farfield_surfaces = [tag for dim, tag in farfield_boundary if dim == 2]

    # Remove farfield volumes
    occm.remove(farfield, recursive = False)

    occm.synchronize()

    # Import rocket geometry
    rocket_path = Path(__file__).parent / "Cohetejaponeses.step"
    rocket = occm.importShapes(str(rocket_path), highestDimOnly=True)

    occm.synchronize()
    occm.translate(rocket, -L, 0, 0)
    occm.synchronize()
    occm.rotate(rocket, 0, 0, 0, 1, 0, 0, -np.pi/4)
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

    gmsh.option.setNumber("Mesh.MeshSizeMax", config["global size"])
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)

    # Tamaño constante sobre todas las superficies del cohete (en unidades del STEP)
    WALL = msh.field.add("MathEval")
    msh.field.setString(WALL, "F", "10")

    WALL_SIZE = msh.field.add("Restrict")
    msh.field.setNumber(WALL_SIZE, "InField", WALL)
    msh.field.setNumbers(WALL_SIZE, "SurfacesList", [tag for dim, tag in rocket_surfaces])

    msh.field.setAsBackgroundMesh(WALL_SIZE)

    msh.generate(2)

    gmsh.fltk.run()

    if inward_surfaces:
        msh.reverse(inward_surfaces)

    extbl = geom.extrudeBoundaryLayer(rocket_surfaces, [1] * N, heights, True)

    geom.synchronize()

    boundary_layer_volumes = [tag for dim, tag in extbl if dim == 3]

    # Rocket surfaces
    rocket_boundary = gmsh.model.getBoundary(rocket, combined = False,oriented = False, recursive = False)
    rocket_surfaces = [tag for dim, tag in rocket_boundary if dim == 2]

    # Remove rocket
    occm.remove(rocket, recursive = True)

    occm.synchronize()

    # BL top faces
    top = []
    for i in range(1, len(extbl)):
        if extbl[i][0] == 3:
            top.append(extbl[i-1])

    # Surface loops
    # s_in = geom.addSurfaceLoop(rocket_surfaces)
    b_in = [s[1] for s in top]
    s_in = geom.addSurfaceLoop(b_in)
    s_out = geom.addSurfaceLoop(farfield_surfaces)

    # Volume
    v = geom.addVolume([s_out, s_in])

    geom.synchronize()

    # Export the boundary markers required by SU2's mesh reader.
    gmsh.model.addPhysicalGroup(2, farfield_surfaces, name = "FARFIELD")
    gmsh.model.addPhysicalGroup(2, rocket_surfaces, name = "WALL")
    gmsh.model.addPhysicalGroup(3, [v, *boundary_layer_volumes], name = "FLUID")

    # ===========================================================
    # Meshing
    # ===========================================================
    #gmsh.option.setNumber("Mesh.Algorithm3D", 4)

    # BOIs
    BOIC1 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIC1, "VIn", config["BOIC1"])
    msh.field.setNumber(BOIC1, "Radius", 7*L)
    msh.field.setNumber(BOIC1, "VOut", config["global size"])
    msh.field.setNumber(BOIC1, "XAxis", 7*L)
    msh.field.setNumber(BOIC1, "YAxis", 0)
    msh.field.setNumber(BOIC1, "ZAxis", 0)
    msh.field.setNumber(BOIC1, "XCenter", 1.5*L)
    msh.field.setNumber(BOIC1, "YCenter", 0)
    msh.field.setNumber(BOIC1, "ZCenter", 0)

    BOIC2 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIC2, "VIn", config["BOIC2"])
    msh.field.setNumber(BOIC2, "Radius", 5*L)
    msh.field.setNumber(BOIC2, "VOut", config["global size"])
    msh.field.setNumber(BOIC2, "XAxis", 5*L)
    msh.field.setNumber(BOIC2, "YAxis", 0)
    msh.field.setNumber(BOIC2, "ZAxis", 0)
    msh.field.setNumber(BOIC2, "XCenter", 1.5*L)
    msh.field.setNumber(BOIC2, "YCenter", 0)
    msh.field.setNumber(BOIC2, "ZCenter", 0)

    BOIC3 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIC3, "VIn", config["BOIC3"])
    msh.field.setNumber(BOIC3, "Radius", 3*L)
    msh.field.setNumber(BOIC3, "VOut", config["global size"])
    msh.field.setNumber(BOIC3, "XAxis", 4*L)
    msh.field.setNumber(BOIC3, "YAxis", 0)
    msh.field.setNumber(BOIC3, "ZAxis", 0)
    msh.field.setNumber(BOIC3, "XCenter", 1.5*L)
    msh.field.setNumber(BOIC3, "YCenter", 0)
    msh.field.setNumber(BOIC3, "ZCenter", 0)

    BOIC4 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIC4, "VIn", config["BOIC4"])
    msh.field.setNumber(BOIC4, "Radius", 1*L)
    msh.field.setNumber(BOIC4, "VOut", config["global size"])
    msh.field.setNumber(BOIC4, "XAxis", 2.5*L)
    msh.field.setNumber(BOIC4, "YAxis", 0)
    msh.field.setNumber(BOIC4, "ZAxis", 0)
    msh.field.setNumber(BOIC4, "XCenter", L)
    msh.field.setNumber(BOIC4, "YCenter", 0)
    msh.field.setNumber(BOIC4, "ZCenter", 0)

    BOIC5 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIC5, "VIn", config["BOIC5"])
    msh.field.setNumber(BOIC5, "Radius", 0.1*L)
    msh.field.setNumber(BOIC5, "VOut", config["global size"])
    msh.field.setNumber(BOIC5, "XAxis", 0.6*L)
    msh.field.setNumber(BOIC5, "YAxis", 0)
    msh.field.setNumber(BOIC5, "ZAxis", 0)
    msh.field.setNumber(BOIC5, "XCenter", -0.5*L)
    msh.field.setNumber(BOIC5, "YCenter", 0)
    msh.field.setNumber(BOIC5, "ZCenter", 0)

    BOIF1 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIF1, "VIn", config["BOIF1"])
    msh.field.setNumber(BOIF1, "Radius", 0.4*L)
    msh.field.setNumber(BOIF1, "VOut", config["global size"])
    msh.field.setNumber(BOIF1, "XAxis", 1.3*L)
    msh.field.setNumber(BOIF1, "YAxis", 0)
    msh.field.setNumber(BOIF1, "ZAxis", 0)
    msh.field.setNumber(BOIF1, "XCenter", L)
    msh.field.setNumber(BOIF1, "YCenter", 0)
    msh.field.setNumber(BOIF1, "ZCenter", 0)

    BOIF2 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIF2, "VIn", config["BOIF2"])
    msh.field.setNumber(BOIF2, "Radius", 0.2*L)
    msh.field.setNumber(BOIF2, "VOut", config["global size"])
    msh.field.setNumber(BOIF2, "XAxis", 0.3*L)
    msh.field.setNumber(BOIF2, "YAxis", 0)
    msh.field.setNumber(BOIF2, "ZAxis", 0)
    msh.field.setNumber(BOIF2, "XCenter", 0.1*L)
    msh.field.setNumber(BOIF2, "YCenter", 0)
    msh.field.setNumber(BOIF2, "ZCenter", 0)

    # BOIF3 = msh.field.add("Box")
    # msh.field.setNumber(BOIF3, "VIn", config["BOIF3"])
    # msh.field.setNumber(BOIF3, "Thickness", config["BOIF3"])
    # msh.field.setNumber(BOIF3, "VOut", config["global size"])
    # msh.field.setNumber(BOIF3, "XMin", 0)
    # msh.field.setNumber(BOIF3, "XMax", -60)
    # msh.field.setNumber(BOIF3, "YMin", 0)
    # msh.field.setNumber(BOIF3, "YMax", 270)
    # msh.field.setNumber(BOIF3, "ZMin", 0)
    # msh.field.setNumber(BOIF3, "ZMax", 0)

    BOIS1 = msh.field.add("Ball")
    msh.field.setNumber(BOIS1, "Radius", 0.25*L)
    msh.field.setNumber(BOIS1, "Thickness", config["BOIS1"])
    msh.field.setNumber(BOIS1, "VIn", config["BOIS1"])
    msh.field.setNumber(BOIS1, "VOut", config["global size"])
    msh.field.setNumber(BOIS1, "XCenter", -L)
    msh.field.setNumber(BOIS1, "YCenter", 0)
    msh.field.setNumber(BOIS1, "ZCenter", 0)

    BOIS2 = msh.field.add("Ball")
    msh.field.setNumber(BOIS2, "Radius", 0.1*L)
    msh.field.setNumber(BOIS2, "Thickness", config["BOIS2"])
    msh.field.setNumber(BOIS2, "VIn", config["BOIS2"])
    msh.field.setNumber(BOIS2, "VOut", config["global size"])
    msh.field.setNumber(BOIS2, "XCenter", -L)
    msh.field.setNumber(BOIS2, "YCenter", 0)
    msh.field.setNumber(BOIS2, "ZCenter", 0)

    BOIS3 = msh.field.add("Ball")
    msh.field.setNumber(BOIS3, "Radius", 0.08*L)
    msh.field.setNumber(BOIS3, "Thickness", config["BOIS3"])
    msh.field.setNumber(BOIS3, "VIn", config["BOIS3"])
    msh.field.setNumber(BOIS3, "VOut", config["global size"])
    msh.field.setNumber(BOIS3, "XCenter", -L)
    msh.field.setNumber(BOIS3, "YCenter", 0)
    msh.field.setNumber(BOIS3, "ZCenter", 0)
    
    BOIP1 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIP1, "VIn", config["BOIP1"])
    msh.field.setNumber(BOIP1, "Radius", 0.025*L)
    msh.field.setNumber(BOIP1, "VOut", config["global size"])
    msh.field.setNumber(BOIP1, "XAxis", 0.1*L)
    msh.field.setNumber(BOIP1, "YAxis", 0)
    msh.field.setNumber(BOIP1, "ZAxis", 0)
    msh.field.setNumber(BOIP1, "XCenter", (1-config["prot_loc"])*L - L)
    msh.field.setNumber(BOIP1, "YCenter", config["R_radius"]*np.cos(np.deg2rad(45)))
    msh.field.setNumber(BOIP1, "ZCenter", config["R_radius"]*np.cos(np.deg2rad(45)))

    BOIP2 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIP2, "VIn", config["BOIP2"])
    msh.field.setNumber(BOIP2, "Radius", 0.05*L)
    msh.field.setNumber(BOIP2, "VOut", config["global size"])
    msh.field.setNumber(BOIP2, "XAxis", 0.4*L)
    msh.field.setNumber(BOIP2, "YAxis", 0)
    msh.field.setNumber(BOIP2, "ZAxis", 0)
    msh.field.setNumber(BOIP2, "XCenter", 0.6*L - L)
    msh.field.setNumber(BOIP2, "YCenter", config["R_radius"]*np.cos(np.deg2rad(45)))
    msh.field.setNumber(BOIP2, "ZCenter", config["R_radius"]*np.cos(np.deg2rad(45)))



    # Combine Sizings
    background = msh.field.add("Min")
    msh.field.setNumbers(background, "FieldsList", [BOIC1, BOIC2, 
                                                    BOIC3, BOIC4, 
                                                    BOIC5, BOIF1, 
                                                    BOIF2, BOIS1, 
                                                    BOIS2, BOIS3,
                                                    BOIP1, BOIP2])
    msh.field.setAsBackgroundMesh(background)

    # Generate mesh
    msh.generate(3)

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
    gmsh.option.setNumber("Mesh.VolumeFaces", 1)

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
        "filename"              : "Mesh.su2",
        "layer thickness"       : 1e-3,
        "layer ratio"           : 1.19,
        "total thickness"       : 0.8,
        "number of layers"      : 40,
        "BOIC1"                 : 200,
        "BOIC2"                 : 100,
        "BOIC3"                 : 50,
        "BOIC4"                 : 20,
        "BOIC5"                 : 7,
        "BOIF1"                 : 5,
        "BOIF2"                 : 3,
        "BOIS1"                 : 5,
        "BOIS2"                 : 2,
        "BOIS3"                 : 1,   
        "global size"           : 400,
        "L"                     : 368,
        "prot_loc"              : 0.75,
        "BOIP1"                 : 1,
        "BOIP2"                 : 2,
        "R_radius"              : 41.5*0.5
    }

    meshgen_3D(config = config)

    # Calculate metrics with SU2_CFD

    #Paths
    mesh_path = Path(__file__).parent / config["filename"]
    su2_cfd_path = shutil.which("SU2_CFD")
    paraview_path = r"C:\Program Files\ParaView 6.2.0\bin\paraview.exe"
    if su2_cfd_path is None:
        raise FileNotFoundError("SU2_CFD was not found. Add the SU2 bin directory to PATH.")
    if not Path(paraview_path).is_file():
        raise FileNotFoundError(f"ParaView was not found at {paraview_path}")

    # Keep SU2's temporary config and output files until ParaView is closed.
    with tempfile.TemporaryDirectory(
        prefix = "su2_mesh_quality_",
        dir = mesh_path.parent,
    ) as output_dir:
        output_dir = Path(output_dir)
        cfg_path = output_dir / "mesh_quality.cfg"
        quality_vtu = output_dir / "quality.vtu"
        config_text = (
            f"MESH_FILENAME = ../{mesh_path.name}\n"
            "MESH_FORMAT = SU2\n"
            "SOLVER = EULER\n"
            "MATH_PROBLEM = DIRECT\n"
            "MARKER_EULER = ( WALL )\n"
            "MARKER_FAR = ( FARFIELD )\n"
            "CONV_NUM_METHOD_FLOW = JST\n"
            "CONV_FIELD = RMS_DENSITY\n"
            "ITER = 0\n"
            "MGLEVEL = 0\n"
            "CONV_FILENAME = quality_history\n"
            "VOLUME_FILENAME = quality\n"
            "VOLUME_OUTPUT = ( COORDINATES, MESH_QUALITY)\n"
            "OUTPUT_FILES = ( PARAVIEW )\n"
        )
        cfg_path.write_text(config_text, encoding = "ascii")

        print("Calculating mesh quality with SU2_CFD...")
        subprocess.run(
            [su2_cfd_path, cfg_path.name],
            cwd = output_dir,
            check = True,
        )
        if not quality_vtu.is_file():
            raise FileNotFoundError(f"SU2 did not create its quality output: {quality_vtu}")

        print("ParaView is open; close it to remove SU2's temporary output files.")
        paraview_process = subprocess.Popen([paraview_path, str(quality_vtu)])
        paraview_process.wait()






    # import meshio
    # import shutil
    # import subprocess

    # # Convert to VTU
    # mesh = meshio.read(Path(__file__).parent / config["filename"])
    # mesh.cell_sets.clear()
    # vtu_path = Path(Path(__file__).parent / "Mesh.vtu").resolve()
    # meshio.write(vtu_path, mesh)

    # # Open in Paraview
    # paraview = shutil.which("paraview") or shutil.which("paraview.exe")
    # if paraview is None:
    #     paraview = r"C:\Program Files\ParaView 6.2.0\bin\paraview.exe"
    #     if not Path(paraview).is_file():
    #         raise FileNotFoundError(
    #             "ParaView was not found. Add paraview.exe to PATH or update its path in BL.py."
    #         )

    # subprocess.Popen([paraview, str(vtu_path)])
