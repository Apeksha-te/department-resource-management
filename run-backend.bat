@echo off
title Department Resource Hub - Django Web Portal
echo Starting Django Web Portal on http://localhost:8090 ...
cd /d "%~dp0\backend"
python manage.py runserver 8090
pause
