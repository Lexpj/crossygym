from crossyroadenv.world import World
from crossyroadenv.const import *
from crossyroadenv.layers import *
from crossyroadenv.agent import Agent
import os
import pygame
from PIL import Image
from pathlib import Path
pygame.init()

def getImage(img, w = 1, h = 1) -> pygame.Surface:
    """
    Returns the image img with a certain width and height according to the TILEWIDTH and TILEHEIGHT
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    surface = pygame.image.load(dir_path+f"\\assets\\{img}.png")
    surface = pygame.transform.scale(surface, (w*TILEWIDTH,h*TILEHEIGHT))
    return surface

def drawLayer(layer: Layer, world: World) -> pygame.Surface:
    
    surface = pygame.Surface((TILEWIDTH*GRIDWIDTH, TILEHEIGHT))
    
    if type(layer) == Empty:
        grass = getImage("grass")
        for i in range(GRIDWIDTH):
            surface.blit(grass, (i*TILEWIDTH, 0))
            
    
    elif type(layer) == Bush:
        grass = getImage("grass")
        for i in range(GRIDWIDTH):
            surface.blit(grass, (i*TILEWIDTH, 0))

        bush = getImage("bush")
        for ind, item in enumerate(layer.representation):
            if item == 'B':
                surface.blit(bush, (ind*TILEWIDTH, 0))  
        
    elif type(layer) == Logs:
        water = getImage("water")
        for i in range(GRIDWIDTH):
            surface.blit(water, (i*TILEWIDTH, 0))

        logsurface = pygame.Surface((TILEWIDTH*GRIDWIDTH*2, TILEHEIGHT))
        logsurface = logsurface.convert_alpha()
        logsurface.fill((0, 0, 0, 0))
        for pos, len in layer.logConfiguration:
            logsurface.blit(getImage(f"log{len}",w=len,h=1),(pos*TILEWIDTH,0))
            
        if layer.direction == "r":
            surface.blit(logsurface, ((((world.t*layer.speed)%layer.maxtime)-GRIDWIDTH) *TILEWIDTH, 0))
        elif layer.direction == "l":
            surface.blit(logsurface, ((-((world.t*layer.speed)%layer.maxtime)) *TILEWIDTH, 0))
        
    
    elif type(layer) == Road:

        road = getImage("road")
        for i in range(GRIDWIDTH):
            surface.blit(road, (i*TILEWIDTH, 0))


        carSurface = pygame.Surface((TILEWIDTH*GRIDWIDTH*2, TILEHEIGHT))
        carSurface = carSurface.convert_alpha()
        carSurface.fill((0, 0, 0, 0))
    
        for pos, len, randomcar in layer.carConfiguration:
            
            if len == 2:
                carimg = getImage(f"car{randomcar}",w=len,h=1)
                if layer.direction == "l":
                    carimg = pygame.transform.rotate(carimg, 180)
                carSurface.blit(carimg,(pos*TILEWIDTH,0))
                carSurface.blit(carimg,((pos+GRIDWIDTH)*TILEWIDTH,0))
            elif len == 3:
                carimg = getImage(f"truck{randomcar}",w=len,h=1)
                if layer.direction == "l":
                    carimg = pygame.transform.rotate(carimg, 180)
                carSurface.blit(carimg,(pos*TILEWIDTH,0))
                carSurface.blit(carimg,((pos+GRIDWIDTH)*TILEWIDTH,0))

            elif len == 4:
                carimg = getImage(f"trailer{randomcar}",w=len,h=1)
                if layer.direction == "l":
                    carimg = pygame.transform.rotate(carimg, 180)
                carSurface.blit(carimg,(pos*TILEWIDTH,0))
                carSurface.blit(carimg,((pos+GRIDWIDTH)*TILEWIDTH,0))
            else:
                for i in range(pos,pos+len):
                    layer.representation[i] = '0'
                    layer.representation[i+GRIDWIDTH] = '0'
        if layer.direction == "r":
            surface.blit(carSurface, ((((world.t*layer.speed)%layer.maxtime)-GRIDWIDTH) *TILEWIDTH, 0))
        
        elif layer.direction == "l":
            surface.blit(carSurface, ((-((world.t*layer.speed)%layer.maxtime)) *TILEWIDTH, 0))
            
            
    elif type(layer) == Lilypad:
        water = getImage("water")
        for i in range(GRIDWIDTH):
            surface.blit(water, (i*TILEWIDTH, 0))

        lilypad = getImage("lilypad")
        for ind, item in enumerate(layer.representation):
            if item == 'P':
                surface.blit(lilypad, (ind*TILEWIDTH, 0))

    elif type(layer) == Rail:
        gravel = getImage("gravel")
        rail = getImage("rail (2)")
        
        for i in range(GRIDWIDTH):
            surface.blit(gravel, (i*TILEWIDTH, 0))
            surface.blit(rail,(i*TILEWIDTH, 0))
    
        # lights and train
        train = getImage('train2',w=7)
        greenlight = getImage("greenlight",w=0.25)
        redlight = getImage("redlight",w=0.25)

        trainsurface = pygame.Surface((TILEWIDTH*7, TILEHEIGHT))
        trainsurface = trainsurface.convert_alpha()
        trainsurface.fill((0, 0, 0, 0))
        if layer.direction == "l":
            train = pygame.transform.flip(train, True, False)
        trainsurface.blit(train,(0,0))
        
        rep = layer.observation(world.t)
        if 't' in rep:
            surface.blit(redlight,(TILEWIDTH*6,0))
            
            if 'T' in rep:
                ind = rep.index('T')
                if ind < 7:
                    surface.blit(trainsurface,((rep.index('T')-(7-rep.count('T')))*TILEWIDTH,0))
                else:
                    surface.blit(trainsurface,(rep.index('T')*TILEWIDTH,0))
            
        else:
            surface.blit(greenlight,(TILEWIDTH*6,0))
        
            
    
    return surface

def overlay(world: World, agent: Agent) -> pygame.Surface:
    """
    Returns an overlay (according to BINARY_VISION) 
    that shows the hitboxes as well as the vision grid
    """                
    overlaySurface = pygame.Surface((APPWIDTH,APPHEIGHT))
    overlaySurface = overlaySurface.convert_alpha()
    overlaySurface.fill((0,0,0,0))
    overlaySurface.set_alpha(128) 

    font = pygame.font.SysFont(None, 24)

    floatobs = world.getObservationFloats(agent)[::-1]
    
    
    # Binary overlay grid
    for i,layer in enumerate(floatobs):
        for j in range(len(layer)):
            
            pygame.draw.rect(overlaySurface, (255*floatobs[i][j],255*(1-floatobs[i][j]),0), [j*TILEWIDTH ,i*TILEHEIGHT, TILEWIDTH, TILEHEIGHT])
            text = font.render(str(layer[j]), True, (255,0,0))
            text_rect = text.get_rect(center=(j*TILEWIDTH + TILEWIDTH//2,i*TILEHEIGHT + TILEHEIGHT//2))
            overlaySurface.blit(text, text_rect)

    # Grid lines
    for i in range(GRIDHEIGHT):
        pygame.draw.line(overlaySurface, (255,255,255), [0,i*TILEHEIGHT],[APPWIDTH,i*TILEHEIGHT])
    for i in range(GRIDWIDTH):
        pygame.draw.line(overlaySurface, (255,255,255), [i*TILEWIDTH,0],[i*TILEHEIGHT,APPHEIGHT])
    
    
    return overlaySurface
        
def renderWorld(world: World, agent: Agent) -> pygame.Surface:
    """
    Draws the entire overlay as a pygame.Surface
    """
    
    def getAgentSprite() -> pygame.Surface:
        """
        Returns the sprite of the agent in the right direction (based on the last action taken
        that is not standing still)
        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        
        chosen = {
            0:"chickup",
            1:"chickside",
            2:"chickdown",
            3:"chickside"
        }        
        surface = pygame.image.load(dir_path+f"./assets/{chosen[agent.lastAction]}.png")
        agentSprite = pygame.transform.scale(surface, (TILEWIDTH,TILEHEIGHT))
        agentSprite = agentSprite.convert_alpha()
        agentSprite.set_colorkey((255,255,255))
        if agent.lastAction == 3:
            agentSprite = pygame.transform.flip(agentSprite, True, False)
            agentSprite = agentSprite.convert_alpha()
            agentSprite.set_colorkey((255,255,255))
        return agentSprite
    
    surface = pygame.Surface((APPWIDTH,APPHEIGHT))
    # Clear current surface
    surface.fill((0,0,0,0))
    
    # Draw layers bottom up # NOTE: unsure about range agentpos[1]+1
    for ind, layer in enumerate(world[agent.y-LAYERS_UNDERNEATH+1:agent.y-LAYERS_UNDERNEATH+1+GRIDHEIGHT]):
        surface.blit(drawLayer(layer, world), (0, (GRIDHEIGHT-1-ind)*TILEHEIGHT))
    
    # Draw agent
    if type(world[agent.y]) == Logs:

        layer = world[agent.y]
        offset = ((layer.speed * world.t) % GRIDWIDTH) % 1
        if layer.direction in "r":
            if round(offset) == 1 or layer.hasMoved:
                surface.blit(getAgentSprite(),((agent.x - (1-offset))*TILEWIDTH, (GRIDHEIGHT-LAYERS_UNDERNEATH)*TILEHEIGHT))
            else:
                surface.blit(getAgentSprite(),((agent.x + offset)*TILEWIDTH, (GRIDHEIGHT-LAYERS_UNDERNEATH)*TILEHEIGHT))
        elif layer.direction == 'l':
            if round(offset) == 0 and not layer.hasMoved:
                surface.blit(getAgentSprite(),((agent.x -offset)*TILEWIDTH, (GRIDHEIGHT-LAYERS_UNDERNEATH)*TILEHEIGHT))
            else:
                surface.blit(getAgentSprite(),((agent.x + (1-offset))*TILEWIDTH, (GRIDHEIGHT-LAYERS_UNDERNEATH)*TILEHEIGHT))
        else:
            surface.blit(getAgentSprite(),(agent.x*TILEWIDTH, (GRIDHEIGHT-LAYERS_UNDERNEATH)*TILEHEIGHT))
    else:
        surface.blit(getAgentSprite(),(agent.x*TILEWIDTH, (GRIDHEIGHT-LAYERS_UNDERNEATH)*TILEHEIGHT))

    # If showscore, show it in the top left corner
    if SHOWSCORE:
        font = pygame.font.SysFont(None, 24)
        txt = font.render(f'Score: {agent.highscore}', True, (255,255,255))
        surface.blit(txt, (0, 0))

    # Draw overlay
    if OVERLAY:
        o = overlay(world,agent)
        surface.blit(o, (0,0))

    return surface

def recordingToGif(path, world: World, agent: Agent) -> None:
    """
    Saves the recording frames to a GIF
    :param pos: last position of the agent
    """
    def getSkull(nr):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        surface = pygame.image.load(dir_path+"./assets/skulls.png")
        surface = pygame.transform.scale(surface, (4*TILEWIDTH,2*TILEHEIGHT))
        subsurface = surface.subsurface(((nr%4)*TILEWIDTH, (nr//4)*TILEHEIGHT, TILEWIDTH, TILEHEIGHT))
        return subsurface
    
    # Replay
    replayAgent = Agent()
    actionTrace = agent.trace_a
    world.t = 0
    frames = []
    
    for a in actionTrace:
        frame = renderWorld(world, replayAgent)
        frames.append(Image.frombytes("RGBA",(APPWIDTH,APPHEIGHT),pygame.image.tostring(frame,"RGBA",False)))
        replayAgent.step(a)
        world.t += 1
        
    endframe = renderWorld(world, replayAgent)
    endframeFig = Image.frombytes("RGBA",(APPWIDTH,APPHEIGHT),pygame.image.tostring(frame,"RGBA",False))
    frames.append(endframeFig)

    for i in range(8):
        newframe = renderWorld(world, replayAgent)

        newframe.blit(getSkull(i),[(min(max(replayAgent.x,-0.5),GRIDWIDTH-0.5))*TILEWIDTH,(GRIDHEIGHT-LAYERS_UNDERNEATH)*TILEHEIGHT])
        
        frames.append(Image.frombytes("RGBA",(APPWIDTH,APPHEIGHT),pygame.image.tostring(newframe,"RGBA",False)))

        world.t += 1
    
    
    Path(path).mkdir(parents=True, exist_ok=True)
    
    frames[0].save(f"{path}{world.seed}-{agent.highscore}-{world.t}.gif", format="GIF", append_images=frames[1:],
        save_all=True, duration=100, loop=0)
