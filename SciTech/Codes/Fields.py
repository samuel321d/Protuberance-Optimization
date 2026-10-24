import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


L = 3240


def dibujar_cilindro_xy(ax, centro_x, semilongitud_x, radio, color, tag):
    rect = Rectangle(
        (centro_x - semilongitud_x, -radio),
        2 * semilongitud_x,
        2 * radio,
        fill=False,
        edgecolor=color,
        label=tag,
    )
    ax.add_patch(rect)


def dibujar_esfera_xy(ax, centro_x, centro_y, radio, color, tag, linestyle="-"):
    circle = Circle(
        (centro_x, centro_y),
        radio,
        fill=False,
        edgecolor=color,
        label=tag,
        linestyle=linestyle,
    )
    ax.add_patch(circle)


fig, ax = plt.subplots(figsize=(12, 8))

# Far-field: bounding box of the sphere + cylinder union in Mesh_3D_w_IL.py.
dibujar_cilindro_xy(ax, 1.5, 13.5, 12, "black", "Far-field extents")

# Axial cylindrical BOIs: center, half-axis length, and radius are normalized by L.
dibujar_cilindro_xy(ax, 1.5, 7, 7, (1.0, 0.0, 0.0), "BOIC1")
dibujar_cilindro_xy(ax, 1.5, 5, 5, (0.9, 0.0, 0.0), "BOIC2")
dibujar_cilindro_xy(ax, 1.5, 4, 3, (0.8, 0.0, 0.0), "BOIC3")
dibujar_cilindro_xy(ax, 1, 2.5, 1, (0.7, 0.0, 0.0), "BOIC4")
dibujar_cilindro_xy(ax, -0.5, 0.6, 0.1, (0.6, 0.0, 0.0), "BOIC5")

# Additional cylinder BOIs.
dibujar_cilindro_xy(ax, 1, 1.3, 0.4, (0.0, 0.3, 0.9), "BOIF1")
dibujar_cilindro_xy(ax, 0.1, 0.3, 0.2, (0.5, 0.5, 0.5), "BOIF2")

rocket_x_min = -3239.353 / L
rocket_x_max = 0.003943 / L
rocket_y_max = 174 / (2*L)

# Rocket bounding box in the XY projection, measured from Rocket.step.
rocket = Rectangle(
    (rocket_x_min, -rocket_y_max),
    rocket_x_max - rocket_x_min,
    2 * rocket_y_max,
    fill=True,
    edgecolor=(0.1, 0.1, 0.1),
    linewidth=2,
    label="Rocket extents",
    zorder=5,
)
ax.add_patch(rocket)

# Protuberance
prot = Rectangle(
    (-0.537, 0.026),
    -0.510 - (-0.537),
    0.033 - 0.026,
    fill=True,
    edgecolor=(0.1, 0.1, 0.1),
    linewidth=2,
    label="Prot",
    zorder=5,
)
ax.add_patch(prot)

# Spherical BOIs and their external transition thickness.
dibujar_esfera_xy(ax, -1, 0, 0.25, (0.0, 0.6, 0.0), "BOIS1")
dibujar_esfera_xy(ax, -1, 0, 0.1, (0.0, 0.8, 0.2), "BOIS2")

ax.set_xlim(-13, 16)
ax.set_ylim(-13, 13)
ax.set_xlabel("X / L")
ax.set_ylabel("Y / L")
ax.set_title("BOIs de Mesh_3D_w_IL.py (vista XY)")
ax.grid(True, linestyle=":", linewidth=0.6)
ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
ax.set_aspect("equal")
fig.tight_layout()
plt.show()
