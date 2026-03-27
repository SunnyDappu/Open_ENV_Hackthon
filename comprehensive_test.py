"""Comprehensive test of fixed agents"""
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

print("="*80)
print("COMPREHENSIVE AGENT TESTING - DISTANCE THRESHOLD FIXES APPLIED")
print("="*80)

# Test greedy agent on all three tasks
for task in ["basic_picking", "complex_sorting"]:
    print(f"\n{'='*80}")
    print(f"GREEDY AGENT - {task.upper()}")
    print(f"{'='*80}")
    
    env = WarehouseEnv(task_name=task, seed=42)
    obs = env.reset()
    agent = get_baseline_agent("greedy")
    
    picks = 0
    sorts = 0
    moves = 0
    
    try:
        for step in range(env.max_steps):
            action = agent(obs)
            obs, reward, done, info = env.step(action)
            
            if action['action_type'] == 'pick':
                new_picks = obs['episode_info']['total_items_picked']
                if new_picks > picks:
                    picks = new_picks
                    print(f"  Step {step+1}: ✓ PICK #{picks} (reward: {reward:.3f})")
            
            elif action['action_type'] == 'drop':
                new_sorts = obs['episode_info']['total_items_sorted_correctly']
                if new_sorts > sorts:
                    sorts = new_sorts
                    print(f"  Step {step+1}: ✓ DROP → Sorted: {sorts} (reward: {reward:.3f})")
            
            elif action['action_type'] == 'move':
                moves += 1
            
            if done:
                print(f"\n  Episode ended at step {step+1}/{env.max_steps}")
                break
        
        print(f"\nFINAL RESULTS:")
        print(f"  - Items picked: {picks}/{env.config['num_items']}")
        print(f"  - Items sorted: {sorts}/{env.config['num_items']}")
        print(f"  - Success rate: {100*sorts/env.config['num_items']:.1f}%")
        print(f"  - Moves: {moves}")
        print(f"  - Battery remaining: {obs['robot_battery']:.3f}/{env.max_battery}")
        
        if sorts > 0:
            print(f"  ✅ AGENT SUCCESSFULLY PICKING AND SORTING!")
        else:
            print(f"  ⚠️ No items sorted (battery/time constraints)")
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
