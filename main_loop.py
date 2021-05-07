'''
This is the main GT program for running the Dephy exos. Read the Readme.
'''

from exo import Exo, connect_to_exo
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


file_ID = input(
    'Other than the date, what would you like added to the filename?')

config = config_util.parse_config_to_use()  # Stores configurable constants
config_saver = config_util.ConfigSaver(
    file_ID=file_ID, config=config)  # Saves config updates

'''Prepare empty lists for exos, gait_state_estimators, and state_machines.'''
exo_list = []
gait_state_estimator_list = []
state_machine_list = []

'''Connect to Exos, instantiate Exo objects.'''
ports, baud_rate = exo.load_ports_and_baud_rate()
for port in ports:
    dev_id = connect_to_exo(port=port, baud_rate=baud_rate,
                            freq=config.ACTPACK_FREQ)
    if dev_id is not None:
        exo_list.append(Exo(dev_id=dev_id, file_ID=file_ID,
                            target_freq=config.TARGET_FREQ,
                            do_read_fsrs=config.DO_READ_FSRS))
if not exo_list:  # (if empty)
    raise RuntimeError('No Exos connected')
print('Battery Voltage: ', exo_list[0].get_batt_voltage(), 'mV')

'''Instantiate gait_state_estimator objects, store in list.'''
for exo in exo_list:
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
        toe_off_detector=toe_off_detector))

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
    elif config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.SAWICKIWICKI:
        stance_controller = controllers.SawickiWickiController(
            exo=exo, k_val=config.k_val)
    state_machine_list.append(state_machines.StanceSwingReeloutReelinStateMachine(exo=exo,
                                                                                  stance_controller=stance_controller,
                                                                                  swing_controller=swing_controller,
                                                                                  reel_in_controller=reel_in_controller,
                                                                                  reel_out_controller=reel_out_controller))


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
if config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.FOURPOINTSPLINE:
    keyboard_thread = parameter_passers.FourPointSplineParameterPasser(
        lock=lock, config=config, quit_event=quit_event, new_params_event=new_params_event)
elif config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.SAWICKIWICKI:
    keyboard_thread = parameter_passers.SawickiWickiParameterPasser(
        lock=lock, config=config, quit_event=quit_event, new_params_event=new_params_event)

while True:
    try:
        timer.pause()
        loop_time = time.perf_counter() - t0

        lock.acquire()
        if new_params_event.is_set():
            config_saver.write_data(loop_time=loop_time)  # Update config file
            if config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.FOURPOINTSPLINE:
                for state_machine in state_machine_list:
                    state_machine.stance_controller.update_spline_with_four_params(rise_fraction=config.RISE_FRACTION,
                                                                                   peak_torque=config.PEAK_TORQUE,
                                                                                   peak_fraction=config.PEAK_FRACTION,
                                                                                   fall_fraction=config.FALL_FRACTION)
            elif config.CONTROL_ARCHITECTURE == config_util.ControlArchitecture.SAWICKIWICKI:
                for state_machine in state_machine_list:
                    state_machine.stance_controller.update_impedance(
                        k_val=config.k_val)
            new_params_event.clear()
        if quit_event.is_set():  # If user enters "quit"
            break
        lock.release()

        for exo in exo_list:
            exo.read_data(loop_time=loop_time)
        for gait_state_estimator in gait_state_estimator_list:
            gait_state_estimator.detect(do_print_heel_strikes=config.PRINT_HS)
        for state_machine in state_machine_list:
            state_machine.step(read_only=config.READ_ONLY)
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
