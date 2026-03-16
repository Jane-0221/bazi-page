#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
赛博算命 - Django 启动脚本
自动检测并使用正确的 Python 环境
"""

import subprocess
import sys
import os

def find_python():
    """查找可用的 Python 解释器"""
    candidates = [
        sys.executable,  # 当前 Python
        'python',
        'python3',
        r'C:\Users\Godwin\anaconda3\python.exe',
        r'C:\Python312\python.exe',
        r'C:\Python311\python.exe',
        r'C:\Python310\python.exe',
    ]
    
    for py in candidates:
        if not py:
            continue
        try:
            result = subprocess.run(
                [py, '-c', 'import django; print(django.VERSION)'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print(f"✓ 找到 Django: {py}")
                return py
        except Exception:
            continue
    
    return None

def main():
    print("=" * 60)
    print("赛博算命 - Django 服务启动")
    print("=" * 60)
    
    # 检查 Django 是否可用
    try:
        import django
        print(f"✓ Django 版本: {django.VERSION}")
        python_exe = sys.executable
    except ImportError:
        print("当前 Python 环境未安装 Django，正在查找其他环境...")
        python_exe = find_python()
        if not python_exe:
            print("✗ 错误: 未找到安装了 Django 的 Python 环境")
            print("请运行: pip install Django djangorestframework django-cors-headers mongoengine")
            sys.exit(1)
    
    # 启动 Django 服务
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"\n启动服务: http://localhost:5000")
    print("按 Ctrl+C 停止服务\n")
    
    if python_exe == sys.executable:
        # 直接运行
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyber_fortune.ysettings')
        from django.core.management import execute_from_command_line
        execute_from_command_line(['ymanage.py', 'runserver', '0.0.0.0:5000'])
    else:
        # 使用子进程运行
        subprocess.run([python_exe, 'ymanage.py', 'runserver', '0.0.0.0:5000'])

if __name__ == '__main__':
    main()