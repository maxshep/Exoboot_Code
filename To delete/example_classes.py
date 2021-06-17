from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt
spline_x = [0, 0.2, 0.5, 0.6]
spline_y = [2, 2, 5, 2]
spline = interpolate.pchip(spline_x, spline_y, extrapolate=False)
x = np.arange(0, 1, 0.01)
y = spline(x)

plt.figure()
plt.plot(x, y)
plt.show()
print(y)
