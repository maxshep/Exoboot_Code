import csv
import logging
import os
import sys
import time
import warnings
from dataclasses import dataclass, field, InitVar
from scipy import interpolate
from typing import Type

import numpy as np
import pdb

import config_util
import constants
import filters
from flexsea import fxEnums as fxe
from flexsea import flexsea as flex
from flexsea import fxUtils as fxu

# Instantiate Dephy's FlexSEA object, which contains important functions
fxs = flex.FlexSEA()


def connect_to_exos(file_ID: str,
                    config: Type[config_util.ConfigurableConstants],
                    sync_detector=None):
    '''Connect to Exos, instantiate Exo objects.'''

    # Load Ports and baud rate
    if fxu.is_win():		# Need for WebAgg server to work in Python 3.8
        print('Detected win32')
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        port_cfg_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "ports.yaml")
        ports, baud_rate = fxu.load_ports_from_file(port_cfg_path)
    elif fxu.is_pi64() or fxu.is_pi():
        ports = ['/dev/ttyACM0', '/dev/ttyACM1']
        baud_rate = constants.DEFAULT_BAUD_RATE
    else:
        raise ValueError('Max Code only supporting Windows or pi64 so far')
    print(f"Using ports:\t{ports}")

    exo_list = []
    for port in ports:
        try:
            dev_id = fxs.open(port, baud_rate, log_level=3)
            fxs.start_streaming(
                dev_id=dev_id, freq=config.ACTPACK_FREQ, log_en=config.DO_DEPHY_LOG)
            exo_list.append(Exo(dev_id=dev_id, file_ID=file_ID,
                                target_freq=config.TARGET_FREQ,
                                do_read_fsrs=config.DO_READ_FSRS,
                                do_include_did_slip=config.DO_DETECT_SLIP,
                                max_allowable_current=config.MAX_ALLOWABLE_CURRENT,
                                do_include_gen_vars=config.DO_INCLUDE_GEN_VARS,
                                sync_detector=sync_detector))
        except IOError:
            print('Unable to open exo on port: ', port,
                  ' This is okay if only one exo is connected!')

    if not exo_list:  # (if empty)
        raise RuntimeError('No Exos connected')
    return exo_list


class Exo():
    def __init__(self,
                 dev_id: int,
                 max_allowable_current: int,
                 file_ID: str = None,
                 target_freq: float = 200,
                 do_read_fsrs: bool = False,
                 do_include_did_slip: bool = False,
                 do_include_gen_vars: bool = False,
                 sync_detector=None):
        '''Exo object is the primary interface with the Dephy ankle exos, and corresponds to a single physical exoboot.
        Args:
            dev_id: int. Unique integer to identify the exo in flexsea's library. Returned by connect_to_exo
            file_ID: str. Unique string added to filename. If None, no file will be saved.
            do_read_fsrs: bool indicating whether to read FSRs.
            sync_detector: gpiozero class for sync line, created in config_util '''
        self.dev_id = dev_id
        self.max_allowable_current = max_allowable_current
        self.file_ID = file_ID
        self.do_read_fsrs = do_read_fsrs
        self.do_include_sync = True if sync_detector else False
        self.sync_detector = sync_detector
        if self.dev_id is None:
            print('Exo obj created but no exoboot connected. Some methods available')
        elif self.dev_id in constants.LEFT_EXO_DEV_IDS:
            self.side = constants.Side.LEFT
            self.motor_sign = -1
            self.ankle_to_motor_angle_polynomial = constants.LEFT_ANKLE_TO_MOTOR
            self.ankle_angle_offset = constants.LEFT_ANKLE_ANGLE_OFFSET
            # self.TR_from_ankle_angle = self.motor_sign * constants.LEFT_ANKLE_TO_TR
        elif self.dev_id in constants.RIGHT_EXO_DEV_IDS:
            self.side = constants.Side.RIGHT
            self.motor_sign = 1
            self.ankle_to_motor_angle_polynomial = constants.RIGHT_ANKLE_TO_MOTOR
            self.ankle_angle_offset = constants.RIGHT_ANKLE_ANGLE_OFFSET
            # self.TR_from_ankle_angle = self.motor_sign * constants.RIGHT_ANKLE_TO_TR
        else:
            raise ValueError(
                'dev_id: ', self.dev_id, 'not found in constants.LEFT_EXO_DEV_IDS or constants.RIGHT_EXO_DEV_IDS')
        self.motor_offset = 0
        # ankle velocity filter is hardcoded for simplicity, but can be factored out if necessary
        self.ankle_velocity_filter = filters.Butterworth(
            N=2, Wn=10, fs=target_freq)
        if self.do_read_fsrs:
            if fxu.is_pi() or fxu.is_pi64():
                import gpiozero  # pylint: disable=import-error
                if self.side == constants.Side.LEFT:
                    self.heel_fsr_detector = gpiozero.InputDevice(
                        pin=constants.LEFT_HEEL_FSR_PIN, pull_up=True)
                    self.toe_fsr_detector = gpiozero.InputDevice(
                        pin=constants.LEFT_TOE_FSR_PIN, pull_up=True)
                else:
                    self.heel_fsr_detector = gpiozero.InputDevice(
                        pin=constants.RIGHT_HEEL_FSR_PIN, pull_up=True)
                    self.toe_fsr_detector = gpiozero.InputDevice(
                        pin=constants.RIGHT_TOE_FSR_PIN, pull_up=True)
            else:
                raise Exception('Can only use FSRs with rapberry pi!')

        self.data = self.DataContainer(
            do_include_FSRs=do_read_fsrs, do_include_did_slip=do_include_did_slip,
            do_include_gen_vars=do_include_gen_vars, do_include_sync=self.do_include_sync)
        self.has_calibrated = False
        self.is_clipping = False
        if self.file_ID is not None:
            self.setup_data_writer(file_ID=file_ID)
        if self.dev_id is not None:
            self.update_gains(Kp=constants.DEFAULT_KP,
                              Ki=constants.DEFAULT_KI,
                              Kd=constants.DEFAULT_KD,
                              k_val=0,
                              b_val=0,
                              ff=constants.DEFAULT_FF)
            self.TR_from_ankle_angle = interpolate.PchipInterpolator(
                constants.ANKLE_PTS, self.motor_sign*constants.TR_PTS)

    @dataclass
    class DataContainer:
        '''A nested dataclass within Exo, reserving space for instantaneous data.'''
        do_include_FSRs: InitVar[bool] = False
        do_include_sync: InitVar[bool] = False
        do_include_did_slip: InitVar[bool] = False
        do_include_gen_vars: InitVar[bool] = False
        state_time: float = 0
        loop_time: float = 0
        accel_x: float = 0
        accel_y: float = 0
        accel_z: float = 0
        gyro_x: float = 0
        gyro_y: float = 0
        gyro_z: float = 0
        motor_angle: int = 0
        motor_velocity: float = 0
        motor_current: int = 0
        ankle_angle: float = 0
        ankle_velocity: float = 0
        ankle_torque_from_current: float = 0
        did_heel_strike: bool = False
        gait_phase: float = None
        did_toe_off: bool = False
        commanded_current: int = None
        commanded_position: int = None
        commanded_torque: float = None
        slack: int = None
        temperature: int = None
        # Optional fields--init in __post__init__
        heel_fsr: bool = field(init=False)
        toe_fsr: bool = field(init=False)
        did_slip: bool = field(init=False)
        sync: bool = field(init=False)
        gen_var1: float = field(init=False)
        gen_var2: float = field(init=False)
        gen_var3: float = field(init=False)

        def __post_init__(self, do_include_FSRs, do_include_sync, do_include_did_slip, do_include_gen_vars):
            # Important! The order of these args need to match their order as InitVars above
            if do_include_FSRs:
                self.heel_fsr = False
                self.toe_fsr = False
            if do_include_did_slip:
                self.did_slip = False
            if do_include_gen_vars:
                self.gen_var1 = None
                self.gen_var2 = None
                self.gen_var3 = None
            if do_include_sync:
                self.sync = True

    def close(self):
        self.update_gains()
        self.command_current(desired_mA=0)
        time.sleep(0.1)
        self.command_controller_off()
        time.sleep(0.05)
        fxs.stop_streaming(self.dev_id)
        time.sleep(0.2)
        fxs.close(self.dev_id)
        self.close_file()
        if self.do_read_fsrs:
            self.heel_fsr_detector.close()
            self.toe_fsr_detector.close()
        if self.do_include_sync:
            self.sync_detector.close()

    def update_gains(self, Kp=None, Ki=None, Kd=None, k_val=None, b_val=None, ff=None):
        '''Optionally updates individual exo gain values, and sends to Actpack.'''
        if Kp is not None:
            self.Kp = Kp
        if Ki is not None:
            self.Ki = Ki
        if Kd is not None:
            self.Kd = Kd
        if k_val is not None:
            self.k_val = k_val
        if b_val is not None:
            self.b_val = b_val
        if ff is not None:
            self.ff = ff
        fxs.set_gains(dev_id=self.dev_id, kp=self.Kp, ki=self.Ki,
                      kd=self.Kd, k_val=self.k_val, b_val=self.b_val, ff=self.ff)

    def read_data(self, loop_time=None):
        '''Read data from Dephy Actpack, store in exo.data Data Container.

        IMU data comes from Dephy in RHR, with positive XYZ pointing
        backwards, downwards, and rightwards on the right side and forwards,
        downwards, and leftwards on the left side. It is converted here
        to LHR on left side and RHR on right side. XYZ axes now point
        forwards, upwards, and outwards (laterally).'''
        if loop_time is not None:
            self.data.loop_time = loop_time
        last_ankle_angle = self.data.ankle_angle
        self.last_state_time = self.data.state_time
        actpack_data = fxs.read_device(self.dev_id)

        # Check to see if values are reasonable
        ankle_angle_temp = (-1 * self.motor_sign * actpack_data.ank_ang *
                            constants.ENC_CLICKS_TO_DEG + self.ankle_angle_offset)
        if ankle_angle_temp > constants.MAX_ANKLE_ANGLE or ankle_angle_temp < constants.MIN_ANKLE_ANGLE:
            print('Bad packet caught on side: ', self.side, 'ankle_angle: ', ankle_angle_temp,
                  'at time: ', self.data.state_time)
            return  # Exit early
        self.data.ankle_angle = ankle_angle_temp
        self.data.state_time = actpack_data.state_time * constants.MS_TO_SECONDS
        self.data.temperature = actpack_data.temperature
        self.data.accel_x = -1 * self.motor_sign * \
            actpack_data.accelx * constants.ACCEL_GAIN
        self.data.accel_y = -1 * actpack_data.accely * constants.ACCEL_GAIN
        self.data.accel_z = actpack_data.accelz * constants.ACCEL_GAIN
        self.data.gyro_x = -1 * actpack_data.gyrox * constants.GYRO_GAIN
        self.data.gyro_y = -1 * self.motor_sign * \
            actpack_data.gyroy * constants.GYRO_GAIN
        self.data.gyro_z = actpack_data.gyroz * constants.GYRO_GAIN # sign may be different from Max's device
        # self.data.gyro_z = self.motor_sign * actpack_data.gyroz * constants.GYRO_GAIN
        '''Motor angle and current are kept in Dephy's orientation, but ankle
        angle and torque are converted to positive = plantarflexion.'''
        self.data.motor_angle = actpack_data.mot_ang
        self.data.motor_velocity = actpack_data.mot_vel
        self.data.motor_current = actpack_data.mot_cur
        self.data.ankle_torque_from_current = self._motor_current_to_ankle_torque(
            self.data.motor_current)

        if self.has_calibrated:
            self.data.slack = self.get_slack()

        if (self.last_state_time is None or
            last_ankle_angle is None or
                self.data.state_time-self.last_state_time > 20):
            self.data.ankle_velocity = 0
        elif self.data.state_time == self.last_state_time:
            pass  # Keep old velocity
        else:
            angular_velocity = (
                self.data.ankle_angle - last_ankle_angle)/(self.data.state_time-self.last_state_time)
            self.data.ankle_velocity = self.ankle_velocity_filter.filter(
                angular_velocity)

        if self.do_read_fsrs:
            self.data.heel_fsr = self.heel_fsr_detector.value
            self.data.toe_fsr = self.toe_fsr_detector.value
        if self.do_include_sync:
            self.data.sync = self.sync_detector.value

    def get_batt_voltage(self):
        actpack_data = fxs.read_device(self.dev_id)
        return actpack_data.batt_volt

    def setup_data_writer(self, file_ID: str):
        '''file_ID is used as a custom file identifier after date.'''
        if file_ID is not None:
            subfolder_name = 'exo_data/'
            self.filename = subfolder_name + \
                time.strftime("%Y%m%d_%H%M_") + file_ID + \
                '_' + self.side.name + '.csv'
            self.my_file = open(self.filename, 'w', newline='')
            self.writer = csv.DictWriter(
                self.my_file, fieldnames=self.data.__dict__.keys())
            self.writer.writeheader()
            self._did_heel_strike_hold = False
            self._did_toe_off_hold = False

    def write_data(self, only_write_if_new: bool = True):
        '''Writes data file, optionally only if there is new actpack data.'''
        if self.file_ID is not None and only_write_if_new:
            # This logic is messy because is_heel_strike and is_toe_off are calculated more frequently,
            # So to write them we need to store if they occurred.
            if self.data.did_heel_strike:
                self._did_heel_strike_hold = True
            if self.data.did_toe_off:
                self._did_toe_off_hold = True
            if self.last_state_time != self.data.state_time:
                # Temporarily replace did_heel_strike and did_toe_off with holds
                current_did_heel_strike = self.data.did_heel_strike
                current_did_toe_off = self.data.did_toe_off
                self.data.did_heel_strike = self._did_heel_strike_hold
                self.data.did_toe_off = self._did_toe_off_hold
                self.writer.writerow(self.data.__dict__)
                # Reset to False (will fail if heel strikes / toe offs occur within ~10 ms of each other.)
                self.data.did_heel_strike = current_did_heel_strike
                self._did_heel_strike_hold = False
                self.data.did_toe_off = current_did_toe_off
                self._did_toe_off_hold = False
        else:
            if self.file_ID is not None:
                self.writer.writerow(self.data.__dict__)

    def close_file(self):
        if self.file_ID is not None:
            self.my_file.close()

    def command_current(self, desired_mA: int):
        '''Commands current (mA), with positive = PF on right, DF on left.'''
        if abs(desired_mA) > self.max_allowable_current:
            self.command_controller_off()
            raise ValueError(
                'abs(desired_mA) must be < config.max_allowable_current')
        fxs.send_motor_command(
            dev_id=self.dev_id, ctrl_mode=fxe.FX_CURRENT, value=desired_mA)
        self.data.commanded_current = desired_mA
        self.data.commanded_position = None

    def command_voltage(self, desired_mV: int):
        '''Commands voltage (mV), with positive = PF on right, DF on left.'''
        if abs(desired_mV) > constants.MAX_ALLOWABLE_VOLTAGE_COMMAND:
            raise ValueError(
                'abs(desired_mV) must be < constants.MAX_ALLOWABLE_VOLTAGE_COMMAND')
        fxs.send_motor_command(
            dev_id=self.dev_id, ctrl_mode=fxe.FX_VOLTAGE, value=desired_mV)
        self.data.commanded_current = None
        self.data.commanded_position = None
        self.data.commanded_torque = None

    def command_motor_angle(self, desired_motor_angle: int):
        '''Commands motor angle (counts). Pay attention to the sign!'''
        fxs.send_motor_command(
            dev_id=self.dev_id, ctrl_mode=fxe.FX_POSITION, value=desired_motor_angle)
        self.data.commanded_current = None
        self.data.commanded_position = desired_motor_angle
        self.data.commanded_torque = None

    def command_motor_impedance(self, theta0: int, k_val: int, b_val: int):
        '''Commands motor impedance, with theta0 a motor position (int).'''
        # k_val and b_val are modified by updating gains (weird, yes)
        if k_val > constants.MAX_ALLOWABLE_K_COMMAND or k_val < 0:
            raise ValueError(
                'k_val must be positive, and less than max. tested k_val in constants.py')
        if b_val > constants.MAX_ALLOWABLE_B_COMMAND or b_val < 0:
            raise ValueError(
                'b_val must be positive, and less than max. tested b_val in constants.py')
        if self.k_val != k_val or self.b_val != b_val:
            # Only send gains when necessary
            self.update_gains(k_val=int(k_val), b_val=int(b_val))
        fxs.send_motor_command(
            dev_id=self.dev_id, ctrl_mode=fxe.FX_IMPEDANCE, value=int(theta0))
        self.data.commanded_current = None
        self.data.commanded_position = None
        self.data.commanded_torque = None

    def command_torque(self, desired_torque: float, do_return_command_torque=False, do_ease_torque_off=True):
        '''Applies desired torque (Nm) in plantarflexion only (positive torque)'''
        self.data.commanded_torque = desired_torque  # TODO(maxshep) remove
        if desired_torque < 0:
            print('desired_torque: ', desired_torque)
            raise ValueError('Cannot apply negative torques')
        max_allowable_torque = self.calculate_max_allowable_torque()
        if desired_torque > max_allowable_torque:
            if self.is_clipping is False:  # Only print once when clipping occurs before reset
                logging.warning('Torque was clipped!')
            desired_torque = max_allowable_torque
            self.is_clipping = True
        else:
            self.is_clipping = False

        # Softly reduce desired torque at high ankle angles when TR approaches 0
        if do_ease_torque_off:
            reel_in_current = self.motor_sign*1000
            if self.data.ankle_angle > 45:
                desired_current = reel_in_current  # A small amount to stay reeled in
            elif 40 < self.data.ankle_angle <= 45:  # Window of taper
                desired_torque = desired_torque*(45-self.data.ankle_angle)/5
                print('after desired_torque',desired_torque)
                desired_current = max(reel_in_current, self._ankle_torque_to_motor_current(
                    torque=desired_torque))
            else:
                desired_current = self._ankle_torque_to_motor_current(
                    torque=desired_torque)
        else:
            desired_current = self._ankle_torque_to_motor_current(
                torque=desired_torque)

        self.command_current(desired_mA=desired_current)
        if do_return_command_torque:
            return desired_torque

    def command_ankle_impedance(self, theta0_ankle: float, K_ankle: float, B_ankle: float = 0):
        theta0_motor = self.ankle_angle_to_motor_angle(theta0_ankle)
        K_dephy = K_ankle / constants.DEPHY_K_TO_ANKLE_K
        # B_dephy = B_ankle / constants.DEPHY_B_TO_ANKLE_B
        self.command_motor_impedance(
            theta0=theta0_motor, k_val=K_dephy, b_val=0)

    def command_controller_off(self):
        fxs.send_motor_command(
            dev_id=self.dev_id, ctrl_mode=fxe.FX_NONE, value=0)

    def command_slack(self, desired_slack=10000):
        if not self.has_calibrated:
            raise ValueError(
                'Must perform standing calibration before performing this task')
        '''Commands position based on desired slack (motor counts)'''
        if desired_slack < 0:
            raise ValueError('Desired slack must be positive')
        # Desired motor angle requires estimating motor angle from ankle angle and adding/subtracting slack
        desired_motor_angle = int(
            -1 * self.motor_sign * desired_slack +
            self.ankle_angle_to_motor_angle(self.data.ankle_angle))
        self.command_motor_angle(
            desired_motor_angle=desired_motor_angle)

    def get_slack(self):
        '''Returns slack in motor counts, with positive = actual slack.'''
        slack = -1*self.motor_sign*(self.data.motor_angle -
                                    self.ankle_angle_to_motor_angle(self.data.ankle_angle))
        return slack

    def calculate_max_allowable_torque(self):
        '''Calculates max allowable torque from self.max_allowable_current and ankle_angle.'''
        max_allowable_torque = max(
            #  0, self._motor_current_to_ankle_torque(current=self.max_allowable_current)*0.1)
            0, self._motor_current_to_ankle_torque(current=self.motor_sign*self.max_allowable_current))
        return max_allowable_torque

    def _motor_current_to_ankle_torque(self, current: int) -> float:
        '''Converts current (mA) to torque (Nm), based on side and transmission ratio (no dynamics)'''
        motor_torque = current*constants.MOTOR_CURRENT_TO_MOTOR_TORQUE
        ankle_torque = motor_torque * \
            self.TR_from_ankle_angle(self.data.ankle_angle)
            # np.polyval(self.TR_from_ankle_angle, self.data.ankle_angle)
            
        return ankle_torque

    def _ankle_torque_to_motor_current(self, torque: float) -> int:
        '''Converts torque (Nm) to current (mA), based on side and transmission ratio (no dynamics)'''
        motor_torque = torque / \
            self.TR_from_ankle_angle(self.data.ankle_angle)
        #    np.polyval(self.TR_from_ankle_angle, self.data.ankle_angle) 
        motor_current = int(
            motor_torque / constants.MOTOR_CURRENT_TO_MOTOR_TORQUE)

        return motor_current

    def ankle_angle_to_motor_angle(self, ankle_angle):
        '''Calculate equivalent motor position via polynomial evaluation.'''
        if not self.has_calibrated:
            raise ValueError(
                'Must perform standing calibration before performing this task')
        else:
            motor_angle = int(np.polyval(
                self.ankle_to_motor_angle_polynomial, ankle_angle) + self.motor_offset)
        return motor_angle

    def standing_calibration(self,
                             calibration_mV: int = 1300,
                             max_seconds_to_calibrate: float = 5,
                             current_threshold: float = 1500,
                             do_zero_ankle_angle: bool = False):
        '''Brings up slack, calibrates ankle and motor offset angles.'''
        input(['Press Enter to calibrate exo on ' + str(self.side)])
        time.sleep(0.2)
        print('Calibrating...')
        current_filter = filters.MovingAverage(window_size=10)
        self.command_voltage(desired_mV=self.motor_sign * calibration_mV)
        t0 = time.time()
        while time.time()-t0 < max_seconds_to_calibrate:
            time.sleep(0.01)
            self.read_data()
            if abs(current_filter.filter(self.data.motor_current)) > current_threshold:
                calibrated_ankle_angle = self.data.ankle_angle
                break
        else:
            # Enters here if while loop doesn't break
            self.command_controller_off()
            raise RuntimeError('Calibration Timed Out!!!')
        self.has_calibrated = True
        self.motor_offset = (self.data.motor_angle -
                             self.ankle_angle_to_motor_angle(self.data.ankle_angle))
        for ramp_down_value in np.arange(1, 0, -0.01):
            time.sleep(0.01)
            self.command_voltage(desired_mV=ramp_down_value *
                                 self.motor_sign * calibration_mV)
        self.command_controller_off()
        print('Finished Calibrating ', self.side)
        return calibrated_ankle_angle
