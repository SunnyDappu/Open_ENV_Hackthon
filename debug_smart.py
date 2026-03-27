"""Debug SmartAgent specifically"""
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

env = WarehouseEnv(task_name="basic_picking", seed=42)
obs = env.reset()
agent = get_baseline_agent("smart")

print(f"SmartAgent Debug")
print(f"Max steps: {env.max_steps}, Battery: {env.max_battery}")

for step in range(150):
    robot_pos = np.array(obs['robot_position'])
    visible_items = obs.get('visible_items', [])
    items_in_hand = obs.get('items_in_hand', [])
    target_bin = obs.get('target_bin')
    
    action = agent(obs)
    obs, reward, done, info = env.step(action)
    
    # Debug output
    if action['action_type'] in ['pick', 'drop'] or step < 5:
        if visible_items:
            closest_dist = min(np.linalg.norm(np.array(item['position']) - robot_pos) 
                             for item in visible_items)
        else:
            closest_dist = None
        
        bin_dist = target_bin['distance'] if target_bin else None
        
        closest_str = f"{closest_dist:.2f}" if closest_dist else "None"
        bin_str = f"{bin_dist:.2f}" if bin_dist else "None"
        print(f"Step {step+1:3d}: {action['action_type']:5s} | "
              f"Closest item: {closest_str:>5} | "
              f"Bin dist: {bin_str:>5} | "
              f"In hand: {len(items_in_hand)} | "
              f"Sorted: {obs['episode_info']['total_items_sorted_correctly']} | "
              f"Battery: {obs['robot_battery']:.3f}")
    
    if done:
        print(f"\nEpisode ended at step {step+1}")
        break
