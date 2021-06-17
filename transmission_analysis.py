import csv
import constants
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy import interpolate
import geomdl
from geomdl import fitting, operations
from geomdl.visualization import VisMPL as vis

# Spline = interpolate.pchip(
#     x=[0, 0.2, 0.53, 0.63], y=[3, 3, 30, 3])
# x = np.arange(0, 0.63, 0.01)
# y = Spline(x)
# plt.plot(x, y)
# plt.ylabel('Torque')
# plt.xlabel('Gait_Phase')
# plt.show()


filename = "20210616_1955_calibration2_RIGHT.csv"
with open(filename) as f:
    left_motor_angle = [int(row["motor_angle"]) for row in csv.DictReader(f)]
with open(filename) as f:
    left_ankle_angle = [np.floor(float(row["ankle_angle"]))
                        for row in csv.DictReader(f)]
left_motor_angle = np.array(left_motor_angle)*constants.ENC_CLICKS_TO_DEG

num_pts_to_use = 100
points = tuple(
    zip(left_ankle_angle[:num_pts_to_use], left_motor_angle[:num_pts_to_use]))
degree = 3
curve = fitting.approximate_curve(
    points=points, degree=degree, ctrlpts_size=20)
# Plot the interpolated curve
evalpts = np.array(curve.evalpts)
ankle_eval = evalpts[:, 0]
motor_eval = evalpts[:, 1]
ctrlpts = np.array(curve.ctrlpts)
pts = np.array(points)
plt.plot(evalpts[:, 0], evalpts[:, 1])
plt.scatter(pts[:, 0], pts[:, 1], color="red")
plt.plot(ctrlpts[:, 0], ctrlpts[:, 1])
plt.show()

left_TR = np.gradient(motor_eval, ankle_eval)
plt.figure()
plt.plot(ankle_eval, left_TR)
plt.show()


'''
filename = "calibration_RIGHT.csv"
with open(filename) as f:
    right_motor_angle = [int(row["motor_angle"]) for row in csv.DictReader(f)]
with open(filename) as f:
    right_ankle_angle = [np.floor(float(row["ankle_angle"]))
                         for row in csv.DictReader(f)]
right_motor_angle = np.array(right_motor_angle)*constants.ENC_CLICKS_TO_DEG

filename = "20210616_1937_calibration2_LEFT.csv"
filename = "calibration_LEFT.csv"
filename = "calibration_RIGHT.csv"
filename = "20210616_1939_calibration2_RIGHT.csv"

# Filter
b, a = signal.butter(N=2, Wn=0.2)
right_motor_angle = signal.filtfilt(b, a, right_motor_angle[20:])
left_motor_angle = signal.filtfilt(b, a, left_motor_angle[20:])
right_ankle_angle = signal.filtfilt(b, a, right_ankle_angle[20:])
left_ankle_angle = signal.filtfilt(b, a, left_ankle_angle[20:])
right_TR = np.gradient(right_motor_angle)/np.gradient(right_ankle_angle)
left_TR = np.gradient(left_motor_angle)/np.gradient(left_ankle_angle)

# Polyfit
p_left = np.polyfit(left_ankle_angle, left_motor_angle, deg=5)
print('Polynomial coefficients for the left: ', p_left)
polyfitted_left_motor_angle = np.polyval(p_left, left_ankle_angle)
p_right = np.polyfit(right_ankle_angle, right_motor_angle, deg=5)
print('Polynomial coefficients for the right: ', p_right)
polyfitted_right_motor_angle = np.polyval(p_right, right_ankle_angle)


plt.figure()
plt.plot(left_ankle_angle, left_motor_angle)
plt.plot(left_ankle_angle, polyfitted_left_motor_angle)
# plt.plot(right_ankle_angle, right_motor_angle)
# plt.plot(right_ankle_angle, polyfitted_right_motor_angle)

plt.xlabel('ankle angle')
plt.ylabel('motor angle')
plt.show()

# plt.figure()
# deriv_left = np.polyder(p_left)
# deriv_right = np.polyder(p_right)
# plt.plot(left_ankle_angle, np.polyval(deriv_left, left_ankle_angle))
# # plt.plot(right_ankle_angle, np.polyval(deriv_right, right_ankle_angle))
# # plt.plot(right_ankle_angle, right_TR)
# plt.plot(left_ankle_angle, left_TR)
# plt.xlim([-50, 80])
# plt.ylim([-22, 22])
# plt.ylabel('Transmission Ratio')
# plt.xlabel('Ankle Angle')
# plt.show()
'''
