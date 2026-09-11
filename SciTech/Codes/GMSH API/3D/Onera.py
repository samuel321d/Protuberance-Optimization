import gmsh
import math
import os

# =============================================================================
# MALLA 3D DEL ONERA (M6 u otro perfil/ala) A PARTIR DE UN .STP CON INFLATION
# LAYERS, USANDO EL KERNEL OCC (necesario para leer geometria CAD tipo STEP)
# =============================================================================
#
# MODULOS
# gmsh.model.occ      -> geometria via OpenCASCADE (booleanas, importar STEP)
# gmsh.model.mesh      -> malla
# gmsh.model.mesh.field -> campos de tamaño de malla (incluye BoundaryLayer)
#
# IMPORTANTE: ajusta estos parametros a tu geometria real antes de correr.

# --------------------------- PARAMETROS ------------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
archivo_stp = os.path.join(base_dir, "ONERAM6_WING.stp")

if not os.path.exists(archivo_stp):
    raise FileNotFoundError(f"No encuentro el STEP: {archivo_stp}\nCopia el archivo .stp en la misma carpeta que este script o ajusta la ruta.")

# Dominio de campo lejano (caja). Ajusta segun envergadura/cuerda de tu ala.
# Regla de dedo tipica: 10-20 veces la cuerda/envergadura en cada direccion.
dom_x0, dom_y0, dom_z0 = -20, -20, -20   # esquina inferior de la caja
dom_dx, dom_dy, dom_dz =  60,  40,  40   # dimensiones de la caja (largo,ancho,alto)

# Inflation layers (capas de prismas cerca de la pared del ala)
y1          = 0.001   # altura de la primera celda (segun tu y+ objetivo)
n_capas     = 15       # numero de capas de inflacion
razon_crec  = 1.2      # growth ratio entre capas sucesivas
espesor_bl  = y1 * (razon_crec**n_capas - 1) / (razon_crec - 1)  # espesor total aprox.

tm_lejano   = 5.0   # tamaño de malla lejos del ala (en el dominio exterior)
tm_cerca    = 0.05  # tamaño de malla en la superficie del ala (sin contar la BL)

# ------------------------- INICIALIZAR --------------------------------------
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.model.add("onera_dominio")

# --------------------- IMPORTAR GEOMETRIA STEP ------------------------------
# importShapes devuelve una lista de tuplas (dim, tag) de todas las entidades
# importadas (usualmente un solido si el STEP viene cerrado/watertight, o
# superficies si viene como shell abierto).
entidades_importadas = gmsh.model.occ.importShapes(archivo_stp)
gmsh.model.occ.synchronize()

print("Entidades importadas del STEP:", entidades_importadas)

# Si el STEP importa como VOLUMEN (solido cerrado, dim=3), lo usamos tal cual
# como la herramienta de corte. Si importa solo como SUPERFICIES (dim=2),
# hay que coserlas en un volumen antes de la operacion booleana.
vols_ala = [e for e in entidades_importadas if e[0] == 3]

if not vols_ala:
    # Geometria vino como shell/superficies sueltas: intentar coser y formar
    # un volumen solido cerrado a partir de las superficies importadas.
    supers_ala = [e for e in entidades_importadas if e[0] == 2]
    surface_loop = gmsh.model.occ.addSurfaceLoop([s[1] for s in supers_ala])
    vol_tag = gmsh.model.occ.addVolume([surface_loop])
    gmsh.model.occ.synchronize()
    vols_ala = [(3, vol_tag)]

# --------------------- DOMINIO DE CAMPO LEJANO -------------------------------
caja_tag = gmsh.model.occ.addBox(dom_x0, dom_y0, dom_z0, dom_dx, dom_dy, dom_dz)
gmsh.model.occ.synchronize()

# --------------------- OPERACION BOOLEANA: CAJA - ALA ------------------------
# El fluido es la caja con el ala "restada" (el ala queda como cavidad/hueco).
dominio_fluido, _ = gmsh.model.occ.cut(
    [(3, caja_tag)],   # objeto (caja)
    vols_ala,          # herramienta a restar (el ala)
    removeObject=True,
    removeTool=True,
)
gmsh.model.occ.synchronize()

# --------------------- IDENTIFICAR SUPERFICIES --------------------------------
# Tras la resta booleana, gmsh crea nuevas superficies. Hay que distinguir:
#   - las 6 caras planas de la caja original (campo lejano / farfield)
#   - la(s) superficie(s) curvas del ala (pared / wall)
# Un criterio simple: las caras del farfield son PLANAS (curvatura ~0) y
# quedan justo en los limites x0/x0+dx, y0/y0+dy, z0/z0+dz de la caja.

todas_superficies = gmsh.model.getEntities(2)

superficies_farfield = []
superficies_ala = []

tol = 1e-6
limites_x = (dom_x0, dom_x0 + dom_dx)
limites_y = (dom_y0, dom_y0 + dom_dy)
limites_z = (dom_z0, dom_z0 + dom_dz)

for dim, tag in todas_superficies:
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
    es_farfield = (
        abs(xmin - limites_x[0]) < tol or abs(xmax - limites_x[1]) < tol or
        abs(ymin - limites_y[0]) < tol or abs(ymax - limites_y[1]) < tol or
        abs(zmin - limites_z[0]) < tol or abs(zmax - limites_z[1]) < tol
    )
    if es_farfield:
        superficies_farfield.append(tag)
    else:
        superficies_ala.append(tag)

print("Superficies de farfield (dominio exterior):", superficies_farfield)
print("Superficies del ala (pared):", superficies_ala)

# --------------------- GRUPOS FISICOS -----------------------------------------
gmsh.model.addPhysicalGroup(2, superficies_ala, 201)
gmsh.model.setPhysicalName(2, 201, "ala_wall")

gmsh.model.addPhysicalGroup(2, superficies_farfield, 202)
gmsh.model.setPhysicalName(2, 202, "farfield")

gmsh.model.addPhysicalGroup(3, [dominio_fluido[0][1]], 203)
gmsh.model.setPhysicalName(3, 203, "fluido")

# --------------------- TAMAÑOS DE MALLA (sin BL) -------------------------------
campo_dist = gmsh.model.mesh.field.add("Distance")
gmsh.model.mesh.field.setNumbers(campo_dist, "SurfacesList", superficies_ala)

campo_thr = gmsh.model.mesh.field.add("Threshold")
gmsh.model.mesh.field.setNumber(campo_thr, "InField", campo_dist)
gmsh.model.mesh.field.setNumber(campo_thr, "SizeMin", tm_cerca)
gmsh.model.mesh.field.setNumber(campo_thr, "SizeMax", tm_lejano)
gmsh.model.mesh.field.setNumber(campo_thr, "DistMin", espesor_bl)
gmsh.model.mesh.field.setNumber(campo_thr, "DistMax", dom_dx / 4)

gmsh.model.mesh.field.setAsBackgroundMesh(campo_thr)

# --------------------- CAPA LIMITE 3D (estrategia A) --------------------------
# En Gmsh 4.x la API de 'mesh.field' no soporta bien BL 3D para este caso.
# La forma robusta es usar extrudeBoundaryLayer() sobre las superficies del ala.
# Esto genera prismas de pared con altura geométrica, útiles para una simulacion
# con objetivo y+ ~ 1.
heights_bl = [y1 * (razon_crec ** i) for i in range(n_capas)]

gmsh.model.geo.extrudeBoundaryLayer(
    [(2, s) for s in superficies_ala],
    numElements=[1] * n_capas,
    heights=heights_bl,
    recombine=True,
)
gmsh.model.geo.synchronize()

# --------------------- GENERAR MALLA 3D ----------------------------------------
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)  # mejor compatibilidad externa
gmsh.model.mesh.generate(3)

gmsh.write("Onera.cgns")

# Descomenta la siguiente linea SOLO si tienes entorno grafico funcional
# (recuerda: en WSL con el bug de WSLg esto va a fallar - genera el .msh
# y visualizalo con ParaView/Gmsh nativo de Windows en su lugar)
# gmsh.fltk.run()

gmsh.finalize()

print(f"\nEspesor total aproximado de la capa limite: {espesor_bl:.4f}")
print("Malla guardada como 3_Malla_ONERA.msh")