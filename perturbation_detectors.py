import exo
from typing import Type
import util


class SlipDetectorAP():
    def __init__(self,
                 data_container: Type[exo.Exo.DataContainer],
                 acc_threshold_x: float = 0.5,
                 time_out: float = 1.1,
                 max_acc_y: float = 0.2,
                 max_acc_z: float = 0.2):
        self.data_container = data_container
        self.acc_threshold_x = acc_threshold_x
        self.max_acc_y = max_acc_y
        self.max_acc_z = max_acc_z
        self.timer = util.DelayTimer(time_out)

    def detect(self):
        if (self.data_container.acc_x > self.acc_threshold_x and
            self.data_container.acc_y < 1 + self.max_acc_y and
                self.data_container.acc_z < self.max_acc_z and
                not self.timer.check()):
            self.timer.set_start()
            return True
        else:
            return False
