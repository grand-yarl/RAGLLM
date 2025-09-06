@echo off
echo Setting up RAG System for Windows...
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed.
    echo Please install Docker Desktop from https://docker.com
    pause
    exit /b 1
)

echo Checking Ollama installation...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo Ollama is not installed.
    echo Please install Ollama from https://ollama.ai/download
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv .venv

echo Activating environment...
call .venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

echo Downloading DeepSeek model...
ollama pull deepseek-coder

echo Creating folders...
if not exist "data\documents" mkdir data\documents

echo Setup completed!
echo.
echo To start the application, run:
echo   run_gui.bat
echo or
echo   .venv\Scripts\activate.bat
echo   python gui.py
pause