"""
Gradio Web Interface for Warehouse Environment
Deploy to HuggingFace Spaces for interactive evaluation
"""

import gradio as gr
import json
import numpy as np
from warehouse_env.env import WarehouseEnv
from warehouse_env.tasks import WarehouseGrader, BenchmarkTasks
from warehouse_env.baselines import evaluate_all_agents, get_baseline_agent
import matplotlib.pyplot as plt
import io
from PIL import Image


class WarehouseEnvUI:
    """Interactive UI for Warehouse Environment"""
    
    def __init__(self):
        self.env = None
        self.current_obs = None
        self.agent = None
        self.episode_data = []
    
    def initialize_env(self, task_name: str) -> str:
        """Initialize environment for a task"""
        try:
            self.env = WarehouseEnv(task_name=task_name, seed=42)
            self.current_obs = self.env.reset()
            self.episode_data = []
            return f"✓ Initialized {task_name} successfully"
        except Exception as e:
            return f"✗ Error: {str(e)}"
    
    def run_agent_step(self, agent_name: str) -> tuple:
        """Run one step of agent"""
        if self.env is None:
            return "Initialize environment first", "{}", json.dumps({})
        
        try:
            if self.agent is None or self.agent.__class__.__name__.replace('Agent', '').lower() != agent_name:
                self.agent = get_baseline_agent(agent_name)
            
            action = self.agent(self.current_obs)
            self.current_obs, reward, done, info = self.env.step(action)
            
            self.episode_data.append({
                'action': action,
                'reward': reward,
                'observation': self.current_obs
            })
            
            status = f"Step {self.env.current_step}/{self.env.max_steps} | " \
                    f"Reward: {reward:.3f} | Battery: {self.current_obs['robot_battery']:.2f} | " \
                    f"Items Sorted: {self.current_obs['episode_info']['total_items_sorted_correctly']}"
            
            if done:
                status += " [EPISODE DONE]"
            
            obs_json = json.dumps({
                'robot_position': self.current_obs['robot_position'],
                'robot_battery': float(self.current_obs['robot_battery']),
                'items_in_hand': len(self.current_obs['items_in_hand']),
                'visible_items': len(self.current_obs['visible_items']),
                'items_sorted': self.current_obs['episode_info']['total_items_sorted_correctly'],
            }, indent=2)
            
            return status, obs_json, json.dumps(action, indent=2)
        
        except Exception as e:
            return f"Error: {str(e)}", "{}", "{}"
    
    def reset_episode(self) -> str:
        """Reset current episode"""
        if self.env is None:
            return "Initialize environment first"
        
        self.current_obs = self.env.reset()
        self.episode_data = []
        self.agent = None
        return "Episode reset successfully"
    
    def run_full_episode(self, task_name: str, agent_name: str, max_steps: int = None) -> tuple:
        """Run a full episode"""
        try:
            env = WarehouseEnv(task_name=task_name, seed=42)
            obs = env.reset()
            agent = get_baseline_agent(agent_name)
            
            total_reward = 0.0
            steps = 0
            trajectory = []
            
            max_steps = max_steps or env.max_steps
            
            while steps < max_steps and not False:
                action = agent(obs)
                obs, reward, done, info = env.step(action)
                total_reward += reward
                trajectory.append({'obs': obs, 'reward': reward})
                steps += 1
                
                if done:
                    break
            
            # Grade the episode
            grade = WarehouseGrader.grade_episode(env, trajectory, task_name)
            
            result_text = f"""
### Episode Results

**Task:** {task_name}
**Agent:** {agent_name}
**Steps:** {steps}/{env.max_steps}
**Total Reward:** {total_reward:.2f}

#### Metrics
- **Final Score:** {grade.final_score:.4f} / 1.0
- **Pick Accuracy:** {grade.pick_accuracy:.4f}
- **Sort Accuracy:** {grade.sort_accuracy:.4f}
- **Efficiency:** {grade.efficiency_score:.4f}
- **Safety:** {grade.safety_score:.4f}

#### Detailed Metrics
- Items Picked: {grade.metrics['items_picked']}/{grade.metrics['total_items']}
- Items Sorted: {grade.metrics['items_sorted']}/{grade.metrics['total_items']}
- Total Distance: {grade.metrics['total_distance']:.2f}
- Collisions: {grade.metrics['collisions']}
- Battery Used: {grade.metrics['battery_used']:.3f}
- Time Used: {grade.metrics['time_used']} steps
"""
            
            return result_text
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run_benchmark(self, selected_agents: list, selected_tasks: list, episodes: int = 3) -> str:
        """Run full benchmark suite"""
        try:
            results = evaluate_all_agents(
                tasks=selected_tasks,
                agents=selected_agents,
                num_episodes=episodes,
                seed=42,
                output_file=None,
                verbose=False
            )
            
            # Format results nicely
            output = "# Benchmark Results\n\n"
            
            for task_result in results['results']:
                output += f"## {task_result['task_name'].upper()}\n\n"
                output += "| Agent | Score | Pick Acc | Sort Acc | Efficiency |\n"
                output += "|-------|-------|----------|----------|------------|\n"
                
                for agent_result in task_result['agent_results']:
                    agent = agent_result['agent_name']
                    score = agent_result['final_score_mean']
                    pick = agent_result['pick_accuracy_mean']
                    sort = agent_result['sort_accuracy_mean']
                    eff = agent_result['efficiency_score_mean']
                    
                    output += f"| {agent} | {score:.4f} | {pick:.4f} | {sort:.4f} | {eff:.4f} |\n"
                
                output += "\n"
            
            return output
        
        except Exception as e:
            return f"Error running benchmark: {str(e)}"


def create_gradio_interface():
    """Create Gradio interface for the environment"""
    
    ui = WarehouseEnvUI()
    
    with gr.Blocks(title="Warehouse Robot Environment - OpenEnv Hackathon") as demo:
        gr.Markdown("""
# 🏭 Warehouse Robot Picking & Sorting Environment
## OpenEnv Hackathon - Real-world Robotics Simulation

A production-ready simulation environment where AI agents learn to efficiently pick items from warehouse shelves and sort them into bins under energy and time constraints.

**Environment Type:** Real-world warehouse automation | **Difficulty:** Easy → Hard |  **Metrics:** 0.0 - 1.0
        """)
        
        # Tab 1: Interactive Playground
        with gr.Tab("📊 Interactive Playground"):
            with gr.Row():
                with gr.Column():
                    task_select = gr.Dropdown(
                        choices=BenchmarkTasks.list_tasks(),
                        value='basic_picking',
                        label="Select Task"
                    )
                    init_btn = gr.Button("Initialize Environment", size="lg")
                    init_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Column():
                    agent_select = gr.Dropdown(
                        choices=['random', 'greedy', 'hierarchical', 'smart'],
                        value='greedy',
                        label="Select Agent"
                    )
                    step_count = gr.Slider(1, 100, value=10, label="Steps to Run")
                    step_btn = gr.Button("Run Step", size="lg")
            
            with gr.Row():
                with gr.Column():
                    obs_display = gr.Textbox(label="Observation State", lines=8, interactive=False)
                    reset_btn = gr.Button("Reset Episode")
                
                with gr.Column():
                    action_display = gr.Textbox(label="Action Executed", lines=8, interactive=False)
                    step_info = gr.Textbox(label="Step Info", interactive=False)
        
        # Tab 2: Full Episode Evaluation
        with gr.Tab("▶️ Full Episode Evaluation"):
            with gr.Row():
                with gr.Column():
                    eval_task = gr.Dropdown(
                        choices=BenchmarkTasks.list_tasks(),
                        value='basic_picking',
                        label="Task"
                    )
                    eval_agent = gr.Dropdown(
                        choices=['random', 'greedy', 'hierarchical', 'smart'],
                        value='smart',
                        label="Agent"
                    )
                    eval_btn = gr.Button("Run Episode", size="lg")
                
                with gr.Column():
                    eval_results = gr.Markdown(label="Results")
        
        # Tab 3: Benchmark Suite
        with gr.Tab("📈 Benchmark Suite"):
            with gr.Row():
                with gr.Column():
                    benchmark_agents = gr.CheckboxGroup(
                        choices=['random', 'greedy', 'hierarchical', 'smart'],
                        value=['greedy', 'smart'],
                        label="Agents to Benchmark"
                    )
                    benchmark_tasks = gr.CheckboxGroup(
                        choices=BenchmarkTasks.list_tasks(),
                        value=BenchmarkTasks.list_tasks(),
                        label="Tasks to Benchmark"
                    )
                    bench_episodes = gr.Slider(1, 10, value=3, label="Episodes per Task")
                    bench_btn = gr.Button("Run Benchmark", size="lg")
                
                with gr.Column():
                    bench_results = gr.Markdown(label="Benchmark Results")
        
        # Tab 4: Documentation
        with gr.Tab("📖 Documentation"):
            gr.Markdown("""
## Environment Specification

### Overview
The Warehouse Robot Picking & Sorting Environment is a realistic simulation where agents learn to:
- Navigate a warehouse grid
- Pick items from shelves
- Sort items into categorized bins
- Optimize for energy efficiency and time

### Action Space
- **move:** Navigate in 8 directions with configurable speed (0.0-1.0)
- **pick:** Pick item by ID (with proximity requirement)
- **drop:** Place item in bin by ID (with proximity requirement)
- **rotate:** Rotate robot orientation

### Observation Space
- Robot position (x, y)
- Robot battery level (0.0-1.0)
- Items in hand (list with properties)
- Visible items (FOV=10 units)
- Target bin (closest empty bin)
- Time remaining
- Bin state (fill percentage)

### Reward Function
- Pick item: +0.1
- Correct sort: +0.3
- Energy bonus: 0.6 × remaining battery
- Time bonus: 0.4 × remaining time
- Path efficiency bonus: 1.0 / (1.0 + distance/grid_size)
- Penalties: collision, invalid action, low battery

### Task Difficulty Levels

#### 🟢 Easy: Basic Picking (10 items, 2 bins)
- 20×20 warehouse
- Simple item types (no requirements)
- 500 max steps
- Full battery (1.0)
- No obstacles

#### 🟡 Medium: Complex Sorting (25 items, 5 bins)
- 30×30 warehouse
- Multiple item types with bin requirements
- 1000 max steps
- Full battery
- 8 obstacles

#### 🔴 Hard: Expert Optimization (50 items, 8 bins)
- 40×40 warehouse
- Complex item-bin matching
- 1500 max steps
- Limited battery (0.8)
- 12 dynamic obstacles

### Evaluation Metrics
Final Score = 0.3 × pick_accuracy + 0.3 × sort_accuracy + 0.2 × efficiency + 0.2 × safety
- **Pick Accuracy:** % of items correctly picked
- **Sort Accuracy:** % of items sorted to correct bins
- **Efficiency:** Energy + time optimization
- **Safety:** Collision avoidance

## Baseline Agents

### Random Agent
Pure random action selection. Baseline for comparison.
- **Expected Score:** 0.2-0.4

### Greedy Agent
Picks nearest items, drops at nearest bin.
- **Expected Score:** 0.4-0.6

### Hierarchical Agent
State machine with sub-goals (explore → pick → drop).
- **Expected Score:** 0.5-0.7

### Smart Agent
Task-aware planning with energy management.
- **Expected Score:** 0.6-0.8

## Getting Started

### Installation
```bash
pip install -r requirements.txt
```

### Running Locally
```bash
python -c "from warehouse_env import WarehouseEnv; env = WarehouseEnv('basic_picking'); obs = env.reset()"
```

### Training Your Agent
```python
from warehouse_env import WarehouseEnv

env = WarehouseEnv(task_name='basic_picking')
obs = env.reset()

for step in range(100):
    action = your_agent_function(obs)
    obs, reward, done, info = env.step(action)
    if done:
        break
```
            """)
        
        # Set up callbacks
        init_btn.click(
            fn=ui.initialize_env,
            inputs=[task_select],
            outputs=[init_status]
        )
        
        step_btn.click(
            fn=lambda agent: ui.run_agent_step(agent),
            inputs=[agent_select],
            outputs=[step_info, obs_display, action_display]
        )
        
        reset_btn.click(
            fn=ui.reset_episode,
            outputs=[init_status]
        )
        
        eval_btn.click(
            fn=ui.run_full_episode,
            inputs=[eval_task, eval_agent, step_count],
            outputs=[eval_results]
        )
        
        bench_btn.click(
            fn=ui.run_benchmark,
            inputs=[benchmark_agents, benchmark_tasks, bench_episodes],
            outputs=[bench_results]
        )
    
    return demo


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 7860))
    # Use 0.0.0.0 for Railway deployment, 127.0.0.1 for local
    server_name = "0.0.0.0" if os.getenv("RAILWAY_ENVIRONMENT_NAME") else "127.0.0.1"
    demo = create_gradio_interface()
    demo.launch(server_name=server_name, server_port=port, share=False)
