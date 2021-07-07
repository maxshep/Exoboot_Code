import os
import sys
import exoboot
import time
import csv
import util
import constants
import time


import RPi.GPIO as GPIO  # import GPIO, in the future use gpiozero module
from hx711 import HX711  # import the class HX711
from hx711 import outliers_filter


def setup_GPIO():
    GPIO.setmode(GPIO.BCM)


def read_load_cell_data():
    data = hx1.get_raw_data_mean(readings=1)
    if data:
        return data
    else:
        return None
        # print('invalid data')


def close_GPIO():
    GPIO.cleanup()


def run_test(exo: exoboot.Exo):
    '''This routine can be used to manually calibrate the relationship
    between ankle and motor angles. Move through the full RoM!!!'''
    exo.update_gains(Kp=constants.DEFAULT_KP, Ki=constants.DEFAULT_KI,
                     Kd=constants.DEFAULT_KD, ff=constants.DEFAULT_FF)

    print('begin!')
    for _ in range(500):
        time.sleep(0.01)
        exo.command_torque(desired_torque=3)
        exo.read_data()
        load_cell_data = read_load_cell_data()
        exo.gen_var1 = load_cell_data
        exo.write_data()
    print('Done! File saved.')


if __name__ == '__main__':
    setup_GPIO()
    hx1 = HX711(dout_pin=21, pd_sck_pin=20,
                gain_channel_A=64, select_channel='A')
    exo_list = exoboot.connect_to_exos(file_ID='dyn_char')
    if len(exo_list) > 1:
        raise ValueError("Just turn on one exo for calibration")
    exo = exo_list[0]
    exo.standing_calibration()
    run_test(exo=exo)
    exo.close()
    close_GPIO()
