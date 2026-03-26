@echo off
REM Warehouse Environment - Windows Quick Launcher

cls
echo.
echo ================================================================================
echo   WAREHOUSE ENVIRONMENT - LOCAL LAUNCHER
echo ================================================================================
echo.

setlocal enabledelayedexpansion

REM Try to find Python
for /f "delims=" %%i in ('where py 2^>nul') do set "PYTHON_EXE=%%i"

if not defined PYTHON_EXE (
    echo ERROR: Python not found!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

%PYTHON_EXE% --version
echo.
echo Found Python at: %PYTHON_EXE%
echo.

echo ================================================================================
echo SELECT AN OPTION:
echo ================================================================================
echo.
echo   1) Check Setup (see what's installed)
echo   2) Run Quick Examples (test environment)
echo   3) Start Web UI (localhost:7860)
echo   4) Run Full Benchmark (3-5 minutes)
echo   5) Run Tests
echo   6) Install Dependencies (pip install)
echo.

set /p CHOICE="Enter your choice (1-6): "

if "%CHOICE%"=="1" (
    echo.
    %PYTHON_EXE% check_setup.py
) else if "%CHOICE%"=="2" (
    echo.
    %PYTHON_EXE% examples.py
) else if "%CHOICE%"=="3" (
    echo.
    echo Starting Gradio Web UI on http://localhost:7860
    echo Press Ctrl+C to stop
    echo.
    %PYTHON_EXE% app.py
) else if "%CHOICE%"=="4" (
    echo.
    %PYTHON_EXE% -c "from warehouse_env.baselines import evaluate_all_agents, print_results_summary; results = evaluate_all_agents(num_episodes=3); print_results_summary(results)"
) else if "%CHOICE%"=="5" (
    echo.
    %PYTHON_EXE% -m pytest warehouse_env/tests/test_env.py -v
) else if "%CHOICE%"=="6" (
    echo.
    echo Installing dependencies from requirements.txt
    echo.
    %PYTHON_EXE% -m pip install -r requirements.txt
    echo.
    echo Installation complete!
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

pause
