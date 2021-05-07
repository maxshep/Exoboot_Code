import controllers
import unittest
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


class Test_PositionController(unittest.TestCase):

    def test_spline_controller(self):
        spline_x = [0, 0.2, 0.5, 0.6, 1]
        spline_y = [0, 6, 10, 0, 0]
        spline_controller = controllers.GenericSplineController(
            Kp=100, Ki=20, Kd=0,
            spline_x=spline_x, spline_y=spline_y)
        time_nows = np.arange(0, 10, 0.01)
        gait_phases = 0.5+0.5*(signal.sawtooth(t=time_nows, width=1))
        desired_currents = []
        for gait_phase in gait_phases:
            desired_currents.append(spline_controller.command(gait_phase))
        plt.plot(gait_phases)
        plt.plot(desired_currents)
        plt.show()

    def test_spline_fade(self):
        spline_controller = controllers.FourPointSplineController(exo)


if __name__ == '__main__':
    unittest.main()
