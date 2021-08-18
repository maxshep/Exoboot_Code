import exoboot
import config_util
import constants
import numpy as np
import ml_util

exo_list = []
for side in [constants.Side.LEFT, constants.Side.RIGHT]:
    exo_list.append(exoboot.Exo(
        dev_id=None, max_allowable_current=0))
    exo_list[-1].side = side


for i in range(10):
    for exo in exo_list:
        exo.data.accel_x = np.random.rand()
        exo.data.accel_y = np.random.rand()
        exo.data.accel_z = np.random.rand()
        exo.data.gyro_x = np.random.rand()
        exo.data.gyro_y = np.random.rand()
        exo.data.gyro_z = np.random.rand()
        exo.data.ankle_angle = np.random.rand()
        exo.data.ankle_velocity = np.random.rand()
        message = ml_util.get_data_string_for_jetson(
            side=exo.side, data=exo.data)
        print(message)
