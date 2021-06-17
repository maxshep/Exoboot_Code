from geomdl import fitting
from geomdl.visualization import VisMPL as vis
import numpy as np
import matplotlib.pyplot as plt

# The NURBS Book Ex9.1
points = ((0, 0), (3, 4), (-1, 4), (-4, 0), (-4, -3))
degree = 3  # cubic curve

# Do global curve approximation
curve = fitting.approximate_curve(points, degree)

# # Visualize data and evaluated points together
evalpts = np.array(curve.evalpts)
pts = np.array(points)
plt.plot(evalpts[:, 0], evalpts[:, 1])
plt.scatter(pts[:, 0], pts[:, 1], color="red")
plt.show()
