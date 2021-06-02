import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# folder = 'exo_data/S03_unkempt/'
folder = ''
filename = "20210602_1749S03_T10_RIGHT.csv"

df = pd.read_csv(folder + filename)

# you can use this to get a preview of the data
print(df.head())

# plot the data
plt.figure()
plt.plot(df.loop_time, df.commanded_current)
plt.plot(df.loop_time, df.motor_current)

plt.show()

plt.legend(['commanded torque', 'measured torque'])
plt.ylabel('Nm')
plt.xlabel('time (s)')
