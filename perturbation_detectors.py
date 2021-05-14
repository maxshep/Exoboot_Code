import exoboot
from typing import Type
import util
import custom_filters


class SlipDetectorAP():
    def __init__(self,
                 data_container: Type[exoboot.Exo.DataContainer],
                 acc_threshold_x: float = 0.5,
                 time_out: float = 5,
                 max_acc_y: float = 0.2,
                 max_acc_z: float = 0.2):
        self.data_container = data_container
        self.acc_threshold_x = acc_threshold_x
        self.max_acc_y = max_acc_y
        self.max_acc_z = max_acc_z
        self.timer = util.DelayTimer(time_out, true_until=True)
        self.accel_x_filter = custom_filters.Butterworth(
            N=2, Wn=[0.01, 0.30], btype='bandpass')
        self.accel_y_filter = custom_filters.Butterworth(
            N=2, Wn=[0.01, 0.30], btype='bandpass')
        self.accel_z_filter = custom_filters.Butterworth(
            N=2, Wn=[0.01, 0.30], btype='bandpass')

    def detect(self):
        accel_x_filt = self.accel_x_filter.filter(self.data_container.accel_x)
        accel_y_filt = self.accel_y_filter.filter(self.data_container.accel_y)
        accel_z_filt = self.accel_z_filter.filter(self.data_container.accel_z)
        self.data_container.gen_var1 = accel_x_filt
        self.data_container.gen_var2 = accel_y_filt
        self.data_container.gen_var3 = accel_z_filt

        if (-1*self.data_container.accel_x > self.acc_threshold_x and
            abs(self.data_container.accel_y-1) < + self.max_acc_y and
                abs(self.data_container.accel_z) < self.max_acc_z and
                not self.timer.check()):
            self.timer.start()
            self.data_container.did_slip = True
            # print('slip detected!')
        else:
            self.data_container.did_slip = False


if __name__ == '__main__':
    import time
    data = exoboot.Exo.DataContainer()
    slip_detector = SlipDetectorAP(data, time_out=0.05)
    accel_x = [0, -0.5, -1.2, -1.5, -1.1, -0.5]
    accel_y = [1, 1, 0.85, 1, 1, 1]
    accel_z = [0, 0, 0, 0, 0, 0]

    for i in range(len(accel_x)):
        time.sleep(0.1)
        data.accel_x = accel_x[i]
        data.accel_y = accel_y[i]
        data.accel_z = accel_z[i]
        slip_detector.detect()
        print(data.did_slip)
