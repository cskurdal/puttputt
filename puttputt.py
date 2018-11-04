#!/usr/bin/python

import sys, math, time, argparse, random 
from threading import Thread
from stepper import Stepper

'''
Revision           : a02082 (Raspberry Pi 3)

J8:
   3V3  (1) (2)  5V    
 GPIO2  (3) (4)  5V    
 GPIO3  (5) (6)  GND   
 GPIO4  (7) (8)  GPIO14
   GND  (9) (10) GPIO15
GPIO17 (11) (12) GPIO18
GPIO27 (13) (14) GND   
GPIO22 (15) (16) GPIO23
   3V3 (17) (18) GPIO24
GPIO10 (19) (20) GND   
 GPIO9 (21) (22) GPIO25
GPIO11 (23) (24) GPIO8 
   GND (25) (26) GPIO7 
 GPIO0 (27) (28) GPIO1 
 GPIO5 (29) (30) GND   
 GPIO6 (31) (32) GPIO12
GPIO13 (33) (34) GND   
GPIO19 (35) (36) GPIO16
GPIO26 (37) (38) GPIO20
   GND (39) (40) GPIO21


Revision: 000f (Raspberry Pi 1 B)
Pinout

   3V3  (1) (2)  5V    
 GPIO2  (3) (4)  5V    
 GPIO3  (5) (6)  GND   
 GPIO4  (7) (8)  GPIO14
   GND  (9) (10) GPIO15
GPIO17 (11) (12) GPIO18
GPIO27 (13) (14) GND   
GPIO22 (15) (16) GPIO23
   3V3 (17) (18) GPIO24
GPIO10 (19) (20) GND   
 GPIO9 (21) (22) GPIO25
GPIO11 (23) (24) GPIO8 
   GND (25) (26) GPIO7 
'''

try:
    import RPi.GPIO as GPIO
	
    isRpi = True
except ImportError:
    print('Not RaspberryPi')
    isRpi = False

#Constants
delay1 = 0.005 #60RPM
delay2 = 0.005 #60RPM
reverseMotor1 = False #Switch if motor turns the wrong way
reverseMotor2 = False #Switch if motor turns the wrong way


class VelocityRPM(object):
    def __init__(self, targetRPM, seconds, stepsPerRev = 200): #Motor 1.8deg/step
        self._currentRPM = 0
        self._targetRPM = targetRPM
        self._seconds = seconds
        self._startTime = time.time()
        self._stepsPerRev = stepsPerRev
        
    def getDelay(self):
        t = time.time()
        
        if t > (self._startTime + self._seconds):
            return 60 / (self._currentRPM * self._stepsPerRev)
        else: #linear acceleration
            return (((self._startTime + t) / (self._startTime + self._seconds)) * 60) / (self._currentRPM * self._stepsPerRev)
        
    def setCurrentRPM(self, rpm):
        self._currentRPM = rpm
	
        
def runMotorThread(motor, start, maxtime, numStepsPerLoop = 1):
    global delay1, delay2, reverseMotor1, reverseMotor2
	
    numStepsPerLoop = numStepsPerLoop
    delay = delay1
    
    #Reverse
    if motor.name == 'Stepper1':
        if reverseMotor1:
            numStepsPerLoop *= -1
    
    #if stepper 2 then set delay2
    if motor.name == 'Stepper2':
        if reverseMotor2:
            numStepsPerLoop *= -1
            
        delay = delay2
        
    
    while (time.time() - start) <= maxtime:
        #TODO: maybe use queue based events as described here: https://www.raspberrypi.org/forums/viewtopic.php?t=178212
        motor.step(numStepsPerLoop, delay = delay, turnOff = False)
    
    motor.turnOff()

    
def main():
    global delay1, delay2, reverseMotor1, reverseMotor2

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

    m1 = Stepper([14,15,23,24], 'Stepper1', stepType = stepType)
    m2 = Stepper([4,17,27,22], 'Stepper2', stepType = stepType)

    #TODO: maybe use queue based events as described here: https://www.raspberrypi.org/forums/viewtopic.php?t=178212
    thread1 = Thread(target=runMotorThread, args=(m1, start, maxtime, numStepsPerLoop))
    thread2 = Thread(target=runMotorThread, args=(m2, start, maxtime, numStepsPerLoop))

    thread1.start()
    thread2.start()
	
    #Wait for threads to complete before exiting. Needed so that GPIO.cleanup can succeed
    thread1.join()
    thread2.join()
        
       
#---------------------------------------------------
try:
    main()
except KeyboardInterrupt: #From https://raspi.tv/2013/rpi-gpio-basics-3-how-to-exit-gpio-programs-cleanly-avoid-warnings-and-protect-your-pi
    print('Keyboard interupt')
except Exception as e:
    print('Caught Exception: ', e)
finally:
    GPIO.cleanup() # this ensures a clean exit 

    
