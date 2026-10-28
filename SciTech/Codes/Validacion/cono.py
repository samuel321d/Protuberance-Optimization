import math

import gmsh


# Dimensiones del dominio cilíndrico y parámetros del cono (en unidades coherentes).
RADIO_CILINDRO = 1.0
ALTURA_CILINDRO = 2.0
ANGULO_CONO_GRADOS = 25.0  # Ángulo entre el eje y la generatriz del cono.

# El tamaño de elemento cambia de TAMANO_MIN a TAMANO_MAX entre ambas distancias.
TAMANO_MIN = 0.03
TAMANO_MAX = 0.15
DISTANCIA_MIN = 0.05
DISTANCIA_MAX = 0.40
ARCHIVO_MALLA = "cono_cilindro.msh"


gmsh.initialize()
gmsh.model.add("cilindro_refinado_cerca_del_cono")
occ = gmsh.model.occ

occ.addCylinder(0, 0, 0, 0, 0, ALTURA_CILINDRO, RADIO_CILINDRO)
radio_cono = 0.9*ALTURA_CILINDRO * math.tan(math.radians(ANGULO_CONO_GRADOS))
cono = occ.addCone(0, 0, 0, 0, 0, 0.9*ALTURA_CILINDRO, 0, radio_cono)
occ.synchronize()

# Guardar la cara lateral del cono como superficie de referencia.
caras_cono = gmsh.model.getBoundary([(3, cono)], oriented=False)
superficies = [
    tag
    for dim, tag in caras_cono
    if dim == 2 and gmsh.model.getType(dim, tag) == "Cone"
]
if not superficies:
    raise RuntimeError("No se encontró la superficie cónica de referencia.")

# El cono solo define la distancia; el dominio mallado es el cilindro.
occ.remove([(3, cono)], recursive=False)
occ.synchronize()

campo_distancia = gmsh.model.mesh.field.add("Distance")
gmsh.model.mesh.field.setNumbers(
    campo_distancia, "SurfacesList", superficies
)
gmsh.model.mesh.field.setNumber(campo_distancia, "Sampling", 100)

campo_umbral = gmsh.model.mesh.field.add("Threshold")
gmsh.model.mesh.field.setNumber(campo_umbral, "InField", campo_distancia)
gmsh.model.mesh.field.setNumber(campo_umbral, "SizeMin", TAMANO_MIN)
gmsh.model.mesh.field.setNumber(campo_umbral, "SizeMax", TAMANO_MAX)
gmsh.model.mesh.field.setNumber(campo_umbral, "DistMin", DISTANCIA_MIN)
gmsh.model.mesh.field.setNumber(campo_umbral, "DistMax", DISTANCIA_MAX)
gmsh.model.mesh.field.setAsBackgroundMesh(campo_umbral)

gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
gmsh.model.mesh.generate(3)
gmsh.write(ARCHIVO_MALLA)
gmsh.fltk.run()
gmsh.finalize()


