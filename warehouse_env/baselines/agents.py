"""
Baseline agents for Warehouse Environment
Demonstrates various strategies from random to rule-based to RL-ready
"""

import numpy as np
from typing import Dict, Any, Callable
from warehouse_env.env import ItemType
import math


class RandomAgent:
    """Baseline random agent - takes random valid actions"""
    
    def __call__(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select a random action.
        
        Args:
            observation: Current environment state
        
        Returns:
            Action dictionary
        """
        action_type = np.random.choice(['move', 'pick', 'drop', 'rotate'])
        
        if action_type == 'move':
            direction = np.random.choice(['north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest'])
            speed = np.random.uniform(0.3, 1.0)
            return {
                'action_type': 'move',
                'parameters': {'direction': direction, 'speed': speed}
            }
        
        elif action_type == 'pick':
            visible_items = observation.get('visible_items', [])
            if visible_items:
                item_id = np.random.choice([item['id'] for item in visible_items])
                return {
                    'action_type': 'pick',
                    'parameters': {'item_id': item_id}
                }
        
        elif action_type == 'drop':
            items_in_hand = observation.get('items_in_hand', [])
            if items_in_hand:
                bin_id = np.random.randint(0, 8)  # Max 8 bins
                return {
                    'action_type': 'drop',
                    'parameters': {'bin_id': bin_id}
                }
        
        elif action_type == 'rotate':
            angle = np.random.uniform(0, 2 * np.pi)
            return {
                'action_type': 'rotate',
                'parameters': {'angle': angle}
            }
        
        # Default: move
        return {
            'action_type': 'move',
            'parameters': {'direction': 'north', 'speed': 0.5}
        }


class GreedyAgent:
    """Greedy agent - prioritizes picking items and dropping them"""
    
    def __call__(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Greedy strategy: pick visible items, then move to bins.
        
        Args:
            observation: Current environment state
        
        Returns:
            Action dictionary
        """
        robot_pos = np.array(observation['robot_position'])
        items_in_hand = observation.get('items_in_hand', [])
        visible_items = observation.get('visible_items', [])
        target_bin = observation.get('target_bin')
        bins_state = observation.get('bins_state', {})
        
        # Strategy 1: Drop items if we have any and are near a bin
        if items_in_hand and target_bin:
            bin_dist = target_bin['distance']
            if bin_dist < 2.0:  # Close to bin
                return {
                    'action_type': 'drop',
                    'parameters': {'bin_id': target_bin['id']}
                }
        
        # Strategy 2: Pick items if visible and hand not full
        if visible_items and len(items_in_hand) < 5:
            # Pick closest item
            closest_item = min(visible_items, 
                             key=lambda x: np.linalg.norm(np.array(x['position']) - robot_pos))
            item_distance = np.linalg.norm(np.array(closest_item['position']) - robot_pos)
            
            if item_distance < 2.0:  # Close enough to pick
                return {
                    'action_type': 'pick',
                    'parameters': {'item_id': closest_item['id']}
                }
            else:
                # Move towards closest item
                direction_vec = np.array(closest_item['position']) - robot_pos
                direction_vec = direction_vec / (np.linalg.norm(direction_vec) + 1e-6)
                
                # Quantize direction
                if abs(direction_vec[1]) > abs(direction_vec[0]):
                    direction = 'north' if direction_vec[1] > 0 else 'south'
                else:
                    direction = 'east' if direction_vec[0] > 0 else 'west'
                
                return {
                    'action_type': 'move',
                    'parameters': {'direction': direction, 'speed': 0.7}
                }
        
        # Strategy 3: Move to target bin if we have items
        if items_in_hand and target_bin:
            direction_vec = np.array(target_bin['position']) - robot_pos
            direction_vec = direction_vec / (np.linalg.norm(direction_vec) + 1e-6)
            
            if abs(direction_vec[1]) > abs(direction_vec[0]):
                direction = 'north' if direction_vec[1] > 0 else 'south'
            else:
                direction = 'east' if direction_vec[0] > 0 else 'west'
            
            return {
                'action_type': 'move',
                'parameters': {'direction': direction, 'speed': 0.8}
            }
        
        # Default: explore by moving in a random direction
        direction = np.random.choice(['north', 'south', 'east', 'west'])
        return {
            'action_type': 'move',
            'parameters': {'direction': direction, 'speed': 0.5}
        }


class HierarchicalAgent:
    """Hierarchical agent - more sophisticated planning"""
    
    def __init__(self):
        self.state = 'explore'  # explore, pick_target, move_to_bin, drop
        self.target_item = None
    
    def __call__(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hierarchical strategy with sub-goals.
        
        Args:
            observation: Current environment state
        
        Returns:
            Action dictionary
        """
        robot_pos = np.array(observation['robot_position'])
        items_in_hand = observation.get('items_in_hand', [])
        visible_items = observation.get('visible_items', [])
        target_bin = observation.get('target_bin')
        battery = observation['robot_battery']
        time_remaining = observation['time_remaining']
        
        # State machine
        if self.state == 'drop' and items_in_hand and target_bin:
            bin_dist = target_bin['distance']
            if bin_dist < 1.5:
                return {
                    'action_type': 'drop',
                    'parameters': {'bin_id': target_bin['id']}
                }
            else:
                # Move to bin
                direction_vec = np.array(target_bin['position']) - robot_pos
                direction = self._vec_to_direction(direction_vec)
                return {
                    'action_type': 'move',
                    'parameters': {'direction': direction, 'speed': 0.8}
                }
        
        if self.state == 'pick_target' and self.target_item:
            item_data = next((i for i in visible_items if i['id'] == self.target_item), None)
            if item_data:
                item_dist = np.linalg.norm(np.array(item_data['position']) - robot_pos)
                if item_dist < 1.0:
                    self.state = 'drop' if items_in_hand else 'explore'
                    return {
                        'action_type': 'pick',
                        'parameters': {'item_id': self.target_item}
                    }
                else:
                    direction_vec = np.array(item_data['position']) - robot_pos
                    direction = self._vec_to_direction(direction_vec)
                    return {
                        'action_type': 'move',
                        'parameters': {'direction': direction, 'speed': 0.7}
                    }
            else:
                self.state = 'explore'
        
        # Explore state - look for items
        if visible_items and len(items_in_hand) < 4:
            self.target_item = visible_items[0]['id']
            self.state = 'pick_target'
        elif items_in_hand and len(items_in_hand) >= 3:
            self.state = 'drop'
        else:
            self.state = 'explore'
        
        # In explore state, move towards items or randomly
        if self.state == 'explore':
            if visible_items:
                closest = visible_items[0]
                direction_vec = np.array(closest['position']) - robot_pos
            else:
                # Random exploration
                direction_vec = np.array([np.random.randn(), np.random.randn()])
            
            direction = self._vec_to_direction(direction_vec)
            return {
                'action_type': 'move',
                'parameters': {'direction': direction, 'speed': 0.6}
            }
        
        return {
            'action_type': 'move',
            'parameters': {'direction': 'north', 'speed': 0.5}
        }
    
    @staticmethod
    def _vec_to_direction(vec: np.ndarray) -> str:
        """Convert vector to discrete direction"""
        vec = vec / (np.linalg.norm(vec) + 1e-6)
        
        if abs(vec[1]) > abs(vec[0]):
            return 'north' if vec[1] > 0 else 'south'
        else:
            return 'east' if vec[0] > 0 else 'west'


class SmartAgent:
    """Smart agent with task-aware planning"""
    
    def __init__(self):
        self.last_action_type = None
        self.action_counter = 0
    
    def __call__(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Smart strategy with task awareness.
        
        Args:
            observation: Current environment state
        
        Returns:
            Action dictionary
        """
        self.action_counter += 1
        robot_pos = np.array(observation['robot_position'])
        items_in_hand = observation.get('items_in_hand', [])
        visible_items = observation.get('visible_items', [])
        target_bin = observation.get('target_bin')
        battery = observation['robot_battery']
        bins_state = observation.get('bins_state', {})
        
        # Energy management - check if there are still visible items to sort
        items_sorted = observation['episode_info']['total_items_sorted_correctly']
        items_remaining = len(visible_items)  # Items still visible
        
        # If low battery and work remaining, prioritize efficiency
        if battery < 0.3 and items_remaining > 0:
            # Fast path to nearest bin
            if items_in_hand and target_bin:
                direction_vec = np.array(target_bin['position']) - robot_pos
                direction = self._vec_to_direction(direction_vec)
                return {
                    'action_type': 'move',
                    'parameters': {'direction': direction, 'speed': 1.0}
                }
        
        # If hand is full, drop items
        if len(items_in_hand) >= 4 and target_bin:
            bin_dist = target_bin['distance']
            if bin_dist < 1.5:
                return {
                    'action_type': 'drop',
                    'parameters': {'bin_id': target_bin['id']}
                }
            else:
                direction_vec = np.array(target_bin['position']) - robot_pos
                direction = self._vec_to_direction(direction_vec)
                return {
                    'action_type': 'move',
                    'parameters': {'direction': direction, 'speed': 0.8}
                }
        
        # If visible items and space in hand, pick them
        if visible_items and len(items_in_hand) < 4:
            closest = min(visible_items, key=lambda x: np.linalg.norm(np.array(x['position']) - robot_pos))
            dist = np.linalg.norm(np.array(closest['position']) - robot_pos)
            
            if dist < 1.0:
                return {
                    'action_type': 'pick',
                    'parameters': {'item_id': closest['id']}
                }
            else:
                direction_vec = np.array(closest['position']) - robot_pos
                direction = self._vec_to_direction(direction_vec)
                return {
                    'action_type': 'move',
                    'parameters': {'direction': direction, 'speed': 0.75}
                }
        
        # Explore for items
        direction = np.random.choice(['north', 'south', 'east', 'west'])
        return {
            'action_type': 'move',
            'parameters': {'direction': direction, 'speed': 0.6}
        }
    
    @staticmethod
    def _vec_to_direction(vec: np.ndarray) -> str:
        """Convert vector to discrete direction"""
        vec = vec / (np.linalg.norm(vec) + 1e-6)
        
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
        
        angle = np.arctan2(vec[1], vec[0])
        closest_direction = min(angles.keys(), key=lambda d: abs(angles[d] - angle))
        return closest_direction


def get_baseline_agent(agent_name: str) -> Callable:
    """
    Get a baseline agent by name.
    
    Args:
        agent_name: One of 'random', 'greedy', 'hierarchical', 'smart'
    
    Returns:
        Agent callable
    """
    agents = {
        'random': RandomAgent(),
        'greedy': GreedyAgent(),
        'hierarchical': HierarchicalAgent(),
        'smart': SmartAgent(),
    }
    
    if agent_name not in agents:
        raise ValueError(f"Unknown agent: {agent_name}")
    
    return agents[agent_name]
