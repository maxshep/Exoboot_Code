import config_util
args = config_util.parse_args()
config = config_util.load_config(args.config)
print(config)
