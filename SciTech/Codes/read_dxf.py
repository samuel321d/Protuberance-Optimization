import ezdxf
import numpy as np
import matplotlib.pyplot as plt

doc = ezdxf.readfile("Rocket_points.dxf")
msp = doc.modelspace()

points = []
print(msp)
for entity in msp:

    # ----------------
    # LINE 
    # ----------------
    if entity.dxftype() == "LINE":

        p1 = entity.dxf.start
        p2 = entity.dxf.end

        points.append((p1.x, p1.y))
        points.append((p2.x, p2.y))

    # ----------------
    # ARC
    # ----------------
    elif entity.dxftype() == "ARC":

        center = entity.dxf.center
        radius = entity.dxf.radius

        theta1 = np.deg2rad(entity.dxf.start_angle)
        theta2 = np.deg2rad(entity.dxf.end_angle)

        theta = np.linspace(theta1, theta2, 50)

        for t in theta:
            x = center.x + radius * np.cos(t)
            y = center.y + radius * np.sin(t)

            points.append((x, y))

    # ----------------
    # SPLINE
    # ----------------
    elif entity.dxftype() == "SPLINE":

        spline_points = entity.flattening(0.01)

        for p in spline_points:
            points.append((p.x, p.y))


points = np.array(points)
print(points[:3])

#xy =points[:,:2]

plt.figure()
plt.plot(points[:,0], points[:,1], ".-")
plt.axis("equal")
plt.grid()
plt.show()
