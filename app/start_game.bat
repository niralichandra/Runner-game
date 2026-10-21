@echo off
rem Starts a local server for Rail Rush (needed to load the 3D models) and opens the game.
cd /d "%~dp0"
start "" http://localhost:8777/app/
python serve.py 8777
