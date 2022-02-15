import sys
import os
pardir = os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/preference_learning_dephy_exo/online_optimization'
print(pardir)
sys.path.append(pardir)
import main_loop
