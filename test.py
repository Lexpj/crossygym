import gymnasium as gym
import crossyroadenv  # This import ensures the registration code in crossyroadenv/__init__.py runs
import time

env = gym.make('CrossyRoadEnv-v0', render_mode = "human")

state, _ = env.reset()
done = False
while not done:
    action = env.action_space.sample()  # Take a random action
    
    state, reward, done, truncated, info = env.step(action)
    print(state)
    done = done or truncated

    env.render()
    
    
env.saveGIF()        
        
env.close()
