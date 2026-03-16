#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
赛博算命 - URL 路由配置
定义前端请求对应的后端处理函数
"""

from flask import jsonify, request


def register_routes(app):
    """
    注册所有路由到 Flask 应用
    
    Args:
        app: Flask 应用实例
    """
    
    @app.route('/api/test', methods=['GET'])
    def test_handler():
        """测试接口"""
        return jsonify({
            'success': True,
            'message': 'API 服务正常运行',
            'endpoints': {
                '/api/query': 'POST - 命理查询',
                '/api/fortune': 'GET - 大运查询',
                '/api/health': 'GET - 健康检查'
            }
        })
    
    @app.route('/api/bazi', methods=['POST'])
    def bazi_handler():
        """
        八字计算接口
        仅返回八字信息，不包含完整分析
        """
        try:
            data = request.get_json()
            birthday = data.get('birthday', '')
            hour = data.get('hour', 12)
            
            if not birthday:
                return jsonify({
                    'success': False,
                    'message': '请提供出生日期'
                }), 400
            
            from datetime import datetime
            from FiveMat import FiveElementsCalculator
            
            birth_date = datetime.strptime(birthday, '%Y-%m-%d')
            birth_date = birth_date.replace(hour=hour)
            
            calculator = FiveElementsCalculator(birth_date, data.get('gender', 'male'))
            bazi = calculator._calculate_bazi()
            
            return jsonify({
                'success': True,
                'data': bazi
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    @app.route('/api/elements', methods=['POST'])
    def elements_handler():
        """
        五行分析接口
        返回五行占比信息
        """
        try:
            data = request.get_json()
            birthday = data.get('birthday', '')
            
            if not birthday:
                return jsonify({
                    'success': False,
                    'message': '请提供出生日期'
                }), 400
            
            from datetime import datetime
            from FiveMat import FiveElementsCalculator
            
            birth_date = datetime.strptime(birthday, '%Y-%m-%d')
            calculator = FiveElementsCalculator(birth_date, data.get('gender', 'male'))
            
            bazi = calculator._calculate_bazi()
            elements = calculator._calculate_five_elements(bazi)
            
            return jsonify({
                'success': True,
                'data': {
                    'bazi': bazi,
                    'elements': elements
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """404 错误处理"""
        return jsonify({
            'success': False,
            'message': '请求的资源不存在',
            'error': 'Not Found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """405 错误处理"""
        return jsonify({
            'success': False,
            'message': '请求方法不允许',
            'error': 'Method Not Allowed'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 错误处理"""
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'error': 'Internal Server Error'
        }), 500