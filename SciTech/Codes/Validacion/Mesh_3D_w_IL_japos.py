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
import math
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

    # Default configuration (in mm)
    default_config = {
        "filename"              : "Mesh.su2",
        "layer thickness"       : 1.12e-3,
        "layer ratio"           : 1.21,
        "total thickness"       : 5.95,
        "number of layers"      : 45,
        "BOIC1"                 : 200,
        "BOIC2"                 : 100,
        "BOIC3"                 : 50,
        "BOIC4"                 : 20,
        "BOIC6"                 : 7,
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

    # Read config
    config = {**default_config, **config}
    L = config["L"]

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setString("Geometry.OCCTargetUnit", "M")
    gmsh.model.add("Rocket")

    # Abreviation
    geom = gmsh.model.geo
    occm = gmsh.model.occ
    msh = gmsh.model.mesh

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

    # Accomodate geometry
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

    # Grow inflation layers (dim, tag surface)
    rocket_volumes = [(dim, tag) for dim, tag in rocket if dim == 3]
    rocket_boundary = gmsh.model.getBoundary(rocket_volumes, oriented = True, recursive = False)
    rocket_surfaces = [(dim, abs(tag)) for dim, tag in rocket_boundary if dim == 2]

    gmsh.option.setNumber("Mesh.MeshSizeMax", config["global size"])
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)

    # Refinement cone 1
    R_Cone1 = 0.9*L * math.tan(math.radians(45))
    LEC = occm.addCone(-L, 0, 0, 0.9*L, 0, 0, 0, R_Cone1)

    occm.synchronize()

    LEC_faces = gmsh.model.getBoundary([(3, LEC)], oriented = False)
    LEC_surfaces = [tag for dim, tag in LEC_faces if dim == 2 and gmsh.model.getType(dim, tag) == "Cone"]
    if not LEC_surfaces:
        raise RuntimeError("Could not find the cone surface for mesh refinement.")

    occm.remove([(3, LEC)], recursive = False)

    occm.synchronize()

    DISTANCE = msh.field.add("Distance")
    msh.field.setNumbers(DISTANCE, "SurfacesList", LEC_surfaces)
    msh.field.setNumber(DISTANCE, "Sampling", 1000)

    CONE = msh.field.add("Threshold")
    msh.field.setNumber(CONE, "InField", DISTANCE)
    msh.field.setNumber(CONE, "SizeMin", config["cone"])
    msh.field.setNumber(CONE, "SizeMax", config["global size"])
    msh.field.setNumber(CONE, "DistMin", 0.01*L)
    msh.field.setNumber(CONE, "DistMax", 0.4*L)

    # Refinement cone 2
    R_Cone2 = 0.9*L * math.tan(math.radians(45))
    LEC2 = occm.addCone(0, 0, 0, 0.9*L, 0, 0, 0, R_Cone2)

    occm.synchronize()

    LEC2_faces = gmsh.model.getBoundary([(3, LEC2)], oriented = False)
    LEC2_surfaces = [tag for dim, tag in LEC2_faces if dim == 2 and gmsh.model.getType(dim, tag) == "Cone"]
    if not LEC2_surfaces:
        raise RuntimeError("Could not find the cone surface for mesh refinement.")

    occm.remove([(3, LEC2)], recursive = False)

    occm.synchronize()

    DISTANCE2 = msh.field.add("Distance")
    msh.field.setNumbers(DISTANCE2, "SurfacesList", LEC2_surfaces)
    msh.field.setNumber(DISTANCE2, "Sampling", 1000)

    CONE2 = msh.field.add("Threshold")
    msh.field.setNumber(CONE2, "InField", DISTANCE2)
    msh.field.setNumber(CONE2, "SizeMin", config["cone2"])
    msh.field.setNumber(CONE2, "SizeMax", config["global size"])
    msh.field.setNumber(CONE2, "DistMin", 0.01*L)
    msh.field.setNumber(CONE2, "DistMax", 2*L)

    # Refinement cone 3
    R_Cone3 = 0.4*L* math.tan(math.radians(45))
    LEC3 = occm.addCone( (1-config["prot_loc"])*L - L -0.04, 0, 0, 0.4*L, 0, 0, 0, R_Cone3, angle= math.pi)
    occm.rotate([(3, LEC3)], 0, 0, 0, 1, 0, 0, -3*math.pi / 4)

    occm.synchronize()

    LEC3_faces = gmsh.model.getBoundary([(3, LEC3)], oriented = False)
    LEC3_surfaces = [tag for dim, tag in LEC3_faces if dim == 2 and gmsh.model.getType(dim, tag) == "Cone"]
    if not LEC3_surfaces:
        raise RuntimeError("Could not find the cone surface for mesh refinement.")
    
    occm.remove([(3, LEC3)], recursive = False)

    occm.synchronize()

    DISTANCE3 = msh.field.add("Distance")
    msh.field.setNumbers(DISTANCE3, "SurfacesList", LEC3_surfaces)
    msh.field.setNumber(DISTANCE3, "Sampling", 1000)

    CONE3 = msh.field.add("Threshold")
    msh.field.setNumber(CONE3, "InField", DISTANCE3)
    msh.field.setNumber(CONE3, "SizeMin", config["cone3"])
    msh.field.setNumber(CONE3, "SizeMax", config["global size"])
    msh.field.setNumber(CONE3, "DistMin", 0.01*L)
    msh.field.setNumber(CONE3, "DistMax", 0.8*L)

    # Spherical BOIs
    BOIS1 = msh.field.add("Ball")
    msh.field.setNumber(BOIS1, "Radius", 0.25*L)
    msh.field.setNumber(BOIS1, "Thickness", 4*config["BOIS1"])
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
    msh.field.setNumber(BOIS3, "Radius", 0.008*L)
    msh.field.setNumber(BOIS3, "Thickness", 4*config["BOIS3"])
    msh.field.setNumber(BOIS3, "VIn", config["BOIS3"])
    msh.field.setNumber(BOIS3, "VOut", config["global size"])
    msh.field.setNumber(BOIS3, "XCenter", -L)
    msh.field.setNumber(BOIS3, "YCenter", 0)
    msh.field.setNumber(BOIS3, "ZCenter", 0)

    SPHERES = msh.field.add("Min")
    msh.field.setNumbers(SPHERES, "FieldsList", [BOIS1, BOIS2, BOIS3, CONE, CONE2, CONE3])
    msh.field.setAsBackgroundMesh(SPHERES)

    # Generate mesh
    msh.generate(2)

    extbl = geom.extrudeBoundaryLayer(rocket_surfaces, [1] * N, heights, True)

    geom.synchronize()

    boundary_layer_volumes = [tag for dim, tag in extbl if dim == 3]

    # Rocket surfaces (tag surface)
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
    b_in = [s[1] for s in top]
    s_in = geom.addSurfaceLoop(b_in)
    s_out = geom.addSurfaceLoop(farfield_surfaces)

    # Volume
    v = geom.addVolume([s_out, s_in])

    geom.synchronize()

    # Physical groups
    gmsh.model.addPhysicalGroup(3, [v, *boundary_layer_volumes], name = "FLUID")
    gmsh.model.addPhysicalGroup(2, farfield_surfaces, name = "FARFIELD")
    gmsh.model.addPhysicalGroup(2, rocket_surfaces, name = "WALL")

    # Cylindrical BOIs
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
    msh.field.setNumber(BOIC5, "Radius", 0.5*L)
    msh.field.setNumber(BOIC5, "VOut", config["global size"])
    msh.field.setNumber(BOIC5, "XAxis", 0.8*L)
    msh.field.setNumber(BOIC5, "YAxis", 0)
    msh.field.setNumber(BOIC5, "ZAxis", 0)
    msh.field.setNumber(BOIC5, "XCenter", -0.5*L)
    msh.field.setNumber(BOIC5, "YCenter", 0)
    msh.field.setNumber(BOIC5, "ZCenter", 0)

    BOIC6 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIC6, "VIn", config["BOIC6"])
    msh.field.setNumber(BOIC6, "Radius", 0.15*L)
    msh.field.setNumber(BOIC6, "VOut", config["global size"])
    msh.field.setNumber(BOIC6, "XAxis", 0.6*L)
    msh.field.setNumber(BOIC6, "YAxis", 0)
    msh.field.setNumber(BOIC6, "ZAxis", 0)
    msh.field.setNumber(BOIC6, "XCenter", -0.5*L)
    msh.field.setNumber(BOIC6, "YCenter", 0)
    msh.field.setNumber(BOIC6, "ZCenter", 0)

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

    BOIP1 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIP1, "VIn", config["BOIP1"])
    msh.field.setNumber(BOIP1, "Radius", 0.025*L)
    msh.field.setNumber(BOIP1, "VOut", config["global size"])
    msh.field.setNumber(BOIP1, "XAxis", 0.1*L)
    msh.field.setNumber(BOIP1, "YAxis", 0)
    msh.field.setNumber(BOIP1, "ZAxis", 0)
    msh.field.setNumber(BOIP1, "XCenter", (1-config["prot_loc"])*L - L)
    msh.field.setNumber(BOIP1, "YCenter", 0.9*config["R_radius"]*np.cos(np.deg2rad(45)))
    msh.field.setNumber(BOIP1, "ZCenter", 0.9*config["R_radius"]*np.cos(np.deg2rad(45)))

    BOIP2 = msh.field.add("Cylinder")
    msh.field.setNumber(BOIP2, "VIn", config["BOIP2"])
    msh.field.setNumber(BOIP2, "Radius", 0.045*L)
    msh.field.setNumber(BOIP2, "VOut", config["global size"])
    msh.field.setNumber(BOIP2, "XAxis", 0.4*L)
    msh.field.setNumber(BOIP2, "YAxis", 0)
    msh.field.setNumber(BOIP2, "ZAxis", 0)
    msh.field.setNumber(BOIP2, "XCenter", 0.4*L - L)
    msh.field.setNumber(BOIP2, "YCenter", 0.9*config["R_radius"]*np.cos(np.deg2rad(45)))
    msh.field.setNumber(BOIP2, "ZCenter", 0.9*config["R_radius"]*np.cos(np.deg2rad(45)))

    DISTANCE3 = msh.field.add("Distance")
    msh.field.setNumbers(DISTANCE3, "SurfacesList", rocket_surfaces)
    msh.field.setNumber(DISTANCE3, "Sampling", 1000)

    WALL = msh.field.add("Threshold")
    msh.field.setNumber(WALL, "InField", DISTANCE3)
    msh.field.setNumber(WALL, "SizeMin", config["wall size"])
    msh.field.setNumber(WALL, "SizeMax", config["global size"])
    msh.field.setNumber(WALL, "DistMin", 0.001*L)
    msh.field.setNumber(WALL, "DistMax", 0.01*L)
    
    # Combine Sizings
    background = msh.field.add("Min")
    msh.field.setNumbers(background, "FieldsList", [BOIC1, BOIC2, BOIC3, BOIC4, BOIC5, BOIC6, 
                                                    BOIF1, BOIF2, 
                                                    BOIS1, BOIS2, BOIS3,
                                                    BOIP1, BOIP2,
                                                    CONE, CONE2 ,CONE3,
                                                    WALL
                                                    ])
    msh.field.setAsBackgroundMesh(background)

    # Generate mesh
    msh.generate(3)

    # If errors
    _, volume_elements, _ = msh.getElements(3, v)
    if not any(len(elements) for elements in volume_elements):
        raise RuntimeError("Gmsh did not generate 3D elements in the fluid volume.")

    # Visualization options
    gmsh.option.setNumber("Geometry.Curves", 1)
    gmsh.option.setNumber("Geometry.Surfaces", 1)
    gmsh.option.setNumber("Mesh.VolumeFaces", 1)

    # Read save directory
    path = Path(__file__).parent / config["filename"]
    gmsh.write(str(path))
    # gmsh.fltk.run()

    # Finalize
    gmsh.finalize()

# ===========================================================
# Test
# ===========================================================
if __name__ == "__main__":
    config = {
        "filename"              : "Mesh_M.su2", # C - M - F
        "layer thickness"       : 9.58e-7, # 9.58e-7 - 
        "layer ratio"           : 1.21, # 1.21 - 
        "total thickness"       : 0.000625, # 0.000625 - 
        "number of layers"      : 25, # 25 - 
        "BOIC1"                 : 0.2, # 0.2 - 
        "BOIC2"                 : 0.1, # 0.1 - 
        "BOIC3"                 : 0.05, # 0.05 - 
        "BOIC4"                 : 0.025, # 0.02 - 
        "BOIC5"                 : 0.008, # 0.01 - 
        "BOIC6"                 : 0.003, # 0.005
        "BOIF1"                 : 0.008, # 0.01 - 
        "BOIF2"                 : 0.003, # 0.005 - 
        "BOIS1"                 : 0.005, # 0.005 - 
        "BOIS2"                 : 0.0025, # 0.0025 - 
        "BOIS3"                 : 0.001, # 0.001 - 
        "global size"           : 0.4, # 0.4 - 
        "L"                     : 0.368,
        "prot_loc"              : 0.75,
        "BOIP1"                 : 0.001, # 0.001 - 
        "BOIP2"                 : 0.0025, # 0.0025 - 
        "R_radius"              : 0.02075,
        "cone"                  : 0.003, # 0.004 - 
        "cone2"                 : 0.01, # 0.01 - 
        "cone3"                 : 0.003, # 0.004 - 
        "wall size"             : 0.0015, # 0.002 - 
        "Prot_height"           : 6.225
    }

    mesh = True
    paraview = True

    # Generate mesh
    if mesh:
        meshgen_3D(config = config)

    # Calculate metrics with SU2_CFD
    if paraview:
        # Paths
        mesh_path = Path(__file__).parent / config["filename"]
        su2_cfd_path = shutil.which("SU2_CFD")
        paraview_path = r"C:\Program Files\ParaView 6.2.0\bin\paraview.exe"

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