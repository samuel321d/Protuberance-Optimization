import gmsh
import numpy as np
from pathlib import Path

# Inicializacion
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.model.add("modelo_1")

# Abreviacion
geom = gmsh.model.geo

# Puntos
p1 = geom.addPoint(-1, 0, 0)
p2 = geom.addPoint(0, 0, 0)
p3 = geom.addPoint(5, 0, 0)
p4 = geom.addPoint(5, 2, 0)
p5 = geom.addPoint(-1, 2, 0)

# Cargar datos
base_dir = Path(__file__).resolve().parent
data = np.loadtxt(base_dir / "Curve.txt", delimiter = ",", skiprows = 1)
x_coords = data[:, 0]
y_coords = data[:, 1]

# Crear un punto por cada fila
point_tags = []
for x, y in zip(x_coords, y_coords):
    tag = geom.addPoint(x, y, 0)
    point_tags.append(tag)

# Lineas
l1 = geom.addLine(p1, point_tags[0])
l2 = geom.addSpline(point_tags)
l3 = geom.addLine(point_tags[-1], p3)
l4 = geom.addLine(p3, p4)
l5 = geom.addLine(p4, p5)
l6 = geom.addLine(p5, p1)

# Curve loop
cl1 = geom.addCurveLoop([l1, l2, l3, l4, l5, l6])

# Cruvas transfinitas
geom.mesh.setTransfiniteCurve(l1, 51)
geom.mesh.setTransfiniteCurve(l2, 101)
geom.mesh.setTransfiniteCurve(l3, 51)
geom.mesh.setTransfiniteCurve(l4, 201)
geom.mesh.setTransfiniteCurve(l5, 201)
geom.mesh.setTransfiniteCurve(l6, 201)

# Superficie
s1 = geom.addPlaneSurface([cl1])

# Superficie transfinita
geom.mesh.setTransfiniteSurface(s1, cornerTags = [p1, p3, p4, p5])
geom.mesh.setRecombine(2, s1)

# Sincronizar
geom.synchronize()

# # Grupos fisicos
gmsh.model.addPhysicalGroup(2, [s1], 101)
gmsh.model.setPhysicalName(2, 101, "Domain")

gmsh.model.addPhysicalGroup(1, [l6], 101)
gmsh.model.setPhysicalName(1, 101, "Inlet")

gmsh.model.addPhysicalGroup(1, [l4], 102)
gmsh.model.setPhysicalName(1, 102, "Outlet")

gmsh.model.addPhysicalGroup(1, [l1, l2, l3, l5], 103)
gmsh.model.setPhysicalName(1, 103, "Wall")

# Opciones de visualizacion
gmsh.option.setNumber("Mesh.SurfaceFaces", 1)
gmsh.option.setNumber("Mesh.Points", 1)

# Generar malla
gmsh.model.mesh.generate(2)

# Guardar malla
gmsh.write(str(base_dir / "Verification.su2"))

# Mostrar resultado en ventana grafica
#gmsh.fltk.run()

# Finalizar
gmsh.finalize()