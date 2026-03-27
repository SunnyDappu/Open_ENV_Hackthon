"""Check visible_items stability"""
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

env = WarehouseEnv(task_name="basic_picking", seed=42)
obs = env.reset()
agent = get_baseline_agent("smart")

target_item_id = obs['visible_items'][0]['id'] if obs['visible_items'] else None
print(f"Initial closest item ID: {target_item_id if obs['visible_items'] else 'None'}")
print(f"Item position: {obs['visible_items'][0]['position'] if obs['visible_items'] else 'None'}")

for step in range(15):
    robot_pos = np.array(obs['robot_position'])
    visible_items = obs.get('visible_items', [])
    
    # Find closest item
    if visible_items:
        closest = min(visible_items, key=lambda x: np.linalg.norm(np.array(x['position']) - robot_pos))
        dist = np.linalg.norm(np.array(closest['position']) - robot_pos)
        print(f"\nStep {step+1}: Closest item ID: {closest['id']}, Distance: {dist:.3f}")
        if closest['id'] != target_item_id:
            print(f"  WARNING: Item ID changed from {target_item_id} to {closest['id']}!")
            print(f"  Item position: {closest['position']}")
    
    action = agent(obs)
    print(f"  Action: {action['parameters']['direction']}")
    obs, reward, done, info = env.step(action)
