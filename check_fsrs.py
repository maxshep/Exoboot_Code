from gpiozero import Button
import constants
import time

left_heel_FSR = Button(constants.LEFT_HEEL_FSR_PIN)
left_toe_FSR = Button(constants.LEFT_TOE_FSR_PIN)
right_heel_FSR = Button(constants.RIGHT_HEEL_FSR_PIN)
right_toe_FSR = Button(constants.RIGHT_TOE_FSR_PIN)

while True:
    if left_heel_FSR.is_pressed:
        print("Left Heel is pressed")
    if left_toe_FSR.is_pressed:
        print("Left Toe is pressed")
    if right_heel_FSR.is_pressed:
        print("Right Heel is pressed")
    if right_toe_FSR.is_pressed:
        print("Right Toe is pressed")
    time.sleep(0.5)
