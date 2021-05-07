import sys
import os
import time
import constants
from flexseapython import fxUtil, pyFlexsea


def load_ports_and_baudrate_from_com():
    if sys.platform == 'win32':		# Need for WebAgg server to work in Python 3.8
        print('Detected win32')
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        scriptPath = os.path.dirname(os.path.abspath(__file__))
        fpath = scriptPath + '/flexseapython/com.txt'
        portList, baudRate = fxUtil.loadPortsFromFile(fpath)
        baudRate = int(baudRate)
    else:
        # Assume raspberry pi for now  TODO(maxshep)
        # WHY DID THEY STICK THIS NECESSARY FUNCTION IN THEIR STUPID LOADPORTSFROMFILE FUNCTION
        # Doing this here so we can avoid touching their loadportsfromfile
        pyFlexsea.loadFlexsea()
        # To my knowledge it's always this...
        portList = ['/dev/ttyACM0', '/dev/ttyACM1']
        baudRate = 230400
    return portList, baudRate


class DelayTimer():
    def __init__(self, delay_time):
        self.delay_time = delay_time
        self.start_time = None

    def set_start(self):
        self.start_time = time.perf_counter()

    def check(self):
        if self.start_time is not None and time.perf_counter() > self.start_time + self.delay_time:
            self.start_time = None
            return True
        else:
            return False


class FlexibleTimer():
    '''A timer that attempts to reach consistent desired frequency by variable pausing.'''

    def __init__(self, target_frequency):
        self.target_period = 1/target_frequency
        self.last_time = time.perf_counter()
        self.over_time = 0

    def pause(self):
        if time.perf_counter()-self.last_time > self.target_period:
            # Penalty for cycle going over time
            self.over_time += 1
        else:
            # liberal reset for every good period
            self.over_time = max(0, self.over_time - 5)
            # Error out if target freqeuncy is not being hit
        if self.over_time > 20:
            raise Exception('Target Frequency is not being hit')
        while time.perf_counter()-self.last_time < self.target_period:
            pass
        self.last_time = time.perf_counter()
