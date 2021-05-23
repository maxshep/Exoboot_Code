import numpy as np
import custom_filters
import exoboot
from scipy import signal
from collections import deque
import time
import constants
from typing import Type
import util
import config_util


class GaitStateEstimator():
    def __init__(self,
                 data_container: Type[exoboot.Exo.DataContainer],
                 heel_strike_detector,
                 gait_phase_estimator,
                 toe_off_detector,
                 do_print_heel_strikes: bool = False,
                 do_print_toe_offs: bool = False,
                 side: Type[constants.Side] = constants.Side.NONE):
        '''Looks at the exo data, applies logic to detect HS, gait phase, and TO, and adds to exo.data'''
        self.side = side
        self.data_container = data_container
        self.heel_strike_detector = heel_strike_detector
        self.gait_phase_estimator = gait_phase_estimator
        self.toe_off_detector = toe_off_detector
        self.do_print_heel_strikes = do_print_heel_strikes
        self.do_print_toe_offs = do_print_toe_offs

    def detect(self):
        data = self.data_container  # For convenience
        data.did_heel_strike = self.heel_strike_detector.detect(data)
        data.gait_phase = self.gait_phase_estimator.estimate(data)
        data.did_toe_off = self.toe_off_detector.detect(data)
        if self.do_print_heel_strikes and data.did_heel_strike:
            print('heel strike detected on side: ', self.side)
        if self.do_print_toe_offs and data.did_toe_off:
            print('toe off detected on side: ', self.side)


class MLGaitStateEstimator():
    def __init__(self,
                 side: Type[constants.Side],
                 data_container: Type[exoboot.Exo.DataContainer],
                 heel_strike_detector,
                 gait_phase_estimator,
                 toe_off_detector):
        '''Looks at the exo data, applies logic to detect HS, gait phase, and TO, and adds to exo.data'''
        self.side = side
        self.data_container = data_container
        self.heel_strike_detector = heel_strike_detector
        self.gait_phase_estimator = gait_phase_estimator
        self.toe_off_detector = toe_off_detector

    def detect(self, data: Type[exoboot.Exo.DataContainer], do_print_heel_strikes=True, do_print_toe_offs=False):
        data = self.data_container  # For convenience
        data.did_heel_strike = self.heel_strike_detector.detect(data)
        data.gait_phase = self.gait_phase_estimator.estimate(data)
        data.did_toe_off = self.toe_off_detector.detect(data)
        if do_print_heel_strikes and data.did_heel_strike:
            print('heel strike detected on side: ', self.side)
        if do_print_toe_offs and data.did_toe_off:
            print('toe off detected on side: ', self.side)


class GyroHeelStrikeDetector():
    def __init__(self, height: float, gyro_filter: Type[custom_filters.Filter], delay=0):
        self.height = height
        self.gyro_filter = gyro_filter
        self.gyro_history = deque([0, 0, 0], maxlen=3)
        self.delay = delay
        self.timer_active = False

    def detect(self, data: Type[exoboot.Exo.DataContainer]):
        self.gyro_history.appendleft(self.gyro_filter.filter(data.gyro_z))
        if (self.timer_active is False and
            self.gyro_history[1] > self.height and
            self.gyro_history[1] > self.gyro_history[0] and
                self.gyro_history[1] > self.gyro_history[2]):
            self.timer_active = True
            self.time_of_last_heel_strike = time.perf_counter()
            return False
        elif self.timer_active and time.perf_counter() - self.time_of_last_heel_strike > self.delay:
            self.timer_active = False
            return True
        else:
            return False


class AnkleAngleBasedToeOffDetector():
    def __init__(self, target_freq, threshold: float = 4, min_phase: float = 0.5):
        '''Uses peak plantarflexion angle to determine toe-off. Warning--does not work well when actuated!'''
        self.threshold = threshold
        self.min_phase = min_phase
        self.ankle_angle_history = deque([0, 0, 0], maxlen=3)
        self.ankle_angle_filter = custom_filters.Butterworth(
            N=2, Wn=10/(target_freq/2))

    def detect(self, data: Type[exoboot.Exo.DataContainer]):
        self.ankle_angle_history.appendleft(
            self.ankle_angle_filter.filter(data.ankle_angle))
        data.accel_x = self.ankle_angle_history[0]
        if data.gait_phase is None:
            did_toe_off = False
        elif (data.gait_phase > self.min_phase and
              self.ankle_angle_history[1] > self.threshold and
                self.ankle_angle_history[1] > self.ankle_angle_history[0] and
              self.ankle_angle_history[1] > self.ankle_angle_history[2]):
            did_toe_off = True
        else:
            did_toe_off = False
        return did_toe_off


class GaitPhaseBasedToeOffDetector():
    def __init__(self, fraction_of_gait):
        '''Uses gait phase estimated from heel strikes to estimate toe-off.'''
        self.fraction_of_gait = fraction_of_gait
        self.has_toe_off_occurred = False

    def detect(self, data: Type[exoboot.Exo.DataContainer]):
        gait_phase = data.gait_phase
        if gait_phase is None:
            did_toe_off = False
        else:
            if gait_phase < self.fraction_of_gait:
                self.has_toe_off_occurred = False
            if gait_phase > self.fraction_of_gait and self.has_toe_off_occurred is False:
                did_toe_off = True
                self.has_toe_off_occurred = True
            else:
                did_toe_off = False
        return did_toe_off


class StrideAverageGaitPhaseEstimator():
    '''Calculates gait phase based on average of recent stride durations.'''

    def __init__(self,
                 num_strides_required: int = 2,
                 num_strides_to_average: int = 2,
                 min_allowable_stride_duration: float = 0.6,
                 max_allowable_stride_duration: float = 2):
        ''' Returns gait phase, which is either None or in [0, 1]
        Arguments:
        num_strides_required: int, number of acceptable strides in a row before gait is deemed steady
        num_strides_to_average: int, number of strides to average
        min_allowable_stride_duration: minimum allowable duration of a stride
        max_allowable_stride_duration: maximum allowable duration of a stride
        Returns: gait_phase, which is either None or in [0, 1].'''
        if num_strides_required < 1:
            raise ValueError('num_strides_required must be >= 1')
        if num_strides_to_average > num_strides_required:
            raise ValueError(
                'num_strides_to_average must be >= num_strides_required')
        self.num_strides_required = num_strides_required
        self.min_allowable_stride_duration = min_allowable_stride_duration
        self.max_allowable_stride_duration = max_allowable_stride_duration
        self.time_of_last_heel_strike = 0  # something a long time ago
        self.last_stride_durations = deque(
            [1000] * self.num_strides_required, maxlen=self.num_strides_required)
        self.stride_duration_filter = custom_filters.MovingAverage(
            window_size=num_strides_to_average)

    def estimate(self, data: Type[exoboot.Exo.DataContainer]):
        time_now = time.perf_counter()
        if data.did_heel_strike:
            stride_duration = time_now - self.time_of_last_heel_strike
            self.last_stride_durations.append(stride_duration)
            self.time_of_last_heel_strike = time_now
            self.mean_stride_duration = self.stride_duration_filter.filter(
                stride_duration)

        time_since_last_heel_strike = time_now - self.time_of_last_heel_strike
        if all(self.min_allowable_stride_duration < last_stride_duration
                < self.max_allowable_stride_duration for last_stride_duration
                in self.last_stride_durations) and (time_since_last_heel_strike
                                                    < 1.2 * self.max_allowable_stride_duration):
            gait_phase = min(1, time_since_last_heel_strike /
                             self.mean_stride_duration)
        else:
            gait_phase = None
        return gait_phase


class SlipDetectorAP():
    def __init__(self,
                 data_container: Type[exoboot.Exo.DataContainer],
                 acc_threshold_x: float = 0.2,
                 time_out: float = 5,
                 max_acc_y: float = 0.1,
                 max_acc_z: float = 0.1,
                 do_filter_accels=True):
        '''Last working with 0.5, 0.2, 0.2, no filter.'''
        self.data_container = data_container
        self.acc_threshold_x = acc_threshold_x
        self.max_acc_y = max_acc_y
        self.max_acc_z = max_acc_z
        self.timer = util.DelayTimer(time_out, true_until=True)
        self.do_filter_accels = do_filter_accels
        self.accel_x_filter = custom_filters.Butterworth(
            N=2, Wn=0.01, btype='high')
        self.accel_y_filter = custom_filters.Butterworth(
            N=2, Wn=0.01, btype='high')
        self.accel_z_filter = custom_filters.Butterworth(
            N=2, Wn=0.01, btype='high')
        self.slip_detect_active = False
        print('slip_detect_active: ', self.slip_detect_active)

    def detect(self):
        accel_x = self.data_container.accel_x
        accel_y = self.data_container.accel_y-1  # Remove effect of gravity
        accel_z = self.data_container.accel_z
        if self.do_filter_accels:
            accel_x = self.accel_x_filter.filter(accel_x)
            accel_y = self.accel_y_filter.filter(accel_y)
            accel_z = self.accel_z_filter.filter(accel_z)
            self.data_container.gen_var1 = accel_x
            self.data_container.gen_var2 = accel_y
            self.data_container.gen_var3 = accel_z

        if (self.slip_detect_active and
            accel_x < -1*self.acc_threshold_x and
            abs(accel_y) < + self.max_acc_y and
                abs(accel_z) < self.max_acc_z and
                not self.timer.check()):
            self.timer.start()
            self.data_container.did_slip = True
        else:
            self.data_container.did_slip = False

    def update_params_from_config(self, config: Type[config_util.ConfigurableConstants]):
        print('slip detection_active: ', config.SLIP_DETECT_ACTIVE)
        self.slip_detect_active = config.SLIP_DETECT_ACTIVE
