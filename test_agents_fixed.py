"""Test that agents now successfully pick and sort items"""
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.baselines.agents import get_baseline_agent

def test_agent(agent_name, task_name="basic_picking", num_steps=500):
    """Run agent and track picking/sorting success"""
    print(f"\n{'='*80}")
    print(f"Testing {agent_name.upper()} on {task_name}")
    print(f"{'='*80}")
    
    env = WarehouseEnv(task_name=task_name, seed=42)
    obs = env.reset()
    agent = get_baseline_agent(agent_name)
    
    picks = 0
    sorts = 0
    max_pick_distance = 0
    
    for step in range(num_steps):
        action = agent(obs)
        obs, reward, done, info = env.step(action)
        
        # Track successful picks/sorts
        current_picks = obs['episode_info']['total_items_picked']
        current_sorts = obs['episode_info']['total_items_sorted_correctly']
        
        if current_picks > picks:
            picks = current_picks
            print(f"  Step {step+1}: ✓ Item picked! (Total: {picks})")
        
        if current_sorts > sorts:
            sorts = current_sorts
            print(f"  Step {step+1}: ✓ Item sorted correctly! (Total: {sorts})")
        
        # Track closest item distance when attempting pick
        if action['action_type'] == 'pick':
            visible_items = obs.get('visible_items', [])
            if visible_items:
                robot_pos = np.array(obs['robot_position'])
                min_dist = min(np.linalg.norm(np.array(item['position']) - robot_pos) 
                             for item in visible_items)
                max_pick_distance = max(max_pick_distance, min_dist)
        
        if done:
            print(f"  Episode completed at step {step+1}")
            break
    
    print(f"\n  RESULTS:")
    print(f"    - Items picked: {picks}/{env.config['num_items']}")
    print(f"    - Items sorted: {sorts}/{env.config['num_items']}")
    print(f"    - Success rate: {100*sorts/env.config['num_items']:.1f}%")
    print(f"    - Battery remaining: {obs['robot_battery']:.3f}")
    print(f"    - Steps taken: {env.current_step}/{env.max_steps}")
    
    return picks > 0 and sorts > 0

# Test all agents
print("\n" + "="*80)
print("TESTING FIXED AGENTS - SHOULD NOW PICK AND SORT ITEMS")
print("="*80)

results = {}
for agent in ['greedy', 'smart', 'hierarchical']:
    try:
        success = test_agent(agent, task_name="basic_picking", num_steps=500)
        results[agent] = "✅ PASS" if success else "❌ FAIL"
    except Exception as e:
        print(f"ERROR testing {agent}: {e}")
        results[agent] = "❌ ERROR"

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
for agent, result in results.items():
    print(f"  {agent.upper():15} {result}")

all_pass = all("✅" in r for r in results.values())
if all_pass:
    print("\n🎉 ALL AGENTS NOW WORKING! Items are being picked and sorted.")
else:
    print("\n⚠️ Some agents still need fixes")
