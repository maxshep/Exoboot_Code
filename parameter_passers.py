import threading
from typing import Type
import config_util


class ParameterPasser(threading.Thread):
    def __init__(self,
                 lock: Type[threading.Lock],
                 config: Type[config_util.ConfigurableConstants],
                 quit_event: Type[threading.Event],
                 new_ctrl_params_event: Type[threading.Event],
                 new_gait_state_params_event: Type[threading.Event],
                 name='keyboard-input-thread'):
        '''This class passes parameters via user input and a parallel thread.

        The general idea is that this thread waits for an input, then grabs a lock (to stop the main thread),
        checks if the message follows the "code" (starts with 'v', ends with '!'), and then updates config
        params, depending on which params your child class wants updated. Then it sets the new_param_event flag
        to signal to the main loop to update the controllers'''
        super().__init__(name=name)
        self.daemon = True  # Thread property
        self.lock = lock
        self.config = config
        self.quit_event = quit_event
        self.new_ctrl_params_event = new_ctrl_params_event
        self.new_gait_state_params_event = new_gait_state_params_event
        self.start()  # Starts the run() function

    # This run function overrides the run() function in threading.Thread
    def run(self):
        while True:
            msg = input()
            if msg == 'a':
                self.lock.acquire()
                self.config.SLIP_DETECT_ACTIVE = not self.config.SLIP_DETECT_ACTIVE
                self.new_gait_state_params_event.set()
                self.lock.release()
            elif len(msg) < 3:
                print('Message must be either "quit" or a string of parameters'
                      ' starting with a letter (v for splines, k for stiffness,'
                      ' s for setpoint) and ending with an exclamation point)')
            elif msg.lower() == 'quit':
                print('Quitting')
                self.lock.acquire()
                self.quit_event.set()
                self.lock.release()
                break
            elif msg[-1] == '!':
                self.lock.acquire()
                first_letter = msg[0]
                msg_content = msg[1:-1]

                if first_letter == 'v':
                    param_list = [float(x) for x in msg_content.split(',')]
                    if len(param_list) != 4:
                        print('Must send four spline points with v<>! message')
                    else:
                        self.config.RISE_FRACTION = param_list[0]
                        self.config.PEAK_TORQUE = param_list[1]
                        self.config.PEAK_FRACTION = param_list[2]
                        self.config.FALL_FRACTION = param_list[3]
                        print('Parameters sent')
                elif first_letter == 'k':
                    if msg_content.isdigit():
                        self.config.K_VAL = int(msg_content)
                        print('k_val updated to: ', msg_content)
                    else:
                        print('Must provide single positive integer to update k_val')
                elif first_letter == 's':
                    if msg_content.lstrip('-').isdigit():
                        self.config.SET_POINT = int(msg_content)
                        print('SET_POINT updated to: ', msg_content)
                    else:
                        print('Must provide single integer to update SET_POINT')
                elif first_letter == 'p':
                    if msg_content.isdigit():
                        if 0 <= int(msg_content) <= 40:
                            self.config.PEAK_TORQUE = int(msg_content)
                            print('peak torque set to: ',
                                  self.config.PEAK_TORQUE)
                    else:
                        print('Must provide single integer to update PEAK_TORQUE')
                self.new_ctrl_params_event.set()
                self.lock.release()

            else:
                print('IDK how to interpret your message')
