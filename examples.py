#!/usr/bin/env python3
"""
Quick Start Example
Demonstrates complete workflow with Warehouse Environment
"""

import sys
from warehouse_env import WarehouseEnv
from warehouse_env.tasks import WarehouseGrader, BenchmarkTasks
from warehouse_env.baselines import get_baseline_agent, evaluate_all_agents, print_results_summary


def example_1_single_step():
    """Example 1: Execute a single step"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Single Step Execution")
    print("="*60)
    
    env = WarehouseEnv(task_name='basic_picking', seed=42)
    obs = env.reset()
    
    print(f"Initial observation:")
    print(f"  Robot Position: {obs['robot_position']}")
    print(f"  Battery: {obs['robot_battery']:.2f}")
    print(f"  Visible Items: {len(obs['visible_items'])}")
    print(f"  Target Bin: {obs['target_bin']}")
    
    # Execute a single move action
    action = {
        'action_type': 'move',
        'parameters': {'direction': 'north', 'speed': 0.7}
    }
    
    obs, reward, done, info = env.step(action)
    
    print(f"\nAfter one step:")
    print(f"  Robot Position: {obs['robot_position']}")
    print(f"  Battery: {obs['robot_battery']:.2f}")
    print(f"  Reward: {reward:.4f}")


def example_2_agent_episode():
    """Example 2: Run full episode with baseline agent"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Full Episode with Greedy Agent")
    print("="*60)
    
    env = WarehouseEnv(task_name='basic_picking', seed=42)
    obs = env.reset()
    agent = get_baseline_agent('greedy')
    
    total_reward = 0.0
    episode_data = []
    
    while True:
        action = agent(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        episode_data.append({'reward': reward})
        
        if done:
            break
    
    print(f"Episode completed:")
    print(f"  Steps: {env.current_step}/{env.max_steps}")
    print(f"  Total Reward: {total_reward:.2f}")
    print(f"  Items Picked: {obs['episode_info']['total_items_picked']}")
    print(f"  Items Sorted Correctly: {obs['episode_info']['total_items_sorted_correctly']}")
    print(f"  Final Battery: {obs['robot_battery']:.2f}")
    
    # Grade the episode
    grade = WarehouseGrader.grade_episode(env, episode_data, 'basic_picking')
    print(f"\nGrade Results:")
    print(f"  Final Score: {grade.final_score:.4f} / 1.0")
    print(f"  Pick Accuracy: {grade.pick_accuracy:.4f}")
    print(f"  Sort Accuracy: {grade.sort_accuracy:.4f}")
    print(f"  Efficiency: {grade.efficiency_score:.4f}")
    print(f"  Safety: {grade.safety_score:.4f}")


def example_3_task_comparison():
    """Example 3: Compare tasks difficulty"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Task Difficulty Comparison")
    print("="*60)
    
    print("\nAvailable Tasks:")
    for task_name in BenchmarkTasks.list_tasks():
        config = BenchmarkTasks.get_task_config(task_name)
        print(f"\n  {task_name}:")
        print(f"    Difficulty: {config['difficulty']}")
        print(f"    Description: {config['description']}")


def example_4_agent_benchmark():
    """Example 4: Benchmark agents on a task"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Agent Benchmark (Mini)")
    print("="*60)
    print("Evaluating 2 agents on 1 task (2 episodes for speed)...\n")
    
    results = evaluate_all_agents(
        tasks=['basic_picking'],
        agents=['greedy', 'smart'],
        num_episodes=2,
        seed=42,
        output_file=None,
        verbose=False
    )
    
    print_results_summary(results)


def example_5_all_baseline_agents():
    """Example 5: Test all baseline agents"""
    print("\n" + "="*60)
    print("EXAMPLE 5: All Baseline Agents")
    print("="*60)
    
    env = WarehouseEnv(task_name='basic_picking', seed=42)
    
    for agent_name in ['random', 'greedy', 'hierarchical', 'smart']:
        obs = env.reset()
        agent = get_baseline_agent(agent_name)
        
        total_reward = 0.0
        steps = 0
        
        for _ in range(50):
            action = agent(obs)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        print(f"{agent_name:<15} | Steps: {steps:3d} | Total Reward: {total_reward:7.2f}")


def example_6_custom_agent():
    """Example 6: Create and test a custom agent"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Custom Agent")
    print("="*60)
    
    class CustomAgent:
        """Simple custom agent: pick items if visible, else move randomly"""
        
        def __call__(self, obs):
            visible_items = obs.get('visible_items', [])
            items_in_hand = obs.get('items_in_hand', [])
            target_bin = obs.get('target_bin')
            
            # Strategy: drop if have items, pick if visible, else explore
            if items_in_hand and target_bin:
                if target_bin['distance'] < 1.5:
                    return {'action_type': 'drop', 'parameters': {'bin_id': target_bin['id']}}
            
            if visible_items and len(items_in_hand) < 3:
                return {'action_type': 'pick', 'parameters': {'item_id': visible_items[0]['id']}}
            
            return {'action_type': 'move', 'parameters': {'direction': 'north', 'speed': 0.5}}
    
    env = WarehouseEnv(task_name='basic_picking', seed=42)
    obs = env.reset()
    agent = CustomAgent()
    
    total_reward = 0.0
    for _ in range(100):
        action = agent(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        
        if done:
            break
    
    print(f"Custom Agent Performance:")
    print(f"  Steps: {env.current_step}")
    print(f"  Total Reward: {total_reward:.2f}")
    print(f"  Items Sorted Correctly: {obs['episode_info']['total_items_sorted_correctly']}")


def main():
    """Run all examples"""
    print("\n" + "🏭 WAREHOUSE ENVIRONMENT - QUICK START EXAMPLES 🏭".center(60))
    
    try:
        example_1_single_step()
        example_2_agent_episode()
        example_3_task_comparison()
        example_4_agent_benchmark()
        example_5_all_baseline_agents()
        example_6_custom_agent()
        
        print("\n" + "="*60)
        print("✓ All examples completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Read the README.md for detailed documentation")
        print("  2. Run: python -m warehouse_env.baselines.inference")
        print("  3. Deploy: python app.py (for Gradio interface)")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
