import gmsh
from math import tan
from numpy import deg2rad

# Inicializacion
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.model.add("modelo_1")

# Abreviacion
geom = gmsh.model.geo

# Puntos
p1 = geom.addPoint(0, 0, 0)
p2 = geom.addPoint(0.5, 0, 0)
p3 = geom.addPoint(1.5, tan(deg2rad(13)), 0)
p4 = geom.addPoint(1.5, 0.934195, 0)
p5 = geom.addPoint(0, 0.934195, 0)

# Lineas
l1 = geom.addLine(p1, p2)
l2 = geom.addLine(p2, p3)
l3 = geom.addLine(p3, p4)
l4 = geom.addLine(p4, p5)
l5 = geom.addLine(p5, p1)

# Curve loop
cl1 = geom.addCurveLoop([l1, l2, l3, l4, l5])

# Cruvas transfinitas
geom.mesh.setTransfiniteCurve(l1, 51)
geom.mesh.setTransfiniteCurve(l2, 101)
geom.mesh.setTransfiniteCurve(l3, 201)
geom.mesh.setTransfiniteCurve(l4, 151)
geom.mesh.setTransfiniteCurve(l5, 201)

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

gmsh.model.addPhysicalGroup(1, [l5], 101)
gmsh.model.setPhysicalName(1, 101, "Inlet")

gmsh.model.addPhysicalGroup(1, [l3], 102)
gmsh.model.setPhysicalName(1, 102, "Outlet")

gmsh.model.addPhysicalGroup(1, [l1, l2, l4], 103)
gmsh.model.setPhysicalName(1, 103, "Wall")

# Opciones de visualizacion
gmsh.option.setNumber("Mesh.SurfaceFaces", 1)
gmsh.option.setNumber("Mesh.Points", 1)

# Generar malla
gmsh.model.mesh.generate(2)

# Guardar malla
gmsh.write("Oblique.su2")

# Mostrar resultado en ventana grafica
gmsh.fltk.run()

# Finalizar
gmsh.finalize()