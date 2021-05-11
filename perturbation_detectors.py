import exoboot
from typing import Type
import util


class SlipDetectorAP():
    def __init__(self,
                 data_container: Type[exoboot.Exo.DataContainer],
                 acc_threshold_x: float = 0.5,
                 time_out: float = 1.1,
                 max_acc_y: float = 0.2,
                 max_acc_z: float = 0.2):
        self.data_container = data_container
        self.acc_threshold_x = acc_threshold_x
        self.max_acc_y = max_acc_y
        self.max_acc_z = max_acc_z
        self.timer = util.DelayTimer(time_out, true_until=True)

    def detect(self):
        if (self.data_container.accel_x > self.acc_threshold_x and
            abs(self.data_container.accel_y-1) < + self.max_acc_y and
                abs(self.data_container.accel_z) < self.max_acc_z and
                not self.timer.check()):
            self.timer.set_start()
            return True
        else:
            return False


if __name__ == '__main__':
    import time
    data = exoboot.Exo.DataContainer()
    slip_detector = SlipDetectorAP(data, time_out=0.05)
    accel_x = [0, 0.5, 1.2, 1.5, 1.1, 0.5]
    accel_y = [1, 1, 0.85, 1, 1, 1]
    accel_z = [0, 0, 0, 0, 0, 0]

    for i in range(len(accel_x)):
        time.sleep(0.1)
        data.accel_x = accel_x[i]
        data.accel_y = accel_y[i]
        data.accel_z = accel_z[i]
        slip = slip_detector.detect()
        print(slip)
