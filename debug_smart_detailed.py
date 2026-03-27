"""Detailed SmartAgent debug"""
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

env = WarehouseEnv(task_name="basic_picking", seed=42)
obs = env.reset()

# Manually run SmartAgent logic to trace it
robot_pos = np.array(obs['robot_position'])
items_in_hand = obs.get('items_in_hand', [])
visible_items = obs.get('visible_items', [])

print(f"Initial state:")
print(f"  Robot position: {robot_pos}")
print(f"  Items in hand: {len(items_in_hand)}")
print(f"  Visible items: {len(visible_items)}")

if visible_items:
    closest = min(visible_items, key=lambda x: np.linalg.norm(np.array(x['position']) - robot_pos))
    dist = np.linalg.norm(np.array(closest['position']) - robot_pos)
    print(f"\nClosest item:")
    print(f"  Item ID: {closest['id']}")
    print(f"  Item position: {closest['position']}")
    print(f"  Distance to item: {dist:.3f}")
    print(f"  Should pick? dist <= 1.5: {dist <= 1.5}")
    print(f"  Should move towards? dist > 1.5: {dist > 1.5}")
    
    if dist > 1.5:
        direction_vec = np.array(closest['position']) - robot_pos
        print(f"\n  Direction vector: {direction_vec}")
        print(f"  Direction magnitude: {np.linalg.norm(direction_vec):.3f}")
        
        # SmartAgent _vec_to_direction
        vec = direction_vec / (np.linalg.norm(direction_vec) + 1e-6)
        print(f"  Normalized vector: {vec}")
        
        angle = np.arctan2(vec[1], vec[0])
        print(f"  Angle (arctan2): {angle:.4f} rad ({np.degrees(angle):.1f}°)")
        
        angles = {
            'north': 0,
            'northeast': np.pi/4,
            'east': np.pi/2,
            'southeast': 3*np.pi/4,
            'south': np.pi,
            'southwest': 5*np.pi/4,
            'west': 3*np.pi/2,
            'northwest': 7*np.pi/4,
        }
        
        print(f"\n  Angle differences:")
        for d, a in angles.items():
            diff = abs(angles[d] - angle)
            print(f"    {d:10s}: {a:6.4f} → diff = {diff:.4f}")
        
        closest_direction = min(angles.keys(), key=lambda d: abs(angles[d] - angle))
        print(f"\n  Chosen direction: {closest_direction}")

# Now test actual agent
print(f"\n{'='*60}")
print("Testing actual SmartAgent:")
agent = get_baseline_agent("smart")
action = agent(obs)
print(f"  Action: {action}")
