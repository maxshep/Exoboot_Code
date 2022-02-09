import os
import glob
import csv
import constants
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal
import filters
from collections import deque

folder = 'exo_data/'
filename = "20220106_1205_swingslack3000_LEFT.csv"

df = pd.read_csv(folder + '/' + filename, usecols=np.arange(23))

plt.figure(1)

plt.plot(df.loop_time, df.ankle_angle, 'g-', label='ankle-angle')
plt.plot(df.loop_time, 5*df.did_heel_strike, 'r-',label='heel_strike')
plt.plot(df.loop_time, df.gait_phase, 'k-', label='gait_phase')
plt.plot(df.loop_time, 3*df.did_toe_off, 'b-', label = 'toe_off')
plt.plot(df.loop_time, df.commanded_torque, 'm-', label = 'commanded torque')
plt.plot(df.loop_time, -df.commanded_position/1000, 'y-',label='commanded position' )

plt.legend()

plt.figure(2)
# plt.plot(df.loop_time, 0.001*df.motor_current, 'm.-',label='motor_current')
plt.plot(df.loop_time, df.ankle_angle, 'g-', label='ankle-angle')
plt.plot(df.loop_time, 5*df.did_heel_strike, 'r-',label='heel_strike')
# plt.plot(df.loop_time, df.ankle_angle)
# plt.plot(df.loop_time, df.accel_x, label='acc x')
# plt.plot(df.loop_time, df.accel_y, label='acc y')
plt.plot(df.loop_time, df.accel_z,'b-', label='acc z')
plt.plot(df.loop_time, df.gyro_z/100, label='gyro z')
plt.legend()

plt.figure(3)
myfilt = filters.Butterworth(N=2, Wn=3, fs = 175)
heelstrike = []
gyro_history = deque([0, 0, 0], maxlen=3)
filtered_gyro = []
# flag = False
for gyro_z in df.gyro_z:
    fitered = -myfilt.filter(gyro_z)
        
    filtered_gyro.append(fitered)
    gyro_history.appendleft(fitered)
    # if (gyro_history[1] < -150 and
    #         gyro_history[1] < gyro_history[0] and
    #             gyro_history[1] < gyro_history[2]):
    #             flag = True
    if (gyro_history[1] > 100 and
            gyro_history[1] > gyro_history[0] and
                gyro_history[1] > gyro_history[2]):
                heelstrike.append(1)
                # flag = False
    else:
        heelstrike.append(0)
    
plt.plot(df.loop_time, np.array(heelstrike)*6,'g-', label='calculated heelstrike')
plt.plot(df.loop_time, 5*df.did_heel_strike, 'r-',label='heel_strike')
# plt.plot(df.loop_time, df.gyro_z/100, label='gyro z')
plt.plot(df.loop_time, df.accel_z,'b-', label='acc z')
plt.plot(df.loop_time, np.array(filtered_gyro)/100, label='filtered gyro z')
plt.legend()

plt.show()
##################
# # # plt.plot(df.loop_time, df.accel_y, 'k-')
# # myfilt = filters.Butterworth(N=2, Wn=0.1)
# # filtered_ankle_angle = []
# # for (ankle_angle, gen_var1) in zip(df.ankle_angle, df.gen_var1):
# #     if gen_var1 >= 5:
# #         filtered_ankle_angle.append(myfilt.filter(ankle_angle))
# #     else:
# #         filtered_ankle_angle.append(None)
# #         myfilt.restart()

# # plt.plot(df.loop_time, df.ankle_torque_from_current, 'y-')
# plt.plot(df.loop_time, df.ankle_angle, 'g-')
# plt.plot(df.loop_time, -5*df.did_heel_strike, 'r-')
# plt.plot(df.loop_time, df.gait_phase, 'k-')
# plt.plot(df.loop_time, -3*df.did_toe_off, 'b-')
# # plt.plot(df.loop_time, filtered_ankle_angle, 'b--')

# # plt.plot(df.loop_time, df.gen_var1, 'b-')
# # plt.plot(df.loop_time, df.gen_var2, 'k-')
# # plt.plot(df.loop_time, df.gen_var3, 'r-')
# # plt.plot(df.loop_time, 0.001*df.slack, 'g--')
# # plt.plot(df.loop_time, df.did_slip)
# # plt.plot(df.loop_time, 0.001*df.commanded_current, 'r-')
# # plt.plot(df.loop_time, df.ankle_torque_from_current, 'm--')
# plt.plot(df.loop_time, df.commanded_torque, 'r-')

# plt.figure()
# dt = np.diff(df.loop_time)
# plt.plot(df.loop_time[1:], dt*10)
# # plt.plot(df.loop_time, df.did_heel_strike)

# # plt.plot(df.loop_time, 0.001*df.motor_current, 'm.-')
# # plt.plot(df.loop_time, df.ankle_angle)
# # plt.plot(df.loop_time, df.accel_x)
# # plt.plot(df.loop_time, df.accel_y)
# # plt.plot(df.loop_time, df.accel_z)

# plt.show()
