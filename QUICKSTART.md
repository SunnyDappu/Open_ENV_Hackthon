# 🏭 WAREHOUSE ENVIRONMENT - QUICK REFERENCE

## ⚡ Start Here (Pick One)

### 🖱️ Easiest (Windows)
```powershell
double-click launch.bat
# Select option 3 for Web UI
```

### 🎯 Direct Web UI
```powershell
python app.py
# Open: http://localhost:7860
```

### 📋 Interactive Menu
```powershell
python run_local.py
# Select whatever you want to do
```

### 🧪 Quick Test (20 seconds)
```powershell
python check_setup.py
```

### 📚 Examples
```powershell
python examples.py
```

---

## 🌐 Web UI Access

Once running, open your browser:
```
http://localhost:7860
```

### What You Get:
- 📊 Interactive playground (control agent manually)
- ▶️ Full episode evaluation (test agents)
- 📈 Benchmark suite (compare all agents)
- 📖 Built-in documentation

---

## 📁 All Available Scripts

| Script | Run With | Time | Purpose |
|--------|----------|------|---------|
| **launch.bat** | Double-click | varies | Interactive menu (Windows) |
| **launch.ps1** | `powershell -File launch.ps1` | varies | Interactive menu (PowerShell) |
| **run_local.py** | `python run_local.py` | varies | Interactive menu (any OS) |
| **check_setup.py** | `python check_setup.py` | 2s | Check if dependencies work |
| **examples.py** | `python examples.py` | 15s | Quick example tests |
| **app.py** | `python app.py` | 10s | Launch Gradio web UI |
| **tests** | `python -m pytest warehouse_env/tests/test_env.py` | 30s | Run unit tests |

---

## 🎮 Web UI Tabs

### Tab 1: Interactive Playground
- Select task
- Select agent
- Run one step at a time
- Watch behavior live

### Tab 2: Full Episode
- Select task
- Select agent
- Run complete episode
- Get detailed metrics

### Tab 3: Benchmark Suite
- Select multiple agents
- Select multiple tasks
- Get results table
- Export to JSON

### Tab 4: Documentation
- Full API docs
- Task specs
- Agent descriptions
- Training examples

---

## 📊 Environment at a Glance

```
Task              | Difficulty | Grid  | Items | Bins | Steps | Score
basic_picking     | Easy       | 20×20 | 10    | 2    | 500   | 0.0-1.0
complex_sorting   | Medium     | 30×30 | 25    | 5    | 1000  | 0.0-1.0
expert_optim.     | Hard       | 40×40 | 50    | 8    | 1500  | 0.0-1.0
```

---

## 🤖 Baseline Agents

| Agent | Basic | Medium | Hard |
|-------|:-----:|:------:|:----:|
| Random | 0.32 | 0.18 | 0.12 |
| Greedy | 0.52 | 0.38 | 0.28 |
| Hierarchical | 0.58 | 0.46 | 0.35 |
| Smart | 0.68 | 0.54 | 0.42 |

---

## 🛠️ Installation (If Needed)

```powershell
pip install -r requirements.txt
```

or use launcher:
```powershell
launch.bat
# Select option 6 (Install Dependencies)
```

---

## 🔧 Troubleshooting Quick Fixes

| Problem | Fix |
|---------|-----|
| Python not found | Install from python.org |
| Module not found | `pip install -r requirements.txt` |
| Port 7860 in use | Use different port (8000, 7861, etc) |
| ImportError | Try: `python check_setup.py` |

---

## 📱 Action Space

```python
# Move
{
    'action_type': 'move',
    'parameters': {
        'direction': 'north|south|east|west|...',
        'speed': 0.0-1.0
    }
}

# Pick
{
    'action_type': 'pick',
    'parameters': {'item_id': int}
}

# Drop
{
    'action_type': 'drop',
    'parameters': {'bin_id': int}
}

# Rotate
{
    'action_type': 'rotate',
    'parameters': {'angle': float}
}
```

---

## 📊 Observation Space

```python
{
    'robot_position': (x, y),
    'robot_battery': 0.0-1.0,
    'items_in_hand': [...],
    'visible_items': [...],
    'target_bin': {...},
    'time_remaining': steps,
    'bins_state': {...},
    'episode_info': {...}
}
```

---

## 🎯 Quick Tasks

### Run Everything (First Time)
```powershell
python check_setup.py      # 2 seconds
python examples.py         # 15 seconds
python app.py              # Open browser to localhost:7860
```

### Full Benchmark
```powershell
python run_local.py        # Select option 2
# or
python -m warehouse_env.baselines.inference --episodes 5
```

### Just Web UI
```powershell
python app.py
# Open: http://localhost:7860
```

### Just Test Environment
```powershell
python examples.py
```

---

## 💾 Results Output

After running benchmark, find results here:
```
results/benchmark_results.json
```

Contains:
- All agent scores
- Per-episode breakdown
- Detailed metrics
- Episode results

---

## 🚀 Next Steps

1. ✅ Run a launcher script
2. ✅ Open web UI (localhost:7860)
3. ✅ Try different agents and tasks
4. ✅ Read HOW_TO_RUN.md for detail
5. ✅ Read README.md for full docs
6. ✅ Create your own agent!

---

## 📚 Documentation Files

| File | Contains |
|------|----------|
| **README.md** | Full detailed documentation |
| **HOW_TO_RUN.md** | Complete run guide |
| **SETUP.md** | Installation & troubleshooting |
| **PROJECT_SUMMARY.md** | Project overview |
| **openenv.yaml** | Environment specification |

---

## 🎓 Example Code

```python
from warehouse_env import WarehouseEnv
from warehouse_env.baselines import get_baseline_agent

# Setup
env = WarehouseEnv(task_name='basic_picking', seed=42)
obs = env.reset()
agent = get_baseline_agent('greedy')

# Run
for step in range(100):
    action = agent(obs)
    obs, reward, done, info = env.step(action)
    if done:
        break

# Done!
print(f"Episode finished in {step} steps")
```

---

## 🎯 Common Commands

```powershell
# Check Python
python --version

# Check setup
python check_setup.py

# Run examples
python examples.py

# Start web UI
python app.py

# Run tests
python -m pytest warehouse_env/tests/ -v

# Run full benchmark
python -m warehouse_env.baselines.inference --episodes 5

# Install dependencies
pip install -r requirements.txt
```

---

## 📍 File Locations

```
c:\Users\PETERSUNNY\OneDrive\Documents\GitHub\Open_ENV_Hackthon\

├── launch.bat                 ← Run this (Windows)
├── run_local.py              ← Run this (any OS)  
├── app.py                    ← Web UI
├── examples.py               ← Quick tests
├── check_setup.py            ← Verify installation
├── README.md                 ← Full documentation
├── HOW_TO_RUN.md            ← How to run guide
├── warehouse_env/            ← Main package
│   ├── env.py               ← Core environment
│   ├── openenv.yaml         ← Specification
│   ├── baselines/           ← Agents
│   └── tasks/               ← Task definitions
└── results/                 ← Output folder
```

---

**Ready? Pick one command above and go! 🚀**

---

**Quick Start Commands (Copy-Paste Ready):**

```powershell
# Windows - Easiest
launch.bat

# Any OS - Web UI
python app.py

# Any OS - Interactive Menu
python run_local.py

# Any OS - Quick Test
python check_setup.py

# Any OS - Examples
python examples.py
```

Then open: **http://localhost:7860**
