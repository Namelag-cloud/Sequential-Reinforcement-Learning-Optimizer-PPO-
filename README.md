
# WUWA-RL-Agent

Reinforcement Learning agent for optimizing combat rotations in **Wuthering Waves** through a fully custom combat simulation environment.

Instead of directly playing the game, the agent interacts with a high-fidelity simulation of team combat mechanics and learns efficient rotations through reinforcement learning.

The project focuses on:
- sequential decision optimization
- action legality constraints
- reward shaping
- cooldown/resource management
- rotation efficiency under real gameplay mechanics

---

# Project Goal

Train an RL agent capable of discovering high-DPS combat rotations for a Wuthering Waves team composition.

Current simulated team:
- Danjin
- Mortefi
- Shorekeeper

The trained PPO agent achieved approximately:

- **~38k DPS**
compared to:
- **~42k DPS** top human speedrun-level rotations

This places the agent within roughly **90–95% of optimized human performance** under the simulated environment.

---

# Core Idea

The project does **not** automate gameplay input or interact with the game client.

Instead:
1. A custom simulator reproduces combat mechanics
2. The RL agent interacts with the simulator
3. The agent iteratively learns efficient move sequences
4. The simulator evaluates DPS, buff efficiency, resource management, and timing

The environment behaves similarly to a constrained optimization problem with sequential decisions.

---

# Technologies Used

- Python
- PyTorch
- Gymnasium
- Stable-Baselines3
- sb3-contrib (MaskablePPO)
- NumPy
- TensorBoard

---

# Key Features

## Custom Combat Simulator

A fully custom simulation environment was developed to model:

- cooldown systems
- buffs/debuffs
- resonance energy
- forte management
- concerto mechanics
- weapon buffs
- echo buffs
- action legality
- combo sequencing
- enemy HP scaling
- time-frame based combat execution

---

## Action Masking

The project uses **Maskable PPO** with dynamic action masking.

At every step:
- the simulator determines which actions are currently legal
- illegal actions are masked out before policy selection

Action legality depends on:
- cooldowns
- resources
- active states
- current character
- game-specific constraints

This significantly stabilized training and prevented invalid policy exploration.

Example:

```python
def action_masks(self):
    return self.sim.get_valid_action_mask()
```

---

# Observation Space

The agent observes a large flattened state representation including:

## Per-unit features
- cooldown states
- resource values
- forte / resonance / concerto
- recent move history
- active buffs
- weapon states
- echo states
- modifier encodings
- stack counts
- buff timers

## Global features
- enemy HP %
- normalized enemy HP range
- current frame/time
- global last action

## Action mask
The legality mask itself is appended to the state representation.

The simulator builds a high-dimensional state vector dynamically from game state information. :contentReference[oaicite:0]{index=0}

---

# Reinforcement Learning Setup

## Algorithm
- PPO (Proximal Policy Optimization)
- MaskablePPO implementation from `sb3-contrib`

## Environment
- Custom Gymnasium environment

## Parallel Training
Training used:
- 32 parallel environments
- `SubprocVecEnv`
- `VecNormalize`

## Network Architecture

```python
policy_kwargs = dict(
    net_arch=dict(pi=[1024, 1024], vf=[1024, 1024]),
    activation_fn=torch.nn.ReLU,
)
```

---

# Reward Design

The reward system was heavily shaped to encourage:
- efficient move usage
- high MV/sec actions
- proper resource spending
- buff optimization
- combo sequencing
- cooldown efficiency

Reward components included:
- damage efficiency
- forte generation/spending
- resonance efficiency
- concerto management
- buff contribution estimation
- action ranking
- combo-chain rewards
- DPS-based terminal rewards

The reward function evolved iteratively throughout experimentation. :contentReference[oaicite:1]{index=1}

---

# Training Infrastructure

Training was performed remotely on a Linux-based machine using:
- RTX 3090
- Ryzen 9 7900X
- 64 GB RAM

Development workflow:
- VSCode Remote
- Tailscale networking

---

# Main Challenges

## 1. Building a Reliable Simulator

The largest engineering challenge was constructing a stable simulation environment capable of accurately reproducing:
- resource interactions
- buff timing
- cooldown logic
- legal move constraints
- combat sequencing

A large portion of the project focused on simulator correctness and consistency.

---

## 2. Preventing Degenerate Policies

Early training frequently resulted in:
- random move spam
- repetitive loops
- low-efficiency action sequences

This required:
- reward shaping
- legality masking
- ranking heuristics
- curriculum adjustments
- entropy experimentation

before the agent consistently learned viable rotations.

---

## 3. Efficient Exploration

Balancing:
- exploration
- exploitation
- action diversity
- policy stability

was an ongoing challenge during training experimentation.

---

# Results

The final trained agents were capable of:
- producing stable rotations
- respecting game constraints
- managing resources correctly
- approaching optimized human-level DPS outputs

Key outcome:
- ~38k DPS achieved
- compared against ~42k optimized human benchmarks

---

# Repository Structure

```
WUWA-RL-Agent/
│
├── Echoes/
├── _pycache_/
├── data/
├── ppo_wuwa_tensorboard/ppo_wuwa_latch_/
├── resonators/
├── simulations/
├── weapons/
├──.gitignore
├── Main.py
└── model_training.py
```

---

# Future Improvements

Potential future directions include:
- multi-team generalization
- automated team composition testing
- improved curriculum learning
- transformer-based policies
- imitation learning from human rotations
- visualization tooling
- larger-scale distributed training

---

# Disclaimer

This project is:
- a simulation and reinforcement learning research project
- not a gameplay automation tool
- not connected to the live game client

---

# Author
Izzy
````
