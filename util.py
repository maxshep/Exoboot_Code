import sys
import os
import time
import constants


class DelayTimer():
    def __init__(self, delay_time):
        self.delay_time = delay_time
        self.start_time = None

    def set_start(self):
        '''Starts the timer.'''
        self.start_time = time.perf_counter()

    def check(self):
        '''Returns True if elapsed time since set_start() if greater than delay_time.'''
        if self.start_time is not None and time.perf_counter() > self.start_time + self.delay_time:
            self.start_time = None
            return True
        else:
            return False

    def reset(self):
        self.start_time = None


class FlexibleTimer():
    '''A timer that attempts to reach consistent desired freq by variable pausing.'''

    def __init__(self, target_freq):
        self.target_period = 1/target_freq
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
