import threading
from typing import Type
import config_util


class ParameterPasser(threading.Thread):
    def __init__(self,
                 lock: Type[threading.Lock],
                 config: Type[config_util.ConfigurableConstants],
                 quit_event: Type[threading.Event],
                 new_params_event: Type[threading.Event],
                 name='keyboard-input-thread'):
        '''This is a parent class for parallel parameter passers.

        The general idea is that this thread waits for an input, then grabs a lock (to stop the main thread),
        checks if the message follows the "code" (starts with 'v', ends with '!'), and then updates config
        params, depending on which params your child class wants updated. Then it sets the new_param_event flag
        to signal to the main loop to update the controllers'''
        super().__init__(name=name)
        self.daemon = True  # Thread property
        self.lock = lock
        self.config = config
        self.quit_event = quit_event
        self.new_params_event = new_params_event
        self.start()  # Starts the run() function

    # This run function overrides the run() function in threading.Thread
    def run(self):
        while True:
            msg = input()
            if len(msg) < 3:
                print('Message must be either "quit" or a string of parameters')
            elif msg[0] == 'v' and msg[-1] == '!':
                msg = msg[1:-1]
                param_list = [float(x) for x in msg.split(',')]
                self.lock.acquire()
                self.update_params(param_list)
                self.new_params_event.set()
                self.lock.release()
                print('Parameters sent')
            elif msg.lower() == 'quit':
                print('Quitting')
                self.lock.acquire()
                self.quit_event.set()
                self.lock.release()
                break
            else:
                print('IDK how to interpret your message')

    def update_params(self, param_list: list):
        raise ValueError(
            'No update_params function implemented yet for this parameter_passer child')


class FourPointSplineParameterPasser(ParameterPasser):
    def __init__(self,
                 lock: Type[threading.Lock],
                 config: Type[config_util.ConfigurableConstants],
                 quit_event: Type[threading.Event],
                 new_params_event: Type[threading.Event],
                 name='keyboard-input-thread'):
        super().__init__(lock=lock, config=config, quit_event=quit_event,
                         new_params_event=new_params_event, name=name)

    def update_params(self, param_list):
        self.config.RISE_FRACTION = param_list[0]
        self.config.PEAK_TORQUE = param_list[1]
        self.config.PEAK_FRACTION = param_list[2]
        self.config.FALL_FRACTION = param_list[3]


class SawickiWickiParameterPasser(ParameterPasser):
    def __init__(self,
                 lock: Type[threading.Lock],
                 config: Type[config_util.ConfigurableConstants],
                 quit_event: Type[threading.Event],
                 new_params_event: Type[threading.Event],
                 name='keyboard-input-thread'):
        super().__init__(lock=lock, config=config, quit_event=quit_event,
                         new_params_event=new_params_event, name=name)

    def update_params(self, param_list):
        self.config.k_val = int(param_list[0])


class StandingSlipControllerParameterPasser(ParameterPasser):
    def __init__(self,
                 lock: Type[threading.Lock],
                 config: Type[config_util.ConfigurableConstants],
                 quit_event: Type[threading.Event],
                 new_params_event: Type[threading.Event],
                 name='keyboard-input-thread'):
        super().__init__(lock=lock, config=config, quit_event=quit_event,
                         new_params_event=new_params_event, name=name)

    def update_params(self, param_list):
        self.config.k_val = int(param_list[0])
