"""
Constants file
These constants will be used if no other adjustments
are made to the parameters.
"""



###
# App constants
###
GRIDWIDTH = 15
GRIDHEIGHT = 14

APPWIDTH = 750
APPHEIGHT = 700

TILEWIDTH = APPWIDTH//GRIDWIDTH
TILEHEIGHT = APPHEIGHT//GRIDHEIGHT

WORLD_GENERATOR = 'hybrid'
MAX_AGE = -1                       # Max age truncated the environment, -1 means endless

###
# Agent
###

LAYERS_UNDERNEATH = 2
STARTLOCATION = [GRIDWIDTH//2, LAYERS_UNDERNEATH-1]

###
# State tags
###

WALKABLE_STATES = 'L0Pt'
INVALID_STATES = 'B'
TERMINAL_STATES = 'CW1T'

STATE_REP = {
    **{s:0 for s in WALKABLE_STATES},
    **{s:1 for s in INVALID_STATES},
    **{s:1 for s in TERMINAL_STATES}
}
STATE_REP['t'] = 0.5

###
# Vision
###

MASK = """..x..
          .xxx.
          xxoxx
          .xxx.
          ..x.."""
FLATTEN = True

###
# Rewards
###

REWARDS = {
    0: 2,
    1: -1,
    2: -4,
    3: -1,
    4: 0
}
REWARD_INVALID = -100
REWARD_TERMINATED = -100
REWARD_TRUNCATED = -100
REWARD_NEWLAYER = 10

###
# Layer constants
###

BUSH_DENSITY_LOW = 0.1
BUSH_DENSITY_HIGH = 0.5

LOGS_DENSITY_LOW = 0.4
LOGS_DENSITY_HIGH = 0.8
LOGS_CYCLE_LOW = 100
LOGS_CYCLE_HIGH = 500
LOGS_DIRECTION_R = 0.5
LOGS_DIRECTION_L = 0.5
LOGS_DIRECTION_S = 0.0

ROAD_DENSITY_LOW = 0.3
ROAD_DENSITY_HIGH = 0.5
ROAD_CYCLE_LOW = 50
ROAD_CYCLE_HIGH = 250
ROAD_DIRECTION_R = 0.5
ROAD_DIRECTION_L = 0.5
ROAD_DIRECTION_S = 0

LILYPAD_DENSITY_LOW = 0.5
LILYPAD_DENSITY_HIGH = 0.8

RAIL_SPEED_LOW = 3
RAIL_SPEED_HIGH = 5
RAIL_INTERVAL_LOW = 20
RAIL_INTERVAL_HIGH = 50
RAIL_DIRECTION_R = 0.5
RAIL_DIRECTION_L = 0.5
RAIL_DIRECTION_S = 0
RAIL_WARN_STEPS = 5

CHANCE_EMPTY = 0.1
CHANCE_BUSH = 0.1
CHANCE_LOGS = 0.2
CHANCE_ROAD = 0.2
CHANCE_LILYPAD = 0.2
CHANCE_RAIL = 0.2

###
# Visuals
###
RECORD_PATH = "./gifs/"         # path where the gifs are saved
SHOWSCORE = True
FPS = 30

###
# Debug
###
OVERLAY = False
