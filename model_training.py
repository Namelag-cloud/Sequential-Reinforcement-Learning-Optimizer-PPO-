import gymnasium as gym
from gymnasium import spaces
import numpy as np
import torch
from pathlib import Path
from Main import build_demo_team
from sb3_contrib import MaskablePPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize, SubprocVecEnv
import os


def linear_schedule(initial_value: float):
    """Linear learning rate schedule."""
    def func(progress_remaining: float) -> float:
        return progress_remaining * initial_value
    return func


# ===================== #
#  WuWa Environment with action masking & logging
# ===================== #
class WuwaSimEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, device="cpu"):
        super().__init__()
        self.sim = build_demo_team()
        self.action_space = spaces.Discrete(len(self.sim.rl_index_to_name))
        obs, _ = self.sim.reset()
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=obs.shape, dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        obs, info = self.sim.reset()
        return obs, info

    def step(self, action):
        mask = self.sim.get_valid_action_mask()
        move_name = self.sim.rl_index_to_name.get(action, "???")

        if not mask[action]:
            print(f"[ILLEGAL] Move rejected: {move_name}", flush=True)
            return self.sim.get_state(), -1.0, True, False, {"illegal_action": True}

        obs, reward, terminated, truncated, info = self.sim.step(move_name)
        return obs, reward, terminated, truncated, info

    def action_masks(self):
        """MaskablePPO automatically uses this if present"""
        return self.sim.get_valid_action_mask()


# ===================== #
#  Training
# ===================== #
def make_env(seed=0):
    def _init():
        env = WuwaSimEnv()
        env.reset(seed=seed)
        return env
    return _init


if __name__ == "__main__":
    SEED = 1
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    # --- Step 1: Vectorized envs ---
    N_ENVS = 32
    base_env = SubprocVecEnv([make_env(SEED + i) for i in range(N_ENVS)])

    # load vecnormalize if available
    if os.path.exists("ppo_wuwa_vecnormalize.pkl"):
        env = VecNormalize.load("ppo_wuwa_vecnormalize.pkl", base_env)
        env.training = True
        env.norm_reward = True
    else:
        env = VecNormalize(base_env, norm_obs=True, norm_reward=True, clip_obs=10.0)

    # --- Step 2: Load or create model ---
    policy_kwargs = dict(
        net_arch=dict(pi=[1024, 1024], vf=[1024, 1024]),
        activation_fn=torch.nn.ReLU,
    )

    checkpoint_path = "ppo_wuwa_5000000.zip"
    if os.path.exists(checkpoint_path):
        print(f"Loading checkpoint from {checkpoint_path}")
        model = MaskablePPO.load(checkpoint_path, env=env, device="cuda", seed=SEED)
        model.ent_coef = 0.05 # e.g., higher than the default 0.01
        model.policy.ent_coef = model.ent_coef  # make sure policy uses it
    else:
        print("No checkpoint found, starting new model.")
        model = MaskablePPO(
            "MlpPolicy",
            env,
            policy_kwargs=policy_kwargs,
            learning_rate=3e-5,
            n_steps=2048,
            batch_size=8192,
            n_epochs=10,
            gamma=0.90,
            gae_lambda=0.95,
            clip_range=0.2,
            verbose=1,
            seed=SEED,
            device="cuda",
            tensorboard_log="./ppo_wuwa_tb/",
        )

    # --- Step 3: Continue training ---
    EXTRA_TIMESTEPS = 5_000_000  # train past 1.5M
    SAVE_FREQ = 1_000_000

    start_step = 0
    for i in range(1, EXTRA_TIMESTEPS // SAVE_FREQ + 1):
        model.learn(total_timesteps=SAVE_FREQ, reset_num_timesteps=False)
        model.save(f"ppo_wuwa_{start_step + i*SAVE_FREQ}")
        # env.save("ppo_wuwa_vecnormalize.pkl")
