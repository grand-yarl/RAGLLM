@echo off
echo Starting RAG System GUI...
echo.

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting application...
python gui.py

pause