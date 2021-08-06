from typing import Type, List
from dataclasses import dataclass, field
import time
import csv
import sys
import importlib
from enum import Enum
import argparse
import constants


class Task(Enum):
    '''Used to determine gait_event_detector used and state machines used.'''
    WALKING = 0
    STANDINGPERTURBATION = 1
    BILATERALSTANDINGPERTURBATION = 2
    SLIPDETECTFROMSYNC = 3


class StanceCtrlStyle(Enum):
    '''Used to determine behavior during stance.'''
    FOURPOINTSPLINE = 0
    GENERICSPLINE = 1
    SAWICKIWICKI = 2
    GENERICIMPEDANCE = 3
    FIVEPOINTSPLINE = 4


@dataclass
class ConfigurableConstants():
    '''Class that stores configuration-related constants.

    These variables serve to allow 1) loadable configurations from files in /custom_constants/, 
    2) online updating of device behavior via parameter_passers.py, and 3) to store calibration 
    details. Below are the default config constants. DO NOT MODIFY DEFAULTS. Write your own short
    script in /custom_constants/ (see default_config.py for example).
    (see )  '''
    # Set by functions... no need to change in config file
    loop_time: float = 0
    actual_time: float = time.time()
    LEFT_STANDING_ANGLE: float = None  # Deg
    RIGHT_STANDING_ANGLE: float = None  # Deg

    TARGET_FREQ: float = 200  # Hz
    ACTPACK_FREQ: float = 200  # Hz
    DO_DEPHY_LOG: bool = True
    DEPHY_LOG_LEVEL: int = 4
    ONLY_LOG_IF_NEW: bool = True

    TASK: Type[Task] = Task.WALKING
    STANCE_CONTROL_STYLE: Type[StanceCtrlStyle] = StanceCtrlStyle.FOURPOINTSPLINE
    MAX_ALLOWABLE_CURRENT = 20000  # mA

    # Gait State details
    HS_GYRO_THRESHOLD: float = 100
    HS_GYRO_FILTER_N: int = 2
    HS_GYRO_FILTER_WN: float = 3
    HS_GYRO_DELAY: float = 0.05
    SWING_SLACK: int = 10000
    TOE_OFF_FRACTION: float = 0.62
    REEL_IN_MV: int = 1200
    REEL_IN_SLACK_CUTOFF: int = 1200
    REEL_IN_TIMEOUT: float = 0.2
    NUM_STRIDES_REQUIRED: int = 2
    SWING_ONLY: bool = False

    # 4 point Spline
    RISE_FRACTION: float = 0.2
    PEAK_FRACTION: float = 0.53
    FALL_FRACTION: float = 0.63
    PEAK_TORQUE: float = 5
    SPLINE_BIAS: float = 3  # Nm

    # Impedance
    K_VAL: int = 500
    B_VAL: int = 0
    SET_POINT: float = 0  # Deg

    READ_ONLY: bool = False  # Does not require Lipos
    DO_READ_FSRS: bool = False
    DO_READ_SYNC: bool = False

    PRINT_HS: bool = True  # Print heel strikes
    VARS_TO_PLOT: List = field(default_factory=lambda: [])
    DO_DETECT_SLIP: bool = False
    SLIP_DETECT_ACTIVE: bool = False
    SLIP_DETECT_DELAY: int = 0
    EXPERIMENTER_NOTES: str = 'Experimenter notes go here'


class ConfigSaver():
    def __init__(self, file_ID: str, config: Type[ConfigurableConstants]):
        '''file_ID is used as a custom file identifier after date.'''
        self.file_ID = file_ID
        self.config = config
        subfolder_name = 'exo_data/'
        filename = subfolder_name + \
            time.strftime("%Y%m%d_%H%M_") + file_ID + \
            '_CONFIG' + '.csv'
        self.my_file = open(filename, 'w', newline='')
        self.writer = csv.DictWriter(
            self.my_file, fieldnames=self.config.__dict__.keys())
        self.writer.writeheader()

    def write_data(self, loop_time):
        '''Writes new row of Config data to Config file.'''
        self.config.loop_time = loop_time
        self.config.actual_time = time.time()
        self.writer.writerow(self.config.__dict__)

    def close_file(self):
        if self.file_ID is not None:
            self.my_file.close()


def load_config(config_filename) -> Type[ConfigurableConstants]:
    try:
        # strip extra parts off
        config_filename = config_filename.lower()
        if config_filename.endswith('_config'):
            config_filename = config_filename[:-7]
        elif config_filename.endswith('_config.py'):
            config_filename = config_filename[:-11]
        elif config_filename.endswith('.py'):
            config_filename = config_filename[:-4]
        config_filename = config_filename + '_config'
        module = importlib.import_module('.' + config_filename,
                                         package='custom_configs')
    except:
        error_str = 'Unable to find config file: ' + \
            config_filename + ' in custom_constants'
        raise ValueError(error_str)
    config = module.config
    print('Using ConfigurableConstants from: ', config_filename)
    return config


def parse_args():
    # Create the parser
    my_parser = argparse.ArgumentParser(prog='Exoboot Code',
                                        description='Run Exoboot Controllers',
                                        epilog='Enjoy the program! :)')
    # Add the arguments
    my_parser.add_argument('-c', '--config', action='store',
                           type=str, required=False, default='default_config')
    # Execute the parse_args() method
    args = my_parser.parse_args()
    return args


def load_config_from_args():
    args = parse_args()
    config = load_config(config_filename=args.config)
    return config


def get_sync_detector(config: Type[ConfigurableConstants]):
    if config.DO_READ_SYNC:
        import gpiozero  # pylint: disable=import-error
        sync_detector = gpiozero.InputDevice(
            pin=constants.SYNC_PIN, pull_up=True)
        return sync_detector
    else:
        return None
