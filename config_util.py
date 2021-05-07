from typing import Type
from dataclasses import dataclass
import time
import csv
import sys
import importlib
from enum import Enum


class ControlArchitecture(Enum):
    FOURPOINTSPLINE = 0
    SAWICKIWICKI = 1
    GENERICIMPEDANCE = 2


@dataclass
class ConfigurableConstants():
    '''Class that stores configuration-related constants.

    Below are the default config constants. DO NOT MODIFY. Write your own short script 
    in /custom_constants/ (see max_config.py for example).
    (see )  '''
    loop_time: float = 0
    actual_time: float = time.time()
    TARGET_FREQUENCY: float = 200  # Hz
    ACTPACK_FREQUENCY: float = 200  # Hz
    CONTROL_ARCHITECTURE: Type[ControlArchitecture] = ControlArchitecture.FOURPOINTSPLINE
    HS_GYRO_THRESHOLD: float = 100
    HS_GYRO_FILTER_N: int = 2
    HS_GYRO_FILTER_WN: float = 3
    HS_GYRO_DELAY: float = 0.05

    SWING_SLACK: int = 10000
    TOE_OFF_FRACTION: float = 0.62
    SPLINE_BIAS: float = 5  # Nm

    REEL_IN_TIMEOUT: float = 0.2

    # 4 point Spline
    RISE_FRACTION: float = 0.2
    PEAK_FRACTION: float = 0.53
    FALL_FRACTION: float = 0.63
    PEAK_TORQUE: float = 5

    # Impedance
    K: int = 500
    B: int = 0

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


def parse_config_to_use() -> Type[ConfigurableConstants]:
    '''Finds file for config to use based on command line passed args.

    To use a config file other than default_config, for example: 

    python main_loop cc max_config

    will import the config object stored in max_config.py.'''
    args = sys.argv[1:]
    if "cc" in args:
        config_filename = args[args.index("cc") + 1]
    else:
        config_filename = 'default_config'
    module = importlib.import_module('.' + config_filename,
                                     package='custom_constants')
    config = module.config
    print('Using ConfigurableConstants from: ', config_filename)
    return config


if __name__ == '__main__':
    from custom_constants import default_config
    config = parse_config_to_use()
    config_saver = ConfigSaver(file_ID='testyo', config=config)
    config_saver.write_data(loop_time=1)
    config_saver.write_data(loop_time=2)
    config_saver.close_file
