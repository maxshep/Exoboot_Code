import sys
import os
import time
import constants


class DelayTimer():
    def __init__(self, delay_time, true_until: bool = False):
        '''
        A timer

        Args:
            delay_time: amount of time to delay
            true_until: option to make the timer go True until delay_time is reached, then False
        '''
        self.delay_time = delay_time
        self.true_until = true_until
        self.start_time = None

    def start(self):
        '''Starts the timer.'''
        self.start_time = time.perf_counter()

    def check(self):
        '''Depending on true_until, will either go True when time is hit, or go False when time is hit.'''
        if self.true_until:
            if self.start_time is not None and time.perf_counter() < self.start_time + self.delay_time:
                return True
            else:
                return False
        else:
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
        if self.over_time > 30:
            # raise Exception('Target Frequency is not being hit')
            print('Waning: Target Frequency is not being hit!')
            self.over_time = 0
        while time.perf_counter()-self.last_time < self.target_period:
            pass
        self.last_time = time.perf_counter()
