import os
import sys
import exoboot
import time
import csv
import util
import constants
import config_util


config = config_util.load_config_from_args() 
exo_list = exoboot.connect_to_exos(file_ID='calibration2',config=config)
if len(exo_list) > 1:
    raise ValueError("Just turn on one exo for calibration")
exo = exo_list[0]
exo.standing_calibration()
exo.update_gains(Kp=constants.DEFAULT_KP, Ki=constants.DEFAULT_KI,
                    Kd=constants.DEFAULT_KD, ff=constants.DEFAULT_FF)
exo.command_current(exo.motor_sign*1000)
# exo.command_current(exo.motor_sign*1000)
print('begin!')
for _ in range(1000):
    
    time.sleep(0.02)
    exo.read_data()
    exo.write_data()
print('Done! File saved.')
exo.close()