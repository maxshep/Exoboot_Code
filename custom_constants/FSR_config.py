import config_util
config = config_util.ConfigurableConstants()
config.READ_ONLY = False
config.DO_READ_FSRS = True

''' Here are the variables that are updatable in config, and their defaults:

    TARGET_FREQ: float = 200  # Hz
    ACTPACK_FREQ: float = 200  # Hz
    CONTROL_ARCHITECTURE: Type[ControlArchitecture] = ControlArchitecture.FOURPOINTSPLINE
    HS_GYRO_THRESHOLD: float = 100
    HS_GYRO_FILTER_N: int = 2
    HS_GYRO_FILTER_WN: float = 3
    HS_GYRO_DELAY: float = 0.05

    SWING_SLACK: int = 10000
    TOE_OFF_FRACTION: float = 0.62

    # 4 point Spline
    RISE_FRACTION: float = 0.2
    PEAK_FRACTION: float = 0.53
    FALL_FRACTION: float = 0.63
    PEAK_TORQUE: float = 5

    # Impedance
    k_val: int = 500
    b_val: int = 0

    READ_ONLY = False  # Does not require Lipos
    DO_READ_FSRS = False

    PRINT_HS = True  # Print heel strikes
    '''
