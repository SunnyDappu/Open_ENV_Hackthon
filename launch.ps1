#!/usr/bin/env powershell
# Warehouse Environment - PowerShell Launcher for Windows

Write-Host ""
Write-Host ("="*80)
Write-Host "🏭 WAREHOUSE ENVIRONMENT - LOCAL LAUNCHER".PadRight(80)
Write-Host ("="*80)
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $pythonCmd = "python"
    } else {
        $pythonCmd = "py"
        $pythonVersion = py --version 2>$null
    }
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from: https://www.python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host ("="*80)
Write-Host "SELECT AN OPTION:"
Write-Host ("="*80)
Write-Host ""
Write-Host "  1) Check Setup (see what dependencies are installed)"
Write-Host "  2) Run Quick Examples (test the environment)"
Write-Host "  3) Start Web UI (open http://localhost:7860 in browser)"
Write-Host "  4) Run Full Benchmark (5-10 minutes)"
Write-Host "  5) Run Unit Tests (verify everything works)"
Write-Host "  6) Install Dependencies (pip install -r requirements.txt)"
Write-Host "  7) Interactive Menu (run_local.py)"
Write-Host ""

$choice = Read-Host "Enter your choice (1-7)"

Write-Host ""

switch ($choice) {
    "1" {
        Write-Host "Checking setup..." -ForegroundColor Cyan
        Write-Host ""
        & $pythonCmd check_setup.py
    }
    "2" {
        Write-Host "Running examples..." -ForegroundColor Cyan
        Write-Host ""
        & $pythonCmd examples.py
    }
    "3" {
        Write-Host "Starting Gradio Web UI..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🌐 Open your browser to: http://localhost:7860"
        Write-Host "   Press Ctrl+C to stop the server"
        Write-Host ""
        & $pythonCmd app.py
    }
    "4" {
        Write-Host "Running full benchmark (this may take 5-10 minutes)..." -ForegroundColor Cyan
        Write-Host ""
        & $pythonCmd -c "
from warehouse_env.baselines import evaluate_all_agents, print_results_summary
results = evaluate_all_agents(
    tasks=['basic_picking', 'complex_sorting', 'expert_optimization'],
    agents=['random', 'greedy', 'hierarchical', 'smart'],
    num_episodes=3,
    seed=42,
    output_file='results/benchmark.json',
    verbose=True
)
print_results_summary(results)
"
    }
    "5" {
        Write-Host "Running unit tests..." -ForegroundColor Cyan
        Write-Host ""
        & $pythonCmd -m pytest warehouse_env/tests/test_env.py -v
    }
    "6" {
        Write-Host "Installing dependencies..." -ForegroundColor Cyan
        Write-Host ""
        & $pythonCmd -m pip install -r requirements.txt
        Write-Host ""
        Write-Host "✓ Installation complete!" -ForegroundColor Green
    }
    "7" {
        Write-Host "Starting interactive menu..." -ForegroundColor Cyan
        Write-Host ""
        & $pythonCmd run_local.py
    }
    default {
        Write-Host "✗ Invalid choice!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
