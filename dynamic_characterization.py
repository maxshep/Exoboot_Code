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


# Set up GPIO and connect
# set GPIO pin mode to the BCM numbering (same as gpiozero
GPIO.setmode(GPIO.BCM)

# Create an HX711 object and attach it to pin 21 for data and pin 20 for serial clock.
# Vcc is attached to 3.3V and Gnd to Gnd.
# There are multiple gain values for channel A, but we select the default (128).
hx1 = HX711(dout_pin=21, pd_sck_pin=20, gain_channel_A=64, select_channel='A')

# HX711 can read 10 readings/sec, so we take 10 readings over 1 second and average them
for i in range(50):
    time.sleep(0.1)
data = hx1.get_raw_data_mean(readings=1)

if data:
    print('Raw data:', data)
else:
    print('invalid data')

GPIO.cleanup()


# def run_constant_current(exo: exoboot.Exo):
#     '''This routine can be used to manually calibrate the relationship
#     between ankle and motor angles. Move through the full RoM!!!'''
#     exo.update_gains(Kp=constants.DEFAULT_KP, Ki=constants.DEFAULT_KI,
#                      Kd=constants.DEFAULT_KD, ff=constants.DEFAULT_FF)

#     print('begin!')
#     for _ in range(500):
#         time.sleep(0.01)
#         exo.command_torque(desired_torque=3)
#         exo.read_data()
#         exo.write_data()
#     print('Done! File saved.')


# if __name__ == '__main__':
#     exo_list = exoboot.connect_to_exos(file_ID='dyn_char')
#     if len(exo_list) > 1:
#         raise ValueError("Just turn on one exo for calibration")
#     exo = exo_list[0]
#     exo.standing_calibration()
#     run_constant_current(exo=exo)
#     exo.close()
