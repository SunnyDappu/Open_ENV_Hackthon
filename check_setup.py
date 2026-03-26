#!/usr/bin/env python
"""
Dependency Checker - See what's installed and what's missing
Run this: python check_setup.py
"""

import sys
import os

print("\n" + "="*70)
print("DEPENDENCY CHECK".center(70))
print("="*70 + "\n")

# Check Python version
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}\n")

# Check required dependencies
dependencies = {
    'core': [
        ('numpy', 'Scientific computing'),
        ('gymnasium', 'RL environment API'),
        ('pydantic', 'Data validation'),
    ],
    'optional': [
        ('gradio', 'Web interface (optional)'),
        ('matplotlib', 'Visualization (optional)'),
        ('torch', 'PyTorch (optional, for RL)'),
        ('pytest', 'Testing (optional)'),
    ]
}

print("Core Dependencies (Required):")
print("-" * 70)
missing_core = []
for package, description in dependencies['core']:
    try:
        module = __import__(package)
        version = getattr(module, '__version__', 'unknown')
        print(f"  ✓ {package:<20} {version:<15} {description}")
    except ImportError:
        print(f"  ✗ {package:<20} {'NOT INSTALLED':<15} {description}")
        missing_core.append(package)

print("\nOptional Dependencies:")
print("-" * 70)
for package, description in dependencies['optional']:
    try:
        module = __import__(package)
        version = getattr(module, '__version__', 'unknown')
        print(f"  ✓ {package:<20} {version:<15} {description}")
    except ImportError:
        print(f"  ✗ {package:<20} {'NOT INSTALLED':<15} {description}")

print("\n" + "="*70)

# Test environment
print("Testing Core Environment...")
print("-" * 70)

try:
    from warehouse_env import WarehouseEnv
    print("  ✓ warehouse_env imports successfully")
    
    env = WarehouseEnv(task_name='basic_picking', seed=42)
    print("  ✓ Environment initializes")
    
    obs = env.reset()
    print("  ✓ Reset works")
    
    action = {'action_type': 'move', 'parameters': {'direction': 'north', 'speed': 0.5}}
    obs, reward, done, info = env.step(action)
    print("  ✓ Step works")
    
    print("\n✓ Core environment is working!\n")
    
except Exception as e:
    print(f"  ✗ Error: {e}\n")
    import traceback
    traceback.print_exc()

# Summary
print("="*70)
print("SUMMARY".center(70))
print("="*70)

if not missing_core:
    print("\n✓ All required dependencies are installed!")
    print("  You can now run:")
    print("    - python run_local.py (interactive menu)")
    print("    - python examples.py (quick examples)")
    print("    - python app.py (web UI - requires gradio)")
else:
    print(f"\n✗ Missing {len(missing_core)} core dependencies:")
    for pkg in missing_core:
        print(f"    - {pkg}")
    
    print("\n  Install with:")
    print("    pip install -r requirements.txt")
    print("\n  Or individually:")
    for pkg in missing_core:
        print(f"    pip install {pkg}")

print("\n" + "="*70 + "\n")
