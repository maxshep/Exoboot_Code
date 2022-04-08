'''This module holds constants and enums that are not intended to change'''
import numpy as np
from enum import Enum

DEFAULT_BAUD_RATE = 230400
TARGET_FREQ = 200
#EB-45
MAX_ANKLE_ANGLE = 90 ## degrees, plantarflexion
MIN_ANKLE_ANGLE = -45 # degrees, dorsiflexion
"""
#EB-51
MAX_ANKLE_ANGLE = 90 
MIN_ANKLE_ANGLE = -80
"""
# These polynomials are derived from the calibration routine (calibrate.py), analyzed with transmission_analysis.py
#EB-45
LEFT_ANKLE_TO_MOTOR = [ 1.42930145e-05,  9.60847697e-04,  9.66033271e-03,  1.21997272e+00,
 -7.39600859e+02, -2.96580581e+04]
RIGHT_ANKLE_TO_MOTOR = [-1.02595964e-05, -9.28352253e-04, -3.10556810e-02, -1.40767218e+00,
  7.57989378e+02, -3.48608044e+03]
"""
#EB-51
LEFT_ANKLE_TO_MOTOR = np.array([-7.19610056e-06,  5.13458100e-04,  8.00853528e-02,  1.58183515e+00,
 -7.24239201e+02, -6.23886726e+04])
RIGHT_ANKLE_TO_MOTOR = np.array([-2.43806787e-06, -4.51986529e-04, -3.88528665e-02, -1.15282680e+00,
  5.96404385e+02,  9.85245200e+03])
"""
# These points are used to create a Pchip spline, which defines the transmission ratio as a function of ankle angle
#EB-45
ANKLE_PTS = np.array([-40, -20, 0, 10, 20, 30, 40, 45.6, 50, 55])  # Deg
TR_PTS = np.array([19, 17, 16.5, 15.5, 13.5, 10, 4, -1, -5, -11 ])  # Nm/Nm
"""
#EB-51
ANKLE_PTS = np.array([-60, -40, -20, -10 ,0, 10, 20, 30, 40, 45.6, 55, 80])
TR_PTS = np.array([18, 13.5, 14.5, 14.9,15, 13.8, 11.5, 7.9, 3.9, 0.8, -3.6, -13])
"""
# TODO: attempt to change the manual picking of ANKLE_PTS and TR_PTS
# LEFT_ANKLE_TO_TR = np.array([ 5.00380707e-07,  8.20159320e-05,  2.53334311e-03,  5.29066571e-02,
#  -1.64252746e+01])
# RIGHT_ANKLE_TO_TR = np.array([ 4.83188447e-07, -3.83712114e-05, -3.61934700e-03,  4.54812251e-01,
#        -2.89416189e+01]) ## NEED TO CHANGE FOR RIGHT ANKLE

#EB-45
LEFT_ANKLE_ANGLE_OFFSET = 201#-92  # 7,
RIGHT_ANKLE_ANGLE_OFFSET = -150#-200# deg
"""
#EB-51
LEFT_ANKLE_ANGLE_OFFSET = -92  # deg
RIGHT_ANKLE_ANGLE_OFFSET = 88.9 #100  # deg
"""
# Add to these lists if dev_ids change, or new exos or actpacks are purchased!
RIGHT_EXO_DEV_IDS = [77] # for the old (EB-45) Exo 
#RIGHT_EXO_DEV_IDS = [17584] #for EB-51
LEFT_EXO_DEV_IDS = [888] #for the old (EB-45) Exo 
#LEFT_EXO_DEV_IDS = [48390] # for EB-51
MS_TO_SECONDS = 0.001
# Converts raw Dephy encoder output to degrees
K_TO_NM_PER_DEGREE = 0  #
B_TO_NM_PER_DEGREE_PER_S = 0

ENC_CLICKS_TO_DEG = 1/(2**14/360)
# Getting the motor current to motor torque conversion is tricky, and any updates to
# the firmware should confirm that Dephy has not changed their internal current units.
# This constant assumes we are using q-axis current.
MOTOR_CURRENT_TO_MOTOR_TORQUE = 0.000146  # mA to Nm

# Dephy units to deg/s --experimentally estimated because their numbers are wrong
DEPHY_VEL_TO_MOTOR_VEL = 0.025*ENC_CLICKS_TO_DEG

# ankle_torque ~ AVERAGE_TRANSMISSION_RATIO*motor_torque
AVERAGE_TRANSMISSION_RATIO = 14  # Used to roughly map motor to ankle impedance

# https://dephy.com/wiki/flexsea/doku.php?id=controlgains
DEPHY_K_CONSTANT = 0.00078125
DEPHY_B_CONSTANT = 0.0000625
# Multiply Dephy's k_val by this to get a motor stiffness in Nm/deg
DEPHY_K_TO_MOTOR_K = MOTOR_CURRENT_TO_MOTOR_TORQUE / (ENC_CLICKS_TO_DEG *
                                                      DEPHY_K_CONSTANT)
# Multiply Dephy's k_val by this to get an estimate of ankle stiffness in Nm/deg
DEPHY_K_TO_ANKLE_K = AVERAGE_TRANSMISSION_RATIO**2 * DEPHY_K_TO_MOTOR_K

# Inferred from https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/
ACCEL_GAIN = 1 / 8192  # LSB -> gs
# Inferred from https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/
GYRO_GAIN = 1 / 32.75  # LSB -> deg/s

LOGGING_FREQ = 200
# Dephy recommends as a starting point: Kp=250, Ki=200, Kd=0, FF=100
# DEFAULT_KP = 300  # updated from 250 on 3/10/2021
# DEFAULT_KI = 360  # updated from 250 on 3/10/2021
# DEFAULT_KD = 5
DEFAULT_KP = 40
DEFAULT_KI = 400
DEFAULT_KD = 0
# Feedforward term. "0 is 0% and 128 (possibly unstable!) is 100%."
DEFAULT_FF = 120  # 126
DEFAULT_SWING_KP = 150
DEFAULT_SWING_KI = 50
DEFAULT_SWING_KD = 0
DEFAULT_SWING_FF = 0

# TODO(maxshep) raise these when it seems safe
MAX_ALLOWABLE_VOLTAGE_COMMAND = 3000  # mV
MAX_ALLOWABLE_CURRENT_COMMAND = 25000  # mA
MAX_ALLOWABLE_K_COMMAND = 8000  # Dephy Internal Units
MAX_ALLOWABLE_B_COMMAND = 5500  # NOT TESTED!


class Side(Enum):
    RIGHT = 1
    LEFT = 2
    NONE = 3


# RPi's GPIO pin numbers (not physical pin number) for FSR testing
LEFT_HEEL_FSR_PIN = 17
LEFT_TOE_FSR_PIN = 18
RIGHT_HEEL_FSR_PIN = 24
RIGHT_TOE_FSR_PIN = 25

# RPi's GPIO pin numbers (not physical pin number) for Sync signal
SYNC_PIN = 16
