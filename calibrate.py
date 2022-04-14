import os
import sys
import exoboot
import time
import csv
import util
import constants
import config_util


def calibrate_encoder_to_ankle_conversion(exo: exoboot.Exo):
    '''This routine can be used to manually calibrate the relationship
    between ankle and motor angles. Move through the full RoM!!!'''
    exo.update_gains(Kp=constants.DEFAULT_KP, Ki=constants.DEFAULT_KI,
                     Kd=constants.DEFAULT_KD, ff=constants.DEFAULT_FF)
    # exo.command_current(exo.motor_sign*1000)
    print('begin!')
    for _ in range(1000):
        exo.command_current(exo.motor_sign*1000)
        time.sleep(0.02)
        exo.read_data()
        exo.write_data()
    print('Done! File saved.')


if __name__ == '__main__':
    config = config_util.load_config_from_args() 
    exo_list = exoboot.connect_to_exos(file_ID='calibration2',config=config)
    if len(exo_list) > 1:
        raise ValueError("Just turn on one exo for calibration")
    exo = exo_list[0]
    exo.standing_calibration()
    calibrate_encoder_to_ankle_conversion(exo=exo)
    exo.close()