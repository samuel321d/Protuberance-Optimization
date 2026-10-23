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
        "layer ratio"        : 1.2,
        "layer thickness"    : 9.75e-7*1000,
        "number of layers"   : 40,
        "BOI1"               : 1000,
        "BOI2"               : 300,
        "BOI3"               : 100,
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
    rocket_path = Path(__file__).parent / "Rocket.step"
    rocket = occm.importShapes(str(rocket_path), highestDimOnly=True)

    occm.synchronize()

    # Rocket surfaces
    rocket_boundary = gmsh.model.getBoundary(rocket, combined = False,oriented = False, recursive = False)
    rocket_surfaces = [tag for dim, tag in rocket_boundary if dim == 2]

    # Remove rocket
    occm.remove(rocket, recursive = False)

    occm.synchronize()

    # Surface loops
    s_in = geom.addSurfaceLoop(rocket_surfaces)
    s_out = geom.addSurfaceLoop(farfield_surfaces)

    # Volume
    v = geom.addVolume([s_out, s_in])

    geom.synchronize()

    # ===========================================================
    # Meshing
    # ===========================================================
    gmsh.option.setNumber("Mesh.Algorithm3D", 4)
    gmsh.option.setNumber("Mesh.MeshSizeMax", config["global size"])
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)

    # BOIs
    BOI1 = msh.field.add("Box")
    msh.field.setNumber(BOI1, "XMin", -5.5*L)
    msh.field.setNumber(BOI1, "XMax", 8.5*L)
    msh.field.setNumber(BOI1, "YMin", -7*L)
    msh.field.setNumber(BOI1, "YMax", 7*L)
    msh.field.setNumber(BOI1, "ZMin", -7*L)
    msh.field.setNumber(BOI1, "ZMax", 7*L)
    msh.field.setNumber(BOI1, "VIn", config["BOI1"])
    msh.field.setNumber(BOI1, "VOut", config["global size"])
    msh.field.setNumber(BOI1, "Thickness", config["BOI1"])

    BOI2 = msh.field.add("Box")
    msh.field.setNumber(BOI2, "XMin", -3.5*L)
    msh.field.setNumber(BOI2, "XMax", 6.5*L)
    msh.field.setNumber(BOI2, "YMin", -5*L)
    msh.field.setNumber(BOI2, "YMax", 5*L)
    msh.field.setNumber(BOI2, "ZMin", -5*L)
    msh.field.setNumber(BOI2, "ZMax", 5*L)
    msh.field.setNumber(BOI2, "VIn", config["BOI2"])
    msh.field.setNumber(BOI2, "VOut", config["global size"])
    msh.field.setNumber(BOI2, "Thickness", config["BOI2"])

    BOI3 = msh.field.add("Box")
    msh.field.setNumber(BOI3, "XMin", -1.5*L)
    msh.field.setNumber(BOI3, "XMax", 4.5*L)
    msh.field.setNumber(BOI3, "YMin", -3*L)
    msh.field.setNumber(BOI3, "YMax", 3*L)
    msh.field.setNumber(BOI3, "ZMin", -3*L)
    msh.field.setNumber(BOI3, "ZMax", 3*L)
    msh.field.setNumber(BOI3, "VIn", config["BOI3"])
    msh.field.setNumber(BOI3, "VOut", config["global size"])
    msh.field.setNumber(BOI3, "Thickness", config["BOI3"])

    BOI4 = msh.field.add("Box")
    msh.field.setNumber(BOI4, "XMin", -1.1*L)
    msh.field.setNumber(BOI4, "XMax", 0.1*L)
    msh.field.setNumber(BOI4, "YMin", -0.5*L)
    msh.field.setNumber(BOI4, "YMax", 0.5*L)
    msh.field.setNumber(BOI4, "ZMin", -0.5*L)
    msh.field.setNumber(BOI4, "ZMax", 0.5*L)
    msh.field.setNumber(BOI4, "VIn", config["BOI4"])
    msh.field.setNumber(BOI4, "Thickness", config["BOI4"])
    msh.field.setNumber(BOI4, "VOut", config["global size"])

    # BOI1 = msh.field.add("Frustum")
    # msh.field.setNumber(BOI1, "InnerR1", 0)
    # msh.field.setNumber(BOI1, "InnerR2", 0)
    # msh.field.setNumber(BOI1, "InnerV1", config["BOI1"])
    # msh.field.setNumber(BOI1, "InnerV2", config["BOI1"])
    # msh.field.setNumber(BOI1, "OuterR1", 7*L)
    # msh.field.setNumber(BOI1, "OuterR2", 7*L)
    # msh.field.setNumber(BOI1, "X1", 8.5*L)
    # msh.field.setNumber(BOI1, "Y1", 0)
    # msh.field.setNumber(BOI1, "Z1", 0)
    # msh.field.setNumber(BOI1, "X2", -5.5*L)
    # msh.field.setNumber(BOI1, "Y2", 0)
    # msh.field.setNumber(BOI1, "Z2", 0)

    # BOI2 = msh.field.add("Frustum")
    # msh.field.setNumber(BOI2, "InnerR1", 0)
    # msh.field.setNumber(BOI2, "InnerR2", 0)
    # msh.field.setNumber(BOI2, "InnerV1", config["BOI2"])
    # msh.field.setNumber(BOI2, "InnerV2", config["BOI2"])
    # msh.field.setNumber(BOI2, "OuterR1", 5*L)
    # msh.field.setNumber(BOI2, "OuterR2", 5*L)
    # msh.field.setNumber(BOI2, "X1", 6.5*L)
    # msh.field.setNumber(BOI2, "Y1", 0)
    # msh.field.setNumber(BOI2, "Z1", 0)
    # msh.field.setNumber(BOI2, "X2", -3.5*L)
    # msh.field.setNumber(BOI2, "Y2", 0)
    # msh.field.setNumber(BOI2, "Z2", 0)

    # BOI3 = msh.field.add("Frustum")
    # msh.field.setNumber(BOI3, "InnerR1", 0)
    # msh.field.setNumber(BOI3, "InnerR2", 0)
    # msh.field.setNumber(BOI3, "InnerV1", config["BOI3"])
    # msh.field.setNumber(BOI3, "InnerV2", config["BOI3"])
    # msh.field.setNumber(BOI3, "OuterR1", 3*L)
    # msh.field.setNumber(BOI3, "OuterR2", 3*L)
    # msh.field.setNumber(BOI3, "X1", 4.5*L)
    # msh.field.setNumber(BOI3, "Y1", 0)
    # msh.field.setNumber(BOI3, "Z1", 0)
    # msh.field.setNumber(BOI3, "X2", -1.5*L)
    # msh.field.setNumber(BOI3, "Y2", 0)
    # msh.field.setNumber(BOI3, "Z2", 0)

    # BOI4 = msh.field.add("Frustum")
    # msh.field.setNumber(BOI4, "InnerR1", 0)
    # msh.field.setNumber(BOI4, "InnerR2", 0)
    # msh.field.setNumber(BOI4, "InnerV1", config["BOI4"])
    # msh.field.setNumber(BOI4, "InnerV2", config["BOI4"])
    # msh.field.setNumber(BOI4, "OuterR1", 0.5*L)
    # msh.field.setNumber(BOI4, "OuterR2", 0.5*L)
    # msh.field.setNumber(BOI4, "X1", 0.1*L)
    # msh.field.setNumber(BOI4, "Y1", 0)
    # msh.field.setNumber(BOI4, "Z1", 0)
    # msh.field.setNumber(BOI4, "X2", -1.1*L)
    # msh.field.setNumber(BOI4, "Y2", 0)
    # msh.field.setNumber(BOI4, "Z2", 0)

    # Combine Sizings
    background = msh.field.add("Min")
    msh.field.setNumbers(background, "FieldsList", [BOI4])
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
        "filename"              : "Mesh.su2",
        "layer thickness"       : 1.12e-3,
        "layer ratio"           : 1.21,
        "total thickness"       : 10,
        "number of layers"      : 45,
        "BOI1"                  : 3000,
        "BOI2"                  : 2000,
        "BOI3"                  : 1000,
        "BOI4"                  : 100,
        "global size"           : 4000,
        "L"                     : 3240
    }

    meshgen_3D(config = config)

    import subprocess
    import os

    # Ruta a tu ParaView en Windows (ajústala a tu versión instalada)
    paraview_path = r"C:\Program Files\ParaView 6.2.0\bin\paraview.exe"
    
    try:
        # 1. Ejecutar el comando SU2_SOL para convertir la malla
        # Esto buscará 'mesh_proyecto.su2' y creará un archivo llamado 'mesh_proyecto.vtk' (o similar)
        print("Convirtiendo malla a formato ParaView...")
        subprocess.run(["SU2_SOL", config["filename"], "-m"], check=True)
        
        # 2. SU2_SOL genera por defecto un archivo con extensión .vtk
        archivo_vtk = "mesh_proyecto.vtk" 
        
        # 3. Lanzar ParaView automáticamente
        if os.path.exists(archivo_vtk) and os.path.exists(paraview_path):
            print(f"Abriendo ParaView con el archivo {archivo_vtk}...")
            subprocess.Popen([paraview_path, archivo_vtk])
        else:
            print("Conversión completada, pero verifica que las rutas de los archivos sean correctas.")

    except subprocess.CalledProcessError:
        print("❌ Error al ejecutar SU2_SOL. Asegúrate de que SU2 esté en las Variables de Entorno (PATH).")


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
