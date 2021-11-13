import os
import glob
import csv
import constants
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal
import filters

folder = 'exo_data/'
filename = "20211109_1448_Spline_Rehab_RIGHT.csv"

df = pd.read_csv(folder + '/' + filename, usecols=np.arange(23))
# df = pd.read_csv(folder + '/' + filename, usecols=np.arange(22))


plt.figure(2)

# # plt.plot(df.loop_time, df.accel_y, 'k-')
# myfilt = filters.Butterworth(N=2, Wn=0.1)
# filtered_ankle_angle = []
# for (ankle_angle, gen_var1) in zip(df.ankle_angle, df.gen_var1):
#     if gen_var1 >= 5:
#         filtered_ankle_angle.append(myfilt.filter(ankle_angle))
#     else:
#         filtered_ankle_angle.append(None)
#         myfilt.restart()

# plt.plot(df.loop_time, df.ankle_torque_from_current, 'y-')
plt.plot(df.loop_time, df.ankle_angle, 'g-')
plt.plot(df.loop_time, -5*df.did_heel_strike, 'r-')
plt.plot(df.loop_time, df.gait_phase, 'k-')
plt.plot(df.loop_time, -3*df.did_toe_off, 'b-')
# plt.plot(df.loop_time, filtered_ankle_angle, 'b--')

# plt.plot(df.loop_time, df.gen_var1, 'b-')
# plt.plot(df.loop_time, df.gen_var2, 'k-')
# plt.plot(df.loop_time, df.gen_var3, 'r-')
# plt.plot(df.loop_time, 0.001*df.slack, 'g--')
# plt.plot(df.loop_time, df.did_slip)
# plt.plot(df.loop_time, 0.001*df.commanded_current, 'r-')
# plt.plot(df.loop_time, df.ankle_torque_from_current, 'm--')
plt.plot(df.loop_time, df.commanded_torque, 'r-')

plt.figure()
dt = np.diff(df.loop_time)
plt.plot(df.loop_time[1:], dt*10)
# plt.plot(df.loop_time, df.did_heel_strike)

# plt.plot(df.loop_time, 0.001*df.motor_current, 'm.-')
# plt.plot(df.loop_time, df.ankle_angle)
# plt.plot(df.loop_time, df.accel_x)
# plt.plot(df.loop_time, df.accel_y)
# plt.plot(df.loop_time, df.accel_z)

plt.show()
