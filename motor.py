

class Motor(object):
    def __init__(self, pins = [], name = None, direction = 1):
        self._pins = pins
        self._name = name
        self._direction = 1
        super().__init__()
       
       
    def step(self):
        raise NotImplementedError
        
        
    def invertDirection(self):
        self._direction *= -1
        
    @property
    def name(self):
        return self._name
