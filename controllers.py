import constants
from exoboot import Exo
from scipy import signal, interpolate
import time
import copy
import filters
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
        self.ankle_angles = deque(maxlen=5)  # looking for peak in pf
        self.ankle_angle_filter = filters.Butterworth(N=2, Wn=0.1)

    def command(self, reset=False):
        if reset:
            self.is_taught = False
            self.found_setpt = False
            self.do_engage = False
            self.ankle_angles.clear()  # Reset the ankle angle deque
            self.ankle_angle_filter.restart()  # Reset the filter
            super().command_gains()
            self.exo.data.gen_var2 = None
        self.ankle_angles.appendleft(
            self.ankle_angle_filter.filter(self.exo.data.ankle_angle))
        self.exo.data.gen_var3 = self.ankle_angles[0]

        # check engagement
        self.slack_cutoff = 1500
        if self.is_taught is False:
            self.is_taught = self.exo.get_slack() < self.slack_cutoff

        if self.found_setpt is False:
            # TODO(maxshep) see if you want to change min val
            if len(self.ankle_angles) == 5 and (self.ankle_angles[1] > self.ankle_angles[0] and
                                                self.ankle_angles[1] > self.ankle_angles[2]) and (
                    self.ankle_angles[0] > 5):
                self.exo.data.gen_var2 = self.ankle_angles[1]
                self.found_setpt = True
                self._update_setpoint(theta0=self.ankle_angles[1])

        if self.is_taught and self.found_setpt:
            self.exo.update_gains(Kp=20, Ki=200, Kd=0, ff=60)
            # super().command_gains()
            # print('engaged..., desired k_val: ', self.k_val,
            #       'setpoint: ', self.ankle_angles[0])
            self.exo.command_motor_impedance(
                theta0=self.theta0_motor, k_val=self.k_val, b_val=self.b_val)
            self.exo.data.gen_var1 = 6

        else:
            self.is_taught = self.exo.get_slack() < self.slack_cutoff
            mv_to_apply = 1500  # 1500
            self.exo.command_voltage(
                desired_mV=self.exo.motor_sign * mv_to_apply)
            # self.exo.command_torque(desired_torque=1)
            self.exo.data.gen_var1 = 5

    def _update_setpoint(self, theta0):
        '''Take in desired ankle setpoint (deg) and stores equivalent motor angle.'''
        if theta0 > constants.MAX_ANKLE_ANGLE or theta0 < constants.MIN_ANKLE_ANGLE:
            raise ValueError(
                'Attempted to command a set point outside the range of motion')
        self.theta0_motor = self.exo.ankle_angle_to_motor_angle(theta0)

    def update_ctrl_params_from_config(self, config: Type[config_util.ConfigurableConstants]):
        'Updates controller parameters from the config object.'''
        if self.k_val != config.K_VAL:
            self.k_val = config.K_VAL
            print('K updated to: ', self.k_val)
        # TODO(maxshep) see what val you like for this in params
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
                 exo: Type[Exo],
                 spline_x: list,
                 spline_y: list,
                 use_gait_phase: bool = True,
                 fade_duration: float = 5,
                 Kp: int = constants.DEFAULT_KP,
                 Ki: int = constants.DEFAULT_KI,
                 Kd: int = constants.DEFAULT_KD,
                 ff: int = constants.DEFAULT_FF):
        self.exo = exo
        self.spline = None  # Placeholds so update_spline can fill self.last_spline
        self.update_spline(spline_x, spline_y, first_call=True)
        self.fade_duration = fade_duration
        self.use_gait_phase = use_gait_phase  # if False, use time (s)
        super().update_controller_gains(Kp=Kp, Ki=Ki, Kd=Kd, ff=ff)
        # Fade timer goes from 0 to fade_duration, active if below fade_duration (starts inactive)
        self.fade_start_time = time.perf_counter()-100
        self.t0 = None

    def command(self, reset=False):
        '''Commands appropriate control. If reset=True, this controller was just switched to.'''
        if reset:
            super().command_gains()
            self.t0 = time.perf_counter()

        if self.use_gait_phase:
            phase = self.exo.data.gait_phase
        else:
            phase = time.perf_counter()-self.t0

        if phase is None:
            # Gait phase is sometimes None
            desired_torque = 0
        elif phase > self.spline_x[-1]:
            # If phase (elapsed time) is longer than spline is specified, use last spline point
            print('phase is longer than specified spline')
            desired_torque = self.spline(self.spline_x)
        elif time.perf_counter() - self.fade_start_time < self.fade_duration:
            # If fading splines
            desired_torque = self.fade_splines(
                phase=phase, fraction=(time.perf_counter()-self.fade_start_time)/self.fade_duration)
        else:
            desired_torque = self.spline(phase)
        print('before command_torque', desired_torque)
        self.exo.command_torque(desired_torque)

    def update_spline(self, spline_x, spline_y, first_call=False):
        if first_call or self.spline_x != spline_x or self.spline_y != spline_y:
            self.spline_x = spline_x
            self.spline_y = spline_y
            print('Splines updated: ', 'x = ', spline_x, 'y = ', spline_y)
            self.fade_start_time = time.perf_counter()
            self.last_spline = copy.deepcopy(self.spline)
            self.spline = interpolate.pchip(
                spline_x, spline_y, extrapolate=False)

    def fade_splines(self, phase, fraction):
        torque_from_last_spline = self.last_spline(phase)
        torque_from_current_spline = self.spline(phase)
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
                 bias_torque: float = 5,
                 use_gait_phase: bool = True,
                 peak_hold_time: float = 0):
        '''Inherits from GenericSplineController, and adds a update_spline_with_list function.'''
        self.bias_torque = bias_torque  # Prevents rounding issues near zero and keeps cord taught
        self.peak_hold_time = peak_hold_time  # can be used to hold a peak
        super().__init__(exo=exo,
                         spline_x=self._get_spline_x(
                             rise_fraction, peak_fraction, fall_fraction),
                         spline_y=self._get_spline_y(peak_torque),
                         Kp=Kp, Ki=Ki, Kd=Kd, ff=ff,
                         fade_duration=fade_duration,
                         use_gait_phase=use_gait_phase)

    def update_ctrl_params_from_config(self, config: Type[config_util.ConfigurableConstants]):
        'Updates controller parameters from the config object.'''
        super().update_spline(spline_x=self._get_spline_x(rise_fraction=config.RISE_FRACTION,
                                                          peak_fraction=config.PEAK_FRACTION,
                                                          fall_fraction=config.FALL_FRACTION),
                              spline_y=self._get_spline_y(peak_torque=config.PEAK_TORQUE))

    def _get_spline_x(self, rise_fraction, peak_fraction, fall_fraction) -> list:
        if self.peak_hold_time > 0:
            return [0, rise_fraction, peak_fraction, peak_fraction+self.peak_hold_time, fall_fraction, 1]
        else:
            return [0, rise_fraction, peak_fraction, fall_fraction, 10]

    def _get_spline_y(self, peak_torque) -> list:
        if self.peak_hold_time > 0:
            return [self.bias_torque, self.bias_torque, peak_torque, peak_torque, self.bias_torque, self.bias_torque]
        else:
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
        '''This controller uses voltage control to get to zero slack, checking for a cutoff..

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
            self.delay_timer.start()
        self.exo.command_voltage(
            desired_mV=self.exo.motor_sign * self.reel_in_mV)

    def check_completion_status(self):
        if self.delay_timer.check() or self.exo.get_slack() < self.slack_cutoff:
            self.delay_timer.reset()
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
                 ff: int = 0,
                 max_reel_out_time: float = 0.2,
                 force_timer_to_complete: bool = False):
        '''This controller uses position control with low gains to reach the desired slack.'''
        self.exo = exo
        super().update_controller_gains(Kp=Kp, Ki=Ki, Kd=Kd, ff=ff)
        self.desired_slack = desired_slack
        # set maximum time for controller
        self.delay_timer = util.DelayTimer(delay_time=max_reel_out_time)
        self.force_timer_to_complete = force_timer_to_complete

    def command(self, reset=False):
        if reset:
            super().command_gains()
            self.delay_timer.start()
        self.exo.command_slack(desired_slack=self.desired_slack)

    def check_completion_status(self):
        slack = self.exo.get_slack()
        return (not self.force_timer_to_complete and
                slack > self.desired_slack-500) or self.delay_timer.check()


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
