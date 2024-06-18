from crossyroadenv.const import *
import numpy as np

class Mask:
    
    def __init__(self, mask: str):
        """
        Make a mask via initializing what parts of the environment you want to see relative to the agent
        This is done via assigning where the agent is relative to your desired observed cell values
        Take for the agent 'o', for the cells you want to see 'x' and for the remainder of the cells '.'
        For example:
        
        ..x..
        .xxx.
        xxoxx
        .xxx.
        ..x.. 

        This allows for more intricate shapes. Anything outside the environment is assigned a terminal value
        NOTE: since this does not always have to be a rectangular shape, the cells with '.' gets assigned -1 as value, and the shape will remain the same
        
        """
        
        self.mask = [[y for y in ''.join(x.split())] for x in mask.split('\n')]
        self.agentPos = []
        self.maskPoints = []
        self.shape = np.array((len(self.mask),len(self.mask[0])))
        
        # Flattens into 1D array, without the need of -1 values
        self.flatten = FLATTEN
        
        if not self.flatten:
            self.shapeObs = np.array((len(self.mask),len(self.mask[0])))
        else:
            self.shapeObs = np.array((len(self.mask)*len(self.mask[0]) - mask.count('.'),))
        
        self._extractMask()
        
    def _extractMask(self):
        self.maskPoints = [(0,0)]
        self.agentPos = []
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if self.mask[i][j] == "o":
                    self.agentPos = [j,i]
        if not self.agentPos:
            raise ValueError("No relative agent location ('o') assigned")
        
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if self.mask[i][j] == "x":
                    self.maskPoints.append((j-self.agentPos[0] , i-self.agentPos[1]))
 
    def apply(self, obs, agent):
        maskobs = np.full(self.shape,-1,dtype='float64')
        
        for dx,dy in self.maskPoints:
            if 0 <= LAYERS_UNDERNEATH-1+dy <= GRIDHEIGHT and 0 <= agent.x+dx < GRIDWIDTH:
                maskobs[dy+self.agentPos[1]][dx+self.agentPos[0]] = obs[LAYERS_UNDERNEATH-1+dy][agent.x+dx]
        
        if self.flatten:
            maskobs = maskobs.flatten()
            maskobs = maskobs[maskobs != -1]
            
        return maskobs[::-1]
        