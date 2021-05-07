import unittest
import util
import time
import random
from matplotlib import pyplot as plt


class Test_timer(unittest.TestCase):

    def test_single_time(self):
        custom_timer = util.FlexibleTimer(target_frequency=2)
        t0 = time.time()
        custom_timer.pause()
        t1 = time.time()-t0
        print(t1)
        self.assertAlmostEqual(t1, 0.5, places=2)

    def test_timer(self):
        custom_timer = util.FlexibleTimer(target_frequency=100)
        periods = []
        delays = []
        for _ in range(500):
            t0 = time.perf_counter()
            random_delay = 0.001*random.randint(1, 11)
            time.sleep(random_delay)
            delays.append(time.perf_counter()-t0)
            custom_timer.pause()
            periods.append(time.perf_counter()-t0)
        plt.plot(delays)
        plt.plot(periods)
        plt.show()


if __name__ == '__main__':
    unittest.main()
