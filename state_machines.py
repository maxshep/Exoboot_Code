from typing import Type

import numpy as np

import constants
import controllers
import filters
import gait_state_estimators
from exoboot import Exo
import util


class HighLevelController():
    '''A class that steps through controllers depending on, for instance, gait events.'''

    def __init__(self,
                 exo: Type[Exo]):
        self.exo = exo

    def step(self, read_only):
        '''Primary function to step through mid-level controllers.'''
        raise ValueError('step() not written yet for this controller')

    def update_ctrl_params_from_config(self, config):
        '''A function to update mid-level control params from the config object.'''
        raise ValueError(
            'update_ctrl_params_from_config() not written yet for this controller')


class StandingPerturbationResponse(HighLevelController):
    '''Pass through high level controller that implements standing perturbation response.'''

    def __init__(self,
                 exo: Type[Exo],
                 standing_controller: Type[controllers.Controller],
                 slip_controller: Type[controllers.Controller],
                 slip_recovery_time: float = 1.5):
        self.exo = exo
        self.standing_controller = standing_controller
        self.slip_controller = slip_controller
        self.slip_ctrl_timer = util.DelayTimer(delay_time=slip_recovery_time)
        self.controller_now = self.standing_controller

    def step(self, read_only):
        '''uses slip detector to detect slip onset, uses timer to stop slip controller.'''

        if self.slip_ctrl_timer.check():
            if self.exo.side == constants.Side.LEFT:
                print('slip timeout--moving back now')
            # If slip controller time has elapsed (goes True) and we need to switch back
            self.slip_ctrl_timer.reset()
            self.controller_now = self.standing_controller
            did_controllers_switch = True
        elif self.exo.data.did_slip:
            if self.exo.side == constants.Side.LEFT:
                print('slip detected, moving to slip controller')
            self.slip_ctrl_timer.start()
            self.controller_now = self.slip_controller
            did_controllers_switch = True
            print(type(self.slip_controller))
        else:
            did_controllers_switch = False

        if not read_only:
            self.controller_now.command(reset=did_controllers_switch)

    def update_ctrl_params_from_config(self, config):
        self.slip_controller.update_ctrl_params_from_config(config=config)


class BilateralSlipStateMachine(HighLevelController):
    '''Bilateral state machine that takes in 2 data containers and applies control.'''

    def __init__(self,
                 left_exo: Type[Exo],
                 right_exo: Type[Exo],
                 left_standing_controller: Type[controllers.Controller],
                 right_standing_controller: Type[controllers.Controller],
                 left_slip_controller: Type[controllers.Controller],
                 right_slip_controller: Type[controllers.Controller],
                 slip_recovery_time: float = 1.5):
        self.left_exo = left_exo
        self.right_exo = right_exo
        self.left_standing_controller = left_standing_controller
        self.right_standing_controller = left_standing_controller
        self.left_slip_controller = left_slip_controller
        self.right_slip_controller = right_slip_controller
        self.slip_ctrl_timer = util.DelayTimer(delay_time=slip_recovery_time)
        self.left_controller_now = self.left_standing_controller
        self.right_controller_now = self.right_standing_controller

    def step(self, read_only):
        '''uses slip detector to detect slip onset, uses timer to stop slip controller.'''

        if self.slip_ctrl_timer.check():
            print('Slip timeout--ready now')
            # If slip controller time has elapsed (goes True) and we need to switch back
            self.slip_ctrl_timer.reset()
            self.left_controller_now = self.left_standing_controller
            self.right_controller_now = self.right_standing_controller
            did_controllers_switch = True
        elif self.left_exo.data.did_slip or self.right_exo.data.did_slip:
            print('Slip detected, moving to slip controller')
            self.left_exo.data.did_slip = True  # Set both to True
            self.right_exo.data.did_slip = True  # Set both to True
            self.slip_ctrl_timer.start()
            self.left_controller_now = self.left_slip_controller
            self.right_controller_now = self.right_slip_controller
            did_controllers_switch = True
        else:
            did_controllers_switch = False

        if not read_only:
            self.left_controller_now.command(reset=did_controllers_switch)
            self.right_controller_now.command(reset=did_controllers_switch)


class StanceSwingStateMachine(HighLevelController):
    '''Unilateral state machine that takes in data, segments strides, and applies controllers'''

    def __init__(self,
                 exo: Type[Exo],
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

    def update_ctrl_params_from_config(self, config):
        self.stance_controller.update_ctrl_params_from_config(config=config)


class StanceSwingReeloutReelinStateMachine(HighLevelController):
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
        self.controller_now = self.reel_out_controller
        self.just_starting = True

    def step(self, read_only=False):
        # Check state machine transition criteria, switching controller_now if criteria are met
        if self.just_starting:
            self.controller_now = self.reel_out_controller
            self.just_starting = False
            did_controllers_switch = True
        elif (self.controller_now == self.swing_controller and
              self.exo.data.did_heel_strike and
                self.exo.data.gait_phase is not None):
            self.controller_now = self.reel_in_controller
            did_controllers_switch = True
            self.exo.data.gen_var1 = 4
        elif self.controller_now == self.reel_in_controller and self.reel_in_controller.check_completion_status():
            self.controller_now = self.stance_controller
            did_controllers_switch = True
            self.exo.data.gen_var1 = 1
        elif self.controller_now == self.stance_controller and (self.exo.data.did_toe_off or self.exo.data.gait_phase is None):
            self.controller_now = self.reel_out_controller
            did_controllers_switch = True
            self.exo.data.gen_var1 = 2
        elif self.controller_now == self.reel_out_controller and self.reel_out_controller.check_completion_status():
            self.controller_now = self.swing_controller
            did_controllers_switch = True
            self.exo.data.gen_var1 = 3

        else:
            did_controllers_switch = False

        if not read_only:
            self.controller_now.command(reset=did_controllers_switch)

    def update_ctrl_params_from_config(self, config):
        self.stance_controller.update_ctrl_params_from_config(config=config)
