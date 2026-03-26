"""
Benchmark tasks and gradeers for Warehouse Environment
"""

import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from warehouse_env.env import WarehouseEnv


@dataclass
class TaskResult:
    """Result of a task evaluation"""
    task_name: str
    pick_accuracy: float
    sort_accuracy: float
    efficiency_score: float
    safety_score: float
    final_score: float
    metrics: Dict[str, Any]


class WarehouseGrader:
    """Grader for warehouse environment tasks"""
    
    @staticmethod
    def grade_episode(
        env: WarehouseEnv,
        agent_trajectory: List[Dict],
        task_name: str
    ) -> TaskResult:
        """
        Grade an episode based on multiple metrics.
        
        Args:
            env: The environment instance
            agent_trajectory: List of (observation, action, reward) tuples
            task_name: Name of the task
        
        Returns:
            TaskResult with detailed metrics
        """
        total_items = env.config["num_items"]
        
        # Metrics calculation
        pick_accuracy = (env.items_picked_correctly / total_items) if total_items > 0 else 0.0
        sort_accuracy = (env.items_sorted_correctly / total_items) if total_items > 0 else 0.0
        
        # Efficiency: Energy and time efficiency combined
        battery_efficiency = env.robot_battery / env.max_battery  # Remaining battery
        time_efficiency = (env.max_steps - env.current_step) / env.max_steps
        efficiency_score = 0.6 * battery_efficiency + 0.4 * time_efficiency
        
        # Safety: Penalize collisions
        max_possible_collisions = env.config["num_obstacles"] * 10
        safety_score = max(0.0, 1.0 - (env.collisions / max(1, max_possible_collisions)))
        
        # Path optimization bonus
        avg_distance_per_item = env.total_distance_traveled / max(1, env.items_picked_correctly)
        path_efficiency = 1.0 / (1.0 + avg_distance_per_item / env.grid_size[0])
        
        # Combined efficiency
        efficiency_score = np.clip(efficiency_score * path_efficiency, 0, 1)
        
        # Final score with proper weights
        final_score = (
            0.3 * pick_accuracy +
            0.3 * sort_accuracy +
            0.2 * efficiency_score +
            0.2 * safety_score
        )
        
        # Additional metrics for analysis
        metrics = {
            'total_items': total_items,
            'items_picked': env.items_picked_correctly,
            'items_sorted': env.items_sorted_correctly,
            'total_distance': env.total_distance_traveled,
            'collisions': env.collisions,
            'battery_used': env.max_battery - env.robot_battery,
            'time_used': env.current_step,
            'avg_distance_per_item': avg_distance_per_item,
            'path_efficiency': path_efficiency,
        }
        
        return TaskResult(
            task_name=task_name,
            pick_accuracy=float(np.clip(pick_accuracy, 0, 1)),
            sort_accuracy=float(np.clip(sort_accuracy, 0, 1)),
            efficiency_score=float(np.clip(efficiency_score, 0, 1)),
            safety_score=float(np.clip(safety_score, 0, 1)),
            final_score=float(np.clip(final_score, 0, 1)),
            metrics=metrics
        )
    
    @staticmethod
    def evaluate_agent(
        agent_fn,
        task_name: str = "basic_picking",
        num_episodes: int = 5,
        seed: int = 42
    ) -> Dict[str, Any]:
        """
        Evaluate an agent over multiple episodes.
        
        Args:
            agent_fn: Function that takes observation and returns action
            task_name: Task to evaluate on
            num_episodes: Number of evaluation episodes
            seed: Random seed
        
        Returns:
            Aggregated evaluation results
        """
        results = []
        
        for episode in range(num_episodes):
            env = WarehouseEnv(task_name=task_name, seed=seed + episode)
            obs = env.reset()
            trajectory = []
            done = False
            
            while not done:
                action = agent_fn(obs)
                obs, reward, done, info = env.step(action)
                trajectory.append({'obs': obs, 'reward': reward})
            
            result = WarehouseGrader.grade_episode(env, trajectory, task_name)
            results.append(result)
        
        # Aggregate results
        return {
            'task_name': task_name,
            'num_episodes': num_episodes,
            'pick_accuracy': np.mean([r.pick_accuracy for r in results]),
            'sort_accuracy': np.mean([r.sort_accuracy for r in results]),
            'efficiency_score': np.mean([r.efficiency_score for r in results]),
            'safety_score': np.mean([r.safety_score for r in results]),
            'final_score': np.mean([r.final_score for r in results]),
            'final_score_std': np.std([r.final_score for r in results]),
            'episode_results': results
        }


class BenchmarkTasks:
    """Collection of benchmark tasks with difficulty levels"""
    
    TASKS = {
        'basic_picking': {
            'name': 'Basic Item Picking',
            'description': 'Pick 10 simple items and sort into 2 bins in a 20x20 warehouse',
            'difficulty': 'easy',
            'expected_score_range': (0.6, 0.9),  # Expected score range for a good agent
        },
        'complex_sorting': {
            'name': 'Complex Sorting Task',
            'description': 'Pick 25 items into 5 bins with type requirements and obstacles (30x30)',
            'difficulty': 'medium',
            'expected_score_range': (0.4, 0.8),
        },
        'expert_optimization': {
            'name': 'Expert-Level Optimization',
            'description': 'Pick 50 items into 8 bins with energy constraints and dynamic obstacles (40x40)',
            'difficulty': 'hard',
            'expected_score_range': (0.2, 0.6),
        }
    }
    
    @staticmethod
    def get_task_config(task_name: str) -> Dict[str, Any]:
        """Get configuration for a specific task"""
        return BenchmarkTasks.TASKS.get(task_name, {})
    
    @staticmethod
    def list_tasks() -> List[str]:
        """List all available tasks"""
        return list(BenchmarkTasks.TASKS.keys())
    
    @staticmethod
    def get_tasks_by_difficulty(difficulty: str) -> List[str]:
        """Get all tasks of a specific difficulty"""
        return [
            name for name, config in BenchmarkTasks.TASKS.items()
            if config['difficulty'] == difficulty
        ]
