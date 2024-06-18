from gymnasium.envs.registration import register

register(
    id='CrossyRoadEnv-v0',
    entry_point='crossyroadenv.env:CrossyRoadEnv',
)