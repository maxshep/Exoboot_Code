import os
import glob
import csv
import constants
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

folder = 'exo_data'
filename = "exo_data/20210323_1233testlevels_RIGHT.csv"

df = pd.read_csv(filename)


plt.figure()
plt.plot(df.loop_time, df.did_heel_strike)
plt.plot(df.loop_time, df.gait_phase)
plt.plot(df.loop_time, df.ankle_angle)
plt.plot(df.loop_time, df.ankle_torque_from_current)
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
