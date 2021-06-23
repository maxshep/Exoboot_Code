import numpy as np
import gait_state_estimators
import unittest
import matplotlib.pyplot as plt
from exoboot import Exo
import filters


class TestGaitEventDetectors(unittest.TestCase):

    def test_GyroHeelStrikeDetector(self):
        data = Exo.DataContainer()
        gyro_signal = [0, 0, 0, 1, 3, 5, 1, 2, 0, 0, 0]
        heel_strike_detector = gait_state_estimators.GyroHeelStrikeDetector(
            height=2.5, gyro_filter=filters.PassThroughFilter())
        did_heel_strikes = []
        for gyro_val in gyro_signal:
            data.gyro_z = gyro_val
            did_heel_strikes.append(
                heel_strike_detector.detect(data))
        self.assertEqual(did_heel_strikes, [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])

    def test_StrideAverageGaitPhaseEstimator(self):
        '''Simultaneously runs roughly simulated gyro through heel strike detector,
         toe off detector, gait phase estimator. Requires looking at the plot to
         confirm.'''
        data = Exo.DataContainer()
        sampling_freq = 100
        time_nows = 1/sampling_freq * np.arange(0, 1300)
        # about 1 heel strike per second
        gyro_values = 0.5*np.sin(6*time_nows + 0.3*np.sin(10*time_nows))
        gyro_values = gyro_values[:len(gyro_values)-300]
        gyro_values = np.append(gyro_values, [0]*300)

        heel_strike_detector = gait_state_estimators.GyroHeelStrikeDetector(
            height=0.3, gyro_filter=filters.Butterworth(N=2, Wn=0.4))
        gait_phase_estimator = gait_state_estimators.StrideAverageGaitPhaseEstimator(
            num_strides_required=4, min_allowable_stride_duration=0.6, max_allowable_stride_duration=1.3)
        toe_off_detector = gait_state_estimators.GaitPhaseBasedToeOffDetector(
            fraction_of_gait=0.6)
        gait_event_detector = gait_state_estimators.GaitStateEstimator(
            data_container=data,
            heel_strike_detector=heel_strike_detector,
            gait_phase_estimator=gait_phase_estimator,
            toe_off_detector=toe_off_detector)
        did_heel_strikes = []
        gait_phases = []
        did_toe_offs = []
        for time_now, gyro_value in zip(time_nows, gyro_values):
            data.gyro_z = gyro_value
            gait_event_detector.detect()
            did_heel_strikes.append(data.did_heel_strike)
            gait_phases.append(data.gait_phase)
            did_toe_offs.append(data.did_toe_off)
        plt.plot(did_heel_strikes, label="heel strike")
        plt.plot(gait_phases, label='gait phase', linestyle='--')
        plt.plot(did_toe_offs, label='toe off')
        plt.plot(gyro_values, label='gyro')
        plt.legend()
        plt.show()


if __name__ == '__main__':
    unittest.main()
