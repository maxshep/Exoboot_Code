'''This module holds constants and enums that are not intended to change'''
import numpy as np
from enum import Enum
from typing import Type

class ExobootModel(Enum):
    EB45 = 0
    EB51 = 1

ExoType : Type[ExobootModel] = ExobootModel.EB51
#ExoType = Type[ExobootModel] = ExobootModel.EB45

DEFAULT_BAUD_RATE = 230400
TARGET_FREQ = 200
if(ExoType == ExobootModel.EB45):
  #EB-45
  MAX_ANKLE_ANGLE = 90 ## degrees, plantarflexion
  MIN_ANKLE_ANGLE = -45 # degrees, dorsiflexion

  # These polynomials are derived from the calibration routine (calibrate.py), analyzed with transmission_analysis.py
  LEFT_ANKLE_TO_MOTOR = [ 1.42930145e-05,  9.60847697e-04,  9.66033271e-03,  1.21997272e+00,
  -7.39600859e+02, -2.96580581e+04]
  RIGHT_ANKLE_TO_MOTOR = [-1.02595964e-05, -9.28352253e-04, -3.10556810e-02, -1.40767218e+00,
  7.57989378e+02, -3.48608044e+03]

  # These points are used to create a Pchip spline, which defines the transmission ratio as a function of ankle angle
  ANKLE_PTS_LEFT = np.array([-40, -20, 0, 10, 20, 30, 40, 45.6, 50, 55])  # Deg
  TR_PTS_LEFT = np.array([19, 17, 16.5, 15.5, 13.5, 10, 4, -1, -5, -11 ])  # Nm/Nm

  ANKLE_PTS_RIGHT = np.array([-40, -20, 0, 10, 20, 30, 40, 45.6, 50, 55])  # Deg
  TR_PTS_RIGHT = np.array([19, 17, 16.5, 15.5, 13.5, 10, 4, -1, -5, -11 ])  # Nm/Nm

  LEFT_ANKLE_ANGLE_OFFSET = 201#-92  # 7,
  RIGHT_ANKLE_ANGLE_OFFSET = -150#-200# deg
 
elif(ExoType == ExobootModel.EB51):

  #EB-51
  MAX_ANKLE_ANGLE = 130 
  MIN_ANKLE_ANGLE = -95

  #EB-51
  LEFT_ANKLE_TO_MOTOR = np.array([-2.32052284e-06,  6.29683551e-05,  4.45431399e-02,  3.09556691e+00,
  -5.49941515e+02, -1.11211736e+04])
  RIGHT_ANKLE_TO_MOTOR = np.array([ 5.37977952e-06, -2.76399833e-04, -7.58092528e-02, -1.65003833e+00,
    6.38860770e+02,  9.21647151e+03])

  #EB-51
  ANKLE_PTS_LEFT = np.array([-67, -60, -40, -20, -10 ,0, 10, 20, 30, 40, 45.6, 55, 80, 90, 100])
  TR_PTS_LEFT = np.array([14.85, 14, 13.8, 13.7, 13.16, 12, 10.43, 8, 5.5, 2.3, 0.4, -3.3, -10, -11.30, -10.95])
  
  
  ANKLE_PTS_RIGHT = np.array([-67, -60, -50, -40, -20, -10 ,0, 10, 20, 30, 40, 45.6, 55, 80, 90])
  TR_PTS_RIGHT = np.array([15.5, 13.35, 11.95, 12.03, 13.82, 14.3, 13.96, 12.77, 10.56, 7.1, 3.19, 0.4, -3.78, -11.94, -12.3])


  # TODO: attempt to change the manual picking of ANKLE_PTS and TR_PTS
  # LEFT_ANKLE_TO_TR = np.array([ 5.00380707e-07,  8.20159320e-05,  2.53334311e-03,  5.29066571e-02,
  #  -1.64252746e+01])
  # RIGHT_ANKLE_TO_TR = np.array([ 4.83188447e-07, -3.83712114e-05, -3.61934700e-03,  4.54812251e-01,
  #        -2.89416189e+01]) ## NEED TO CHANGE FOR RIGHT ANKLE

  #EB-51
  LEFT_ANKLE_ANGLE_OFFSET = -67  # deg
  RIGHT_ANKLE_ANGLE_OFFSET = 87.1 #100  # deg

# Add to these lists if dev_ids change, or new exos or actpacks are purchased!

RIGHT_EXO_DEV_IDS = [77, 17584] #for EB-51

LEFT_EXO_DEV_IDS = [888, 48390] # for EB-51
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
