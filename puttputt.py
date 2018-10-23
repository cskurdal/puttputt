#!/usr/bin/python

import sys, math, time, argparse, random 
from threading import Thread


try:
	import RPi.GPIO as GPIO
	isRpi = True
except ImportError:
	print 'Not RaspberryPi'
	isRpi = False	

if isRpi:
	#Raspberry Pi GPIO Setup
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	# Enable pins 
	motor1_A_1_pin = 14
	motor1_A_2_pin = 15
	motor1_B_1_pin = 23
	motor1_B_2_pin = 24

	motor2_A_1_pin = 4
	motor2_A_2_pin = 17
	motor2_B_1_pin = 27
	motor2_B_2_pin = 22

	GPIO.setup(motor1_A_1_pin, GPIO.OUT)
	GPIO.setup(motor1_A_2_pin, GPIO.OUT)
	GPIO.setup(motor1_B_1_pin, GPIO.OUT)
	GPIO.setup(motor1_B_2_pin, GPIO.OUT)

	GPIO.setup(motor2_A_1_pin, GPIO.OUT)
	GPIO.setup(motor2_A_2_pin, GPIO.OUT)
	GPIO.setup(motor2_B_1_pin, GPIO.OUT)
	GPIO.setup(motor2_B_2_pin, GPIO.OUT)
    
    
#Constants
stepsPerRev = 200 #Motor 1.8deg/step
    
delay1 = 0.0055
delay2 = 0.0055
reverseMotor1 = False #Switch if motor turns the wrong way
reverseMotor2 = False #Switch if motor turns the wrong way

currMotor1Step = 0b1000
currMotor2Step = 0b1000

def runMotorThread(motor, start, maxtime):
	global stepsPerRev
	
 	while (time.time() - start) <= maxtime:
        #TODO: maybe use queue based events as described here: https://www.raspberrypi.org/forums/viewtopic.php?t=178212
        moveSteps(motor, 1*stepsPerRev))
    

def main():
    global stepsPerRev, delay1, delay2, reverseMotor1, reverseMotor2

    parser = argparse.ArgumentParser(description='Pi Putt')

    parser.add_argument('mode', choices=['once', 'voice', 'loop'], default='once', help='run mode (default: once)')
    parser.add_argument('maxtime', type=float, default=5, help='seconds to run (default: 5)')
    parser.add_argument('delay1', type=float, default=0.0055, help='delay after each step of motor 1 (default: 0.0055s)')
    parser.add_argument('delay2', type=float, default=0.0055, help='delay after each step of motor 2 (default: 0.0055s)')
    parser.add_argument('t1', type=float, default=0, help='the starting theta of motor 1 (default: 0)')
    parser.add_argument('t2', type=float, default=0, help='the starting theta of motor 2 (default: 0)')
    parser.add_argument('--setup', '-s', dest='setup', action='store_true', default=False, help='setup (default: False)')
    
    args = parser.parse_args()
		
    print 'args:',	args
    
    mode = args.mode
    maxtime = args.maxtime
    t1 = args.t1
    t2 = args.t2
	delay1 = args.delay1
	delay2 = args.delay2
    
    print "Raspberry Pi" if isRpi else "NOT a Pi!"
    
    start = time.time()
    
    while (time.time() - start) <= maxtime:
        #TODO: maybe use queue based events as described here: https://www.raspberrypi.org/forums/viewtopic.php?t=178212
        thread1 = Thread(target=runMotorThread, args=(1, start, maxtime))
        thread2 = Thread(target=runMotorThread, args=(2, start, maxtime))
        
        thread1.start()
        thread2.start()
    
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
	print e
finally:
	if isRpi:
		setStep1(0,0,0,0)

    
