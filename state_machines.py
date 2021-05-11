import numpy as np
from exoboot import Exo
import controllers
import custom_filters
import gait_state_estimators
import constants
from typing import Type


class StanceSwingStateMachine():
    '''Unilateral state machine that takes in data, segments strides, and applies controllers'''

    def __init__(self,
                 exo: Exo,
                 stance_controller: Type[controllers.Controller],
                 swing_controller: Type[controllers.Controller]
                 ):
        '''A state machine object is associated with an exo, and reads/stores exo data, applies logic to
        determine gait states and phases, chooses the correct controllers, and applies the
        controller.'''
        self.exo = exo
        self.stance_controller = stance_controller
        self.swing_controller = swing_controller
        self.controller_now = self.swing_controller

    def step(self, read_only=False):
        # Check state machine transition criteria, switching controller_now if criteria are met
        if (self.controller_now == self.swing_controller and
            self.exo.data.did_heel_strike and
                self.exo.data.gait_phase is not None):
            self.controller_now = self.stance_controller
            did_controllers_switch = True
        elif self.exo.data.did_toe_off or self.exo.data.gait_phase is None:
            self.controller_now = self.swing_controller
            did_controllers_switch = True
        else:
            did_controllers_switch = False

        if not read_only:
            self.controller_now.command(reset=did_controllers_switch)


class StanceSwingReeloutReelinStateMachine():
    '''Unilateral state machine that takes in data, segments strides, and applies controllers'''

    def __init__(self,
                 exo: Exo,
                 stance_controller: Type[controllers.Controller],
                 swing_controller: Type[controllers.Controller],
                 reel_out_controller: Type[controllers.Controller],
                 reel_in_controller: Type[controllers.Controller]
                 ):
        '''A state machine object is associated with an exo, and reads/stores exo data, applies logic to
        determine gait states and phases, chooses the correct controllers, and applies the
        controller.'''
        self.exo = exo
        self.stance_controller = stance_controller
        self.swing_controller = swing_controller
        self.reel_out_controller = reel_out_controller
        self.reel_in_controller = reel_in_controller
        self.controller_now = self.swing_controller

    def step(self, read_only=False):
        # Check state machine transition criteria, switching controller_now if criteria are met
        if (self.controller_now == self.swing_controller and
            self.exo.data.did_heel_strike and
                self.exo.data.gait_phase is not None):
            self.controller_now = self.reel_in_controller
            did_controllers_switch = True
        elif self.controller_now == self.reel_in_controller and self.reel_in_controller.check_completion_status():
            self.controller_now = self.stance_controller
            did_controllers_switch = True
        elif self.controller_now == self.stance_controller and (self.exo.data.did_toe_off or self.exo.data.gait_phase is None):
            self.controller_now = self.reel_out_controller
            did_controllers_switch = True
        elif self.controller_now == self.reel_out_controller and self.reel_out_controller.check_completion_status():
            self.controller_now = self.swing_controller
            did_controllers_switch = True
        else:
            did_controllers_switch = False

        if not read_only:
            self.controller_now.command(reset=did_controllers_switch)
