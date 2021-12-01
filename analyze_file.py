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
filename = "20211130_1141_m1_LEFT.csv"

df = pd.read_csv(folder + '/' + filename, usecols=np.arange(23))
# df = pd.read_csv(folder + '/' + filename, usecols=np.arange(22))


plt.figure(2)
[print(col) for col in df.columns]

# # plt.plot(df.loop_time, df.accel_y, 'k-')
# myfilt = filters.Butterworth(N=2, Wn=0.1)
# filtered_ankle_angle = []
# for (ankle_angle, gen_var1) in zip(df.ankle_angle, df.gen_var1):
#     if gen_var1 >= 5:
#         filtered_ankle_angle.append(myfilt.filter(ankle_angle))
#     else:
#         filtered_ankle_angle.append(None)
#         myfilt.restart()

b, a = signal.butter(Wn=0.05, N=2)
print(b, a)
print(df.gait_phase.to_numpy())
gait_phase_filt = signal.lfilter(b, a, df.gait_phase.fillna(0).to_numpy())
plt.plot(df.loop_time, gait_phase_filt, 'r:')
print(gait_phase_filt)


# plt.plot(df.loop_time, df.ankle_torque_from_current, 'y-')
plt.plot(df.loop_time, 0.1*df.commanded_torque, 'y-')

# plt.plot(df.loop_time, df.ankle_angle, 'g-')
plt.plot(df.loop_time, -1.2*df.did_heel_strike, 'r-')
plt.plot(df.loop_time, df.gait_phase, 'k-')
plt.plot(df.loop_time, -1*df.did_toe_off, 'b-')
plt.plot(df.loop_time, 0.9*np.ones_like(df.loop_time), 'k:')
# plt.plot(df.loop_time, filtered_ankle_angle, 'b--')

# plt.plot(df.loop_time, df.gen_var1, 'b-')
# plt.plot(df.loop_time, df.gen_var2, 'k-')
# plt.plot(df.loop_time, df.gen_var3, 'r-')
# plt.plot(df.loop_time, 0.001*df.slack, 'g--')
# plt.plot(df.loop_time, df.did_slip)
# plt.plot(df.loop_time, 0.001*df.commanded_current, 'r-')
# plt.plot(df.loop_time, df.ankle_torque_from_current, 'm--')
# plt.plot(df.loop_time, df.commanded_torque, 'r-')
# plt.plot(df.loop_time, 0.01*df.gyro_z, 'r-')


# plt.figure()
# dt = np.diff(df.loop_time)
# plt.plot(df.loop_time[1:], dt*10)


# plt.plot(df.loop_time, df.did_heel_strike)

# plt.plot(df.loop_time, 0.001*df.motor_current, 'm.-')
# plt.plot(df.loop_time, df.ankle_angle)
# plt.plot(df.loop_time, df.accel_x)
# plt.plot(df.loop_time, df.accel_y)
# plt.plot(df.loop_time, df.accel_z)


plt.show()
