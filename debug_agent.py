"""Debug script to trace agent behavior"""
import json
import sys
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

# Initialize environment
env = WarehouseEnv(task_name="basic_picking", seed=42)
obs = env.reset()

print("=" * 80)
print("INITIAL OBSERVATION")
print("=" * 80)
print(f"Type of observation: {type(obs)}")
print(f"Keys in observation: {obs.keys()}")
print(f"\nvisible_items type: {type(obs['visible_items'])}")
print(f"visible_items length: {len(obs['visible_items'])}")
print(f"visible_items content (first 2): {obs['visible_items'][:2] if obs['visible_items'] else 'EMPTY'}")
print(f"\nitems_in_hand type: {type(obs['items_in_hand'])}")
print(f"items_in_hand: {obs['items_in_hand']}")
print(f"\nrobot_position: {obs['robot_position']}")
print(f"target_bin: {obs['target_bin']}")

# Test each agent
for agent_name in ['greedy', 'smart', 'hierarchical']:
    print(f"\n{'=' * 80}")
    print(f"TESTING {agent_name.upper()} AGENT")
    print(f"{'=' * 80}")
    
    env = WarehouseEnv(task_name="basic_picking", seed=42)
    obs = env.reset()
    agent = get_baseline_agent(agent_name)
    
    # Run 10 steps and trace
    for step in range(10):
        print(f"\n--- STEP {step + 1} ---")
        
        # Debug info
        robot_pos = np.array(obs['robot_position'])
        visible_items = obs.get('visible_items', [])
        items_in_hand = obs.get('items_in_hand', [])
        print(f"Visible items: {len(visible_items)}")
        print(f"Items in hand: {len(items_in_hand)}")
        
        if visible_items:
            closest = min(visible_items, 
                        key=lambda x: np.linalg.norm(np.array(x['position']) - robot_pos))
            dist = np.linalg.norm(np.array(closest['position']) - robot_pos)
            print(f"Closest item distance: {dist:.3f}")
            print(f"Closest item: {closest}")
        
        # Get action from agent
        try:
            action = agent(obs)
            print(f"Agent action: {action}")
            
            # Execute step
            obs, reward, done, info = env.step(action)
            print(f"Reward: {reward:.3f}, Done: {done}")
            print(f"Battery: {obs['robot_battery']:.3f}, Items sorted: {obs['episode_info']['total_items_sorted_correctly']}")
            
            if done:
                print("Episode done!")
                break
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            break
