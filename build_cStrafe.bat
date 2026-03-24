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

REM Build an ICO from app_icon.png so PNG is the source of truth for EXE icon
IF NOT EXIST build mkdir build
.venv\Scripts\python.exe -c "from PIL import Image; img=Image.open('images/app_icon.png').convert('RGBA'); img.save('build/app_icon_from_png.ico', format='ICO', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
IF %ERRORLEVEL% NEQ 0 (
	echo Failed to generate build\app_icon_from_png.ico from images\app_icon.png
	exit /b 1
)

REM Build the executable
if exist dist\CSstrafe.exe del /f /q dist\cStrafe.exe

.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --hidden-import=pynput --name cStrafe --icon build/app_icon_from_png.ico --add-data "images;images" main.py

echo Build complete! Check dist\cStrafe.exe
