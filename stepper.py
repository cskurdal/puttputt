import time
from motor import Motor
import RPi.GPIO as GPIO
    
'''
    #Calling code will need to set GPIO mode
    RPi.GPIO.setmode(GPIO.BCM)
'''
class Stepper(Motor):
    def __init__(self, pins, name = None, stepType = 'full', mode = 'BCM'):
        super().__init__(pins, name)      
        
        if stepType == 'full':
            self._trajectory = [[1,0,1,0],[0,1,1,0],[0,1,0,1],[1,0,0,1]]
        elif stepType == 'half':
            self._trajectory = [[1,0,1,0],[0,0,1,0],[0,1,1,0],[0,1,0,0],[0,1,0,1],[0,0,0,1],[1,0,0,1],[1,0,0,0]]
        elif stepType == 'single':
            #self._trajectory = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]] #TODO: doesn't work
            self._trajectory = [[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]]
        else:
            raise Exception('invalid stepType')
        
        self._position = 0
        self._delay = 0.005
        
        if len(self._pins) != 4:
            raise Exception('pins must be length of 4')
            
        #Raspberry Pi GPIO Setup
        if mode == 'BOARD':
            GPIO.setmode(GPIO.BOARD)
        else:
            GPIO.setmode(GPIO.BCM)

        for p in self._pins:
            GPIO.setup(p, GPIO.OUT)
        

    #Modeled after: http://homepage.divms.uiowa.edu/~jones/step/midlevel.html
    def step(self, steps, delay = self._delay, turnOff = True):
        for s in range(steps):
            if steps > 0:
                self._position += 1 #positive, go forward
            else:
                self._position -= 1 #if negative, go backwards
                
            p = (self._position + len(self._trajectory)) % len(self._trajectory)
                        
            #print('position: ', self._position)
            for o in range(len(self._pins)):
                GPIO.output(self._pins[o], self._trajectory[p][o])
                #print(' pin=', self._pins[o], ':', self._trajectory[p][o])

            time.sleep(self._delay)
            
        if turnOff:
            for o in self._pins:
                GPIO.output(o, 0)
        
        
    #Turns off motors power then sleeps, will reduce heat, but also allow motor to turn will sleeping
    def stepWithTurnOffAndSleep(self, steps, delay = self._delay, turnOff = True):
        for s in range(steps):
            if steps > 0:
                self._position += 1 #positive, go forward
            else:
                self._position -= 1 #if negative, go backwards
                
            p = (self._position + len(self._trajectory)) % len(self._trajectory)
                        
            #print('position: ', self._position)
            for o in range(len(self._pins)):
                GPIO.output(self._pins[o], self._trajectory[p][o])
                #print(' pin=', self._pins[o], ':', self._trajectory[p][o])

            #Turn off, THEN sleep
            if turnOff:
                for o in self._pins:
                    GPIO.output(o, 0)
                    
            time.sleep(self._delay)
            
        
    @property
    def delay(self):
        return self._delay

    
    @delay.setter
    def delay(self, delay):
        if delay < 0.001:
            raise Exception("too small")
        else:
            self._delay = delay
       

    def turnOff(self):
        for o in self._pins:
            GPIO.output(o, 0)
            
