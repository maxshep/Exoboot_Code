from gpiozero import Button  # pylint: disable=import-error
import constants
import time

left_heel_FSR = Button(constants.LEFT_HEEL_FSR_PIN)
left_toe_FSR = Button(constants.LEFT_TOE_FSR_PIN)
right_heel_FSR = Button(constants.RIGHT_HEEL_FSR_PIN)
right_toe_FSR = Button(constants.RIGHT_TOE_FSR_PIN)

while True:
    print('Left heel: ', left_heel_FSR.is_pressed, 'Left toe: ', left_toe_FSR.is_pressed,
          'Right heel: ', right_heel_FSR.is_pressed, 'Right toe: ', right_toe_FSR.is_pressed)
    time.sleep(0.25)
