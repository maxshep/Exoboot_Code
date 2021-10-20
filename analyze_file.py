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
filename = "20211020_1233_moreswingslack_RIGHT.csv"

df = pd.read_csv(folder + '/' + filename)


plt.figure(2)

# plt.plot(df.loop_time, df.accel_y, 'k-')
myfilt = filters.Butterworth(N=2, Wn=0.1)
filtered_ankle_angle = []
for (ankle_angle, gen_var1) in zip(df.ankle_angle, df.gen_var1):
    if gen_var1 >= 5:
        filtered_ankle_angle.append(myfilt.filter(ankle_angle))
    else:
        filtered_ankle_angle.append(None)
        myfilt.restart()

# plt.plot(df.loop_time, df.ankle_torque_from_current, 'y-')
plt.plot(df.loop_time, df.ankle_angle, 'g-')
plt.plot(df.loop_time, -5*df.did_heel_strike, 'r-')
# plt.plot(df.loop_time, df.gait_phase, 'k-')
plt.plot(df.loop_time, -3*df.did_toe_off, 'b-')
plt.plot(df.loop_time, filtered_ankle_angle, 'b--')

plt.plot(df.loop_time, df.gen_var1, 'b-')
plt.plot(df.loop_time, df.gen_var2, 'k-')
plt.plot(df.loop_time, df.gen_var3, 'r-')
plt.plot(df.loop_time, 0.001*df.slack, 'g--')
plt.plot(df.loop_time, 0.001*df.motor_current, 'm.-')


plt.figure()
plt.plot(df.ankle_angle[2000:3000], df.ankle_torque_from_current[2000:3000])

plt.show()
