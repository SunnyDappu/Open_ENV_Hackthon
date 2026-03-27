"""Test SmartAgent movement direction"""
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

env = WarehouseEnv(task_name="basic_picking", seed=42)
obs = env.reset()
agent = get_baseline_agent("smart")

print(f"Starting position: {obs['robot_position']}")
print(f"Closest visible item: {obs['visible_items'][0] if obs['visible_items'] else 'None'}")

for step in range(10):
    print(f"\nStep {step+1}:")
    print(f"  Robot pos: {obs['robot_position']}")
    
    action = agent(obs)
    print(f"  Action: {action['action_type']} - {action['parameters']}")
    
    obs, reward, done, info = env.step(action)
    print(f"  New pos: {obs['robot_position']}")
    print(f"  Battery: {obs['robot_battery']:.3f}")
