@echo off
REM Build standalone executable using PyInstaller
python -m pip install --user pyinstaller
python -m PyInstaller --onefile russian_roulette.py
