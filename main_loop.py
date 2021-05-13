'''
This is the main GT program for running the Dephy exos. Read the Readme.
'''

import exoboot
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
import perturbation_detectors


file_ID = input(
    'Other than the date, what would you like added to the filename?')

args = config_util.parse_args()  # args passed via command line
config = config_util.load_config(args.config)  # loads config from passed fn
config_saver = config_util.ConfigSaver(
    file_ID=file_ID, config=config)  # Saves config updates

'''Connect to Exos, instantiate Exo objects.'''
exo_list = exoboot.connect_to_exos(file_ID=file_ID, target_freq=config.TARGET_FREQ,
                                   actpack_freq=config.ACTPACK_FREQ, do_read_fsrs=config.DO_READ_FSRS)
print('Battery Voltage: ', 0.001*exo_list[0].get_batt_voltage(), 'V')

'''Prepare empty lists for exos, gait_state_estimators, and state_machines.'''
gait_state_estimator_list = []
state_machine_list = []

'''Instantiate gait_state_estimator objects, store in list.'''
for exo in exo_list:
    if (config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.FOURPOINTSPLINE or
            config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.SAWICKIWICKI):
        heel_strike_detector = gait_state_estimators.GyroHeelStrikeDetector(
            height=config.HS_GYRO_THRESHOLD,
            gyro_filter=custom_filters.Butterworth(N=config.HS_GYRO_FILTER_N,
                                                   Wn=config.HS_GYRO_FILTER_WN,
                                                   fs=config.TARGET_FREQ),
            delay=config.HS_GYRO_DELAY)
        gait_phase_estimator = gait_state_estimators.StrideAverageGaitPhaseEstimator()
        toe_off_detector = gait_state_estimators.GaitPhaseBasedToeOffDetector(
            fraction_of_gait=config.TOE_OFF_FRACTION)
        gait_state_estimator_list.append(gait_state_estimators.GaitStateEstimator(
            side=exo.side,
            data_container=exo.data,
            heel_strike_detector=heel_strike_detector,
            gait_phase_estimator=gait_phase_estimator,
            toe_off_detector=toe_off_detector,
            do_print_heel_strikes=config.PRINT_HS))
    elif config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.STANDINGPERTURBATION:
        gait_state_estimator_list.append(
            perturbation_detectors.SlipDetectorAP(data_container=exo.data, acc_threshold_x=0.7,
                                                  time_out=2, max_acc_y=0.5, max_acc_z=0.5))

'''Instantiate controllers, link to a state_machine, store state_machines in list.'''
for exo in exo_list:
    reel_in_controller = controllers.BallisticReelInController(
        exo=exo, time_out=config.REEL_IN_TIMEOUT)
    swing_controller = controllers.StalkController(
        exo=exo, desired_slack=config.SWING_SLACK)
    reel_out_controller = controllers.SoftReelOutController(
        exo=exo, desired_slack=config.SWING_SLACK)
    if config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.FOURPOINTSPLINE:
        stance_controller = controllers.FourPointSplineController(
            exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
            peak_fraction=config.PEAK_FRACTION,
            fall_fraction=config.FALL_FRACTION,
            bias_torque=config.SPLINE_BIAS)
        state_machine_list.append(state_machines.StanceSwingReeloutReelinStateMachine(exo=exo,
                                                                                      stance_controller=stance_controller,
                                                                                      swing_controller=swing_controller,
                                                                                      reel_in_controller=reel_in_controller,
                                                                                      reel_out_controller=reel_out_controller))
    elif config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.SAWICKIWICKI:
        stance_controller = controllers.SawickiWickiController(
            exo=exo, k_val=config.K_VAL)
        state_machine_list.append(state_machines.StanceSwingReeloutReelinStateMachine(exo=exo,
                                                                                      stance_controller=stance_controller,
                                                                                      swing_controller=swing_controller,
                                                                                      reel_in_controller=reel_in_controller,
                                                                                      reel_out_controller=reel_out_controller))

    elif config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.STANDINGPERTURBATION:
        slip_controller = controllers.GenericImpedanceController(
            exo=exo, setpoint=config.SET_POINT, k_val=config.K_VAL)
        standing_controller = controllers.GenericImpedanceController(
            exo=exo, setpoint=10, k_val=200)
        state_machine_list.append(state_machines.StandingPerturbationResponse(exo=exo,
                                                                              standing_controller=standing_controller,
                                                                              slip_controller=slip_controller))


'''Prep parameter passing.'''
lock = threading.Lock()
quit_event = threading.Event()
new_params_event = threading.Event()
# v0.2,30,0.53,0.62!
# k500!

'''Perform standing calibration.'''
if not config.READ_ONLY:
    for exo in exo_list:
        exo.standing_calibration()
else:
    print('Not calibrating... READ_ONLY = True in config')

input('Press any key to begin')
print('Start!')

'''Main Loop: Check param updates, Read data, calculate gait state, apply control, write data.'''
timer = util.FlexibleTimer(
    target_freq=config.TARGET_FREQ)  # attempts constants freq
t0 = time.perf_counter()
keyboard_thread = parameter_passers.ParameterPasser(
    lock=lock, config=config, quit_event=quit_event, new_params_event=new_params_event)

while True:
    try:
        timer.pause()
        loop_time = time.perf_counter() - t0

        lock.acquire()
        if new_params_event.is_set():
            config_saver.write_data(loop_time=loop_time)  # Update config file
            for state_machine in state_machine_list:
                state_machine.update_ctrl_params_from_config(config)
            new_params_event.clear()
        if quit_event.is_set():  # If user enters "quit"
            break
        lock.release()

        for exo in exo_list:
            exo.read_data(loop_time=loop_time)
        for gait_state_estimator in gait_state_estimator_list:
            gait_state_estimator.detect()
        for state_machine in state_machine_list:
            state_machine.step(read_only=config.READ_ONLY)
        for exo in exo_list:
            exo.write_data(only_write_if_new=not config.READ_ONLY)
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
