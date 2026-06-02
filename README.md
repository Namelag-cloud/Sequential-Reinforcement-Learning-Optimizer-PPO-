# Sequential Reinforcement Learning Optimizer (PPO)

Reinforcement learning agent for **sequential decision optimization under dynamic constraints**, applied to a complex real-time combat system.

The agent learns near-optimal action sequences through a fully custom simulation environment — without interacting with any live game client. The problem structure closely mirrors constrained optimization challenges found in operations research, algorithmic trading, and resource scheduling: a high-dimensional state space, time-dependent action legality, and reward signals that emerge from long action sequences rather than individual decisions.

---

## Results

| Metric | Value |
|---|---|
| Agent DPS | ~38,000 |
| Expert human benchmark | ~42,000 |
| Performance vs benchmark | ~90–95% |

The remaining gap reflects a fundamental tradeoff: expert human rotations are near-deterministic finite state machines memorized through thousands of repetitions. A stochastic PPO policy optimizes for expected return across diverse states — sacrificing peak performance for generalization.

---

## Problem Structure

The simulation models a team of three units executing a sequence of actions over a fixed time window. Each action affects a shared global state — cooldown timers, resource levels, buff stacks, energy gauges — which then determines which actions are legal at the next step.

This creates a constrained sequential decision problem with:

- **Long credit assignment horizons** — a suboptimal decision at step *t* may only show up in damage output at step *t+20*
- **Dynamic action legality** — the valid action set changes every step based on current state
- **Interacting reward components** — buff timing, resource management, and combo sequencing all contribute to the terminal DPS outcome

---

## Technical Implementation

### Environment

Custom `Gymnasium` environment with a high-dimensional flattened observation vector including:

- Per-unit cooldown states, resource values, energy and gauge levels
- Active buff timers and stack counts
- Recent action history (last N moves per unit)
- Weapon and passive modifier encodings
- Global combat state (time elapsed, enemy HP)
- Dynamic action legality mask (appended directly to observation)

### Algorithm

`MaskablePPO` (from `sb3-contrib`) with dynamic action masking — at each step, the environment computes which actions are currently legal and masks the rest before policy selection. This eliminated invalid policy exploration and substantially stabilized early training.

```python
def action_masks(self):
    return self.sim.get_valid_action_mask()
```

Network architecture:

```python
policy_kwargs = dict(
    net_arch=dict(pi=[1024, 1024], vf=[1024, 1024]),
    activation_fn=torch.nn.ReLU,
)
```

### Training Infrastructure

- 32 parallel environments via `SubprocVecEnv`
- Observation and reward normalization via `VecNormalize`
- Remote training on RTX 3090 / Ryzen 9 7900X / 64GB RAM
- Experiment tracking via TensorBoard

### Reward Design

The reward function was shaped iteratively to address sparse terminal rewards. Components included:

- Damage efficiency per action (motion value / time)
- Resource generation and expenditure efficiency
- Buff contribution estimation
- Combo chain bonuses
- Terminal DPS reward at episode end

Reward shaping was the most iteratively difficult component — early designs produced degenerate policies (action loops, repetitive sequences) before the final formulation reliably encouraged efficient rotations.

---

## Key Engineering Challenges

**Simulator correctness** was the largest time investment. The simulation needed to accurately reproduce the interaction between cooldown systems, buff timers, resource mechanics, and action legality — any inconsistency between the simulator and actual game mechanics invalidated the learned policy.

**Degenerate policy prevention** required the combination of action masking, reward shaping, ranking heuristics, and entropy tuning before the agent consistently learned viable behavior.

**Credit assignment** over long action sequences (60–120 steps per episode) meant the agent had to learn that early-episode setup actions — building buff stacks, managing energy — determined late-episode damage output.

---

## Stack

Python · PyTorch · Gymnasium · Stable-Baselines3 · sb3-contrib (MaskablePPO) · NumPy · TensorBoard

---

## Potential Extensions

- Imitation learning pretraining from human expert trajectories
- Transformer-based policy for improved temporal reasoning
- Multi-team generalization across different unit compositions
- Automated team composition search

---

## Disclaimer

This project is a simulation and reinforcement learning research exercise. It does not automate gameplay, interact with any live game client, or violate any terms of service.

---

*Author: Izzy*
