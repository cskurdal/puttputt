

class Motor:
    def __init__(self, pins = [], direction = 1):
        self.pins = pins
        self.direction = 1
        super().__init__()
       
       
    def step(self):
        raise NotImplementedError
        
        
    def invertDirection(self):
        self.direction *= -1
        
        
