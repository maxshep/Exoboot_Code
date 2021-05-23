from typing import Type
import config_util
import state_machines
import perturbation_detectors
import gait_state_estimators
import exoboot
import custom_filters
import controllers


def get_gait_state_estimator(exo: exoboot.Exo,
                             config: Type[config_util.ConfigurableConstants]):
    '''Uses info from the config option to build a gait_state_estimator for a single exo.
    Refactored out of main_loop for readability.'''
    if (config.HIGH_LEVEL_CTRL_STYLE == config_util.CtrlStyle.FOURPOINTSPLINE or
            config.HIGH_LEVEL_CTRL_STYLE == config_util.CtrlStyle.SAWICKIWICKI):
        heel_strike_detector = gait_state_estimators.GyroHeelStrikeDetector(
            height=config.HS_GYRO_THRESHOLD,
            gyro_filter=custom_filters.Butterworth(N=config.HS_GYRO_FILTER_N,
                                                   Wn=config.HS_GYRO_FILTER_WN,
                                                   fs=config.TARGET_FREQ),
            delay=config.HS_GYRO_DELAY)
        gait_phase_estimator = gait_state_estimators.StrideAverageGaitPhaseEstimator()
        toe_off_detector = gait_state_estimators.GaitPhaseBasedToeOffDetector(
            fraction_of_gait=config.TOE_OFF_FRACTION)
        gait_state_estimator = gait_state_estimators.GaitStateEstimator(
            side=exo.side,
            data_container=exo.data,
            heel_strike_detector=heel_strike_detector,
            gait_phase_estimator=gait_phase_estimator,
            toe_off_detector=toe_off_detector,
            do_print_heel_strikes=config.PRINT_HS)

    elif config.HIGH_LEVEL_CTRL_STYLE == config_util.CtrlStyle.STANDINGPERTURBATION:
        gait_state_estimator = gait_state_estimators.SlipDetectorAP(
            data_container=exo.data)  # acc_threshold_x=0.35, time_out=5, max_acc_y=0.25, max_acc_z=0.25

    else:
        raise ValueError('Unknown CtrlStyle for get_gait_state_estimator')

    return gait_state_estimator


def get_state_machine(exo: exoboot.Exo,
                      config: Type[config_util.ConfigurableConstants]):
    '''Uses info from the config option to build a state_machine for a single exo.
    Refactored out of main_loop for readability.'''
    if config.HIGH_LEVEL_CTRL_STYLE == config_util.CtrlStyle.FOURPOINTSPLINE:
        reel_in_controller = controllers.BallisticReelInController(
            exo=exo, time_out=config.REEL_IN_TIMEOUT)
        swing_controller = controllers.StalkController(
            exo=exo, desired_slack=config.SWING_SLACK)
        reel_out_controller = controllers.SoftReelOutController(
            exo=exo, desired_slack=config.SWING_SLACK)
        stance_controller = controllers.FourPointSplineController(
            exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
            peak_fraction=config.PEAK_FRACTION,
            fall_fraction=config.FALL_FRACTION,
            bias_torque=config.SPLINE_BIAS)
        state_machine = state_machines.StanceSwingReeloutReelinStateMachine(exo=exo,
                                                                            stance_controller=stance_controller,
                                                                            swing_controller=swing_controller,
                                                                            reel_in_controller=reel_in_controller,
                                                                            reel_out_controller=reel_out_controller)
    elif config.HIGH_LEVEL_CTRL_STYLE == config_util.CtrlStyle.SAWICKIWICKI:
        reel_in_controller = controllers.BallisticReelInController(
            exo=exo, time_out=config.REEL_IN_TIMEOUT)
        swing_controller = controllers.StalkController(
            exo=exo, desired_slack=config.SWING_SLACK)
        reel_out_controller = controllers.SoftReelOutController(
            exo=exo, desired_slack=config.SWING_SLACK)
        stance_controller = controllers.SawickiWickiController(
            exo=exo, k_val=config.K_VAL)
        state_machine = state_machines.StanceSwingReeloutReelinStateMachine(exo=exo,
                                                                            stance_controller=stance_controller,
                                                                            swing_controller=swing_controller,
                                                                            reel_in_controller=reel_in_controller,
                                                                            reel_out_controller=reel_out_controller)

    elif config.HIGH_LEVEL_CTRL_STYLE == config_util.CtrlStyle.STANDINGPERTURBATION:
        slip_controller = controllers.GenericImpedanceController(
            exo=exo, setpoint=config.SET_POINT, k_val=config.K_VAL)
        standing_controller = controllers.GenericImpedanceController(
            exo=exo, setpoint=10, k_val=100)
        state_machine = state_machines.StandingPerturbationResponse(exo=exo,
                                                                    standing_controller=standing_controller,
                                                                    slip_controller=slip_controller)
    else:
        raise ValueError('Unknown CtrlStyle for get_state_machine')

    return state_machine
