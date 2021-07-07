import os
import glob
import csv
import constants
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal

folder = 'exo_data/'
filename = "20210702_1513_test5pt2_RIGHT.csv"

df = pd.read_csv(folder + '/' + filename)


# plt.figure()
# # plt.plot(df.loop_time, df.heel_fsr)
# # plt.plot(df.loop_time, df.toe_fsr)
# # plt.plot(df.loop_time, df.ankle_angle)
# plt.plot(df.loop_time, df.commanded_current)
# plt.plot(df.loop_time, df.motor_current)
# # plt.plot(df.loop_time, df.commanded_position*0.001)
# # plt.plot(df.loop_time, df.motor_angle*0.001)
# plt.plot(df.loop_time, -1*df.did_slip*1000)


plt.figure(2)
plt.plot(df.loop_time, df.commanded_torque, marker='o')
plt.show()


# plt.figure()
# plt.plot(df.loop_time, df.accel_x)
# plt.plot(df.loop_time, df.accel_y, 'k-')
# plt.plot(df.loop_time, df.accel_z, 'k-')
# plt.plot(df.loop_time, df.gen_var1, 'b--')
# plt.plot(df.loop_time, df.gen_var2, 'k--')
# plt.plot(df.loop_time, df.gen_var3, 'k--')

plt.show()
