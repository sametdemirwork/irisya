@echo off
rem Irisya Clinic sitesini yerelde acar: http://localhost:5510
cd /d "%~dp0irisya-clinic"
start "" http://localhost:5510
python -m http.server 5510
