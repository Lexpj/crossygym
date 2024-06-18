from crossyroadenv.const import *
import numpy as np

"""
The representation is as follows:
1 for blocked
0 for free

C: car
L: log
B: bush
W: water
0: ground/free
P: lilypad

"""

def compactAttributes(lst, obstacleID, figID = False) -> list[tuple]:
    """
    Compacts a list of elements into a list with tuples with (location,length)
    """
    res = []
    
    i = 0
    while i < len(lst):
        if lst[i] == obstacleID:
            loc = i
            i += 1
            while i < len(lst) and lst[i] == obstacleID and i-loc<5:
                i += 1
            length = i-loc
            
            if figID:
                if length == 2:
                    res.append((loc,length,np.random.randint(1,6)))
                elif length == 3:
                    res.append((loc,length,np.random.randint(1,3)))
                elif length == 4:
                    res.append((loc,length,np.random.randint(1,2)))
            else:
                res.append((loc,length))
            
        else:
            i += 1

    return res

class Layer:
    """
    Default layer. Every new layer can inherit this class to avoid
    to forget the bare minimum that defines a layer.
    """
    def __init__(self):
        self.representation = ['0']*GRIDWIDTH
        self.isStatic = True

    def update(self) -> None:
        return
    def observation(self,t) -> list:
        return self.representation
    def copy(self):
        c = globals()[self.__class__.__name__]()
        for key, value in dict(vars(self)).items():
            setattr(c,key,value)
        return c
    
class Empty(Layer):
    """
    The empty layer consists of just grass, which is walkable
    """
    def __init__(self):
        self.representation = ['0'] * GRIDWIDTH
        self.isStatic = True
  
class Bush(Layer):
    """
    The bush layer is a grass layer filled with a number of bushes. These
    bushes are obstacles you cannot walk in. Taking an action that results 
    the agent to be in the position of the bush will count as an INVALID move.
    """
    def __init__(self, density=0.3, border = False):
        self.representation = list(np.random.choice(['0','B'], p=[1-density,density], size = GRIDWIDTH))
        if border:
            self.representation[0] = 'B'
            self.representation[-1] = 'B'
        self.isStatic = True

class Logs(Layer):
    """
    The log section consists of water where a few logs can move from one direction.
    Walking on water results in TERMINATION. The logs can be dynamic.
    NOTE: standing still on a log results in moving along with the log.
    You can move outside the environment, which results in TERMINATION
    The logs can be OFFSET, but are still GRIDBASED. This means moving towards
    this layer results in getting in the grid cell that is rounded the closest to you
    You move in a grid based manner on the logs.
    """
    def __init__(self, density = 0.6, cycle = 1500, direction = "s"):
        
        self.direction = direction
        self.speed = GRIDWIDTH/cycle
        self.maxtime = GRIDWIDTH

        # self.representation = list(np.random.choice(['L','W'], p=[density,1-density], size = GRIDWIDTH))
        self.representation = np.random.choice(
                                ['WLLLWLLLWLLLWWW',
                                'WWLLWWLLWWLLWWW',
                                'WLLWWLLLWWLLWLL',
                                'WWLLLLWLWLLLLWL',
                                'WWWLLLWWWLLLWWW',
                                'LWLLLWWLLWWLLWW'])
        self.representation = list(self.representation)
        self.representation = self.representation * 2

        self.logConfiguration = compactAttributes(self.representation, obstacleID='L')
        self.isStatic = False if direction != 's' else True
        
        # Check whether log layer has moved in representation
        self.prevPartition = [GRIDWIDTH - int(round(0)),GRIDWIDTH*2 -int(round(0))]
        self.hasMoved = False
           

    def observation(self,t):
        if self.direction == "r":
            translate_t = ((self.speed * t) % GRIDWIDTH)
            
        elif self.direction == "l":
            translate_t = GRIDWIDTH - ((self.speed * t) % GRIDWIDTH)
                        
        elif self.direction == "s":
            translate_t = 0
            
        
        
        # Check whether log layer has moved
        if self.prevPartition != [GRIDWIDTH - int(round(translate_t)),GRIDWIDTH*2 -int(round(translate_t))]:
            self.prevPartition = [GRIDWIDTH - int(round(translate_t)),GRIDWIDTH*2 -int(round(translate_t))]
            self.hasMoved = True
        else:
            self.hasMoved = False
            
        return self.representation[GRIDWIDTH - int(round(translate_t)): GRIDWIDTH*2 -int(round(translate_t))]
    
class Road(Layer):
    """
    The road section consists of roads where cars can come from one direction.
    The roads itself are safe to walk on. Hitting a car will TERMINATE the environment.
    """
    def __init__(self, density=0.3, cycle = 1500, direction = "s"):

        self.direction = direction
        self.speed = GRIDWIDTH/cycle
        self.maxtime = GRIDWIDTH
        self.isStatic = False if direction != 's' else True

        # self.representation = list(np.random.choice(['C','0'], p=[density,1-density], size = GRIDWIDTH))
        self.representation = np.random.choice([
                                '00CCCC000000000',
                                '000CCC000CCC000',
                                '00CC000000CC000',
                                '0CCC00CC00CC000',
                                'CC0000CCC000000',
                                '00CC00000000000'])
        self.representation = list(self.representation)
        self.carConfiguration = compactAttributes(self.representation,obstacleID='C',figID = True)
        self.representation = self.representation * 2
    
    def observation(self, t):
        if self.direction == "r":
            translate_t = ((self.speed * t) % GRIDWIDTH)
            
        elif self.direction == "l":
            translate_t = GRIDWIDTH - ((self.speed * t) % GRIDWIDTH)
                        
        elif self.direction == "s":
            translate_t = 0
            
        return self.representation[GRIDWIDTH - int(round(translate_t)): GRIDWIDTH*2 -int(round(translate_t))]

class Lilypad(Layer):
    """
    The lilypad layer consists of water, where a few lilypads are placed.
    Walking on water results in TERMINATION. The lilypads are static and safe to walk on.
    """
    def __init__(self, density=0.6):
        self.representation = list(np.random.choice(['W','P'], p=[1-density,density], size = GRIDWIDTH))
        self.isStatic = True

class Rail(Layer):
    def __init__(self, interval = 60, speed = 3, direction = "s"):
        
        self.direction = direction
        self.interval = interval
        
        self.speed = speed
        self.isStatic = False if direction != 's' else True        
    
    def observation(self, t):
        
        translate_t = t % self.interval
        
        # Warn
        if translate_t < RAIL_WARN_STEPS + (GRIDWIDTH // self.speed)*2:
            representation = ['t']*GRIDWIDTH
            
            # Train
            if translate_t > RAIL_WARN_STEPS:
                tt = (translate_t - RAIL_WARN_STEPS) * self.speed
                
                representation[max(0,tt-7):min(tt,GRIDWIDTH)] = ['T']*(min(tt,GRIDWIDTH)-max(0,tt-7))
                if self.direction == "l":
                    representation = representation[::-1]
                    
        else:
            representation = ['0']*GRIDWIDTH

        return representation
        
