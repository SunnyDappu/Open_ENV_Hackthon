"""Check why drop doesn't trigger"""
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

env = WarehouseEnv(task_name="basic_picking", seed=42)
obs = env.reset()
agent = get_baseline_agent("smart")

for step in range(2, 101):
    items_in_hand = obs.get('items_in_hand', [])
    target_bin = obs.get('target_bin')
    visible_items = obs.get('visible_items', [])
    
    if len(items_in_hand) > 0:
        print(f"Step {step}: items_in_hand={len(items_in_hand)}, target_bin dist={target_bin['distance'] if target_bin else 'None'}, visible_items={len(visible_items)}")
    
    action = agent(obs)
    
    if len(items_in_hand) > 0 and action['action_type'] != 'pick':
        print(f"  → action: {action['action_type']}")
    
    obs, reward, done, info = env.step(action)
    
    if done:
        break
