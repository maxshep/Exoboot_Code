import csv
import constants
import numpy as np
import matplotlib.pyplot as plt

filename = "calibration_LEFT.csv"
with open(filename) as f:
    left_motor_angle = [int(row["motor_angle"]) for row in csv.DictReader(f)]
with open(filename) as f:
    left_ankle_angle = [np.floor(float(row["ankle_angle"]))
                        for row in csv.DictReader(f)]
p_left = np.polyfit(left_ankle_angle, left_motor_angle, deg=5)
print('Polynomial coefficients for the left: ', p_left)
polyfitted_left_motor_angle = np.polyval(p_left, left_ankle_angle)

filename = "calibration_RIGHT.csv"
with open(filename) as f:
    right_motor_angle = [int(row["motor_angle"]) for row in csv.DictReader(f)]
with open(filename) as f:
    right_ankle_angle = [np.floor(float(row["ankle_angle"]))
                         for row in csv.DictReader(f)]
p_right = np.polyfit(right_ankle_angle, right_motor_angle, deg=5)
print('Polynomial coefficients for the right: ', p_right)
polyfitted_right_motor_angle = np.polyval(p_right, right_ankle_angle)

plt.figure()
plt.plot(left_ankle_angle, left_motor_angle)
plt.plot(left_ankle_angle, polyfitted_left_motor_angle)
plt.plot(right_ankle_angle, right_motor_angle)
plt.plot(right_ankle_angle, polyfitted_right_motor_angle)
plt.xlabel('ankle angle')
plt.ylabel('motor angle')
plt.show()

plt.figure()
deriv_left = np.polyder(p_left)
deriv_right = np.polyder(p_right)
plt.plot(left_ankle_angle, np.polyval(deriv_left, left_ankle_angle))
plt.plot(right_ankle_angle, np.polyval(deriv_right, right_ankle_angle))

plt.show()
