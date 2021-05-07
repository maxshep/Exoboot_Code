from scipy import signal
import numpy as np
import collections


class Filter(object):
    '''Parent class for filters, to help with type hinting. 

    Note: for filter modularity, all child classes should have a filter() 
    function that takes only the most recent value. This way, different custom_filters 
    can be passed to objects constructors without replacing that class's code'''

    def filter(self, new_val):
        raise ValueError('filter() not implemented for child class of Filter')


class PassThroughFilter(Filter):
    def filter(self, new_val):
        return new_val


class Butterworth(Filter):
    '''Implements a real-time Butterworth filter using second orded cascaded custom_filters.'''

    def __init__(self, N: int, Wn: float, btype='low', fs=None):
        ''' 
        N: order
        Wn: (default) normalized cutoff frequency (cutoff freq / Nyquist freq). If fs is passed, cutoff is in freq.
        btyple: 'low', 'high', or 'bandpass'
        fs: Optional: sample freq, Hz. If not None, Wn describes the cutoff frequency in Hz
        '''
        self.N = N
        if fs is not None:
            self.Wn = Wn/(fs/2)
        else:
            self.Wn = Wn
        self.btype = btype
        self.sos = signal.butter(N=self.N, Wn=self.Wn,
                                 btype=self.btype, output='sos')
        self.zi = signal.sosfilt_zi(self.sos)

    def filter(self, new_val: float) -> float:
        filtered_val, self.zi = signal.sosfilt(
            sos=self.sos, x=[new_val], zi=self.zi)
        return filtered_val[0]


class MovingAverage(Filter):
    '''Implements a real-time moving average filter.'''

    def __init__(self, window_size):
        self.deque = collections.deque([], maxlen=window_size)

    def filter(self, new_val):
        # Optimize for efficiency is window size is large
        self.deque.append(new_val)
        return np.mean(self.deque)
