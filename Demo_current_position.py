
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
    exo.read_data()
    t0 = exo.data.state_time
    while True:
        try:
            for _ in range(100):
                exo.command_current(exo.motor_sign*1000)
                time.sleep(0.02)
                exo.read_data()
                exo.write_data()
            print("Current Control",exo.data.state_time-t0)
            for _ in range(100):
                exo.command_slack()
                time.sleep(0.02)
                exo.read_data()
                exo.write_data()
            print("Position Control",exo.data.state_time-t0)
        except KeyboardInterrupt:
            print('Ctrl-C detected, Exiting Gracefully')
            break

    print('Done! File saved.')
    '''Safely close files, stop streaming, optionally saves plots'''
    config_saver.close_file()
    for exo in exo_list:
        exo.close()

if __name__ == '__main__':
    config = config_util.load_config_from_args() 
    file_ID = input(
    'Other than the date, what would you like added to the filename?')
    config_saver = config_util.ConfigSaver(
    file_ID=file_ID, config=config)  # Saves config updates
    exo_list = exoboot.connect_to_exos(file_ID='calibration2',config=config)
    if len(exo_list) > 1:
        raise ValueError("Just turn on one exo for calibration")
    exo = exo_list[0]
    exo.standing_calibration()
    calibrate_encoder_to_ankle_conversion(exo=exo)
    exo.close()