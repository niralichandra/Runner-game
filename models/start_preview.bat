@echo off
rem Serves the romantic maps (no browser caching) and opens the 3D preview.
cd /d "%~dp0"
start "" http://localhost:8766/preview/
python serve.py 8766
