from crossyroadenv.const import *
import numpy as np

class Agent:
    """
    Simple agent that just stores the position and the trace
    """
    def __init__(self):
        
        self.x,self.y = np.array(STARTLOCATION)
        self.lastAction = 2
        self.trace_a = []
        
        self.highscore = 0
    
    def step(self, action):
        if action == 0:
            self.y += 1
        elif action == 1:
            self.x -= 1
        elif action == 2:
            self.y -= 1
        elif action == 3:
            self.x += 1
        elif action == 4:
            pass
        
        if action != 4:
            self.lastAction = action
        self.trace_a.append(action)
        
        self.highscore = max(self.highscore, self.y)
    
    def pos(self):
        return (self.x, self.y)
    
    def reset(self):
        self.x,self.y = np.array(STARTLOCATION)
        self.trace_a.clear()
        self.lastAction = 2
        self.highscore = 0
        
        
