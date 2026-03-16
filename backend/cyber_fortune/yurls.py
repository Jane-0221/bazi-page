"""
赛博算命 - Django URL 配置
"""
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime


class IndexView(APIView):
    """首页 API 信息"""
    
    def get(self, request):
        return Response({
            'name': '赛博算命 API (Django)',
            'version': '2.0.0',
            'description': '基于五行理论的命理分析系统 - Django REST Framework',
            'framework': 'Django',
            'endpoints': {
                'query': '/api/query - POST - 查询命理信息',
                'fortune': '/api/fortune - GET - 获取大运信息',
                'config': '/api/config/<type> - GET/POST - 配置管理',
                'health': '/api/health - GET - 健康检查',
                'db_status': '/api/db/status - GET - 数据库状态'
            }
        })


class HealthCheckView(APIView):
    """健康检查接口"""
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'cyber-fortune-api-django'
        })


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('api/health', HealthCheckView.as_view(), name='health'),
    path('api/', include('fortune.yurls')),
]