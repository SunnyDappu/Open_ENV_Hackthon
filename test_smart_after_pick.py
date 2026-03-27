"""See all SmartAgent actions after picking"""
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

env = WarehouseEnv(task_name="basic_picking", seed=42)
obs = env.reset()
agent = get_baseline_agent("smart")

pick_happened = False
for step in range(100):
    action = agent(obs)
    obs, reward, done, info = env.step(action)
    
    # Mark when pick happens
    if len(obs['items_in_hand']) > 0 and not pick_happened:
        pick_happened = True
        print(f"Step {step+1}: PICK SUCCESSFUL! items_in_hand={len(obs['items_in_hand'])}")
    
    # Show all actions after pick
    if pick_happened and step >= (step if step > 60 else 60):
        print(f"Step {step+1}: {action['action_type']:6s} | items_in_hand={len(obs['items_in_hand'])} | items_sorted={obs['episode_info']['total_items_sorted_correctly']} | battery={obs['robot_battery']:.3f}")
        if step > 70:
            break

print(f"\nFinal: items_in_hand={len(obs['items_in_hand'])}, sorted={obs['episode_info']['total_items_sorted_correctly']}")
