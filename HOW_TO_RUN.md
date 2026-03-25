# 🚀 How To Run Warehouse Environment Locally

This guide shows you all the ways to run the environment on your machine.

---

## ⚡ Quickest Way (Right Now!)

### Using Windows Launcher (Easiest)

**Double-click:**
```
launch.bat
```

This opens a menu where you can:
- Check setup
- Run examples  
- Start web UI
- Run benchmark
- Run tests
- Install dependencies

---

## 📋 Alternative Ways to Run

### Method 1: PowerShell Launcher

Open PowerShell in the project directory and run:

```powershell
# Option A: Using batch file
.\launch.bat

# Option B: Using PowerShell script
powershell -ExecutionPolicy Bypass -File .\launch.ps1

# This opens an interactive menu with the same options as above
```

### Method 2: Direct Python Command

```powershell
# Interactive menu with all options
python run_local.py

# Then select from the menu:
# 1) Examples
# 2) Full Benchmark
# 3) Web UI
# 4) Tests
# 5) Single Agent Test
```

### Method 3: Run Specific Scripts

```powershell
# Check what dependencies are installed
python check_setup.py

# Run quick examples (5-10 seconds)
python examples.py

# Start the web UI (localhost:7860)
python app.py

# Run unit tests
python -m pytest warehouse_env/tests/test_env.py -v

# Run full benchmark (5-10 minutes)
python -m warehouse_env.baselines.inference --episodes 5
```

### Method 4: Python API (For Developers)

```python
from warehouse_env import WarehouseEnv
from warehouse_env.baselines import get_baseline_agent

# Create environment
env = WarehouseEnv(task_name='basic_picking', seed=42)
obs = env.reset()

# Create agent
agent = get_baseline_agent('smart')

# Run episode
total_reward = 0.0
for step in range(100):
    action = agent(obs)
    obs, reward, done, info = env.step(action)
    total_reward += reward
    if done:
        break

print(f"Score: {total_reward:.2f}")
```

---

## 🌐 Web UI Setup

### Option 1: Using Launcher

1. **Run:** `launch.bat` (Windows) or `python run_local.py` (any OS)
2. **Select:** Option 3 (Start Web UI)
3. **Open Browser:** `http://localhost:7860`

### Option 2: Direct

```powershell
python app.py
```

Then open: **http://localhost:7860**

### What You'll See

The Gradio web interface has these tabs:

#### 📊 Interactive Playground
- Initialize different tasks
- Select agents
- Run steps manually
- Watch the agent's behavior in real-time
- See live observation state and metrics

#### ▶️ Full Episode Evaluation  
- Run complete episodes
- See final scores (0.0 - 1.0)
- View metrics:
  - Pick Accuracy
  - Sort Accuracy
  - Efficiency
  - Safety
- Compare agent performance

#### 📈 Benchmark Suite
- Test multiple agents at once
- Test multiple tasks
- Get detailed results table
- Export results

#### 📖 Documentation
- Full environment spec
- Task descriptions
- Agent information
- Training examples

---

## 🎯 What Each Option Does

### 1️⃣ Check Setup (`check_setup.py`)
**Time:** 2 seconds
**What:** Verifies all dependencies are installed correctly

**Output:**
```
✓ numpy 1.21.0
✓ gymnasium 0.27.0  
✓ pydantic 1.10.0
✓ warehouse_env imports successfully
✓ Core environment is working!
```

### 2️⃣ Run Examples (`examples.py` or Menu Option 1)
**Time:** 10-20 seconds
**What:** Runs 6 different example scenarios

**Tests:**
- Single step execution
- Full episode with agent
- Task comparison
- Agent benchmarking
- All baseline agents
- Custom agent creation

### 3️⃣ Start Web UI (`app.py` or Menu Option 3)
**Time:** 10 seconds startup + interactive
**What:** Launch interactive Gradio interface

**Access:** http://localhost:7860

**Features:**
- Interactive agent control
- Real-time metrics
- Benchmark runner
- Built-in docs

### 4️⃣ Run Full Benchmark (Menu Option 2)
**Time:** 5-10 minutes
**What:** Evaluate all agents on all tasks

**Setup:**
- 3 tasks (easy, medium, hard)
- 4 agents (random, greedy, hierarchical, smart)
- 3-5 episodes each
- Saves results to JSON

**Output:**
```
BASIC_PICKING
Agent         | Score  | Pick Acc | Sort Acc | Efficiency
Greedy        | 0.5432 | 0.8000   | 0.7000   | 0.6500
Smart         | 0.6821 | 0.9000   | 0.8500   | 0.7200
```

### 5️⃣ Run Tests (Menu Option 4)
**Time:** 30 seconds
**What:** Verify all functionality works

**Coverage:**
- 25+ unit tests
- Environment core
- All task types
- All agents
- Grading system

**Sample Output:**
```
test_initialization ... ok
test_reset ... ok
test_state_returns_observation ... ok
test_move_action ... ok
test_pick_action ... ok
...
Ran 25 tests in 0.834s ✓
```

---

## 🔧 Troubleshooting

### Problem: "Python not found"

**Solution:**
1. Open PowerShell
2. Try: `py --version`
3. If that works, use `py` instead of `python`
4. If that fails, install from: https://www.python.org/downloads/

### Problem: "ModuleNotFoundError"

**Solution:**
```powershell
# Install all dependencies
pip install -r requirements.txt

# Or install specific package:
pip install gradio numpy gymnasium
```

### Problem: Port 7860 already in use

**Solution:**
```powershell
# Find the process
netstat -ano | findstr :7860

# Kill it (replace NNNN with the PID)
taskkill /PID NNNN /F

# Or use a different port - edit app.py line:
# demo.launch(server_name="127.0.0.1", server_port=7861, share=False)
```

### Problem: "Permission Denied" on launch.ps1

**Solution:**
```powershell
# Allow PowerShell scripts to run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use this one-liner:
powershell -ExecutionPolicy Bypass -File .\launch.ps1
```

---

## 📊 Expected Output Examples

### From Examples (`python examples.py`)

```
Example 1: Single Step Execution
==========================================
✓ Environment initialized
  Robot Position: (10.0, 10.0)
  Battery: 1.00
  Visible Items: 3

✓ Step executed - Reward: -0.0100

Example 2: Full Episode with Smart Agent  
==========================================
✓ Episode completed in 87 steps
  Total Reward: 12.45
  Final Score: 0.6821
  Pick Accuracy: 0.9000
  Sort Accuracy: 0.8500
  Items Sorted: 9/10
```

### From Web UI (`python app.py`)

```
Starting server on http://localhost:7860

Running on local URL:  http://127.0.0.1:7860

To create a public link, set share=True in launch().
```

Then browser shows:
- Interactive controls
- Real-time metrics
- Formatted results

---

## 📁 Your First Steps

1. **Check Everything Works:**
   ```powershell
   python check_setup.py
   ```

2. **Run Quick Test:**
   ```powershell
   python examples.py
   ```
   This takes ~10 seconds and shows you the environment works

3. **Try the Web UI:**
   ```powershell
   python app.py
   ```
   Then open http://localhost:7860 in your browser

4. **Run Full Benchmark:**
   ```powershell
   python run_local.py
   # Select option 2
   ```
   This takes 5-10 minutes and tests all agents

5. **Explore the Code:**
   - `warehouse_env/env.py` - Core environment
   - `warehouse_env/baselines/agents.py` - Agent implementations
   - `warehouse_env/tasks/__init__.py` - Task definitions
   - `app.py` - Web interface

---

## 💡 Tips & Tricks

### Run Without Installation
No need to install with `pip install -e` - just run scripts directly!

### Faster Testing
Set fewer episodes in benchmark:
```powershell
python -m warehouse_env.baselines.inference --episodes 1
```

### Custom Task
Edit `warehouse_env/openenv.yaml` and create custom task config

### Export Results
Results automatically saved to `results/benchmark_results.json`

### Use Different Port for Web UI
```powershell
# Edit the bottom of app.py:
# demo.launch(server_name="127.0.0.1", server_port=8080, share=False)
python app.py
# Then open http://localhost:8080
```

---

## 📱 Full Command Reference

| Command | Time | Purpose |
|---------|------|---------|
| `python check_setup.py` | 2s | Verify setup |
| `python examples.py` | 15s | Quick tests |
| `python app.py` | 5s | Web UI |
| `python run_local.py` | varies | Interactive menu |
| `python -m pytest warehouse_env/tests/test_env.py -v` | 30s | Unit tests |
| `python -m warehouse_env.baselines.inference --episodes 3` | 3-5m | Full benchmark |

---

## 🎮 Your First Steps with Web UI

1. Open http://localhost:7860
2. Go to "Interactive Playground"
3. Select task: "basic_picking"
4. Click "Initialize Environment"
5. Select agent: "smart"
6. Click "Run Step" to execute one action
7. Watch the observation and metrics update
8. Go to "Full Episode" and click "Run Episode" to see a complete run

---

## ✅ Verification Checklist

After running, you should see:

- [x] Environment initializes correctly
- [x] Steps execute and return rewards
- [x] Observations have proper structure
- [x] Battery decreases with movement
- [x] Items can be picked and dropped
- [x] Episodes terminate properly
- [x] Grading scores are 0.0-1.0
- [x] Web UI loads on localhost:7860
- [x] All 4 agents work
- [x] All 3 tasks load

If any of these fail, check the Troubleshooting section.

---

## 🎓 Learning Path

1. **Run Examples** → Understand the API
2. **Test Interactive Playground** → See agent behavior
3. **Run One Full Episode** → Learn metrics
4. **Run Benchmark** → Compare agents
5. **Read Code** → Understand internals
6. **Create Custom Agent** → Implement your own

---

## 🚀 You're All Set!

Pick any method above and get started:

**Fastest Way:**
```powershell
launch.bat
# Select 3 (Web UI)
```

**Manual Way:**
```powershell
python app.py
```

**Learning Path:**
```powershell
python examples.py
python app.py
python -m warehouse_env.baselines.inference
```

---

**Happy Learning! 🚀**

For detailed API docs, see: [README.md](README.md)
For implementation details, see: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
