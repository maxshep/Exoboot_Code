'''
This is the main GT program for running the Dephy exos. Read the Readme.
'''

from exo import Exo, connect_to_exos
import threading
import controllers
import state_machines
import gait_state_estimators
import constants
import custom_filters
import time
import sys
import os
import util
import config_util
import parameter_passers
import argparse


file_ID = input(
    'Other than the date, what would you like added to the filename?')

args = config_util.parse_args()  # args passed via command line
config = config_util.load_config(args.config)  # loads config from passed fn
config_saver = config_util.ConfigSaver(
    file_ID=file_ID, config=config)  # Saves config updates

'''Connect to Exos, instantiate Exo objects.'''
exo_list = connect_to_exos(file_ID=file_ID, target_freq=config.TARGET_FREQ,
                           actpack_freq=config.ACTPACK_FREQ, do_read_fsrs=config.DO_READ_FSRS)
print('Battery Voltage: ', 0.001*exo_list[0].get_batt_voltage(), 'V')

'''Prepare empty lists for exos, gait_state_estimators, and state_machines.'''
gait_state_estimator_list = []
controller_list = []

'''Instantiate controllers, link to a state_machine, store state_machines in list.'''
for exo in exo_list:
    controller_list.append(controllers.StandingSlipController(exo=exo))

'''Prep parameter passing.'''
lock = threading.Lock()
quit_event = threading.Event()
new_params_event = threading.Event()
# v0.2,30,0.53,0.62!
# v500!

'''Perform standing calibration.'''
if not config.READ_ONLY:
    for exo in exo_list:
        exo.standing_calibration()

input('Press any key to begin')
print('Start!')

'''Main Loop: Check param updates, Read data, calculate gait state, apply control, write data.'''
timer = util.FlexibleTimer(
    target_freq=config.TARGET_FREQ)  # attempts constants freq
t0 = time.perf_counter()
keyboard_thread = parameter_passers.StandingSlipControllerParameterPasser(
    lock=lock, config=config, quit_event=quit_event, new_params_event=new_params_event)

while True:
    try:
        timer.pause()
        loop_time = time.perf_counter() - t0

        lock.acquire()
        if new_params_event.is_set():
            config_saver.write_data(loop_time=loop_time)  # Update config file
            for controller in controller_list:
                controller.update_pf_setpoint(config.k_val)
            new_params_event.clear()
        if quit_event.is_set():  # If user enters "quit"
            break
        lock.release()

        for exo in exo_list:
            exo.read_data(loop_time=loop_time)
        for controller in controller_list:
            controller.command()
        for exo in exo_list:
            exo.write_data(only_write_if_new=True)
    except KeyboardInterrupt:
        print('Ctrl-C detected, Exiting Gracefully')  # TODO(maxshep) Debug
        break
    except Exception as err:
        print("Unexpected error:", err)
        break

'''Safely close files and stop streaming.'''
config_saver.close_file()
for exo in exo_list:
    exo.close()
print('Done!!!')
