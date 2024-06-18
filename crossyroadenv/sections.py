from crossyroadenv.layers import *
import numpy as np
from crossyroadenv.const import *
from collections import deque

def check(lst, max_steps, worldT):
    """
    3D-frame A* path finding I guess
    :param lst: lst of the layers that are about to get added
    :param max_steps: the maximum steps to look ahead in order to say there is a path or not
    return: bool
    """
    
    # environment, GRIDWIDTH * len(lst) * LCM(lst.cycle)
    box = []
    copylst = [x.copy() for x in lst]

    def generate_box_layer():
        
        fullobs = []
        for layer in copylst:
            obs = np.array([1 if x in TERMINAL_STATES+INVALID_STATES else 0 for x in layer.observation(worldT)])
            fullobs.append(obs)
            layer.update()
        return np.array(fullobs)
    
    # Add first layer
    for _ in range(max_steps):
        box.append(generate_box_layer())
    
    box = np.array(box)
    
    directions = [(1,1,0),(1,0,1),(1,0,-1),(1,-1,0),(1,0,0)]
    queue = deque([(0,0,ind) for ind, x in enumerate(box[0][0]) if x == 0])
    newqueue = deque()
    
    # Keep going
    while queue:
        while queue:
            
            p = queue[0]
            queue.popleft()
            
            box[p[0]][p[1]][p[2]] = 2
            
            if p[0] == len(lst)-1:
                return True
            
            for item in directions:
                z = p[0] + item[0]
                y = p[1] + item[1]
                x = p[2] + item[2]
                
                if z >= 0 and y >= 0 and x >= 0 and x < GRIDWIDTH and y < len(lst) and z < max_steps and box[z][y][x] != 1:
                    newqueue.append((z,y,x))
        queue = newqueue.copy()
        newqueue.clear()
    
    return False

def env_checker(func, max_steps = 50):
    def wrapper(*args, **kwargs):
        lst = func(*args, **kwargs)
        while not check(lst, max_steps=max_steps, worldT = args[-1]):
            lst = func(*args, **kwargs)
        return lst
    return wrapper

class Sections:

    def __init__(self):
        """
        The basic section class.
        Must contain:
        - add() -> Layer
        """
        pass
    
    def add(self) -> list[Layer]:
        raise Exception("Must be implemented!")
    def copy(self):
        c = globals()[self.__class__.__name__]()
        for key, value in dict(vars(self)).items():
            setattr(c,key,value)
        return c

class Default(Sections):
    """
    The section with all default settings
    """

    @env_checker
    def add(self,t):
        lst = []
        for i in range(5):
            lst.append(np.random.choice([
            Empty(),
            Bush(
                density=np.random.uniform(BUSH_DENSITY_LOW,BUSH_DENSITY_HIGH),
                ),
            Logs(
                density=np.random.uniform(LOGS_DENSITY_LOW,LOGS_DENSITY_HIGH), 
                direction=np.random.choice(['r','l','s'], p=[LOGS_DIRECTION_R,LOGS_DIRECTION_L,LOGS_DIRECTION_S]), 
                cycle=np.random.randint(LOGS_CYCLE_LOW,LOGS_CYCLE_HIGH),
                ),
            Road(
                density=np.random.uniform(ROAD_DENSITY_LOW,ROAD_DENSITY_HIGH), 
                direction=np.random.choice(['r','l','s'], p=[ROAD_DIRECTION_R,ROAD_DIRECTION_L,ROAD_DIRECTION_S]), 
                cycle=np.random.randint(ROAD_CYCLE_LOW,ROAD_CYCLE_HIGH),
                ),
            Lilypad(
                density=np.random.uniform(LILYPAD_DENSITY_LOW,LILYPAD_DENSITY_HIGH),
                ),
            Rail(
                direction=np.random.choice(['r','l','s'], p=[RAIL_DIRECTION_R,RAIL_DIRECTION_L,RAIL_DIRECTION_S]),
                speed=np.random.randint(RAIL_SPEED_LOW,RAIL_SPEED_HIGH+1),
                interval=np.random.randint(RAIL_INTERVAL_LOW,RAIL_INTERVAL_HIGH),
            )
            ], p=[CHANCE_EMPTY,CHANCE_BUSH,CHANCE_LOGS,CHANCE_ROAD,CHANCE_LILYPAD,CHANCE_RAIL]))
        return lst
    
class NoLogs(Sections):
    """
    Section adder without logs. 
    """

    @env_checker
    def add(self,t) -> list[Layer]:
        lst = []
        for i in range(5):
            lst.append(np.random.choice([
            Empty(),
            Bush(
                density=np.random.uniform(BUSH_DENSITY_LOW,BUSH_DENSITY_HIGH),
                ),
            Road(
                density=np.random.uniform(ROAD_DENSITY_LOW,ROAD_DENSITY_HIGH), 
                direction=np.random.choice(['r','l','s'], p=[ROAD_DIRECTION_R,ROAD_DIRECTION_L,ROAD_DIRECTION_S]), 
                cycle=np.random.randint(ROAD_CYCLE_LOW,ROAD_CYCLE_HIGH),
                ),
            Lilypad(
                density=np.random.uniform(LILYPAD_DENSITY_LOW,LILYPAD_DENSITY_HIGH),
                ),
            Rail(
                direction=np.random.choice(['r','l','s'], p=[RAIL_DIRECTION_R,RAIL_DIRECTION_L,RAIL_DIRECTION_S]),
                speed=np.random.randint(RAIL_SPEED_LOW,RAIL_SPEED_HIGH+1),
                interval=np.random.randint(RAIL_INTERVAL_LOW,RAIL_INTERVAL_HIGH),
            )
            ], p=[0.2]*5))
        return lst 

class Hybrid(Sections):
    """
    Hybrid uses premade sections, such that every section is
    divided by a static layer. In between, 1-4 
    non-static layers are used of the same type. Here, rails are considered
    as non-static.
    """
    
    def addLogs(self):
        return Logs(
                density=np.random.uniform(LOGS_DENSITY_LOW,LOGS_DENSITY_HIGH), 
                direction=np.random.choice(['r','l','s'], p=[LOGS_DIRECTION_R,LOGS_DIRECTION_L,LOGS_DIRECTION_S]), 
                cycle=np.random.randint(LOGS_CYCLE_LOW,LOGS_CYCLE_HIGH),
                )
    
    def addRoad(self):
        return Road(
                density=np.random.uniform(ROAD_DENSITY_LOW,ROAD_DENSITY_HIGH), 
                direction=np.random.choice(['r','l','s'], p=[ROAD_DIRECTION_R,ROAD_DIRECTION_L,ROAD_DIRECTION_S]), 
                cycle=np.random.randint(ROAD_CYCLE_LOW,ROAD_CYCLE_HIGH),
                )
    
    def addRails(self):
        return Rail(
                direction=np.random.choice(['r','l','s'], p=[RAIL_DIRECTION_R,RAIL_DIRECTION_L,RAIL_DIRECTION_S]),
                speed=np.random.randint(RAIL_SPEED_LOW,RAIL_SPEED_HIGH+1),
                interval=np.random.randint(RAIL_INTERVAL_LOW,RAIL_INTERVAL_HIGH),
                )
    
    def addLilypads(self):
        return Lilypad(
                density=np.random.uniform(LILYPAD_DENSITY_LOW,LILYPAD_DENSITY_HIGH),
                )
    
    def addBush(self):
        return Bush(
                density=np.random.uniform(BUSH_DENSITY_LOW,BUSH_DENSITY_HIGH),
                )
    
    def addEmpty(self):
        return Empty(
                )
    
    @env_checker
    def add(self,t) -> list[Layer]:
        
        nonstatic = np.random.randint(0,3)
        static = np.random.randint(0,3)
        nrlayers = np.random.randint(1,5)

        lst = []
        for l in range(nrlayers):
            if nonstatic == 0: 
                newlayer = self.addLogs()
            elif nonstatic == 1:
                newlayer = self.addRails()
            elif nonstatic == 2:
                newlayer = self.addRoad()
            lst.append(newlayer)
        
        if static == 0: 
            newlayer = self.addBush()
        elif static == 1:
            newlayer = self.addEmpty()
        elif static == 2:
            newlayer = self.addLilypads()
        lst.append(newlayer)
        
        return lst

class Lookalike(Sections):
    """
    This section maker focusses on reproducing the structure of the actual
    game Crossy Road.
    """

    def addLogs(self):
        return Logs(
                density=np.random.uniform(LOGS_DENSITY_LOW,LOGS_DENSITY_HIGH), 
                direction=np.random.choice(['r','l','s'], p=[LOGS_DIRECTION_R,LOGS_DIRECTION_L,LOGS_DIRECTION_S]), 
                cycle=np.random.randint(LOGS_CYCLE_LOW,LOGS_CYCLE_HIGH),
                )
    
    def addRoad(self):
        return Road(
                density=np.random.uniform(ROAD_DENSITY_LOW,ROAD_DENSITY_HIGH), 
                direction=np.random.choice(['r','l','s'], p=[ROAD_DIRECTION_R,ROAD_DIRECTION_L,ROAD_DIRECTION_S]), 
                cycle=np.random.randint(ROAD_CYCLE_LOW,ROAD_CYCLE_HIGH),
                )
    
    def addRails(self):
        return Rail(
                direction=np.random.choice(['r','l','s'], p=[RAIL_DIRECTION_R,RAIL_DIRECTION_L,RAIL_DIRECTION_S]),
                speed=np.random.randint(RAIL_SPEED_LOW,RAIL_SPEED_HIGH+1),
                interval=np.random.randint(RAIL_INTERVAL_LOW,RAIL_INTERVAL_HIGH),
                )
    
    def addLilypads(self):
        return Lilypad(
                density=np.random.uniform(LILYPAD_DENSITY_LOW,LILYPAD_DENSITY_HIGH),
                )
    
    def addBush(self):
        return Bush(
                density=np.random.uniform(BUSH_DENSITY_LOW,BUSH_DENSITY_HIGH),
                )
    
    def addEmpty(self):
        return Empty(
                )
    
    @env_checker
    def add(self,t):

        def carSection():
            base = 1
            lst = [self.addRoad()]

            while np.random.uniform() <= base:
                base *= 0.7
                lst.append(self.addRoad())
            
            lst.append(self.addBush())
            return lst
        
        def logSection():
            base = 1
            lst = [self.addLogs()]

            while np.random.uniform() <= base:
                base *= 0.5
                lst.append(self.addLogs())
            
            if np.random.uniform() <= 0.3:
                lst.append(self.addBush())
            else:
                lst.append(self.addLilypads())

            return lst
        
        def trainSection():
            if np.random.uniform() <= 0.5:
                return [self.addRails(), self.addRails(), self.addBush()]
            return [self.addRails(), self.addBush()]

        def emptySection():
            base = 1
            lst = [self.addEmpty()]

            while np.random.uniform() <= base:
                base *= 0.2
                if np.random.uniform() <= 0.1:
                    lst.append(self.addEmpty())
                else:
                    lst.append(self.addBush())
            return lst
        
        
        dic = {
            0: logSection(),
            1: carSection(),
            2: trainSection(),
            3: emptySection()
        }
        lst = dic[np.random.randint(4)]

        return lst

class LookalikeIncDif(Sections):
    def __init__(self):
        """
        This section maker focusses on reproducing the structure of the actual
        game Crossy Road.
        """
        self.base = 0.5

    def addLogs(self):
        return Logs(
                density=np.random.uniform(LOGS_DENSITY_LOW,LOGS_DENSITY_HIGH), 
                direction=np.random.choice(['r','l','s'], p=[LOGS_DIRECTION_R,LOGS_DIRECTION_L,LOGS_DIRECTION_S]), 
                cycle=np.random.randint(LOGS_CYCLE_LOW,LOGS_CYCLE_HIGH),
                )
    
    def addRoad(self):
        return Road(
                density=np.random.uniform(ROAD_DENSITY_LOW,ROAD_DENSITY_HIGH), 
                direction=np.random.choice(['r','l','s'], p=[ROAD_DIRECTION_R,ROAD_DIRECTION_L,ROAD_DIRECTION_S]), 
                cycle=np.random.randint(ROAD_CYCLE_LOW,ROAD_CYCLE_HIGH),
                )
    
    def addRails(self):
        return Rail(
                direction=np.random.choice(['r','l','s'], p=[RAIL_DIRECTION_R,RAIL_DIRECTION_L,RAIL_DIRECTION_S]),
                speed=np.random.randint(RAIL_SPEED_LOW,RAIL_SPEED_HIGH+1),
                interval=np.random.randint(RAIL_INTERVAL_LOW,RAIL_INTERVAL_HIGH),
                )
    
    def addLilypads(self):
        return Lilypad(
                density=np.random.uniform(LILYPAD_DENSITY_LOW,LILYPAD_DENSITY_HIGH),
                )
    
    def addBush(self):
        return Bush(
                density=np.random.uniform(BUSH_DENSITY_LOW,BUSH_DENSITY_HIGH),
                )
    
    def addEmpty(self):
        return Empty(
                )
    
    @env_checker
    def add(self,t):

        def carSection():
            base = self.base
            lst = [self.addRoad()]

            while np.random.uniform() <= base:
                base *= 0.7
                lst.append(self.addRoad())
            
            lst.append(self.addBush())
            return lst
        
        def logSection():
            base = self.base
            lst = [self.addLogs()]

            while np.random.uniform() <= base:
                base *= 0.5
                lst.append(self.addLogs())
            
            if np.random.uniform() <= 0.3:
                lst.append(self.addBush())
            else:
                lst.append(self.addLilypads())

            return lst
        
        def trainSection():
            if np.random.uniform() <= 0.5:
                return [self.addRails(), self.addRails(), self.addBush()]
            return [self.addRails(), self.addBush()]

        def emptySection():
            base = 1
            lst = [self.addEmpty()]

            while np.random.uniform() <= base:
                base *= 0.2
                if np.random.uniform() <= 0.1:
                    lst.append(self.addEmpty())
                else:
                    lst.append(self.addBush())
            return lst
        
        self.base += 0.01
        
        dic = {
            0: logSection(),
            1: carSection(),
            2: trainSection(),
            3: emptySection()
        }
        lst = dic[np.random.randint(4)]

        return lst

class AllGrass(Sections):
    """
    The section with all default settings
    """

    @env_checker
    def add(self,t):
        lst = []
        for i in range(5):
            lst.append(np.random.choice([
            Empty(),
            Bush(
                density=np.random.uniform(BUSH_DENSITY_LOW,BUSH_DENSITY_HIGH),
                ),
            ], p=[0.8,0.2]))
        return lst
    
class AllLogs(Sections):
    """
    The section with all default settings
    """
    def addLogs(self):
        return Logs(
                density=np.random.uniform(LOGS_DENSITY_LOW,LOGS_DENSITY_HIGH), 
                direction=np.random.choice(['r','l','s'], p=[LOGS_DIRECTION_R,LOGS_DIRECTION_L,LOGS_DIRECTION_S]), 
                cycle=np.random.randint(LOGS_CYCLE_LOW,LOGS_CYCLE_HIGH),
                )
        
    @env_checker
    def add(self,t):
        lst = []
        for i in range(3):
            lst.append(self.addLogs())
        lst.append(Empty())
        return lst