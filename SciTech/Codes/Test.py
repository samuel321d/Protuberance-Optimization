import shutil
import subprocess
from pathlib import Path

import gmsh

# Initialize
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.model.add("Cilindro_BL")
geom = gmsh.model.geo

# Bounding box
xmin, xmax = -1.5, 1.5
ymin, ymax = -1.5, 1.5
zmin, zmax = -4, 4.0

cylinder2 = gmsh.model.occ.addCylinder(0, 0, 0, 0, 0, 4, 1.5)

# Add sphere
circle = gmsh.model.occ.addSphere(0, 0, 0, 1.5)

gmsh.model.occ.synchronize()

total, __ = gmsh.model.occ.fuse([(3, cylinder2)], [(3, circle)])

gmsh.model.occ.synchronize()

surfaces = gmsh.model.getBoundary(total, combined=False, oriented=False, recursive=False)
surface_tags = [tag for dim, tag in surfaces if dim == 2]

# Remove only the fused solid; keep its boundary faces for the surface loop.
gmsh.model.occ.remove(total, recursive=False)

gmsh.model.occ.synchronize()

# Surface loop
sl = geom.addSurfaceLoop(surface_tags)

# Volume
v = geom.addVolume([sl])

geom.synchronize()

gmsh.option.setNumber("Mesh.Algorithm3D", 4)

# Finalize
gmsh.model.mesh.generate(3)
gmsh.write("BL.msh")
gmsh.fltk.run()
gmsh.finalize()


import meshio

# Convert to VTU
mesh = meshio.read("BL.msh")
mesh.cell_sets.clear()
vtu_path = Path("BL.vtu").resolve()
meshio.write(vtu_path, mesh)

# Open mesh in ParaView
paraview = shutil.which("paraview") or shutil.which("paraview.exe")
if paraview is None:
    paraview = r"C:\Program Files\ParaView 6.2.0\bin\paraview.exe"
    if not Path(paraview).is_file():
        raise FileNotFoundError(
            "ParaView was not found. Add paraview.exe to PATH or update its path in BL.py."
        )

subprocess.Popen([paraview, str(vtu_path)])