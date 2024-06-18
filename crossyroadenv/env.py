import gymnasium as gym
from gymnasium import spaces
import numpy as np
from crossyroadenv.const import *
from crossyroadenv.world import World
from crossyroadenv.agent import Agent
from crossyroadenv.mask import Mask
from crossyroadenv.render import *

class CrossyRoadEnv(gym.Env):
    
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, render_mode = None, **kwargs):
        super(CrossyRoadEnv, self).__init__()
        
        self.render_mode = render_mode
        
        # Agent position
        self.agent: Agent = Agent()
        
        # World
        self.world: World = World()
        
        # Mask observation
        self.mask: Mask = Mask(MASK)
        
        # Define action and observation space
        self.action_space = spaces.Discrete(5) 
        self.observation_space = spaces.Box(low=-1,high=1, shape=self.mask.shapeObs, dtype=float)

        # Setup visuals
        self._setupRendering()

    def _get_action_definitions(self) -> dict:
        return {0: "up", 1: "left", 2: "down", 3: "right", 4: "still"}

    def _get_action_tuples(self) -> dict:
        return {0: (0,1), 1: (-1,0), 2: (0,-1), 3: (1,0), 4: (0,0)}
    
    def _setupRendering(self) -> None:
        """
        Human render mode:
        """
        if self.render_mode == "human":
            import pygame
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((APPWIDTH,APPHEIGHT))
            self.clock = pygame.time.Clock() 
    
    def _isTruncated(self, pos, action):
        action = self._get_action_tuples()[action]
        if not 0 <= pos[0]+action[0] < GRIDWIDTH:
            return True
        elif MAX_AGE != -1 and self.world.t > MAX_AGE:
            return True
        return False
    
    def _isTerminal(self, obs, pos, action):
        action = self._get_action_tuples()[action]
        return obs[LAYERS_UNDERNEATH-1+action[1]][pos[0]+action[0]] in TERMINAL_STATES
        
    def _isInvalid(self, obs, pos, action):
        action = self._get_action_tuples()[action]
        return pos[1]+action[1] == 0 or obs[LAYERS_UNDERNEATH-1+action[1]][pos[0]+action[0]] in INVALID_STATES 
    
    def _newHighscore(self, agent: Agent, action):
        action = self._get_action_tuples()[action]
        return agent.pos()[1]+action[1] > agent.highscore
    
    def _correctLogOffset(self, agent, action):
        obsInfo = self.world.getObservationInfo(agent)
        if action == 4:
            if type(obsInfo[1]) == Logs and obsInfo[1].hasMoved:
                if obsInfo[1].direction == "r":
                    agent.x += 1
                elif obsInfo[1].direction == "l":
                    agent.x -= 1
    
    def _getReward(self, isInvalid, isTruncated, isTerminal, newHighscore, action):
        if isInvalid:
            return REWARD_INVALID
        elif isTruncated:
            return REWARD_TRUNCATED
        elif isTerminal:
            return REWARD_TERMINATED
        elif newHighscore:
            return REWARD_NEWLAYER
        else:
            return REWARDS[action]
         
    def step(self, action):

        # Update world
        obs = self.world.getObservation(self.agent)
        
        isTruncated = self._isTruncated(self.agent.pos(), action)
        
        if not isTruncated:
            isInvalid = self._isInvalid(obs, self.agent.pos(), action)
        else:
            isInvalid = False
        
        # Correct for log offset
        self._correctLogOffset(self.agent, action)
        
        isTruncated = self._isTruncated(self.agent.pos(), action)
        if not isTruncated:
            isTerminal = self._isTerminal(obs, self.agent.pos(), action)
        else:
            isTerminal = False
        
        # Update new highscore
        newHighscore = False
        if not isInvalid and not isTerminal:
            newHighscore = self._newHighscore(self.agent, action)
        

        # Do the actual step in the environment                
        if not isTruncated and not isInvalid:
            self.agent.step(action)
        
        r = self._getReward(isInvalid, isTruncated, isTerminal, newHighscore, action)
        
        # Update world
        self.world.t += 1
        
        
        # Check whether new layer has been added
        if not isInvalid and not isTruncated:
            while self.agent.highscore > len(self.world)-20:
                self.world.add_section()
                
        info = {
            "onLayer": self.world.getObservationInfo(self.agent)[1],
            "newHighscore": newHighscore
            }
        
    
        obs = self.world.getObservationFloats(self.agent)
        obs = self.mask.apply(obs, self.agent)
        
        return obs, r, isTerminal, isTruncated, info
    
    def reset(self, seed = None, options=None):
        
        self.agent.reset()
        self.world = World(seed=seed)
    
        obs = self.world.getObservationFloats(self.agent)
        obs = self.mask.apply(obs, self.agent)
        
        info = {
            "onLayer": self.world.getObservationInfo(self.agent)[1],
            "newHighscore": False
            }
        
        return obs, info

    def render(self):
        if self.render_mode == None:
            raise ValueError("Cannot render when not in render_mode = human")
        
        elif self.render_mode == "human":
            self.window.blit(renderWorld(self.world, self.agent),(0,0))
            pygame.display.flip()
            self.clock.tick(FPS)

    def close(self):
        if self.render_mode == "human":
            pygame.display.quit()
            pygame.quit()

    def saveGIF(self, path = RECORD_PATH):
        if self.render_mode == None:
            raise ValueError("Cannot render when not in render_mode = human")
        
        recordingToGif(path, self.world, self.agent)
        
