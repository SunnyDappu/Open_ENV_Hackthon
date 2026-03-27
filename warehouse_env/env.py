"""
Warehouse Robot Picking & Sorting Environment
Real-world warehouse automation simulation for AI agent learning
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, List, Tuple, Any, Optional
import json
from dataclasses import dataclass, asdict
from enum import Enum
import math


class ItemType(Enum):
    """Item types in the warehouse"""
    SMALL = 1
    MEDIUM = 2
    LARGE = 3


@dataclass
class Item:
    """Item in the warehouse"""
    id: int
    type: ItemType
    position: Tuple[float, float]
    weight: float
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.name,
            'position': self.position,
            'weight': self.weight
        }


@dataclass
class Bin:
    """Sorting bin"""
    id: int
    position: Tuple[float, float]
    capacity: int
    required_type: Optional[ItemType]
    items: List[Item]
    
    def to_dict(self):
        return {
            'id': self.id,
            'position': self.position,
            'capacity': self.capacity,
            'required_type': self.required_type.name if self.required_type else None,
            'num_items': len(self.items),
            'fill_percentage': len(self.items) / self.capacity
        }


class WarehouseEnv:
    """
    Warehouse Robot Picking & Sorting Environment
    
    An OpenEnv compliant environment where an RL agent learns to pick items
    from shelves and sort them into bins under time and energy constraints.
    """
    
    def __init__(self, task_name: str = "basic_picking", seed: int = None):
        """
        Initialize the warehouse environment.
        
        Args:
            task_name: One of 'basic_picking', 'complex_sorting', 'expert_optimization'
            seed: Random seed for reproducibility
        """
        self.task_name = task_name
        self.seed_value = seed
        
        # Task configurations
        self.task_configs = {
            "basic_picking": {
                "grid_size": (20, 20),
                "num_items": 10,
                "num_bins": 2,
                "max_steps": 500,
                "battery_capacity": 1.0,
                "item_complexity": "simple",
                "num_obstacles": 0,
            },
            "complex_sorting": {
                "grid_size": (30, 30),
                "num_items": 25,
                "num_bins": 5,
                "max_steps": 1000,
                "battery_capacity": 1.0,
                "item_complexity": "medium",
                "num_obstacles": 8,
            },
            "expert_optimization": {
                "grid_size": (40, 40),
                "num_items": 50,
                "num_bins": 8,
                "max_steps": 1500,
                "battery_capacity": 0.8,
                "item_complexity": "hard",
                "num_obstacles": 12,
            }
        }
        
        # Load task config
        if task_name not in self.task_configs:
            raise ValueError(f"Unknown task: {task_name}")
        
        self.config = self.task_configs[task_name]
        
        # Initialize RNG
        if seed is not None:
            np.random.seed(seed)
        
        # Environment state
        self.grid_size = self.config["grid_size"]
        self.max_steps = self.config["max_steps"]
        self.current_step = 0
        
        # Robot state
        self.robot_position = np.array([self.grid_size[0] // 2, self.grid_size[1] // 2], dtype=np.float32)
        self.robot_rotation = 0.0
        self.robot_battery = self.config["battery_capacity"]
        self.max_battery = self.config["battery_capacity"]
        self.items_in_hand: List[Item] = []
        self.max_hand_capacity = 5
        
        # Warehouse objects
        self.items: Dict[int, Item] = {}
        self.bins: Dict[int, Bin] = {}
        self.obstacles: List[Tuple[float, float]] = []
        
        # Tracking metrics
        self.items_picked_correctly = 0
        self.items_sorted_correctly = 0
        self.total_distance_traveled = 0.0
        self.collisions = 0
        
        # Setup initial warehouse
        self._initialize_warehouse()
        
    def _initialize_warehouse(self):
        """Initialize the warehouse layout"""
        # Create items
        self.items = {}
        for i in range(self.config["num_items"]):
            item_type = self._generate_item_type()
            position = self._generate_random_position()
            item = Item(
                id=i,
                type=item_type,
                position=tuple(position),
                weight=self._get_item_weight(item_type)
            )
            self.items[i] = item
        
        # Create bins
        self.bins = {}
        for i in range(self.config["num_bins"]):
            bin_type = self._generate_bin_type()
            position = self._generate_random_position()
            bin_obj = Bin(
                id=i,
                position=tuple(position),
                capacity=10 + i * 2,  # Increasing capacity
                required_type=bin_type,
                items=[]
            )
            self.bins[i] = bin_obj
        
        # Create obstacles
        self.obstacles = []
        for _ in range(self.config["num_obstacles"]):
            obs_pos = self._generate_random_position()
            # Ensure not too close to robot start
            while np.linalg.norm(np.array(obs_pos) - self.robot_position) < 5:
                obs_pos = self._generate_random_position()
            self.obstacles.append(tuple(obs_pos))
    
    def _generate_item_type(self) -> ItemType:
        """Generate a random item type based on task complexity"""
        complexity = self.config["item_complexity"]
        if complexity == "simple":
            return ItemType.SMALL
        elif complexity == "medium":
            return np.random.choice([ItemType.SMALL, ItemType.MEDIUM])
        else:  # hard
            return np.random.choice([ItemType.SMALL, ItemType.MEDIUM, ItemType.LARGE])
    
    def _generate_bin_type(self) -> Optional[ItemType]:
        """Generate a bin type requirement"""
        if self.config["item_complexity"] == "simple":
            return None  # No type requirements
        return np.random.choice([ItemType.SMALL, ItemType.MEDIUM, ItemType.LARGE])
    
    def _get_item_weight(self, item_type: ItemType) -> float:
        """Get weight of item type"""
        return {ItemType.SMALL: 0.5, ItemType.MEDIUM: 1.0, ItemType.LARGE: 2.0}[item_type]
    
    def _generate_random_position(self) -> np.ndarray:
        """Generate random position within warehouse"""
        return np.array([
            np.random.uniform(1, self.grid_size[0] - 1),
            np.random.uniform(1, self.grid_size[1] - 1)
        ])
    
    def reset(self) -> Dict[str, Any]:
        """
        Reset environment to initial state.
        
        Returns:
            Initial observation dictionary
        """
        self.current_step = 0
        self.robot_position = np.array([self.grid_size[0] // 2, self.grid_size[1] // 2], dtype=np.float32)
        self.robot_rotation = 0.0
        self.robot_battery = self.max_battery
        self.items_in_hand = []
        
        # Reset metrics
        self.items_picked_correctly = 0
        self.items_sorted_correctly = 0
        self.total_distance_traveled = 0.0
        self.collisions = 0
        
        # Reinitialize warehouse
        self._initialize_warehouse()
        
        return self._get_observation()
    
    def state(self) -> Dict[str, Any]:
        """
        Get current environment state (observation).
        
        Returns:
            Complete state observation
        """
        return self._get_observation()
    
    def _get_observation(self) -> Dict[str, Any]:
        """Get complete observation of the environment"""
        # Visible items (within 10 unit radius)
        visible_items = []
        for item in self.items.values():
            dist = np.linalg.norm(np.array(item.position) - self.robot_position)
            if dist < 10.0:
                visible_items.append(item.to_dict())
        
        # Current target bin (closest empty bin with matching type)
        target_bin = None
        closest_bin = None
        min_dist = float('inf')
        
        for bin_obj in self.bins.values():
            if len(bin_obj.items) < bin_obj.capacity:
                dist = np.linalg.norm(np.array(bin_obj.position) - self.robot_position)
                if dist < min_dist:
                    min_dist = dist
                    closest_bin = bin_obj
        
        if closest_bin:
            target_bin = {
                'id': closest_bin.id,
                'position': closest_bin.position,
                'required_type': closest_bin.required_type.name if closest_bin.required_type else None,
                'distance': float(min_dist)
            }
        
        return {
            'robot_position': tuple(self.robot_position.astype(float)),
            'robot_rotation': float(self.robot_rotation),
            'robot_battery': float(self.robot_battery),
            'items_in_hand': [item.to_dict() for item in self.items_in_hand],
            'visible_items': visible_items,
            'target_bin': target_bin,
            'time_remaining': float(self.max_steps - self.current_step),
            'bins_state': {bin_id: bin_obj.to_dict() for bin_id, bin_obj in self.bins.items()},
            'episode_info': {
                'current_step': int(self.current_step),
                'total_items_picked': sum(len(b.items) for b in self.bins.values()),
                'total_items_sorted_correctly': self.items_sorted_correctly
            }
        }
    
    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.
        
        Args:
            action: Dictionary with 'action_type' and 'parameters'
                   - move: {direction: str, speed: float}
                   - pick: {item_id: int}
                   - drop: {bin_id: int}
                   - rotate: {angle: float}
        
        Returns:
            (observation, reward, done, info)
        """
        self.current_step += 1
        
        action_type = action.get('action_type', 'move')
        parameters = action.get('parameters', {})
        
        reward = 0.0
        info = {'action_executed': action_type}
        
        # Execute action
        if action_type == 'move':
            reward += self._execute_move(parameters)
        elif action_type == 'pick':
            reward += self._execute_pick(parameters)
        elif action_type == 'drop':
            reward += self._execute_drop(parameters)
        elif action_type == 'rotate':
            reward += self._execute_rotate(parameters)
        else:
            reward -= 0.01  # Small penalty for invalid action
        
        # Battery drain
        self.robot_battery = max(0, self.robot_battery - 0.01)
        
        # Check termination
        done = self.current_step >= self.max_steps or self.robot_battery <= 0
        
        # Add time bonus if all items sorted
        total_sorted = sum(len(b.items) for b in self.bins.values())
        if total_sorted == self.config["num_items"] and not done:
            time_remaining_ratio = (self.max_steps - self.current_step) / self.max_steps
            reward += 0.5 * time_remaining_ratio  # Bonus for early completion
        
        # Penalty for low battery
        if self.robot_battery < 0.2:
            reward -= 0.05
        
        observation = self._get_observation()
        
        return observation, float(reward), done, info
    
    def _execute_move(self, params: Dict) -> float:
        """Execute move action"""
        direction = params.get('direction', 'north')
        speed = np.clip(params.get('speed', 0.5), 0, 1.0)
        
        # Direction vectors
        directions = {
            'north': np.array([0, 1]),
            'south': np.array([0, -1]),
            'east': np.array([1, 0]),
            'west': np.array([-1, 0]),
            'northeast': np.array([1, 1]) / np.sqrt(2),
            'northwest': np.array([-1, 1]) / np.sqrt(2),
            'southeast': np.array([1, -1]) / np.sqrt(2),
            'southwest': np.array([-1, -1]) / np.sqrt(2),
        }
        
        if direction not in directions:
            return -0.05
        
        # Calculate new position
        move_dist = speed * 0.5  # Base movement distance
        new_position = self.robot_position + directions[direction] * move_dist
        
        # Check boundaries
        if 0 <= new_position[0] < self.grid_size[0] and 0 <= new_position[1] < self.grid_size[1]:
            # Check collisions with obstacles
            collision = False
            for obstacle in self.obstacles:
                if np.linalg.norm(new_position - np.array(obstacle)) < 0.5:
                    collision = True
                    self.collisions += 1
                    break
            
            if not collision:
                distance = np.linalg.norm(new_position - self.robot_position)
                self.total_distance_traveled += distance
                self.robot_position = new_position
                return -0.01  # Small movement cost
        
        return -0.05  # Penalty for invalid move
    
    def _execute_pick(self, params: Dict) -> float:
        """Execute pick action"""
        item_id = params.get('item_id', -1)
        
        if item_id not in self.items:
            return -0.05
        
        if len(self.items_in_hand) >= self.max_hand_capacity:
            return -0.05  # Hand is full
        
        item = self.items[item_id]
        distance = np.linalg.norm(np.array(item.position) - self.robot_position)
        
        if distance <= 1.5:  # Can pick if reasonably close (increased from 1.0 to 1.5)
            self.items_in_hand.append(item)
            del self.items[item_id]
            self.items_picked_correctly += 1
            return 0.1  # Reward for picking
        
        return -0.02  # Penalty for picking from far away
    
    def _execute_drop(self, params: Dict) -> float:
        """Execute drop action"""
        bin_id = params.get('bin_id', -1)
        
        if bin_id not in self.bins or not self.items_in_hand:
            return -0.05
        
        bin_obj = self.bins[bin_id]
        distance = np.linalg.norm(np.array(bin_obj.position) - self.robot_position)
        
        if distance <= 1.5:  # Can drop if reasonably close (increased from 1.0 to 1.5)
            if len(bin_obj.items) < bin_obj.capacity:
                item = self.items_in_hand.pop(0)
                
                # Check if correct type
                reward = 0.0
                if bin_obj.required_type is None or item.type == bin_obj.required_type:
                    reward = 0.3  # Bonus for correct placement
                    self.items_sorted_correctly += 1
                else:
                    reward = 0.05  # Small reward for any placement
                
                bin_obj.items.append(item)
                return reward
        
        return -0.02  # Penalty for dropping from far away
    
    def _execute_rotate(self, params: Dict) -> float:
        """Execute rotate action"""
        angle = params.get('angle', 0.0)
        self.robot_rotation = (self.robot_rotation + angle) % (2 * np.pi)
        return -0.001  # Minimal cost for rotation
    
    def render(self, mode: str = 'human') -> Optional[np.ndarray]:
        """
        Render the environment.
        
        Args:
            mode: 'human' or 'rgb_array'
        
        Returns:
            RGB array if mode is 'rgb_array', else None
        """
        # Simple text rendering
        if mode == 'human':
            print(f"Step {self.current_step}/{self.max_steps} | "
                  f"Battery: {self.robot_battery:.2f} | "
                  f"Sorted: {sum(len(b.items) for b in self.bins.values())}/{self.config['num_items']}")
    
    def close(self):
        """Close the environment"""
        pass


def make_warehouse_env(task_name: str = "basic_picking", seed: int = None) -> WarehouseEnv:
    """
    Factory function to create warehouse environment.
    
    Args:
        task_name: Task configuration name
        seed: Random seed
    
    Returns:
        WarehouseEnv instance
    """
    return WarehouseEnv(task_name=task_name, seed=seed)
