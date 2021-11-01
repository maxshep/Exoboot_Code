## Notes on working with the Dephy exoboots:
This code works with Dephy's exoboots. There are a couple pains that make this code a little more complicated: 1) it's a unidirectional actuator, so managing slack is important when you want zero torque, 2) The actpacks don't know they are part of an ankle, so raw imu, current, and angle data for left/right are flipped different directions, 3) The transmission ratio is variable, and even flips to negative around 30 deg plantarflexion, 4) both the ankle and motor use absolute encoders, but the motor spins more than 10 times through the RoM, so it doesn't know where it is within that RoM when you first turn it on, so requires calibration every time it's turned on. As such, some decisions were made and functions implemented:

1) Slack controllers have been designed to command the motor to a position that will keep a constant amount of slack.

2) motor angle (int: counts), current (int: mA), and voltage (int: mV) are kept in the actpack reference frame (ie, the sign is not flipped for consistency between left and right). However, torque (Nm) and ankle angle (deg) are consistent, with plantarflexion = positive.

3) Some protections are built in. Even though you can provide a dorsiflexion torque at highly plantarflexed angles, the code only allows requesting positive torque (plantarflexion). Torque limits thus are also a function of ankle angle, and warnings are printed when torque is being clipped by these limits.

4) A calibration routine applies a small, sign-appropriate voltage to each ankle and waits for current to rise above a threshold to indicate slack has been removed. This then calculates the appropriate offset so that the zero-slack relationship between motor angle and ankle angle is known

## Notes on the code architecture
To make the code more useable and customizable, I've organized the architecture like this:
1) Exo class, in exo.py.  This object stores variables associated with the specific exoboot, reads and writes data, and handles ALL direct ommunication with the exoboot. It should be the only interface with Dephy's scripts, flexsea.py and fxUtils.py. It also contains a number of safety checks, and some low-level control.  Notably, data associated with an exoboot is stored in a subclass "DataContainer"

2) Controllers, in controllers.py. These are like mid-level controllers, like a spline-based stance controller, that store information such as controller-specific gains and behaviors.

3) Gait State Estimators, in gait_state_estimators.py.  These take in exo-specific data from its DataContainer, and do some logic to determine things like heel strike, toe off, and gait phase.

4) State machines, in state_machines.py. These take in an exo, controllers, and a gait_state_estimator, and apply transition logic to switch between controllers.

5) Main loop, in main_loop.py. Instantiates all the gait_state_estimators and controllers, and steps through the state machine/s for the connected exo/s.


## To use this code:
Run main_loop.py, or your custom main_loop script, from the command line.
For info on running it with the pi we have setup: https://docs.google.com/document/d/1HhQxAFK55nA6wYKboyCqtMmRvlXgh4rKzXELoV7ybzg/edit?usp=sharing
Latest notes on Dephy's suggested gains and such: https://dephy.com/wiki/flexsea/doku.php?id=controlgains#typical_values

## To modify this code:
Avoid editing exo.py. There are a number of tricky things it does, particularly around sign conventions for the left and right exos. The best way to work with this code is to add controllers if necessary and state_machines, and make small modifications to main_loop.py so that it works

## To pull/push your code to/from the pi:
This is mostly for Max, since the git is linked to his github account on the pi.
navigate to Documents/Actuator-Package-Master
git pull origin
To push changes
git add .
git commit
git push something? test


## Some best practices: 
Use pylint!

When writing new functions or classes, use type hints.

When passing arguments to functions or classes, if there are more than two arguments, pass your arguments as keyword arguments. 

It should be illegal to use " import as * ". Dephy uses it in their examples--don't follow their examples. It makes it impossible for type hinting and for linters to do their jobs.

If you find yourself repeating a block of code, it should probably be a function.



