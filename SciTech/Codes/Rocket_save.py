import ezdxf
import numpy as np
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
# Read rocket surface
path = Path(__file__).with_name("Rocket_points.dxf")
doc = ezdxf.readfile(path)
msp = doc.modelspace()

# =================================================================
# Function to identify upper and lower points on rocket surface
# =================================================================

def classify_point(x, y, points_up, points_down):
    if y >= 0:
        points_up.append((x, y))
    else:
        points_down.append((x, y))
# =================================================================



points = []

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
        
        theta = np.linspace(theta1, theta2, 32)
        
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

n_points = len(points)
print(n_points)
rocket_coords = points[:int(n_points/2 -2)]
print(f"Inicial:{rocket_coords[0]}")
print(f"Penultimo:{rocket_coords[-2]}")
print(f"FInal:{rocket_coords[-1]}")

np.savetxt(Path(__file__).with_name("Rocket_points.txt"), rocket_coords, delimiter = ",", newline = "\n")

points_plot = pd.read_csv("Rocket_points.txt", header = None)
points_plot.columns = ["x", "y"]

