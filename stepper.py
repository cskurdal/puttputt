import time
from motor import Motor
import RPi.GPIO as GPIO
    
class Stepper(Motor):
    def __init__(self, pins, name = None, stepType = 'full'):
        super().__init__(pins, name)      
        
        if stepType == 'full':
            self._trajectory = [[1,0,1,0],[1,0,0,1],[0,1,0,1],[0,1,1,0]]
        elif stepType == 'single':
            self._trajectory = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
        else:
            raise Exception('invalid stepType')
        
        self._position = 0
        
        if len(self._pins) != 4:
            raise Exception('pins must be length of 4')
        
        #Raspberry Pi GPIO Setup
        GPIO.setmode(GPIO.BCM)

        for p in self._pins:
            GPIO.setup(p, GPIO.OUT)
        
    #Modeled after: http://homepage.divms.uiowa.edu/~jones/step/midlevel.html
    def step(self, steps, delay = 0.0055, turnOff = True):
        if steps > 0:
            for s in range(steps):
                self.position = (self.position + s + len(self.trajectory)) % len(self.trajectory)

                for o in range(len(self._pins)):
                    GPIO.output(self._pins[o], self.trajectory[self.position][o])

                time.sleep(delay)
        else:            
            for s in list(reversed(range(steps))):
                self.position = (self.position + s + len(self.trajectory)) % len(self.trajectory)

                for o in range(len(self._pins)):
                    GPIO.output(self._pins[o], self.trajectory[self.position][o])

                time.sleep(delay)
            
        if turnOff:
            for o in self._pins:
                GPIO.output(o, 0)
        

    def turnOff(self):
        for o in self._pins:
            GPIO.output(o, 0)
            
