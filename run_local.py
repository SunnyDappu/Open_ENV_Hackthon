#!/usr/bin/env python
"""
Quick Start Runner - No installation required!
Just run this directly: python run_local.py
"""

import sys
import os

# Add warehouse_env to path so we can import it directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("\n" + "="*70)
    print("🏭 WAREHOUSE ENVIRONMENT - LOCAL RUNNER".center(70))
    print("="*70 + "\n")
    
    # Option menu
    print("Select what you want to run:\n")
    print("  1) Quick Examples (test environment)")
    print("  2) Full Benchmark Suite (evaluate all agents)")
    print("  3) Start Web UI (Gradio on localhost:7860)")
    print("  4) Run Tests (unit tests)")
    print("  5) Single Agent Test (interactive)")
    print("\nEnter choice (1-5): ", end="")
    
    try:
        choice = input().strip()
        
        if choice == "1":
            run_examples()
        elif choice == "2":
            run_benchmark()
        elif choice == "3":
            run_web_ui()
        elif choice == "4":
            run_tests()
        elif choice == "5":
            run_single_agent()
        else:
            print("Invalid choice!")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_examples():
    """Run quick examples"""
    print("\n📊 Running Quick Examples...\n")
    
    from warehouse_env import WarehouseEnv
    from warehouse_env.baselines import get_baseline_agent
    from warehouse_env.tasks import WarehouseGrader
    
    # Example 1: Single step
    print("="*70)
    print("Example 1: Single Step Execution")
    print("="*70)
    env = WarehouseEnv(task_name='basic_picking', seed=42)
    obs = env.reset()
    print(f"✓ Environment initialized")
    print(f"  Robot Position: {obs['robot_position']}")
    print(f"  Battery: {obs['robot_battery']:.2f}")
    print(f"  Visible Items: {len(obs['visible_items'])}")
    
    action = {'action_type': 'move', 'parameters': {'direction': 'north', 'speed': 0.7}}
    obs, reward, done, info = env.step(action)
    print(f"✓ Step executed - Reward: {reward:.4f}\n")
    
    # Example 2: Full episode
    print("="*70)
    print("Example 2: Full Episode with Smart Agent")
    print("="*70)
    env = WarehouseEnv(task_name='basic_picking', seed=42)
    obs = env.reset()
    agent = get_baseline_agent('smart')
    
    total_reward = 0.0
    trajectory = []
    step_count = 0
    
    while step_count < 100:
        action = agent(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        trajectory.append({'reward': reward})
        step_count += 1
        
        if done:
            break
    
    grade = WarehouseGrader.grade_episode(env, trajectory, 'basic_picking')
    
    print(f"✓ Episode completed in {env.current_step} steps")
    print(f"  Total Reward: {total_reward:.2f}")
    print(f"  Final Score: {grade.final_score:.4f}")
    print(f"  Pick Accuracy: {grade.pick_accuracy:.4f}")
    print(f"  Sort Accuracy: {grade.sort_accuracy:.4f}")
    print(f"  Items Sorted: {grade.metrics['items_sorted']}/{grade.metrics['total_items']}\n")
    
    # Example 3: All agents quick test
    print("="*70)
    print("Example 3: Quick Test - All Baseline Agents")
    print("="*70)
    
    for agent_name in ['random', 'greedy', 'hierarchical', 'smart']:
        env = WarehouseEnv(task_name='basic_picking', seed=42)
        obs = env.reset()
        agent = get_baseline_agent(agent_name)
        
        total_reward = 0.0
        for _ in range(50):
            action = agent(obs)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            if done:
                break
        
        print(f"  {agent_name:<15} | Total Reward: {total_reward:7.2f}")
    
    print("\n✓ Examples completed successfully!\n")


def run_benchmark():
    """Run full benchmark"""
    print("\n📈 Running Full Benchmark Suite...\n")
    print("This may take 2-5 minutes depending on your system.\n")
    
    from warehouse_env.baselines import evaluate_all_agents, print_results_summary
    
    results = evaluate_all_agents(
        tasks=['basic_picking', 'complex_sorting', 'expert_optimization'],
        agents=['random', 'greedy', 'hierarchical', 'smart'],
        num_episodes=3,
        seed=42,
        output_file='results/benchmark_results.json',
        verbose=True
    )
    
    print_results_summary(results)
    print("\n✓ Benchmark completed! Results saved to results/benchmark_results.json\n")


def run_web_ui():
    """Start Gradio web UI"""
    print("\n🌐 Starting Web UI...\n")
    
    try:
        from app import create_gradio_interface
        
        print("="*70)
        print("GRADIO WEB INTERFACE".center(70))
        print("="*70)
        print("\nStarting server on http://localhost:7860")
        print("Press Ctrl+C to stop the server\n")
        
        demo = create_gradio_interface()
        demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
    
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nTo use the web UI, install gradio:")
        print("  pip install gradio")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error starting UI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_tests():
    """Run unit tests"""
    print("\n🧪 Running Unit Tests...\n")
    
    import unittest
    from warehouse_env.tests.test_env import (
        TestWarehouseEnv, 
        TestTasks, 
        TestGrader,
        TestBaselineAgents,
        TestMultipleTasks
    )
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestWarehouseEnv))
    suite.addTests(loader.loadTestsFromTestCase(TestTasks))
    suite.addTests(loader.loadTestsFromTestCase(TestGrader))
    suite.addTests(loader.loadTestsFromTestCase(TestBaselineAgents))
    suite.addTests(loader.loadTestsFromTestCase(TestMultipleTasks))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    if result.wasSuccessful():
        print(f"✓ All {result.testsRun} tests passed!".center(70))
    else:
        print(f"✗ {len(result.failures)} failures, {len(result.errors)} errors".center(70))
    print("="*70 + "\n")


def run_single_agent():
    """Run single agent interactively"""
    print("\n🤖 Single Agent Interactive Test\n")
    
    from warehouse_env import WarehouseEnv
    from warehouse_env.baselines import get_baseline_agent
    
    # Select task
    print("Select task:")
    print("  1) basic_picking (easy)")
    print("  2) complex_sorting (medium)")
    print("  3) expert_optimization (hard)")
    task_choice = input("Enter 1-3: ").strip()
    
    tasks = {
        '1': 'basic_picking',
        '2': 'complex_sorting',
        '3': 'expert_optimization'
    }
    
    if task_choice not in tasks:
        print("Invalid choice!")
        return
    
    task = tasks[task_choice]
    
    # Select agent
    print("\nSelect agent:")
    print("  1) random")
    print("  2) greedy")
    print("  3) hierarchical")
    print("  4) smart")
    agent_choice = input("Enter 1-4: ").strip()
    
    agents_map = {
        '1': 'random',
        '2': 'greedy',
        '3': 'hierarchical',
        '4': 'smart'
    }
    
    if agent_choice not in agents_map:
        print("Invalid choice!")
        return
    
    agent_name = agents_map[agent_choice]
    
    print(f"\n▶️  Running {agent_name} agent on {task}...\n")
    
    env = WarehouseEnv(task_name=task, seed=42)
    obs = env.reset()
    agent = get_baseline_agent(agent_name)
    
    total_reward = 0.0
    step = 0
    
    while step < 100:
        action = agent(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        step += 1
        
        # Print progress every 20 steps
        if step % 20 == 0:
            sorted_items = obs['episode_info']['total_items_sorted']
            total_items = obs['episode_info']['total_items']
            battery = obs['robot_battery']
            print(f"Step {step:3d} | Sorted: {sorted_items:2d}/{total_items:2d} | "
                  f"Battery: {battery:.2f} | Reward: {reward:7.3f}")
        
        if done:
            break
    
    print(f"\n✓ Episode completed!")
    print(f"  Total Steps: {step}")
    print(f"  Total Reward: {total_reward:.2f}")
    print(f"  Items Sorted: {obs['episode_info']['total_items_sorted']}/{obs['episode_info']['total_items']}")
    print(f"  Final Battery: {obs['robot_battery']:.2f}\n")


if __name__ == '__main__':
    main()
