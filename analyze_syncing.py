import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from scipy import interpolate
import constants
import filters
import exoboot
import analysis_util
import gait_state_estimators

folder = 'exo_data'
markers = ['-', '--']
print('hi')
# for i, filename in enumerate(["20210617_2351_sync6_LEFT.csv", '20210617_2351_sync6_RIGHT.csv']):
for i, filename in enumerate(["20210617_2351_sync6_LEFT.csv"]):
    data = exoboot.Exo.DataContainer()
    df = pd.read_csv(folder + '/' + filename)
    slip_detector = gait_state_estimators.SlipDetectorAP(
        data_container=data, return_did_slip=True, start_active=True)

    mydatalist = []
    for idx, row in df.iterrows():
        data = analysis_util.populate_data_container_from_series(row)
        mydatalist.append(data.__dict__)
        did_slip = slip_detector.detect()
        if did_slip:
            print('slipped!')

    new_df = pd.DataFrame(mydatalist)
    plt.figure(1)
    plt.xlabel('time')
    # plt.plot(df.loop_time, df.did_slip, color='black', linestyle=markers[i])
    # plt.plot(df.loop_time, df.heel_fsr, color='brown', linestyle=markers[i])
    plt.plot(new_df.loop_time, df.accel_x,
             color='darkred', linestyle=markers[i])
    plt.plot(df.loop_time, df.gen_var1)
    plt.plot(new_df.loop_time, new_df.gen_var1)

    # plt.plot(df.loop_time, accel_x_filt, color='green', linestyle=markers[i])
    # plt.plot(df.loop_time, df.accel_y-1,
    #          color='indianred', linestyle=markers[i])
    # plt.plot(df.loop_time, df.accel_z,
    #          color='lightcoral', linestyle=markers[i])

plt.show()
