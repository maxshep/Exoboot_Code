import os
import glob
import csv
import constants
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal

folder = 'exo_data/'
filename = "20210618_1448_Rish3_LEFT.csv"

df = pd.read_csv(folder + '/' + filename)


plt.figure()
# plt.plot(df.loop_time, df.heel_fsr)
# plt.plot(df.loop_time, df.toe_fsr)
# plt.plot(df.loop_time, df.ankle_angle)
plt.plot(df.loop_time, df.commanded_current)
plt.plot(df.loop_time, df.motor_current)
# plt.plot(df.loop_time, df.commanded_position*0.001)
# plt.plot(df.loop_time, df.motor_angle*0.001)
plt.plot(df.loop_time, -1*df.did_slip*1000)

filename = "20210618_1448_Rish3_RIGHT.csv"
df = pd.read_csv(folder + '/' + filename)
plt.plot(df.loop_time, df.accel_x*500)


# plt.figure()
# plt.plot(df.loop_time, df.heel_fsr)
# plt.plot(df.loop_time, df.toe_fsr)
# # plt.plot(df.loop_time, df.ankle_angle)
plt.plot(df.loop_time, df.commanded_current)
plt.plot(df.loop_time, df.motor_current)
plt.plot(df.loop_time, df.did_slip*1000)

plt.show()


# plt.figure()
# plt.plot(df.loop_time, df.commanded_current)
# plt.plot(df.loop_time, df.motor_current)
# plt.plot(df.loop_time, df.motor_velocity)

# plt.figure()
# plt.plot(df.loop_time, df.commanded_torque)
# plt.plot(df.loop_time, df.ankle_torque_from_current)
# plt.plot(df.loop_time, df.commanded_current/-1000)
# plt.plot(df.loop_time, df.ankle_velocity/12)
# plt.show()

# plt.legend(['commanded torque', 'measured torque', 'motor velocity'])
# plt.ylabel('Nm')
# plt.xlabel('time (s)')
# plt.show()
