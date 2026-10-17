import gmsh

# Initialize
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.model.add("Cilindro_BL")
geom = gmsh.model.geo

# BL parameters
N = 15
r = 1.15
h0 = 0.01
heights = [h0]
for i in range(1, N):
    heights.append(heights[-1] + h0 * r**i)

# Cylinder
R = 0.5
L = 2.0
cylinder = gmsh.model.occ.addCylinder(0, 0, 0, 0, 0, L, R)

gmsh.model.occ.synchronize()

cyl_surfaces = gmsh.model.getEntities(2)

# Boundary layer
extbl = gmsh.model.geo.extrudeBoundaryLayer([(2, 1), (2, 2)], [1] * N, heights, True)

gmsh.model.geo.synchronize()

# BL top faces
top = []
for i in range(1, len(extbl)):
    if extbl[i][0] == 3:
        top.append(extbl[i-1])

# BL curve loop
bnd = gmsh.model.getBoundary(top)
cl2 = geom.addCurveLoop([c[1] for c in bnd])

# Bounding box
xmin, xmax = -1.5, 1.5
ymin, ymax = -1.5, 1.5
zmin, zmax = 0.0, 4.0

# Symmetry face
p1 = geom.addPoint(xmin, ymin, zmin)
p2 = geom.addPoint(xmax, ymin, zmin)
p3 = geom.addPoint(xmax, ymax, zmin)
p4 = geom.addPoint(xmin, ymax, zmin)
l1 = geom.addLine(p1, p2)
l2 = geom.addLine(p2, p3)
l3 = geom.addLine(p3, p4)
l4 = geom.addLine(p4, p1)

# BL hole
cl3 = geom.addCurveLoop([l1, l2, l3, l4])
s2 = geom.addPlaneSurface([cl3, cl2])

# Upper face
p5 = geom.addPoint(xmin, ymin, zmax)
p6 = geom.addPoint(xmax, ymin, zmax)
p7 = geom.addPoint(xmax, ymax, zmax)
p8 = geom.addPoint(xmin, ymax, zmax)
ls1 = geom.addLine(p5, p6)
ls2 = geom.addLine(p6, p7)
ls3 = geom.addLine(p7, p8)
ls4 = geom.addLine(p8, p5)
cls = geom.addCurveLoop([ls1, ls2, ls3, ls4])
ss = geom.addPlaneSurface([cls])

# Lateral faces
lv1 = geom.addLine(p1, p5)
lv2 = geom.addLine(p2, p6)
lv3 = geom.addLine(p3, p7)
lv4 = geom.addLine(p4, p8)
cll1 = geom.addCurveLoop([l1, lv2, -ls1, -lv1])
cll2 = geom.addCurveLoop([l2, lv3, -ls2, -lv2])
cll3 = geom.addCurveLoop([l3, lv4, -ls3, -lv3])
cll4 = geom.addCurveLoop([l4, lv1, -ls4, -lv4])
sl1 = geom.addPlaneSurface([cll1])
sl2 = geom.addPlaneSurface([cll2])
sl3 = geom.addPlaneSurface([cll3])
sl4 = geom.addPlaneSurface([cll4])

# Surface loop
b = [s[1] for s in top]
b.extend([s2, ss, sl1, sl2, sl3, sl4])
sl = geom.addSurfaceLoop(b)

# Volume
v = geom.addVolume([sl])

geom.synchronize()

# Finalize
gmsh.model.mesh.generate(3)
gmsh.write("BL.msh")
gmsh.finalize()