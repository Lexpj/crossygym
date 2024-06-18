import gymnasium as gym
import crossyroadenv 

env = gym.make('CrossyRoadEnv-v0', render_mode = "human")

state, _ = env.reset()

done = False

while not done:
    action = env.action_space.sample()  # Take a random action
    
    state, reward, done, truncated, info = env.step(action)

    done = done or truncated

    env.render()
    
env.saveGIF()        
        
env.close()
