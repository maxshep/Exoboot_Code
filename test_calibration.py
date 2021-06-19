import os
import sys
import exoboot
import time
import csv
import util
import constants


def run_constant_torque(exo: exoboot.Exo):
    '''This routine can be used to manually calibrate the relationship
    between ankle and motor angles. Move through the full RoM!!!'''
    exo.update_gains(Kp=constants.DEFAULT_KP, Ki=constants.DEFAULT_KI,
                     Kd=constants.DEFAULT_KD, ff=constants.DEFAULT_FF)

    print('begin!')
    for _ in range(500):
        time.sleep(0.01)
        if exo.data.ankle_angle > 44:
            print('ankle angle too high')
            exo.command_torque(desired_torque=0)
            break
        else:
            exo.command_torque(desired_torque=3)
        exo.read_data()
        exo.write_data()
    print('Done! File saved.')


if __name__ == '__main__':
    exo_list = exoboot.connect_to_exos(file_ID='test_torque_control')
    if len(exo_list) > 1:
        raise ValueError("Just turn on one exo for calibration")
    exo = exo_list[0]
    exo.standing_calibration()
    run_constant_torque(exo=exo)
    exo.close()
