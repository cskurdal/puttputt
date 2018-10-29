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
    parser.add_argument('delay1', type=float, default=0.0055, help='delay after each step of motor 1 (default: 0.0055s)')
    parser.add_argument('delay2', type=float, default=0.0055, help='delay after each step of motor 2 (default: 0.0055s)')
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
    #thread2 = Thread(target=runMotorThread, args=(m2, start, maxtime, numStepsPerLoop))
        
    thread1.start()
    #thread2.start()
    
#---------------------------------------------------
if isRpi:
	def setStep1(w1, w2, w3, w4):
		GPIO.output(motor1_A_1_pin, w1)
		GPIO.output(motor1_B_1_pin, w2)
		GPIO.output(motor1_A_2_pin, w3)
		GPIO.output(motor1_B_2_pin, w4)

if isRpi:
	def moveSteps(motor, numSteps, turnOff = True):
		try:
			global currMotor1Step, currMotor2Step, delay1, delay2, reverseMotor1, reverseMotor2
			numSteps = int(round(numSteps))
			#currMotor1Step = 0b1000
			#currMotor2Step = 0b1000
#			print 'moving motor:', motor, ' steps:', numSteps, ' rev1:', reverseMotor1, ' rev2:', reverseMotor2, ' delay1:', delay1, ' delay2:', delay2

			if motor == 1 and ((numSteps > 0 and not reverseMotor1) or\
					(numSteps < 0 and reverseMotor1) ): #Motor 1 spinning +
				for i in range(0, abs(numSteps)):
					#Set next step
					currMotor1Step = currMotor1Step>>1
					if currMotor1Step == 0b0000:
						currMotor1Step = 0b1000

					p1 = (currMotor1Step>>3)&1
					p2 = (currMotor1Step>>2)&1
					p3 = (currMotor1Step>>1)&1
					p4 = currMotor1Step&1
					
					#print '    output to motor 1+',p1,p2,p3,p4
					GPIO.output(motor1_A_1_pin, p1)
					GPIO.output(motor1_B_1_pin, p2)
					GPIO.output(motor1_A_2_pin, p3)
					GPIO.output(motor1_B_2_pin, p4)
					
					time.sleep(delay1)

			elif motor == 1 and ((numSteps > 0 and reverseMotor1) or\
					(numSteps < 0 and not reverseMotor1) ): #Motor 1 spinning -
				for i in range(0, abs(numSteps)):
					#Set next step
					currMotor1Step = currMotor1Step>>1
					if currMotor1Step == 0b0000:
						currMotor1Step = 0b1000

					p1 = currMotor1Step&1
					p2 = (currMotor1Step>>1)&1
					p3 = (currMotor1Step>>2)&1
					p4 = (currMotor1Step>>3)&1

					#print '    output to motor 1-',p1,p2,p3,p4
					GPIO.output(motor1_A_1_pin, p1)
					GPIO.output(motor1_B_1_pin, p2)
					GPIO.output(motor1_A_2_pin, p3)
					GPIO.output(motor1_B_2_pin, p4)
					
					time.sleep(delay1)
			elif motor == 2 and ((numSteps > 0 and not reverseMotor2) or\
					(numSteps < 0 and reverseMotor2) ): #Motor 2 spinning +
				for i in range(0, abs(numSteps)):
					#Set next step
					currMotor2Step = currMotor2Step>>1
					if currMotor2Step == 0b0000:
						currMotor2Step = 0b1000

					p1 = (currMotor2Step>>3)&1
					p2 = (currMotor2Step>>2)&1
					p3 = (currMotor2Step>>1)&1
					p4 = currMotor2Step&1

					#print '    output to motor 2+        ',p1,p2,p3,p4
					GPIO.output(motor2_A_1_pin, p1)
					GPIO.output(motor2_B_1_pin, p2)
					GPIO.output(motor2_A_2_pin, p3)
					GPIO.output(motor2_B_2_pin, p4)
				
					time.sleep(delay2)
			elif motor == 2 and ((numSteps > 0 and reverseMotor2) or\
					(numSteps < 0 and not reverseMotor2) ): #Motor 2 spinning -
				for i in range(0, abs(numSteps)):
					#Set next step
					currMotor2Step = currMotor2Step>>1
					if currMotor2Step == 0b0000:
						currMotor2Step = 0b1000

					p1 = currMotor2Step&1
					p2 = (currMotor2Step>>1)&1
					p3 = (currMotor2Step>>2)&1
					p4 = (currMotor2Step>>3)&1

					#print '    output to motor 2-        ',p1,p2,p3,p4
					GPIO.output(motor2_A_1_pin, p1)
					GPIO.output(motor2_B_1_pin, p2)
					GPIO.output(motor2_A_2_pin, p3)
					GPIO.output(motor2_B_2_pin, p4)

					time.sleep(delay2)

		finally:
#			print 'turning off motors'
			#TURN OFF! SO MOTOR AND CONTROLLER DON'T OVERHEAT!!
			if turnOff:
				GPIO.output(motor1_A_1_pin, 0)
				GPIO.output(motor1_B_1_pin, 0)
				GPIO.output(motor1_A_2_pin, 0)
				GPIO.output(motor1_B_2_pin, 0)

				GPIO.output(motor2_A_1_pin, 0)
				GPIO.output(motor2_B_1_pin, 0)
				GPIO.output(motor2_A_2_pin, 0)
				GPIO.output(motor2_B_2_pin, 0)
			
			


try:
	main()
except Exception as e:
	print(e)
finally:
	if isRpi:
		setStep1(0,0,0,0)
        #TODO turn motor 2 off

    
