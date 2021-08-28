import pandas as pd
import numpy as np
import ml_util
import exoboot
import constants
import matplotlib.pyplot as plt

df = pd.read_csv('20210727_1253_S01_T04_LEFT_processed.csv')
df['gp_jetson'] = 0
df['ss_jetson'] = 0

jetson_interface = ml_util.JetsonInterface(
    server_ip='192.168.1.2', recv_port=8080)
data_container = exoboot.Exo.DataContainer()

for idx, row in df.iterrows():
    data_container.accel_x = row.accel_x
    data_container.accel_y = row.accel_y
    data_container.accel_z = row.accel_z
    data_container.gyro_x = row.gyro_x
    data_container.gyro_y = row.gyro_y
    data_container.gyro_z = row.gyro_z
    data_container.ankle_angle = row.ankle_angle
    data_container.ankle_velocity = row.ankle_velocity

    jetson_interface.package_and_send_message(
        side=constants.Side.LEFT, data_container=data_container)
    jetson_interface.grab_message_and_parse()
    gp, ss = jetson_interface.get_most_recent_gait_phase(
        side=constants.Side.LEFT)
    df.loc[idx, 'gp_jetson'] = gp
    df.loc[idx, 'ss_jetson'] = ss
    print(gp, ss)
    if idx > 400:
        break


plt.plot(df['gp_jetson'])
plt.plot(df['ss_jetson'])
plt.show()

df.to_csv('test_jetson.csv')
