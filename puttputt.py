#!/usr/bin/python

import sys, math, time, argparse, random 
from threading import Thread
from stepper import Stepper
import snowboydecoder
import signal
from os import listdir
from os.path import isfile, join

modelsPath = './resources/models/'
interrupted = False
interruptStart = -1


def normal_RPM_function(t, start):
    rpm = 30 + 30 * math.sin((t - start) / (2 * math.pi))
    return rpm

#start parameter is the interruptStart
def slowdown_RPM_function(t, start, currentRPM, slowDownTime, interruptedTime):
    global interrupted, interruptStart
    
    print('slowdown_RPM_function: ', t, start, currentRPM, slowDownTime, interruptedTime)
    
    if t <= (start + slowDownTime):
        return (-currentRPM / slowDownTime) + currentRPM
    else:
        #When start + slow down and interrupted time is elasped then restart
        if t > (start + slowDownTime + interruptedTime):
            interrupted = False
            interruptStart = -1 #reset
            print('set interrupted = False')
            
        return 0
    
def recognition_callback():
    global interrupted
    interrupted = True
    print('recognition_callback')

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted, thread1Done, thread2Done
    
    #If Ctrl-C or motors are done spinning
    return interrupted or (thread1Done and thread2Done)


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
slowDown1 = False
slowDown2 = False

#Set to True on completion of runMotor method to interupt voice hot word detection
thread1Done = False
thread2Done = False


class VelocityRPM(object):
    def __init__(self, targetRPM, seconds, stepsPerRev = 200): #Motor 1.8deg/step
        self._startTime = time.time()
        self._stepsPerRev = stepsPerRev
        self._currentOscillatingRPM = lambda self, t: 30 + 30 * math.sin((time.time() - self._startTime) / (2 * math.pi)) #Osilates from 0-60 RPM every minute
        
    def getDelay(self):
        t = time.time()
        
        if t > (self._startTime + self._seconds):
            return 60 / (self._currentRPM * self._stepsPerRev)
        else: #linear acceleration
            return (((self._startTime + t) / (self._startTime + self._seconds)) * 60) / (self._currentRPM * self._stepsPerRev)


def runMotor1(motor, start, maxtime, numStepsPerLoop = 1):
    global delay1, reverseMotor1, slowDown1, thread1Done, interrupted, interruptStart

    numStepsPerLoop = numStepsPerLoop
    
    #Reverse
    motor.delay = delay1
    slowDownCountdown = 0
        
    if reverseMotor1:
        numStepsPerLoop *= -1
        
    interruptedTime = 5 #time interrupted
    slowDownTime = 2 #seconds to stop
    
    rpm = 0
    t = time.time()
    while (t - start) <= maxtime:
        if interrupted:            
            print('1 INTERRUPTED!!')
            #Set the interruptStart 
            if interruptStart < start:
                interruptStart = t
          
            rpm = slowdown_RPM_function(t, interruptStart, rpm, slowDownTime, interruptedTime)
                
            #If rpm is less than 1RPM then just sleep, this keeps the delay from being very large
            if rpm <= abs(1):                    
                time.sleep(0.05)
                t = time.time()
                continue

            motor.setCurrentRPM(rpm)
            #else:
            #    currentRPM = normalRPMFunction(t, start)
                
                #Create lambda function
                #slowDownRPMFunction = lambda t, start, currentRPM: slowdown_RPM_function(t, start, currentRPM, slowDownTime, interruptedTime)
             #   slowDownInitComplete = True
             #   continue
        else:
            rpm = normal_RPM_function(t, start)
            
            #If rpm is less than 1RPM then just sleep, this keeps the delay from being very large
            if rpm <= abs(1): 
                time.sleep(0.05)
                t = time.time()
                continue
                
            motor.setCurrentRPM(rpm) #Osilates from 0-60 RPM every minute
            
        print(motor.name + ' delay: ' + str(motor.delay))
        
        #rpm / math.abs(rpm) will reverse motor direction if RPM is a - value
        if True:
            motor.stepWithTurnOffAndSleep(numStepsPerLoop * int(rpm / abs(rpm)), turnOff = False)
        else:
            motor.step(numStepsPerLoop * int(rpm / abs(rpm)), turnOff = True)
            
        t = time.time()
        
    motor.turnOff()
    thread1Done = True

        
def runMotor2(motor, start, maxtime, numStepsPerLoop = 1):
    global delay2, reverseMotor2, slowDown2, thread2Done, interrupted, interruptStart

    numStepsPerLoop = numStepsPerLoop
    
    motor.delay = delay2
        
    if reverseMotor2:
        numStepsPerLoop *= -1
        
    interruptedTime = 5 #time interrupted
    slowDownTime = 2 #seconds to stop
    
    rpm = 0
    t = time.time()
    while (t - start) <= maxtime:
        if interrupted:
            print('2 INTERRUPTED!!')
            #Set the interruptStart 
            if interruptStart < start:
                interruptStart = t
                
            rpm = slowdown_RPM_function(t, interruptStart, rpm, slowDownTime, interruptedTime)
 
            #If rpm is less than 1RPM then just sleep, this keeps the delay from being very large
            if rpm <= abs(1): 
                time.sleep(0.05)
                t = time.time()
                continue

            motor.setCurrentRPM(rpm)
        else:
            rpm = normal_RPM_function(t, start)
 
            #If rpm is less than 1RPM then just sleep, this keeps the delay from being very large
            if rpm <= abs(1):                 
                time.sleep(0.05)
                t = time.time()
                continue
                
            motor.setCurrentRPM(rpm)
                
        print(motor.name + ' delay: ' + str(motor.delay))
        
        #rpm / math.abs(rpm) will reverse motor direction if RPM is a - value
        if False:
            motor.stepWithTurnOffAndSleep(numStepsPerLoop * int(rpm / abs(rpm)), turnOff = False)
        else:
            motor.step(numStepsPerLoop * int(rpm / abs(rpm)), turnOff = True)
            
        t = time.time()
        
    motor.turnOff()
    thread2Done = True

    
def main():
    global delay1, delay2, reverseMotor1, reverseMotor2, thread1Done, thread2Done

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
    thread1 = Thread(target=runMotor1, args=(m1, start, maxtime, numStepsPerLoop))
    thread2 = Thread(target=runMotor2, args=(m2, start, maxtime, numStepsPerLoop))

    thread1.start()
    thread2.start()

    if mode == 'voice':
        models = [modelsPath + f for f in listdir(modelsPath) if isfile(join(modelsPath, f))]
        #models = []
        
        print('Voice models: ', models)
        
        callbacks = []
        for m in models:
            callbacks.append(lambda: recognition_callback())
        
        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, signal_handler)

        sensitivity = [0.5]*len(models)
        detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)
        
        print('Listening... Press Ctrl+C to exit')

        # main loop
        # make sure you have the same numbers of callbacks and models
        while not (thread1Done and thread2Done):
            detector.start(detected_callback=callbacks,
                           interrupt_check=interrupt_callback,
                           sleep_time=0.03)

            detector.terminate()
            print('detector.terminate()')
    
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

    
