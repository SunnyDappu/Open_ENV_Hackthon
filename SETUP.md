# 🚀 Local Setup & Run Guide

## Quick Start (No Installation Required)

If you just want to **test the environment right now**, run this directly:

```powershell
python run_local.py
```

This gives you an interactive menu to:
- 📊 Run quick examples
- 📈 Run full benchmark
- 🌐 Start Gradio web UI (localhost:7860)
- 🧪 Run tests
- 🤖 Test single agents

---

## Option 1: Quick Run (Fastest - No Install)

### Prerequisites
- Python 3.8+ already installed

### Steps

```powershell
# Navigate to project directory
cd C:\Users\PETERSUNNY\OneDrive\Documents\GitHub\Open_ENV_Hackthon

# Run the interactive menu
python run_local.py
```

**Then select option 3 to launch the web UI!**

---

## Option 2: Proper Installation (Recommended)

### Step 1: Find Your Python Installation

On Windows, find Python by opening PowerShell and trying:

```powershell
# Check if python works
py --version

# If not, find where Python is installed
Get-ChildItem "C:\Program Files\Python*" -ErrorAction SilentlyContinue
Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\*" -ErrorAction SilentlyContinue
```

If you see something like `Python 3.10.5`, Python is installed! Otherwise:
- **Download Python:** https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### Step 2: Install Dependencies

```powershell
# Navigate to project
cd C:\Users\PETERSUNNY\OneDrive\Documents\GitHub\Open_ENV_Hackthon

# Install dependencies
pip install -r requirements.txt

# Or with verbose output if there are errors
pip install -r requirements.txt -v
```

### Step 3: Run the Application

**Run Examples:**
```powershell
python examples.py
```

**Run the Web UI:**
```powershell
python app.py
```

Then open your browser to: **http://localhost:7860**

---

## Option 3: Development Setup (With Testing)

```powershell
# Install in development mode
pip install -e .

# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest warehouse_env/tests/test_env.py -v

# Run with coverage
pytest warehouse_env/tests/test_env.py --cov=warehouse_env
```

---

## Option 4: Docker (If you have Docker installed)

```powershell
# Build the image
docker build -t warehouse-env .

# Run the container
docker run -p 7860:7860 warehouse-env

# Then open: http://localhost:7860
```

---

## Troubleshooting

### Error: "Python was not found"

**Solution 1:** Use full path to Python
```powershell
# Find where Python is installed
$pythonPath = (Get-Command python.exe).Source
echo "Python is at: $pythonPath"

# Then use the full path
& "C:\Program Files\Python310\python.exe" run_local.py
```

**Solution 2:** Install Python
- Download from https://www.python.org/downloads/
- During installation, **check "Add Python to PATH"**
- Restart your PowerShell/terminal

### Error: "ModuleNotFoundError: No module named 'warehouse_env'"

**Solution:**
```powershell
# Make sure you're in the right directory
cd C:\Users\PETERSUNNY\OneDrive\Documents\GitHub\Open_ENV_Hackthon

# Install dependencies
pip install -r requirements.txt
```

### Error: "Port 7860 already in use"

**Solution:**
```powershell
# Use a different port
# Edit app.py and change the last line to:
# demo.launch(server_name="127.0.0.1", server_port=7861, share=False)
```

Or kill the process using the port:
```powershell
# Find process using port 7860
netstat -ano | findstr :7860

# Kill process (replace PID with the number from above)
taskkill /PID <PID> /F
```

---

## What You'll See

### Option 1: Running Examples
```
================================================================================
Example 1: Single Step Execution
================================================================================
✓ Environment initialized
  Robot Position: (10.0, 10.0)
  Battery: 1.00
  Visible Items: 3

✓ Step executed - Reward: -0.0100
...
```

### Option 2: Running Tests
```
test_initialization ... ok
test_reset ... ok
test_state_returns_observation ... ok
...
Ran 25 tests in 1.234s
✓ All tests passed!
```

### Option 3: Starting Web UI
```
🌐 Starting Web UI...

GRADIO WEB INTERFACE

Starting server on http://localhost:7860
Press Ctrl+C to stop the server

Running on local URL:  http://127.0.0.1:7860
```

Then you can:
1. Open browser to **http://localhost:7860**
2. Select task (basic_picking, complex_sorting, expert_optimization)
3. Click "Initialize Environment"
4. Select agent and run steps
5. See live metrics and evaluation

---

## Web UI Features

### Tab 1: Interactive Playground
- Initialize environment
- Run steps one at a time
- Watch agent behavior
- See live observation state

### Tab 2: Full Episode Evaluation
- Run complete episodes
- Get detailed metrics:
  - Final Score (0.0-1.0)
  - Pick Accuracy
  - Sort Accuracy
  - Efficiency
  - Safety

### Tab 3: Benchmark Suite
- Run multiple episodes
- Compare agents
- Compare tasks
- View detailed results

### Tab 4: Documentation
- Full environment specs
- Task descriptions
- Baseline agent info
- Training examples

---

## Running Your Own Agent

Create a Python script:

```python
from warehouse_env import WarehouseEnv
from warehouse_env.tasks import WarehouseGrader

# Create environment
env = WarehouseEnv(task_name='basic_picking', seed=42)
obs = env.reset()

# Your agent function
def my_agent(observation):
    # Your agent logic here
    return {
        'action_type': 'move',
        'parameters': {'direction': 'north', 'speed': 0.5}
    }

# Run episode
total_reward = 0.0
trajectory = []

for step in range(500):
    action = my_agent(obs)
    obs, reward, done, info = env.step(action)
    total_reward += reward
    trajectory.append({'reward': reward})
    
    if done:
        break

# Evaluate
grade = WarehouseGrader.grade_episode(env, trajectory, 'basic_picking')
print(f"Score: {grade.final_score:.4f}")
```

---

## File Locations

After running, you'll see:

```
results/
├── benchmark_results.json    # Benchmark scores
├── logs/                     # If logging enabled
└── ...

warehouse_env/
├── env.py                    # Main environment
├── openenv.yaml              # Specification
├── baselines/                # Agents & evaluation
└── tests/                    # Unit tests
```

---

## Python Installation Check

Run this in PowerShell to verify your Python setup:

```powershell
# Check Python version
py -3 --version

# Check pip
py -3 -m pip --version

# Check installed packages
py -3 -m pip list | grep -E "numpy|gymnasium|gradio"
```

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run from project directory, install deps |
| Port 7860 in use | Use different port (7861, 8000, etc) |
| `Python not found` | Install Python + add to PATH |
| Slow performance | Normal for first run (imports take time) |
| Out of memory | Reduce num_episodes in benchmark |

---

## Next Steps

1. ✅ Run `python run_local.py` to test everything
2. ✅ Open `http://localhost:7860` in browser
3. ✅ Try different agents and tasks
4. ✅ Read README.md for full documentation
5. ✅ Modify `openenv.yaml` to create custom tasks
6. ✅ Build your own agent in Python

---

## Getting Help

- **Errors?** Check the Troubleshooting section above
- **Stuck?** Run `python run_local.py` and select option 4 (Run Tests)
- **Questions?** See README.md and docstrings in code

---

**Ready to start? Run this now:**
```powershell
python run_local.py
```
