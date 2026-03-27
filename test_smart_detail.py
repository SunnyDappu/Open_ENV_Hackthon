"""Test SmartAgent in detail"""
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

env = WarehouseEnv(task_name="basic_picking", seed=42)
obs = env.reset()
agent = get_baseline_agent("smart")

print(f"Initial items in env: {len(env.items)}")
print(f"Initial bins: {list(env.bins.keys())}")

for step in range(100):
    action = agent(obs)
    
    # DEBUG: Track action before step
    if action['action_type'] in ['pick', 'drop']:
        print(f"Step {step+1}: Attempting {action['action_type']}")
    
    obs, reward, done, info = env.step(action)
    
    # DEBUG: Track state after step
    if action['action_type'] == 'pick':
        print(f"  → After pick: items_in_hand={len(obs['items_in_hand'])}, items_picked={obs['episode_info']['total_items_picked']}, reward={reward:.3f}")
    elif action['action_type'] == 'drop':
        print(f"  → After drop: items_in_hand={len(obs['items_in_hand'])}, items_sorted={obs['episode_info']['total_items_sorted_correctly']}, reward={reward:.3f}")
    
    if done:
        print(f"\nEpisode ended at step {step+1}")
        break

print(f"\nFinal: picked={obs['episode_info']['total_items_picked']}, sorted={obs['episode_info']['total_items_sorted_correctly']}")
