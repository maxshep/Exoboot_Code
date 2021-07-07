import RPi.GPIO as GPIO # import GPIO, in the future use gpiozero module
from hx711 import HX711 # import the class HX711
from hx711 import outliers_filter
import os
from time import sleep
from datetime import datetime

# Set up file and path
path = '/media/pi/CLARK2/Research/Working_Code'
filename = 'test_data_04202021_2.csv'
file = open(path+'/'+filename,'a')

# If the file is empty, start writing in it
if os.stat(path).st_size == 0:
    file.write('Time,HX711_Data\n')
else:
    print('Old file in use, appending to previous file data...\n')
    file.write('Appending to previous file data...\n')

# Set up GPIO and connect 
GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to the BCM numbering (same as gpiozero

# Create an HX711 object and attach it to pin 21 for data and pin 20 for serial clock.
# Vcc is attached to 3.3V and Gnd to Gnd.
# There are multiple gain values for channel A, but we select the default (128).
hx1 = HX711(dout_pin=21, pd_sck_pin=20, gain_channel_A=64, select_channel='A')

# Start our "main loop"
try:
    # Read and store data continuously
    while True: 
        
        # HX711 can read 10 readings/sec, so we take 10 readings over 1 second and average them
        data = hx1.get_raw_data_mean(readings=1)

        if data:
            print('Raw data:', data)
        else:
            print('invalid data')

        # write to file with timestamp
        now = datetime.now()
        file.write(str(now)+','+str(data)+'\n')
        file.flush()

# If ctrl+c is entered we stop collecting data and close down
except (KeyboardInterrupt, SystemExit):
    print('Done')

# Clean up GPIO
finally:
    GPIO.cleanup()

