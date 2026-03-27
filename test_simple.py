"""Simple test to see items being picked step by step"""
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

env = WarehouseEnv(task_name="basic_picking", seed=42)
obs = env.reset()
agent = get_baseline_agent("greedy")

print(f"Task: basic_picking")
print(f"Max steps: {env.max_steps}")
print(f"Battery capacity: {env.max_battery}")
print(f"Initial items: {len(env.items)}")
print(f"Initial visible items: {len(obs['visible_items'])}")

for step in range(150):
    action = agent(obs)
    obs, reward, done, info = env.step(action)
    
    if action['action_type'] in ['pick', 'drop']:
        print(f"Step {step+1:3d}: {action['action_type']:5s} | Items in hand: {len(obs['items_in_hand'])} | Items picked: {obs['episode_info']['total_items_picked']} | Items sorted: {obs['episode_info']['total_items_sorted_correctly']} | Battery: {obs['robot_battery']:.3f}")
    
    if done:
        print(f"\nEpisode ended at step {step+1}")
        break

print(f"\nFinal state:")
print(f"  Items picked: {obs['episode_info']['total_items_picked']}")
print(f"  Items sorted: {obs['episode_info']['total_items_sorted_correctly']}")
print(f"  Items in hand: {len(obs['items_in_hand'])}")
print(f"  Battery: {obs['robot_battery']:.3f}")
