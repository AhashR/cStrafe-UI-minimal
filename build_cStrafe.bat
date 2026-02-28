@echo off
REM Create venv and install requirements
REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
	echo Python is not installed. Please install Python and try again.
	exit /b 1
)

REM Create virtual environment in .venv folder if it doesn't exist
IF NOT EXIST .venv (
	python -m venv .venv
)

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Install requirements
IF EXIST requirements.txt (
	pip install -r requirements.txt
) ELSE (
	echo requirements.txt not found!
	exit /b 1
)

REM Build the executable
if exist dist\CSstrafe.exe del /f /q dist\cStrafe.exe

.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --hidden-import=pynput --name cStrafe --icon images/app_icon.ico --add-data "images;images" main.py

echo Build complete! Check dist\cStrafe.exe
pause
