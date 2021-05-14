import os
import sys
import exoboot
import time
import csv
import util


def calibrate_encoder_to_ankle_conversion(exo: exoboot.Exo):
    '''This routine can be used to manually calibrate the relationship
    between ankle and motor angles. Move through the full RoM!!!'''
    exo.command_current(exo.motor_sign*2000)
    for _ in range(200):
        time.sleep(0.05)
        exo.read_data()
        exo.write_data()
    print('Done! File saved.')


if __name__ == '__main__':
    exo_list = exoboot.connect_to_exos(file_ID='calibration')
    if len(exo_list) > 1:
        raise ValueError("Just turn on one exo for calibration")
    exo = exo_list[0]
    exo.standing_calibration()
    calibrate_encoder_to_ankle_conversion(exo=exo)
    exo.close()
