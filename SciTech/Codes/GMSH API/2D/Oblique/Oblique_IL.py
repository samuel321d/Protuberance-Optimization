import gmsh
from math import tan
from numpy import deg2rad

# Parametros de la capa limite.
wall_size = 0.005
layer_ratio = 1.15
layer_thickness = 0.05
number_of_layers = 15

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

# Superficie
s1 = geom.addPlaneSurface([cl1])

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

# Sizing
D = gmsh.model.mesh.field.add("Distance")
gmsh.model.mesh.field.setNumbers(D, "CurvesList", [l1, l2, l3])  # en 3D usas SurfacesList

T = gmsh.model.mesh.field.add("Threshold")
gmsh.model.mesh.field.setNumber(T, "InField", D)
gmsh.model.mesh.field.setNumber(T, "SizeMin", 0.01)   # tamaño cerca de la superficie
gmsh.model.mesh.field.setNumber(T, "SizeMax", 0.02)   # tamaño lejos
gmsh.model.mesh.field.setNumber(T, "DistMin", 0.05)   # hasta dónde aplica SizeMin
gmsh.model.mesh.field.setNumber(T, "DistMax", 0.30)   # a partir de dónde aplica SizeMax

gmsh.model.mesh.field.setAsBackgroundMesh(T)

# Cruvas transfinitas
geom.mesh.setTransfiniteCurve(l1, 51)
geom.mesh.setTransfiniteCurve(l2, 101)
geom.mesh.setTransfiniteCurve(l3, 201)
geom.mesh.setTransfiniteCurve(l4, 151)
geom.mesh.setTransfiniteCurve(l5, 201)

# Crear inflation layers
BL = gmsh.model.mesh.field.add("BoundaryLayer")

# Elegir curvas
gmsh.model.mesh.field.setNumbers(BL, "CurvesList", [l1, l2])

# Configurar parametros
gmsh.model.mesh.field.setNumber(BL, "hwall_n", wall_size)
gmsh.model.mesh.field.setNumber(BL, "ratio", layer_ratio)
gmsh.model.mesh.field.setNumber(BL, "thickness", layer_thickness)
gmsh.model.mesh.field.setNumber(BL, "NbLayers", number_of_layers)
gmsh.model.mesh.field.setNumber(BL, "Quads", 1)
gmsh.model.mesh.field.setAsBoundaryLayer(BL)

# Opciones de visualizacion
gmsh.option.setNumber("Mesh.SurfaceFaces", 1)
gmsh.option.setNumber("Mesh.Points", 1)

# Generar malla
gmsh.model.mesh.generate(2)

# Guardar malla
gmsh.write("Oblique_IL.su2")

# Mostrar resultado en ventana grafica
#gmsh.fltk.run()

# Finalizar
gmsh.finalize()