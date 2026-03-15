@echo off
title VEDA CORE - Tactical Repair Tool
echo --------------------------------------------------
echo VEDA CORE | REPAIR PROTOCOL INITIATED
echo --------------------------------------------------
echo.

echo [1/3] VERIFYING PYTHON LINK...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in system path.
    pause
    exit /b
)

echo [2/3] ESTABLISHING TACTICAL MODULES...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [3/3] CLEARING CACHE...
del /s /q *.pyc >nul 2>&1
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo.
echo --------------------------------------------------
echo REPAIR COMPLETE. ALL SYSTEMS NOMINAL.
echo YOU MAY NOW RUN 'python main.py'
echo --------------------------------------------------
pause
