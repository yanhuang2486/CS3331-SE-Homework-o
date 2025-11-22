@echo off
REM Batch script to install pyinstaller and build the exe (Windows cmd)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pyinstaller --onefile --noconsole --add-data "data;data" --name ResurrectionApp main.py
if %ERRORLEVEL% EQU 0 (
    echo Build finished. Executable is in the 'dist' folder: dist\ResurrectionApp.exe
) else (
    echo Build failed. See PyInstaller output above.
)
