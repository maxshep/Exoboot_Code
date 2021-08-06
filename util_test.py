import unittest
import util
import time
import random
from matplotlib import pyplot as plt


class Test_timer(unittest.TestCase):

    def test_delay_timer(self):
        delay_timer1 = util.DelayTimer(delay_time=0.5)
        delay_timer2 = util.DelayTimer(delay_time=0.5, true_until=True)
        vals1 = []
        vals2 = []
        for i in range(300):
            time.sleep(0.01)
            vals1.append(delay_timer1.check())
            vals2.append(delay_timer2.check()+1.5)
            if i == 50:
                delay_timer1.start()
                delay_timer2.start()
            if i == 250:
                delay_timer1.reset()
                delay_timer2.reset()
        plt.plot(vals1)
        plt.plot(vals2)
        plt.show()

    # def test_single_time(self):
    #     custom_timer = util.FlexibleTimer(target_freq=2)
    #     t0 = time.time()
    #     custom_timer.pause()
    #     t1 = time.time()-t0
    #     print(t1)
    #     self.assertAlmostEqual(t1, 0.5, places=2)

    # def test_timer(self):
    #     custom_timer = util.FlexibleTimer(target_freq=100)
    #     periods = []
    #     delays = []
    #     for _ in range(500):
    #         t0 = time.perf_counter()
    #         random_delay = 0.001*random.randint(1, 11)
    #         time.sleep(random_delay)
    #         delays.append(time.perf_counter()-t0)
    #         custom_timer.pause()
    #         periods.append(time.perf_counter()-t0)
    #     plt.Figure()
    #     plt.plot(delays)
    #     plt.plot(periods)
    #     plt.show()


if __name__ == '__main__':
    unittest.main()
