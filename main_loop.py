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
import util
import config_util
import parameter_passers
import control_muxer


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

'''Instantiate gait_state_estimator objects, store in list.'''
gait_state_estimator_list = []
state_machine_list = []
for exo in exo_list:
    gait_state_estimator_list.append(
        control_muxer.get_gait_state_estimator(exo=exo, config=config))
    state_machine_list.append(
        control_muxer.get_state_machine(exo=exo, config=config))


'''Prep parameter passing.'''
lock = threading.Lock()
quit_event = threading.Event()
new_ctrl_params_event = threading.Event()
new_gait_state_params_event = threading.Event()
# v0.2,25,0.53,0.62!
# k500!

'''Perform standing calibration.'''
if not config.READ_ONLY:
    for exo in exo_list:
        standing_angle = exo.standing_calibration()
        if exo.side == constants.Side.LEFT:
            config.LEFT_STANDING_ANGLE = standing_angle
        else:
            config.RIGHT_STANDING_ANGLE = standing_angle
else:
    print('Not calibrating... READ_ONLY = True in config')

input('Press any key to begin')
print('Start!')

'''Main Loop: Check param updates, Read data, calculate gait state, apply control, write data.'''
timer = util.FlexibleTimer(
    target_freq=config.TARGET_FREQ)  # attempts constants freq
t0 = time.perf_counter()
keyboard_thread = parameter_passers.ParameterPasser(
    lock=lock, config=config, quit_event=quit_event,
    new_ctrl_params_event=new_ctrl_params_event,
    new_gait_state_params_event=new_gait_state_params_event)
config_saver.write_data(loop_time=0)  # Write first row on config

while True:
    try:
        timer.pause()
        loop_time = time.perf_counter() - t0

        lock.acquire()
        if new_ctrl_params_event.is_set():
            config_saver.write_data(loop_time=loop_time)  # Update config file
            for state_machine in state_machine_list:
                state_machine.update_ctrl_params_from_config(config=config)
            new_ctrl_params_event.clear()
        if new_gait_state_params_event.is_set():
            config_saver.write_data(loop_time=loop_time)  # Update config file
            for gait_state_estimator in gait_state_estimator_list:
                gait_state_estimator.update_params_from_config(config=config)
            new_gait_state_params_event.clear()
        if quit_event.is_set():  # If user enters "quit"
            break
        lock.release()

        for exo in exo_list:
            exo.read_data(loop_time=loop_time)
            if exo.errored_out is True:
                break
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
