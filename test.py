# myls.py
# Import the argparse library
import argparse

import os
import sys

# Create the parser
my_parser = argparse.ArgumentParser(prog='Exoboot Code',
                                    description='Run Exoboot Controllers',
                                    epilog='Enjoy the program! :)')

# Add the arguments
my_parser.add_argument('-c', '--config', action='store',
                       type=str, required=False, default='default_config')


# Execute the parse_args() method
args = my_parser.parse_args()

print(args.config)
