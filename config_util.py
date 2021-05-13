from typing import Type
from dataclasses import dataclass
import time
import csv
import sys
import importlib
from enum import Enum
import argparse


class CtrlStyle(Enum):
    FOURPOINTSPLINE = 0
    SAWICKIWICKI = 1
    GENERICIMPEDANCE = 2
    STANDINGPERTURBATION = 3


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
    LEFT_ANKLE_ANGLE_ZERO: float = None  # Deg
    RIGHT_ANKLE_ANGLE_ZERO: float = None  # Deg

    TARGET_FREQ: float = 200  # Hz
    ACTPACK_FREQ: float = 200  # Hz
    HIGH_LEVEL_CTRL_STYLE: Type[CtrlStyle] = CtrlStyle.FOURPOINTSPLINE

    # Gait State details
    HS_GYRO_THRESHOLD: float = 100
    HS_GYRO_FILTER_N: int = 2
    HS_GYRO_FILTER_WN: float = 3
    HS_GYRO_DELAY: float = 0.05
    SWING_SLACK: int = 10000
    TOE_OFF_FRACTION: float = 0.62
    REEL_IN_TIMEOUT: float = 0.2

    # 4 point Spline
    RISE_FRACTION: float = 0.2
    PEAK_FRACTION: float = 0.53
    FALL_FRACTION: float = 0.63
    PEAK_TORQUE: float = 5
    SPLINE_BIAS: float = 5  # Nm

    # Impedance
    K_VAL: int = 500
    B_VAL: int = 0
    SET_POINT: float = 0  # Deg

    READ_ONLY = False  # Does not require Lipos
    DO_READ_FSRS = False

    PRINT_HS = True  # Print heel strikes


class ConfigSaver():
    def __init__(self, file_ID: str, config: Type[ConfigurableConstants]):
        '''file_ID is used as a custom file identifier after date.'''
        self.file_ID = file_ID
        self.config = config
        subfolder_name = 'exo_data/'
        filename = subfolder_name + \
            time.strftime("%Y%m%d-%H%M") + file_ID + \
            '_CONFIG' + '.csv'
        self.my_file = open(filename, 'w', newline='')
        self.writer = csv.DictWriter(
            self.my_file, fieldnames=self.config.__dict__.keys())
        self.writer.writeheader()
        self.write_data(loop_time=0)

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
    return(args)
