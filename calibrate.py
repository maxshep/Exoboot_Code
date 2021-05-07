import os
import sys
from exo import Exo
from flexseapython import pyFlexsea, fxUtil
import time
from signal import signal, SIGINT
import csv
import util


def calibrate_encoder_to_ankle_conversion(exo: Exo):
    '''This routine can be used to manually calibrate the relationship
    between ankle and motor angles. Move through the full RoM!!!'''
    exo.command_current(exo.motor_sign*2000)
    for _ in range(200):
        time.sleep(0.05)
        exo.read_data()
        exo.write_data()
    print('Done! File saved.')


if __name__ == '__main__':
    ports, baud_rate = util.load_ports_and_baud_rate_from_com()
    exo = Exo(port=ports[0], baud_rate=baud_rate,
              log_en=False, file_ID='Calibration')
    exo.standing_calibration()

    calibrate_encoder_to_ankle_conversion(exo=exo)
    exo.stop_streaming()
    exo.close()
