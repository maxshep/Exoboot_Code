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
filename = "DDMtest.csv"

# df = pd.read_csv(folder + '/' + filename)
df = pd.read_pickle(folder + '/' + filename)
# df = pd.read_csv(folder + '/' + filename, usecols=np.arange(22))

print(df.head())
# [print(col_name) for col_name in df.columns]
plt.figure()
plt.plot(df['imu.RIGHT-FOOT-IMUSOURCE_INSOLE.linear.y'])
plt.plot(df['imu.RIGHT-SHANK-IMUSOURCE_STAND_ALONE.linear.y'])
plt.plot(df['imu.RIGHT-THIGH-IMUSOURCE_STAND_ALONE.linear.y'])


# plt.plot(df['gait_state.LEFT-UNSPECIFIED_METHOD.gait_phase'])
# plt.plot(df['gait_state.LEFT-UNSPECIFIED_METHOD.is_stance'])
# plt.plot(df['gait_state.LEFT-UNSPECIFIED_METHOD.is_swing'])
# plt.plot(0.001*df['insole.LEFT-MOTICON.total_force'])

plt.show()
