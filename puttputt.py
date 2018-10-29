#!/usr/bin/python

import sys, math, time, argparse, random 
from threading import Thread
from stepper import Stepper

try:
    import RPi.GPIO as GPIO
	
    isRpi = True
except ImportError:
    print('Not RaspberryPi')
    isRpi = False

#Constants
stepsPerRev = 200 #Motor 1.8deg/step

delay1 = 0.0055
delay2 = 0.0055
reverseMotor1 = False #Switch if motor turns the wrong way
reverseMotor2 = False #Switch if motor turns the wrong way


def runMotorThread(motor, start, maxtime, numStepsPerLoop = 1):
    global stepsPerRev, delay1, delay2, reverseMotor1, reverseMotor2
	
    numStepsPerLoop = numStepsPerLoop
    delay = delay1
    
    #Reverse
    if (motor.name == 'Stepper1' and reverseMotor1) or (motor.name == 'Stepper2' and reverseMotor2):
        numStepsPerLoop *= -1
    
    #if stepper 2 then set delay2
    if motor.name == 'Stepper2':
        delay = delay2
    
    while (time.time() - start) <= maxtime:
        #TODO: maybe use queue based events as described here: https://www.raspberrypi.org/forums/viewtopic.php?t=178212
        #moveSteps(motor, 1*stepsPerRev)
        motor.step(numStepsPerLoop, delay = delay, turnOff = False)
    
    motor.turnOff()

    
def main():
    global stepsPerRev, delay1, delay2, reverseMotor1, reverseMotor2

    parser = argparse.ArgumentParser(description='Pi Putt')

    parser.add_argument('mode', choices=['once', 'voice', 'loop'], default='once', help='run mode (default: once)')
    parser.add_argument('numStepsPerLoop', type=int, default=1, help='number of steps per loop (default: 1)')    
    parser.add_argument('stepType', choices=['full', 'half', 'single'], default='full', help='step type (default: full)')
    parser.add_argument('maxtime', type=float, default=5, help='seconds to run (default: 5)')
    parser.add_argument('delay1', type=float, default=0.005, help='delay in seconds after each step of motor 1 (default: 0.005)')
    parser.add_argument('delay2', type=float, default=0.005, help='delay in seconds after each step of motor 2 (default: 0.005)')
    parser.add_argument('t1', type=float, default=0, help='the starting theta of motor 1 (default: 0)')
    parser.add_argument('t2', type=float, default=0, help='the starting theta of motor 2 (default: 0)')
    parser.add_argument('--setup', '-s', dest='setup', action='store_true', default=False, help='setup (default: False)')
    
    args = parser.parse_args()
		
    print('args:', args)
    
    mode = args.mode
    numStepsPerLoop = args.numStepsPerLoop
    stepType = args.stepType
    maxtime = args.maxtime
    t1 = args.t1
    t2 = args.t2
    delay1 = args.delay1
    delay2 = args.delay2
    
    start = time.time()
    try:
        m1 = Stepper([14,15,23,24], 'Stepper1', stepType = stepType)
        m2 = Stepper([4,17,27,22], 'Stepper2', stepType = stepType)

        #TODO: maybe use queue based events as described here: https://www.raspberrypi.org/forums/viewtopic.php?t=178212
        thread1 = Thread(target=runMotorThread, args=(m1, start, maxtime, numStepsPerLoop))
        #thread2 = Thread(target=runMotorThread, args=(m2, start, maxtime, numStepsPerLoop))

        thread1.start()
        #thread2.start()
    except KeyboardInterrupt: #From https://raspi.tv/2013/rpi-gpio-basics-3-how-to-exit-gpio-programs-cleanly-avoid-warnings-and-protect-your-pi
        print('Keyboard interupt')
    finally:
        GPIO.cleanup() # this ensures a clean exit 
        
       
#---------------------------------------------------
try:
    main()
except Except as e:
    print('Caught Exception: ', e)
