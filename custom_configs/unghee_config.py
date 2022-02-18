import config_util
config = config_util.ConfigurableConstants()

config.REEL_IN_MV = 100
config.SWING_SLACK = 3000
config.DO_INCLUDE_GEN_VARS = True
config.SWING_ONLY = False
config.MAX_ALLOWABLE_CURRENT = 10000  # mA
config.PEAK_TORQUE = 15
config.HS_GYRO_THRESHOLD = 10