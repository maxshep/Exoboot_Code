from typing import Type
import config_util
import state_machines
import gait_state_estimators
import exoboot
import filters
import controllers


def get_do_bilateral_data(config: Type[config_util.ConfigurableConstants]):
    if config.TASK == config_util.Task.STANDINGPERTURBATION:
        print('yoyoyo')
        return False
    else:
        return False


def get_gse_and_sm_lists(exo_list, config: Type[config_util.ConfigurableConstants]):
    '''depending on config, uses exo list to create gait state estimator and state machine lists.'''
    gait_state_estimator_list = []
    state_machine_list = []
    if config.TASK == config_util.Task.WALKING:
        for exo in exo_list:
            heel_strike_detector = gait_state_estimators.GyroHeelStrikeDetector(
                height=config.HS_GYRO_THRESHOLD,
                gyro_filter=filters.Butterworth(N=config.HS_GYRO_FILTER_N,
                                                Wn=config.HS_GYRO_FILTER_WN,
                                                fs=config.TARGET_FREQ),
                delay=config.HS_GYRO_DELAY)
            gait_phase_estimator = gait_state_estimators.StrideAverageGaitPhaseEstimator(
                num_strides_required=config.NUM_STRIDES_REQUIRED)
            toe_off_detector = gait_state_estimators.GaitPhaseBasedToeOffDetector(
                fraction_of_gait=config.TOE_OFF_FRACTION)
            gait_state_estimator = gait_state_estimators.GaitStateEstimator(
                side=exo.side,
                data_container=exo.data,
                heel_strike_detector=heel_strike_detector,
                gait_phase_estimator=gait_phase_estimator,
                toe_off_detector=toe_off_detector,
                do_print_heel_strikes=config.PRINT_HS)
            gait_state_estimator_list.append(gait_state_estimator)

            # Define State Machine
            reel_in_controller = controllers.SmoothReelInController(
                exo=exo, reel_in_mV=config.REEL_IN_MV, slack_cutoff=config.REEL_IN_SLACK_CUTOFF, time_out=config.REEL_IN_TIMEOUT)
            swing_controller = controllers.StalkController(
                exo=exo, desired_slack=config.SWING_SLACK)
            reel_out_controller = controllers.SoftReelOutController(
                exo=exo, desired_slack=config.SWING_SLACK)
            if config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.FOURPOINTSPLINE:
                stance_controller = controllers.FourPointSplineController(
                    exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
                    peak_fraction=config.PEAK_FRACTION,
                    fall_fraction=config.FALL_FRACTION,
                    bias_torque=config.SPLINE_BIAS)
            elif config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.SAWICKIWICKI:
                stance_controller = controllers.SawickiWickiController(
                    exo=exo, k_val=config.K_VAL, b_val=config.B_VAL)
            state_machine = state_machines.StanceSwingReeloutReelinStateMachine(exo=exo,
                                                                                stance_controller=stance_controller,
                                                                                swing_controller=swing_controller,
                                                                                reel_in_controller=reel_in_controller,
                                                                                reel_out_controller=reel_out_controller)
            state_machine_list.append(state_machine)

    # elif config.TASK == config_util.Task.STANDINGPERTURBATION:
    #     for exo in exo_list:
    #         gait_state_estimator = gait_state_estimators.SlipDetectorAP(
    #             data_container=exo.data)
    #         gait_state_estimator_list.append(gait_state_estimator)
    #         standing_controller = controllers.GenericImpedanceController(
    #             exo=exo, setpoint=10, k_val=100)
    #         if config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.GENERICIMPEDANCE:
    #             slip_controller = controllers.GenericImpedanceController(
    #                 exo=exo, setpoint=config.SET_POINT, k_val=config.K_VAL)
    #             slip_recovery_time = 1.01  # TODO(maxshep)
    #         elif config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.FOURPOINTSPLINE:
    #             print("using a spline based controller!")
    #             slip_controller = controllers.FourPointSplineController(
    #                 exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
    #                 peak_fraction=config.PEAK_FRACTION,
    #                 fall_fraction=config.FALL_FRACTION,
    #                 bias_torque=config.SPLINE_BIAS,
    #                 use_gait_phase=False)
    #             # slip_recovery_time = config.FALL_FRACTION-0.01
    #             slip_recovery_time = 0.99
    #         elif config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.FIVEPOINTSPLINE:
    #             print("using a spline based controller!")
    #             slip_controller = controllers.FourPointSplineController(
    #                 exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
    #                 peak_fraction=config.PEAK_FRACTION,
    #                 fall_fraction=config.FALL_FRACTION,
    #                 bias_torque=config.SPLINE_BIAS,
    #                 use_gait_phase=False,
    #                 peak_hold_time=0.1)
    #             slip_recovery_time = 0.99

    #         state_machine = state_machines.StandingPerturbationResponse(exo=exo,
    #                                                                     standing_controller=standing_controller,
    #                                                                     slip_controller=slip_controller,
    #                                                                     slip_recovery_time=slip_recovery_time)
    #         state_machine_list.append(state_machine)

    elif config.TASK == config_util.Task.SLIPDETECTFROMSYNC:
        if len(exo_list) != 2:
            raise ValueError(
                'Must have two exos connected for task=BILATERALSTANDINGPERTURBATION')
        gait_phase_estimator = gait_state_estimators.BilateralSlipDetectorFromSync(
            exo_1=exo_list[0], exo_2=exo_list[1])
        gait_state_estimator_list.append(gait_phase_estimator)
        for exo in exo_list:
            standing_controller = controllers.GenericImpedanceController(
                exo=exo, setpoint=10, k_val=100)
            if config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.GENERICIMPEDANCE:
                slip_controller = controllers.GenericImpedanceController(
                    exo=exo, setpoint=config.SET_POINT, k_val=config.K_VAL)
                slip_recovery_time = 1.01  # TODO(maxshep)
            elif config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.FOURPOINTSPLINE:
                print("using a spline based controller!")
                slip_controller = controllers.FourPointSplineController(
                    exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
                    peak_fraction=config.PEAK_FRACTION,
                    fall_fraction=config.FALL_FRACTION,
                    bias_torque=config.SPLINE_BIAS,
                    use_gait_phase=False)
                # slip_recovery_time = config.FALL_FRACTION-0.01
                slip_recovery_time = 0.99

            elif config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.FIVEPOINTSPLINE:
                print("using a spline based controller!")
                slip_controller = controllers.FourPointSplineController(
                    exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
                    peak_fraction=config.PEAK_FRACTION,
                    fall_fraction=config.FALL_FRACTION,
                    bias_torque=config.SPLINE_BIAS,
                    use_gait_phase=False,
                    peak_hold_time=0.1)
                slip_recovery_time = 0.99

            state_machine = state_machines.StandingPerturbationResponse(exo=exo,
                                                                        standing_controller=standing_controller,
                                                                        slip_controller=slip_controller,
                                                                        slip_recovery_time=slip_recovery_time)
            state_machine_list.append(state_machine)

    elif config.TASK == config_util.Task.BILATERALSTANDINGPERTURBATION:
        if len(exo_list) != 2:
            raise ValueError(
                'Must have two exos connected for task=BILATERALSTANDINGPERTURBATION')
        gait_phase_estimator = gait_state_estimators.BilateralSlipDetectorIMU(
            exo_1=exo_list[0], exo_2=exo_list[1])
        gait_state_estimator_list.append(gait_phase_estimator)
        for exo in exo_list:
            standing_controller = controllers.GenericImpedanceController(
                exo=exo, setpoint=10, k_val=100)
            if config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.GENERICIMPEDANCE:
                slip_controller = controllers.GenericImpedanceController(
                    exo=exo, setpoint=config.SET_POINT, k_val=config.K_VAL)
                slip_recovery_time = 1.01  # TODO(maxshep)
            elif config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.FOURPOINTSPLINE:
                print("using a spline based controller!")
                slip_controller = controllers.FourPointSplineController(
                    exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
                    peak_fraction=config.PEAK_FRACTION,
                    fall_fraction=config.FALL_FRACTION,
                    bias_torque=config.SPLINE_BIAS,
                    use_gait_phase=False)
                # slip_recovery_time = config.FALL_FRACTION-0.01
                slip_recovery_time = 0.99

            elif config.STANCE_CONTROL_STYLE == config_util.StanceCtrlStyle.FIVEPOINTSPLINE:
                print("using a spline based controller!")
                slip_controller = controllers.FourPointSplineController(
                    exo=exo, rise_fraction=config.RISE_FRACTION, peak_torque=config.PEAK_TORQUE,
                    peak_fraction=config.PEAK_FRACTION,
                    fall_fraction=config.FALL_FRACTION,
                    bias_torque=config.SPLINE_BIAS,
                    use_gait_phase=False,
                    peak_hold_time=0.1)
                slip_recovery_time = 0.99

            state_machine = state_machines.StandingPerturbationResponse(exo=exo,
                                                                        standing_controller=standing_controller,
                                                                        slip_controller=slip_controller,
                                                                        slip_recovery_time=slip_recovery_time)
            state_machine_list.append(state_machine)

    return gait_state_estimator_list, state_machine_list
