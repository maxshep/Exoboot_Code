import unittest

import numpy as np
from scipy import signal

import filters


class Test_custom_filters(unittest.TestCase):

    def test_Butterworth(self):
        # Ensure the realtime filter behaves like scipy.sosfilt
        x = (np.arange(250) < 100).astype(int).tolist()
        sos = signal.butter(4, 0.1, output='sos')
        zi = signal.sosfilt_zi(sos)
        y, _ = signal.sosfilt(sos, x, zi=zi)

        test_filter = filters.Butterworth(N=4, Wn=0.1)
        # Simulate data coming in real time
        y_real_time_filter = []
        for new_val in x:
            y_real_time_filter.append(test_filter.filter(new_val))

        self.assertListEqual(y.tolist(), y_real_time_filter)

    def test_MovingAverageFilter(self):
        test_filter = filters.MovingAverage(window_size=3)
        test_signal = [0, 1, 5, 3, 4, -10, 3, 6, 0]
        correct_answer = [0, 0.5, 2, 3, 4, -1, -1, -1/3, 3]
        filtered_answer = []
        for signal_value in test_signal:
            filtered_answer.append(test_filter.filter(signal_value))
        for true_val, test_val in zip(correct_answer, filtered_answer):
            self.assertAlmostEqual(true_val, test_val)


if __name__ == '__main__':
    unittest.main()
