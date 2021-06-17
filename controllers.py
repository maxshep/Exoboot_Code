import constants
from exoboot import Exo
from scipy import signal, interpolate
import time
import copy
import custom_filters
import config_util
import util
from collections import deque
from typing import Type


class Controller(object):
    '''Parent controller object. Child classes inherit methods.'''

    def __init__(self, exo: Exo):
        self.exo = exo

    def command(self, reset):
        '''For modularity, new controllers will ideally not take any arguments with
        their command() function. The exo object stored on self will have updated
        data, which is accessible to controller objects.'''
        raise ValueError('command() not defined in child class of Controller')

    def update_controller_gains(self, Kp: int, Ki: int, Kd: int = 0, ff: int = 0):
        '''Updated internal controller gains. Note: None (default) means no change will be commanded.'''
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.ff = ff

    def command_gains(self):
        self.exo.update_gains(Kp=self.Kp, Ki=self.Ki, Kd=self.Kd, ff=self.ff)

    def update_ctrl_params_from_config(self, config: Type[config_util.ConfigurableConstants]):
        '''For modularity, new controllers ideally use this function to update internal
        control params (e.g., k_val, or rise_time) from the config object. If needed, add
        new ctrl params to ConfigurableConstants.'''
        raise ValueError(
            'update_ctrl_params_from_config() not defined in child class of Controller')


class SawickiWickiController(Controller):
    def __init__(self,
                 exo: Exo,
                 k_val: int,
                 b_val: int = 0,
                 Kp: int = constants.DEFAULT_KP,
                 Ki: int = constants.DEFAULT_KI,
                 Kd: int = constants.DEFAULT_KD,
                 ff: int = constants.DEFAULT_FF):
        self.exo = exo
        self.k_val = k_val
        self.b_val = b_val
        super().update_controller_gains(Kp=Kp, Ki=Ki, Kd=Kd, ff=ff)
        self.ankle_angles = deque(maxlen=3)  # looking for peak in pf
        self.ankle_angle_filter = custom_filters.Butterworth(N=2, Wn=0.2)

    def command(self, reset=False):
        self.ankle_angles.append(
            self.ankle_angle_filter.filter(self.exo.data.ankle_angle))
        if reset:
            self.do_engage = False
            super().command_gains()
        if self.do_engage is False:
            if len(self.ankle_angles) == 3:
                if (self.ankle_angles[1] > self.ankle_angles[0] and
                        self.ankle_angles[1] > self.ankle_angles[2]):
                    self.do_engage = True
                    self._update_setpoint(theta0=self.ankle_angles[0])

                    super().command_gains()
                    print('engaged..., desired k_val: ', self.k_val,
                          'setpoint: ', self.ankle_angles[0])
                    self.ankle_angles.clear()  # Reset the ankle angle deque
                    self.exo.command_motor_impedance(
                        theta0=self.theta0_motor, k_val=self.k_val, b_val=self.b_val)

            else:
                # Basically keep it reeled in
                self.exo.command_torque(desired_torque=1)
        else:
            pass  # Engage command was sent when do_engage went true

    def _update_setpoint(self, theta0):
        '''Take in desired ankle setpoint (deg) and stores equivalent motor angle.'''
        if theta0 > constants.MAX_ANKLE_ANGLE or theta0 < constants.MIN_ANKLE_ANGLE:
            raise ValueError(
                'Attempted to command a set point outside the range of motion')
        self.theta0_motor = self.exo.ankle_angle_to_motor_angle(theta0)

    def update_ctrl_params_from_config(self, config: Type[config_util.ConfigurableConstants]):
        'Updates controller parameters from the config object.'''
        self.k_val = config.K_VAL
        self.b_val = config.B_VAL


class ConstantTorqueController(Controller):
    def __init__(self,
                 exo: Exo,
                 desired_torque,
                 Kp: int = constants.DEFAULT_KP,
                 Ki: int = constants.DEFAULT_KI,
                 Kd: int = constants.DEFAULT_KD,
                 ff: int = constants.DEFAULT_FF):
        self.exo = exo
        self.desired_torque = desired_torque
        super().update_controller_gains(Kp=Kp, Ki=Ki, Kd=Kd, ff=ff)

    def command(self, reset=False):
        if reset:
            super().command_gains()
        self.exo.command_torque(self.desired_torque)


class StalkController(Controller):
    def __init__(self,
                 exo: Exo,
                 desired_slack: float,
                 Kp: int = constants.DEFAULT_SWING_KP,
                 Ki: int = constants.DEFAULT_SWING_KI,
                 Kd: int = constants.DEFAULT_SWING_KD,
                 ff: int = constants.DEFAULT_SWING_FF):
        self.exo = exo
        self.desired_slack = desired_slack
        super().update_controller_gains(Kp=Kp, Ki=Ki, Kd=Kd, ff=ff)

    def command(self, reset=False):
        if reset:
            super().command_gains()
        self.exo.command_slack(desired_slack=self.desired_slack)


class GenericSplineController(Controller):
    def __init__(self,
                 exo: Exo,
                 spline_x: list,
                 spline_y: list,
                 Kp: int = constants.DEFAULT_KP,
                 Ki: int = constants.DEFAULT_KI,
                 Kd: int = constants.DEFAULT_KD,
                 ff: int = constants.DEFAULT_FF,
                 fade_duration: float = 5):
        self.exo = exo
        self.spline = None  # Placeholds so update_spline can fill self.last_spline
        self.update_spline(spline_x, spline_y, first_call=True)
        self.fade_duration = fade_duration
        super().update_controller_gains(Kp=Kp, Ki=Ki, Kd=Kd, ff=ff)
        # Fade timer goes from 0 to fade_duration, active if below fade_duration (starts inactive)
        self.fade_start_time = time.perf_counter()-100

    def command(self, reset=False):
        '''Commands appropriate control. If reset=True, this controller was just switched to.'''
        if reset:
            super().command_gains()
        if self.exo.data.gait_phase is None:
            desired_torque = 0
        elif time.perf_counter() - self.fade_start_time < self.fade_duration:
            desired_torque = self.fade_splines(
                gait_phase=self.exo.data.gait_phase, fraction=(time.perf_counter()-self.fade_start_time)/self.fade_duration)
        else:
            desired_torque = self.spline(self.exo.data.gait_phase)
        if desired_torque < 0:
            print('ruh roh')
            print('gait phase:', self.exo.data.gait_phase)
            print('desired_torque: ', desired_torque)
        self.exo.command_torque(desired_torque)

    def update_spline(self, spline_x, spline_y, first_call=False):
        if any(x < 0 or x > 1 for x in spline_x):
            raise ValueError('spline_x can only contain values within [0, 1]')
        # if not first_call:
        #     self.fade_start_time = time.perf_counter()
        self.fade_start_time = time.perf_counter()
        self.spline_x = spline_x
        self.spline_y = spline_y
        self.last_spline = copy.deepcopy(self.spline)
        self.spline = interpolate.pchip(spline_x, spline_y)
        print('Spline Updated')

    def fade_splines(self, gait_phase, fraction):
        torque_from_last_spline = self.last_spline(gait_phase)
        torque_from_current_spline = self.spline(gait_phase)
        desired_torque = (1-fraction)*torque_from_last_spline + \
            fraction*torque_from_current_spline
        return desired_torque


class FourPointSplineController(GenericSplineController):
    def __init__(self,
                 exo: Exo,
                 rise_fraction: float = 0.2,
                 peak_torque: float = 5,
                 peak_fraction: float = 0.55,
                 fall_fraction: float = 0.6,
                 Kp: int = constants.DEFAULT_KP,
                 Ki: int = constants.DEFAULT_KI,
                 Kd: int = constants.DEFAULT_KD,
                 ff: int = constants.DEFAULT_FF,
                 fade_duration: float = 5,
                 bias_torque: float = 5):
        '''Inherits from GenericSplineController, and adds a update_spline_with_list function.'''
        self.bias_torque = bias_torque  # Prevents rounding issues near zero and keeps cord taught
        super().__init__(exo=exo,
                         spline_x=self._get_spline_x(
                             rise_fraction, peak_fraction, fall_fraction),
                         spline_y=self._get_spline_y(peak_torque),
                         Kp=Kp, Ki=Ki, Kd=Kd, ff=ff,
                         fade_duration=fade_duration)

    def update_ctrl_params_from_config(self, config: Type[config_util.ConfigurableConstants]):
        'Updates controller parameters from the config object.'''
        print('Updating spline...')
        super().update_spline(spline_x=self._get_spline_x(rise_fraction=config.RISE_FRACTION,
                                                          peak_fraction=config.PEAK_FRACTION,
                                                          fall_fraction=config.FALL_FRACTION),
                              spline_y=self._get_spline_y(peak_torque=config.PEAK_TORQUE))

    def _get_spline_x(self, rise_fraction, peak_fraction, fall_fraction) -> list:
        return [0, rise_fraction, peak_fraction, fall_fraction, 1]

    def _get_spline_y(self, peak_torque) -> list:
        return [self.bias_torque, self.bias_torque, peak_torque, self.bias_torque, self.bias_torque]


class SmoothReelInController(Controller):
    def __init__(self,
                 exo: Exo,
                 reel_in_mV: int = 1200,
                 slack_cutoff: float = 1500,
                 time_out: float = 0.3,
                 Kp: int = 30,  # 50  150
                 Ki: int = 300,  # 10   50
                 Kd: int = 0,
                 ff: int = 0):
        '''This controller uses current control to get to zero slack, checking for a cutoff..

        Arguments:
            exo: exo.Exo instance
            slack_cutoff: the amount of slack (in motor counts) for the controller to be completed
            time_out: defines maximum amount of time to reel in
        Returns:
            Bool describing whether reel in operation has completed.
         '''
        self.exo = exo
        super().update_controller_gains(Kp=Kp, Ki=Ki, Kd=Kd, ff=ff)
        self.slack_cutoff = slack_cutoff
        # set maximum time for controller
        self.delay_timer = util.DelayTimer(delay_time=time_out)
        self.reel_in_mV = reel_in_mV

    def command(self, reset=False):
        if reset:
            super().command_gains()
            self.t0 = time.perf_counter()
        self.exo.command_voltage(
            desired_mV=self.exo.motor_sign * self.reel_in_mV)

    def check_completion_status(self):
        if self.delay_timer.check() or self.exo.get_slack() < self.slack_cutoff:
            return True
        else:
            return False


class BallisticReelInController(Controller):
    def __init__(self,
                 exo: Exo,
                 slack_cutoff: float = 1500,
                 time_out: float = 0.2,
                 Kp: int = 3,  # 50  150
                 Ki: int = 1,  # 10   50
                 Kd: int = 0,
                 ff: int = 0):
        '''This controller uses position control for zero slack, checking for a cutoff.

        Arguments:
            exo: exo.Exo instance
            slack_cutoff: the amount of slack (in motor counts) for the controller to be completed
            time_out: defines maximum amount of time to reel in
        Returns:
            Bool describing whether reel in operation has completed.
         '''
        self.exo = exo
        super().update_controller_gains(Kp=Kp, Ki=Ki, Kd=Kd, ff=ff)
        self.slack_cutoff = slack_cutoff
        # set maximum time for controller
        self.delay_timer = util.DelayTimer(delay_time=time_out)

    def command(self, reset=False):
        if reset:
            super().command_gains()
            self.delay_timer.start()
        self.exo.command_slack(desired_slack=0)

    def check_completion_status(self):
        slack = self.exo.get_slack()
        if slack < self.slack_cutoff or self.delay_timer.check():
            return True
        else:
            return False


class SoftReelOutController(Controller):
    def __init__(self,
                 exo: Exo,
                 desired_slack: float = 7000,
                 Kp: int = 100,
                 Ki: int = 10,
                 Kd: int = 0,
                 ff: int = 0):
        '''This controller uses position control with low gains to reach the desired slack.'''
        self.exo = exo
        super().update_controller_gains(Kp=Kp, Ki=Ki, Kd=Kd, ff=ff)
        self.desired_slack = desired_slack
        # set maximum time for controller
        self.delay_timer = util.DelayTimer(delay_time=0.2)

    def command(self, reset=False):
        if reset:
            super().command_gains()
            self.delay_timer.start()
        self.exo.command_slack(desired_slack=self.desired_slack)

    def check_completion_status(self):
        slack = self.exo.get_slack()
        if slack > self.desired_slack-500 or self.delay_timer.check():
            return True
        else:
            return False


class GenericImpedanceController(Controller):
    def __init__(self,
                 exo: Exo,
                 setpoint,
                 k_val,
                 b_val=0,
                 Kp: int = constants.DEFAULT_KP,
                 Ki: int = constants.DEFAULT_KI,
                 Kd: int = constants.DEFAULT_KD,
                 ff: int = constants.DEFAULT_FF):
        self.exo = exo
        self.setpoint = setpoint
        self.k_val = k_val
        self.b_val = b_val
        super().update_controller_gains(Kp=Kp, Ki=Ki, Kd=Kd, ff=ff)

    def command(self, reset=False):
        if reset:
            super().command_gains()
        theta0_motor = self.exo.ankle_angle_to_motor_angle(self.setpoint)
        self.exo.command_motor_impedance(
            theta0=theta0_motor, k_val=self.k_val, b_val=self.b_val)

    def update_ctrl_params_from_config(self, config: Type[config_util.ConfigurableConstants],
                                       update_k=True, update_b=True, update_setpoint=True):
        'Updates controller parameters from the config object.'''
        if update_k:
            self.k_val = config.K_VAL
        if update_b:
            self.b_val = config.B_VAL
        if update_setpoint:
            self.setpoint = config.SET_POINT
