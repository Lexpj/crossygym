from crossyroadenv.const import *
from crossyroadenv.layers import *
from crossyroadenv.sections import *
from crossyroadenv.agent import *
import numpy as np

class World:
    def __init__(self, seed = None, **kwargs):
        
        self.seed = seed
        np.random.seed(seed)
        self.t = 0
        
        # World generation
        self.worldGenerator = self.getWorldGenerator(WORLD_GENERATOR)
        
        self.world: list[Layer] = [Bush(density=1)]*(LAYERS_UNDERNEATH-1) + [
                      Bush(density=0,border=True),
                      Bush(density=0,border=True),
                      ]
        while len(self.world) < 20:
            self.add_section()
    
    def getObservationFloats(self, agent: Agent):
        """Gets the representation usable for RL"""
        obs = self.getObservation(agent)
        layers = self.getObservationInfo(agent)
        
        lst = []
        for i in range(len(obs)):
            if layers[i].isStatic:
                lst.append([STATE_REP[x] for x in obs[i]])
                
            else:
                rep = [0 for _ in range(GRIDWIDTH)]
                d = ((layers[i].speed * self.t) % GRIDWIDTH) % 1
                
                for j in range(GRIDWIDTH):
                    left = STATE_REP[obs[i][j-1]]
                    right = STATE_REP[obs[i][0]] if j+1 == GRIDWIDTH else STATE_REP[obs[i][j+1]]
                    middle = STATE_REP[obs[i][j]]
                    
                    if left == right == middle:
                        rep[j] = middle
                    else:
                        if layers[i].direction == "l":
                            if round(d) == 1:
                                rep[j] = (1-d) * left + (d) * middle
                            else:
                                rep[j] = d * right + (1-d) * middle
                        elif layers[i].direction == "r":
                            if round(d) == 1:
                                rep[j] = (1-d) * right + (d) * middle
                            else:
                                rep[j] = d * left + (1-d) * middle
                
                lst.append([round(x,2) for x in rep])
        return lst    
                  
    def getObservation(self,agent: Agent):
        """Raw observation: in terms of letters"""
        obs = []
        for layer in self.world[agent.y-LAYERS_UNDERNEATH+1:agent.y-LAYERS_UNDERNEATH+1+GRIDHEIGHT]:
            obs.append(layer.observation(self.t))
        return obs
    
    def getObservationInfo(self, agent: Agent):
        """Extracts the type(layer) in the visible world"""
        obs = []
        for layer in self.world[agent.y-LAYERS_UNDERNEATH+1:agent.y-LAYERS_UNDERNEATH+1+GRIDHEIGHT]:
            obs.append(layer)
        return obs

    def getWorldGenerator(self,wg:str):
        """
        Returns a class in crossyroadgym.envs.sections that can make sections
        If worldGenerator == None, the Default class will be used
        If worldGenerator does not match any of the classes, it will use default and warn the user
        """
        if wg == None: return Default()
        generators = {
            'default': Default(),
            'nologs': NoLogs(),
            'hybrid': Hybrid(),
            'lookalike': Lookalike(),
            'lookalikeincdif': LookalikeIncDif(),
            'allgrass': AllGrass(),
            'alllogs': AllLogs()
        }
        if generators.get(wg, False): return generators[wg]
        print(f"WARNING: {wg} is not in {list(generators.keys())}; using Default() instead.")
        return Default()
    
    def add_section(self) -> None:
        """
        Adds a single layer, with properties defined in CONST
        You can add sections as well, though these are lists of layers
        so you will have to append each layer or use the + operator
        """
        section = self.worldGenerator.add(self.t)
        self.world.extend(section)
    
    def __len__(self):
        return len(self.world)
    def __iter__(self):
        return self.world
    def __getitem__(self,i):
        return self.world[i]
  
  