#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
赛博算命 - Django 管理脚本
"""
import os
import sys


def main():
    """运行管理任务"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyber_fortune.ysettings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入 Django。请确保已安装 Django 并且 "
            "PYTHONPATH 环境变量正确设置。"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()