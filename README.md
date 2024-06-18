
![](./example.gif)
# Crossy Road Gym

## Introduction
This GitHub contains the code for a simplified version of CrossyRoad. The objective of the game is to get as far as possible without colliding with vehicles, while utilizing objects. There are many obstacles such as cars and trains that the player must avoid. Furthermore, it must also use objects like logs and lilypads to cross water sections. The game plays out on an infinite world with a finite width.

The original game plays out on a grid world with a 2.5D top-level view. This game however is just a 2D level view. There are a lot of heuristics that go into generating such a world, which are explained in the original Bachelor thesis [1]. I will spare the details in this README, but you should know that this environment is highly adaptable to your likings, which I will explain here.

## Environmental details
I will go over the the details of this environment in terms of a Markov Decision Process in the form $<\mathcal{S},\mathcal{A},T(s'|s,a),r(s,a,s),p_0>$

First, the state space $\mathcal{S}$ is defined as follows. Since this environment is infinite, you cannot pass the whole state space to the agent. Therefore, only a portion of the environment is returned back as observation. This portion is relative to the agent, which can be adjusted via a `Mask` $\mathcal{M}$. For the sake of easy direct use, provides the current mask all information of every cell that is within 2 Manhattan distance of the agent. This normally is a 2D array, but again for easy direct use, this is flattened. All these options may be adjusted via `const.py`. 
The statespace itself is a `gym.Box` with size $|\mathcal{M}|$ with $\forall s \in \mathcal{S}, s \in [0,1]$. For 2D representation, a matrix is returned. Irregular masks will contain -1 values for cells not observed via the mask. Values of 0 means there is no obstruction, values of 1 means there is either an obstruction of a inaccessible cell, a terminal cell or a cell outside of the environment.

The action space $\mathcal{A}$ is a discrete set of 5 actions. These are, in chronological order, {up, left, down, right, still}. Actions $a \in \mathcal{A}$ integers between 0 up and including 4.

The transition function $\mathcal{T(s'|s,a)}$ is the probability of moving from state $s$ to state $s'$ via action $a$. There are two important things to denote here. First of all, the agent cannot enter inaccessible cells. This 'cancels' the action and does not move the agent. A penalty does apply, as seen in the reward function. Second, the agent moves along on a log. The game is still grid based, and will move the agent along with the log in the same way the grid is updated. Movement on the logs layer can be done, and standing still may move the agent along with the grid. 

The reward function $r(s,a,s')$ denotes the reward received when moving from state $s$ to state $s'$ via action $a$. This is defined as the following:

$$r(s,a,s') =
    \begin{cases}
      -100, & \text{if}\text{ $s'$ is terminal} \\
      -100, & \text{if}\text{ $s'$ is outside of the environment}\\
      -100, & \text{if}\text{ $s'$ is inaccessible} \\
      10, &\text{if}\ a = \text{up and to an unvisited (new) layer } \\  
      \text{otherwise $r(a)$} & \begin{cases}
          2, &\text{if}\ a =  \text{up} \\
          -1, &\text{if}\ a =  \text{left} \\
          -4, &\text{if}\ a =  \text{down} \\
          -1, &\text{if}\ a =  \text{right} \\
          0, &\text{if}\ a =  \text{still} \\
          \end{cases}
    \end{cases}
$$

The initial state distribution $p_0$ only states that the first 3 layers are defined as a starting area. These layers make up a boxed area of inaccessible states with only once side (forward) open for movement. 


## Usability
This is an Reinforcement Learning environment build with the framework Gymnasium, by Farama. This environment can be used to train RL agents, both via own implementation or via Stable Baselines 3 implementations. 

```python
import gymnasium as gym
import crossyroadenv 

env = gym.make('CrossyRoadEnv-v0', render_mode = "human")

state, _ = env.reset()
done = False
while not done:
    action = env.action_space.sample()
    state, reward, done, truncated, info = env.step(action)
    done = done or truncated
    env.render()
            
env.close()
```

Furthermore, this environment is serializable, since the environment is a function of some time $t$. 

## Customizable
There are a few ways to customize the generation of the environment. First of all, each environment is generated via a world generator. This generates new sections the further the agent progresses. Each section consists of layers, which is just a single row in the environment. Each layer can be customizable in the sense that you can adjust the hyperparameters of each layer which may affect the difficulty, the amount of layers generated in a section, different layers in a single section, or even adding own layers. There are many hyperparameters to play with in `const.py`, a few prebuild world generators in `sections.py`, and many layers in `layers.py`. Feel free to adjust the difficulty to your liking. 

The observation space, as mentioned, is also customizable. This is done via a mask. More info in `mask.py`.

## Recording
You may want to save a run as a GIF. This is possible via `env.saveGIF`, which outputs a rerun of your trace. This can only be done when the environment was initialized in `render_mode = 'human'`.

## Questions
If you have any questions, feel free to ask them on the following email:

s2989344(at)vuw(dot)leidenuniv(dot)nl

## Sources
All sources of public material is listed in the README within `./assets/`. The thesis and this environment is written by me. You may cite it via:

[1]: https://theses.liacs.nl/2690


```bibtex
@bachelorthesis{Janssens_2023, 
    type={thesis},
    title={Crossy Road AI: How will the chicken cross the road?}, 
    url={https://theses.liacs.nl/pdf/2022-2023-JanssensL.pdf}, 
    journal={Leiden Institute of Advanced Computer Science (LIACS)},
    author={Janssens, Lex}, 
    year={2023}, 
    month=jul}
```