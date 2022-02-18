import csv
import constants
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy import interpolate

LEFT_ANKLE_TO_MOTOR = np.array(
    [ 4.39808862e-06, -4.36579117e-04, -5.49068346e-02,  1.03495054e+01,
 -1.31716523e+03,  4.97232882e+04])

RIGHT_ANKLE_TO_MOTOR = np.array(
    [6.53412109e-06, -5.10000261e-04, -7.52460274e-02, -1.27584877e+00,
     7.05016223e+02, -1.09811413e+04])

folder = 'exo_data/'
for filename in ["20211117_2240_calibration2_LEFT.csv"]:
    # filename = "20210616_1945_calibration2_RIGHT.csv"
    with open(folder + filename) as f:
        motor_angle = [int(row["motor_angle"])
                       for row in csv.DictReader(f)]
    with open(folder + filename) as f:
        ankle_angle = [np.floor(float(row["ankle_angle"]))
                       for row in csv.DictReader(f)]
    motor_angle = np.array(motor_angle)*constants.ENC_CLICKS_TO_DEG

    plt.figure(1)
    plt.xlabel('ankle angle')
    plt.ylabel('motor angle')
    # plt.plot(ankle_angle, motor_angle)
    # Sort the data points
    zipped_sorted_lists = sorted(zip(ankle_angle, motor_angle))
    mytuples = zip(*zipped_sorted_lists)
    ankle_angle, motor_angle = [
        list(mytuple) for mytuple in mytuples]
    plt.plot(ankle_angle, motor_angle)

    # Filter
    b, a = signal.butter(N=1, Wn=0.05)
    motor_angle = signal.filtfilt(
        b, a, motor_angle, method="gust")
    ankle_angle = signal.filtfilt(
        b, a, ankle_angle, method="gust")
    plt.plot(ankle_angle, motor_angle)

    # Calculate Gradient
    TR = np.gradient(motor_angle)/np.gradient(ankle_angle)



    plt.plot(ankle_angle, motor_angle /
                   constants.ENC_CLICKS_TO_DEG)
    # Polyfit
    p = np.polyfit(ankle_angle, motor_angle /
                   constants.ENC_CLICKS_TO_DEG, deg=5)
    print('Polynomial coefficients: ', p)
    polyfitted_left_motor_angle = np.polyval(p, ankle_angle)
    plt.plot(ankle_angle, polyfitted_left_motor_angle)

    pcurrent = LEFT_ANKLE_TO_MOTOR
    polyfitted_left_motor_angle = np.polyval(pcurrent, ankle_angle)
    plt.plot(ankle_angle, polyfitted_left_motor_angle, linestyle='dashed')

    plt.figure(2)
    p_deriv = np.polyder(p)
    TR_from_polyfit = np.polyval(p_deriv, ankle_angle)
    # plt.plot(ankle_angle, -TR_from_polyfit)

    p = np.polyfit(ankle_angle, TR, deg=4)
    deriv_left2 = np.polyval(p, ankle_angle)

    # plt.plot(ankle_angle, -TR)

    ankle_pts = [-60, -40, 0, 10, 20, 30, 40, 45.6, 55, 80]
    deriv_pts = [16, 16, 15, 14.5, 14, 11.5, 5, 0, -6.5, -12]

    deriv_spline_fit = interpolate.pchip_interpolate(
        ankle_pts, deriv_pts, ankle_angle)
    plt.plot(ankle_angle, deriv_spline_fit, linewidth=5)
    plt.xlim([-50, 80])
    plt.ylim([-22, 22])
    plt.ylabel('Transmission Ratio')
    plt.xlabel('Ankle Angle')

plt.show()
