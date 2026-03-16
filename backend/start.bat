@echo off
chcp 65001 > nul
echo ============================================================
echo 赛博算命 - Django 服务启动
echo ============================================================
echo.

REM 使用 Anaconda Python
set PYTHON_EXE=C:\Users\Godwin\anaconda3\python.exe

if exist %PYTHON_EXE% (
    echo 使用 Python: %PYTHON_EXE%
    %PYTHON_EXE% manage.py runserver 0.0.0.0:5000
) else (
    echo Anaconda Python 未找到，尝试使用系统 Python...
    python manage.py runserver 0.0.0.0:5000
)

pause