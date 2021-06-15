import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# folder = 'exo_data/S03_unkempt/'
folder = 'To delete/'
filename = "20210525_1529fiddle_LEFT.csv"

df = pd.read_csv(folder + filename)

# you can use this to get a preview of the data
# print(df.head())

# # plot the data
# plt.figure()
# plt.plot(df.loop_time, df.commanded_current)
# plt.plot(df.loop_time, df.motor_current)

# plt.show()

# plt.legend(['commanded torque', 'measured torque'])
# plt.ylabel('Nm')
# plt.xlabel('time (s)')

num_of_prev_vals_to_use = 5
list_of_last_n_vals = [0]*num_of_prev_vals_to_use
print(list_of_last_n_vals)
for i in range(10):
    motor_current_right_now = df.motor_current[i]
    list_of_last_n_vals.insert(0, motor_current_right_now)
    list_of_last_n_vals.pop()
    print(list_of_last_n_vals)
