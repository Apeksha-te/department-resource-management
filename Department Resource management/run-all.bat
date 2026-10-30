@echo off
title Department Resource Sharing Portal - Launcher
echo ==============================================================
echo   Department Resource Sharing Portal (Mini Project 23IS503)
echo   Malnad College of Engineering (MCE Hassan)
echo   Frontend: HTML, CSS | Backend: Python (Django) | Database: SQLite
echo ==============================================================
echo.
echo Launching Django Web Portal on http://localhost:8090 ...
cd /d "%~dp0\backend"
start "Department Resource Portal" python manage.py runserver 8090
timeout /t 3 /nobreak >nul
echo.
echo Opening portal in default browser...
start http://localhost:8090
echo.
echo ==============================================================
echo   Portal is LIVE:
echo   Main Web Portal:  http://localhost:8090
echo   Admin Dashboard:  http://localhost:8090/admin/
echo   Faculty Portal:   http://localhost:8090/faculty/dashboard/
echo   Student Portal:   http://localhost:8090/student/dashboard/
echo ==============================================================
pause
