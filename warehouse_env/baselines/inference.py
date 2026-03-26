"""
Baseline Inference Script - Evaluate agents on benchmark tasks
Produces reproducible scores across different agents and tasks
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Any
from warehouse_env.env import WarehouseEnv
from warehouse_env.tasks import WarehouseGrader, BenchmarkTasks
from warehouse_env.baselines.agents import get_baseline_agent


def evaluate_agent_on_task(
    agent_name: str,
    task_name: str,
    num_episodes: int = 5,
    seed: int = 42,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Evaluate a single agent on a single task.
    
    Args:
        agent_name: Name of the agent
        task_name: Name of the task
        num_episodes: Number of evaluation episodes
        seed: Random seed for reproducibility
        verbose: Print progress
    
    Returns:
        Evaluation results dictionary
    """
    agent = get_baseline_agent(agent_name)
    results = []
    rewards_log = []
    
    for episode in range(num_episodes):
        env = WarehouseEnv(task_name=task_name, seed=seed + episode)
        obs = env.reset()
        done = False
        episode_reward = 0.0
        steps = 0
        trajectory = []
        
        while not done and steps < env.max_steps:
            action = agent(obs)
            obs, reward, done, info = env.step(action)
            episode_reward += reward
            trajectory.append({
                'observation': obs,
                'reward': reward,
                'action': action
            })
            steps += 1
        
        # Grade the episode
        grade = WarehouseGrader.grade_episode(env, trajectory, task_name)
        results.append(grade)
        rewards_log.append(episode_reward)
        
        if verbose:
            print(f"  Episode {episode + 1}/{num_episodes} | "
                  f"Score: {grade.final_score:.4f} | "
                  f"Reward: {episode_reward:.2f} | "
                  f"Steps: {steps}")
    
    # Aggregate statistics
    final_scores = [r.final_score for r in results]
    pick_accs = [r.pick_accuracy for r in results]
    sort_accs = [r.sort_accuracy for r in results]
    eff_scores = [r.efficiency_score for r in results]
    saf_scores = [r.safety_score for r in results]
    
    return {
        'agent_name': agent_name,
        'task_name': task_name,
        'num_episodes': num_episodes,
        'seed': seed,
        'final_score_mean': float(np.mean(final_scores)),
        'final_score_std': float(np.std(final_scores)),
        'final_score_min': float(np.min(final_scores)),
        'final_score_max': float(np.max(final_scores)),
        'pick_accuracy_mean': float(np.mean(pick_accs)),
        'pick_accuracy_std': float(np.std(pick_accs)),
        'sort_accuracy_mean': float(np.mean(sort_accs)),
        'sort_accuracy_std': float(np.std(sort_accs)),
        'efficiency_score_mean': float(np.mean(eff_scores)),
        'efficiency_score_std': float(np.std(eff_scores)),
        'safety_score_mean': float(np.mean(saf_scores)),
        'safety_score_std': float(np.std(saf_scores)),
        'total_reward_mean': float(np.mean(rewards_log)),
        'total_reward_std': float(np.std(rewards_log)),
        'episode_results': [
            {
                'episode': i,
                'final_score': float(r.final_score),
                'pick_accuracy': float(r.pick_accuracy),
                'sort_accuracy': float(r.sort_accuracy),
                'efficiency': float(r.efficiency_score),
                'safety': float(r.safety_score),
                'metrics': {k: float(v) if isinstance(v, (int, float, np.number)) else v
                           for k, v in r.metrics.items()}
            }
            for i, r in enumerate(results)
        ]
    }


def evaluate_all_agents(
    tasks: List[str] = None,
    agents: List[str] = None,
    num_episodes: int = 3,
    seed: int = 42,
    output_file: str = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Evaluate all agents on all tasks.
    
    Args:
        tasks: List of task names, or None for all
        agents: List of agent names, or None for all
        num_episodes: Episodes per task-agent pair
        seed: Random seed
        output_file: Path to save results JSON
        verbose: Print progress
    
    Returns:
        Complete evaluation results
    """
    if tasks is None:
        tasks = BenchmarkTasks.list_tasks()
    if agents is None:
        agents = ['random', 'greedy', 'hierarchical', 'smart']
    
    all_results = {
        'timestamp': None,
        'config': {
            'tasks': tasks,
            'agents': agents,
            'num_episodes': num_episodes,
            'seed': seed
        },
        'results': []
    }
    
    total_evals = len(tasks) * len(agents)
    eval_count = 0
    
    for task_name in tasks:
        print(f"\n{'='*60}")
        print(f"Evaluating task: {task_name}")
        print(f"{'='*60}")
        
        task_results = {
            'task_name': task_name,
            'task_config': BenchmarkTasks.get_task_config(task_name),
            'agent_results': []
        }
        
        for agent_name in agents:
            eval_count += 1
            print(f"\n[{eval_count}/{total_evals}] Agent: {agent_name}")
            print("-" * 40)
            
            result = evaluate_agent_on_task(
                agent_name=agent_name,
                task_name=task_name,
                num_episodes=num_episodes,
                seed=seed + task_name.count('_') * 1000,
                verbose=verbose
            )
            task_results['agent_results'].append(result)
        
        all_results['results'].append(task_results)
    
    # Save results if requested
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        if verbose:
            print(f"\n\nResults saved to: {output_file}")
    
    return all_results


def print_results_summary(results: Dict[str, Any]):
    """Print a formatted summary of evaluation results"""
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    
    for task_result in results['results']:
        task_name = task_result['task_name']
        print(f"\n{task_name.upper()}")
        print("-" * 80)
        print(f"{'Agent':<15} {'Score':<10} {'Pick Acc':<10} {'Sort Acc':<10} {'Efficiency':<12}")
        print("-" * 80)
        
        for agent_result in task_result['agent_results']:
            agent = agent_result['agent_name']
            score = agent_result['final_score_mean']
            pick = agent_result['pick_accuracy_mean']
            sort = agent_result['sort_accuracy_mean']
            eff = agent_result['efficiency_score_mean']
            
            print(f"{agent:<15} {score:>9.4f} {pick:>9.4f} {sort:>9.4f} {eff:>11.4f}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate baseline agents on warehouse tasks')
    parser.add_argument('--tasks', nargs='+', default=None, help='Tasks to evaluate')
    parser.add_argument('--agents', nargs='+', default=None, help='Agents to evaluate')
    parser.add_argument('--episodes', type=int, default=5, help='Episodes per evaluation')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output', type=str, default='results/baseline_results.json', help='Output file')
    parser.add_argument('--verbose', action='store_true', default=True, help='Verbose output')
    
    args = parser.parse_args()
    
    # Run evaluation
    results = evaluate_all_agents(
        tasks=args.tasks,
        agents=args.agents,
        num_episodes=args.episodes,
        seed=args.seed,
        output_file=args.output,
        verbose=args.verbose
    )
    
    # Print summary
    print_results_summary(results)
