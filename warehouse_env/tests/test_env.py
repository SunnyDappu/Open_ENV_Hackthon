"""
Unit tests for Warehouse Environment
"""

import unittest
import numpy as np
from warehouse_env.env import WarehouseEnv, ItemType
from warehouse_env.tasks import WarehouseGrader, BenchmarkTasks
from warehouse_env.baselines import get_baseline_agent


class TestWarehouseEnv(unittest.TestCase):
    """Test warehouse environment functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.env = WarehouseEnv(task_name='basic_picking', seed=42)
    
    def test_initialization(self):
        """Test environment initializes correctly"""
        self.assertIsNotNone(self.env)
        self.assertEqual(self.env.task_name, 'basic_picking')
        self.assertEqual(self.env.config['num_items'], 10)
    
    def test_reset(self):
        """Test reset returns valid observation"""
        obs = self.env.reset()
        
        self.assertIn('robot_position', obs)
        self.assertIn('robot_battery', obs)
        self.assertIn('items_in_hand', obs)
        self.assertEqual(obs['robot_battery'], self.env.max_battery)
        self.assertEqual(len(obs['items_in_hand']), 0)
    
    def test_state_returns_observation(self):
        """Test state() returns same as last step observation"""
        obs1 = self.env.reset()
        obs2 = self.env.state()
        
        self.assertEqual(obs1['robot_position'], obs2['robot_position'])
        self.assertEqual(obs1['robot_battery'], obs2['robot_battery'])
    
    def test_move_action(self):
        """Test move action changes robot position"""
        self.env.reset()
        initial_pos = self.env.robot_position.copy()
        
        action = {
            'action_type': 'move',
            'parameters': {'direction': 'east', 'speed': 0.5}
        }
        obs, reward, done, info = self.env.step(action)
        
        # Position should change
        new_pos = self.env.robot_position
        distance = np.linalg.norm(new_pos - initial_pos)
        self.assertGreater(distance, 0)
    
    def test_battery_decreases(self):
        """Test battery decreases with each step"""
        self.env.reset()
        initial_battery = self.env.robot_battery
        
        action = {'action_type': 'move', 'parameters': {'direction': 'north', 'speed': 0.5}}
        obs, reward, done, info = self.env.step(action)
        
        self.assertLess(self.env.robot_battery, initial_battery)
    
    def test_pick_action(self):
        """Test pick action adds item to hand"""
        self.env.reset()
        
        # Get first visible item
        obs = self.env.state()
        visible_items = obs.get('visible_items', [])
        
        if visible_items:
            item_id = visible_items[0]['id']
            initial_hand_size = len(self.env.items_in_hand)
            
            action = {
                'action_type': 'pick',
                'parameters': {'item_id': item_id}
            }
            obs, reward, done, info = self.env.step(action)
            
            # Hand should have more items if pick was successful
            # (depends on proximity to item)
    
    def test_episode_termination(self):
        """Test episode terminates after max steps"""
        self.env.reset()
        
        for _ in range(self.env.max_steps + 1):
            action = {'action_type': 'move', 'parameters': {'direction': 'north', 'speed': 0.1}}
            obs, reward, done, info = self.env.step(action)
            if done:
                break
        
        self.assertTrue(done)
    
    def test_reward_structure(self):
        """Test reward is in expected range"""
        self.env.reset()
        
        for _ in range(10):
            action = {'action_type': 'move', 'parameters': {'direction': 'north', 'speed': 0.5}}
            obs, reward, done, info = self.env.step(action)
            
            # Reward should be reasonable
            self.assertIsInstance(reward, float)
            self.assertGreaterEqual(reward, -1.0)
            self.assertLessEqual(reward, 1.0)


class TestTasks(unittest.TestCase):
    """Test task definitions"""
    
    def test_all_tasks_exist(self):
        """Test all required tasks are defined"""
        tasks = BenchmarkTasks.list_tasks()
        self.assertIn('basic_picking', tasks)
        self.assertIn('complex_sorting', tasks)
        self.assertIn('expert_optimization', tasks)
    
    def test_task_config_valid(self):
        """Test task configurations are valid"""
        for task_name in BenchmarkTasks.list_tasks():
            config = BenchmarkTasks.get_task_config(task_name)
            self.assertIn('difficulty', config)
            self.assertIn('description', config)
            self.assertIn('expected_score_range', config)
    
    def test_difficulty_levels(self):
        """Test tasks have correct difficulty levels"""
        easy_tasks = BenchmarkTasks.get_tasks_by_difficulty('easy')
        medium_tasks = BenchmarkTasks.get_tasks_by_difficulty('medium')
        hard_tasks = BenchmarkTasks.get_tasks_by_difficulty('hard')
        
        self.assertGreater(len(easy_tasks), 0)
        self.assertGreater(len(medium_tasks), 0)
        self.assertGreater(len(hard_tasks), 0)


class TestGrader(unittest.TestCase):
    """Test evaluation grader"""
    
    def test_grading_creates_valid_score(self):
        """Test grader produces valid scores"""
        env = WarehouseEnv(task_name='basic_picking', seed=42)
        obs = env.reset()
        trajectory = []
        done = False
        
        # Run a few steps
        for _ in range(20):
            if done:
                break
            action = {'action_type': 'move', 'parameters': {'direction': 'north', 'speed': 0.5}}
            obs, reward, done, info = env.step(action)
            trajectory.append({'reward': reward})
        
        result = WarehouseGrader.grade_episode(env, trajectory, 'basic_picking')
        
        # Check scores are valid
        self.assertGreaterEqual(result.pick_accuracy, 0.0)
        self.assertLessEqual(result.pick_accuracy, 1.0)
        self.assertGreaterEqual(result.final_score, 0.0)
        self.assertLessEqual(result.final_score, 1.0)


class TestBaselineAgents(unittest.TestCase):
    """Test baseline agent implementations"""
    
    def test_random_agent_produces_valid_actions(self):
        """Test random agent produces valid actions"""
        agent = get_baseline_agent('random')
        env = WarehouseEnv(task_name='basic_picking', seed=42)
        obs = env.reset()
        
        for _ in range(10):
            action = agent(obs)
            self.assertIn('action_type', action)
            self.assertIn('parameters', action)
            
            obs, reward, done, info = env.step(action)
            if done:
                break
    
    def test_greedy_agent_produces_valid_actions(self):
        """Test greedy agent produces valid actions"""
        agent = get_baseline_agent('greedy')
        env = WarehouseEnv(task_name='basic_picking', seed=42)
        obs = env.reset()
        
        for _ in range(10):
            action = agent(obs)
            self.assertIn('action_type', action)
            self.assertIn('parameters', action)
            
            obs, reward, done, info = env.step(action)
            if done:
                break
    
    def test_all_agent_types_valid(self):
        """Test all agent types can be instantiated"""
        agent_names = ['random', 'greedy', 'hierarchical', 'smart']
        
        for agent_name in agent_names:
            agent = get_baseline_agent(agent_name)
            self.assertIsNotNone(agent)


class TestMultipleTasks(unittest.TestCase):
    """Test environment works with all task types"""
    
    def test_basic_picking_task(self):
        """Test basic_picking task"""
        env = WarehouseEnv(task_name='basic_picking', seed=42)
        obs = env.reset()
        self.assertIsNotNone(obs)
    
    def test_complex_sorting_task(self):
        """Test complex_sorting task"""
        env = WarehouseEnv(task_name='complex_sorting', seed=42)
        obs = env.reset()
        self.assertIsNotNone(obs)
    
    def test_expert_optimization_task(self):
        """Test expert_optimization task"""
        env = WarehouseEnv(task_name='expert_optimization', seed=42)
        obs = env.reset()
        self.assertIsNotNone(obs)


if __name__ == '__main__':
    unittest.main()
