
import config_util
config = config_util.ConfigurableConstants()
config.TASK = config_util.Task.SLIPDETECTFROMSYNC
config.STANCE_CONTROL_STYLE = config_util.StanceCtrlStyle.FOURPOINTSPLINE

config.DO_DETECT_SLIP = True
config.RISE_FRACTION = 0.001
config.PEAK_FRACTION = 0.05
config.FALL_FRACTION = 0.2
config.PEAK_TORQUE = 15
config.SPLINE_BIAS = 0.5  # Nm
config.DO_READ_SYNC = True
config.READ_ONLY = False


''' Here are the variables that are updatable in config, and their defaults:

    TARGET_FREQ: float = 200  # Hz
    ACTPACK_FREQ: float = 200  # Hz
    DO_DEPHY_LOG: bool = True
    DEPHY_LOG_LEVEL: int = 4
    TASK: Type[Task] = Task.WALKING
    STANCE_CONTROL_STYLE: Type[StanceCtrlStyle] = StanceCtrlStyle.FOURPOINTSPLINE
    MAX_ALLOWABLE_CURRENT = 20000  # mA

    # Gait State details
    HS_GYRO_THRESHOLD: float = 100
    HS_GYRO_FILTER_N: int = 2
    HS_GYRO_FILTER_WN: float = 3
    HS_GYRO_DELAY: float = 0.05
    SWING_SLACK: int = 10000
    TOE_OFF_FRACTION: float = 0.62
    REEL_IN_TIMEOUT: float = 0.2

    # 4 point Spline
    RISE_FRACTION: float = 0.2
    PEAK_FRACTION: float = 0.53
    FALL_FRACTION: float = 0.63
    PEAK_TORQUE: float = 5
    SPLINE_BIAS: float = 3  # Nm

    # Impedance
    K_VAL: int = 500
    B_VAL: int = 0
    SET_POINT: float = 0  # Deg

    READ_ONLY = False  # Does not require Lipos
    DO_READ_FSRS = False

    PRINT_HS = True  # Print heel strikes
    SLIP_DETECT_ACTIVE = False
'''
