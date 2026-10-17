import gmsh

# Inicializar
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.model.add("Cubo")
geom = gmsh.model.geo

# Puntos
p1 = geom.addPoint(0, 0, 0)
p2 = geom.addPoint(1, 0, 0)
p3 = geom.addPoint(1, 1, 0)
p4 = geom.addPoint(0, 1, 0)
p5 = geom.addPoint(0, 0, 1)
p6 = geom.addPoint(1, 0, 1)
p7 = geom.addPoint(1, 1, 1)
p8 = geom.addPoint(0, 1, 1)

# Lineas
li1 = geom.addLine(p1, p2)
li2 = geom.addLine(p2, p3)
li3 = geom.addLine(p3, p4)
li4 = geom.addLine(p4, p1)
ls1 = geom.addLine(p5, p6)
ls2 = geom.addLine(p6, p7)
ls3 = geom.addLine(p7, p8)
ls4 = geom.addLine(p8, p5)
l1 = geom.addLine(p1, p5)
l2 = geom.addLine(p2, p6)
l3 = geom.addLine(p3, p7)
l4 = geom.addLine(p4, p8)

# Curve loops
cli = geom.addCurveLoop([li1, li2, li3, li4])
cls = geom.addCurveLoop([ls1, ls2, ls3, ls4])
cll1 = geom.addCurveLoop([li1, l2, -ls1, -l1])
cll2 = geom.addCurveLoop([li2, l3, -ls2, -l2])
cll3 = geom.addCurveLoop([li3, l4, -ls3, -l3])
cll4 = geom.addCurveLoop([li4, l1, -ls4, -l4])

# Superficies
si = geom.addPlaneSurface([cli])
ss = geom.addPlaneSurface([cls])
sl1 = geom.addPlaneSurface([cll1])
sl2 = geom.addPlaneSurface([cll2])
sl3 = geom.addPlaneSurface([cll3])
sl4 = geom.addPlaneSurface([cll4])

# Surface loop
sloop = geom.addSurfaceLoop([si, ss, sl1, sl2, sl3, sl4])

# Volumen
v = geom.addVolume([sloop])

# Sincronizar
geom.synchronize()

# Parametros de la capa limite
N = 5
r = 1.2
h0 = 0.01

# Calcular alturas
heights = [h0]
for i in range(1, N):
    heights.append(heights[-1] + h0 * r**i)

# Extruir capas
extbl = geom.extrudeBoundaryLayer([(2, si)], [1] * N, heights, True)

# Sincronizar
geom.synchronize()

# Generar malla
gmsh.model.mesh.generate(3)

# Guardar malla
gmsh.write("Cube1.cgns")

# Finalizar
gmsh.finalize()