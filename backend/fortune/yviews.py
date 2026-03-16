"""
赛博算命 - Django API 视图
"""

import logging
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .yservices import FiveElementsCalculator, ConfigService, KnowledgeService, build_frontend_config
from .yserializers import (
    QueryRequestSerializer, FortuneRequestSerializer,
    ConfigSerializer, ConfigUpdateSerializer
)
from .ymodels import Config, FortuneKnowledgeBase

logger = logging.getLogger('fortune')


@method_decorator(csrf_exempt, name='dispatch')
class QueryView(APIView):
    """命理查询接口"""
    
    def post(self, request):
        serializer = QueryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            name = serializer.validated_data['name']
            birthday = serializer.validated_data['birthday']
            gender = serializer.validated_data.get('gender', 'male')
            
            # 计算命理信息
            calculator = FiveElementsCalculator(birthday, gender)
            result = calculator.calculate()
            
            # 构建前端配置
            frontend_config = build_frontend_config(name, birthday, result)
            
            logger.info(f"命理查询成功: {name}, {birthday}")
            
            return Response({
                'success': True,
                'message': '查询成功',
                'data': frontend_config
            })
            
        except Exception as e:
            logger.error(f"命理查询失败: {e}")
            return Response({
                'success': False,
                'message': f'查询失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class FortuneView(APIView):
    """大运查询接口"""
    
    def post(self, request):
        serializer = FortuneRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            birthday = serializer.validated_data['birthday']
            gender = serializer.validated_data.get('gender', 'male')
            
            calculator = FiveElementsCalculator(birthday, gender)
            periods = calculator.calculate_fortune_periods()
            
            return Response({
                'success': True,
                'message': '查询成功',
                'data': {'fortune_periods': periods}
            })
            
        except Exception as e:
            logger.error(f"大运查询失败: {e}")
            return Response({
                'success': False,
                'message': f'查询失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfigDetailView(APIView):
    """配置详情接口"""
    
    def get(self, request, config_type):
        try:
            data = ConfigService.get_config(config_type)
            if data:
                return Response({
                    'success': True,
                    'data': data
                })
            else:
                return Response({
                    'success': False,
                    'message': f'配置类型 {config_type} 不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, config_type):
        serializer = ConfigUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            config_name = serializer.validated_data.get('name', config_type)
            data = serializer.validated_data['data']
            
            success = ConfigService.update_config(config_type, config_name, data)
            
            if success:
                return Response({
                    'success': True,
                    'message': '配置更新成功'
                })
            else:
                return Response({
                    'success': False,
                    'message': '配置更新失败'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClearCacheView(APIView):
    """清除缓存接口"""
    
    def post(self, request):
        config_type = request.query_params.get('type')
        ConfigService.clear_cache(config_type)
        
        return Response({
            'success': True,
            'message': f'缓存已清除: {config_type or "全部"}'
        })


class KnowledgeSearchView(APIView):
    """知识库搜索接口"""
    
    def get(self, request):
        keywords = request.query_params.get('keywords', '').split(',')
        material_type = request.query_params.get('type')
        limit = int(request.query_params.get('limit', 10))
        
        if not keywords or keywords == ['']:
            return Response({
                'success': False,
                'message': '请提供搜索关键词'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            results = KnowledgeService.search(keywords, material_type, limit)
            data = [{
                'id': str(r.id),
                'material_type': r.material_type,
                'keywords': r.keywords,
                'content': r.content,
                'hit_count': r.hit_count
            } for r in results]
            
            return Response({
                'success': True,
                'data': data,
                'count': len(data)
            })
            
        except Exception as e:
            logger.error(f"知识库搜索失败: {e}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatabaseStatusView(APIView):
    """数据库状态接口"""
    
    def get(self, request):
        try:
            from pymongo import MongoClient
            from django.conf import settings
            
            client = MongoClient(settings.MONGO_URI)
            db = client[settings.DB_NAME]
            
            collections = {}
            for coll_name in db.list_collection_names():
                collections[coll_name] = db[coll_name].count_documents({})
            
            return Response({
                'success': True,
                'data': {
                    'available': True,
                    'connected': True,
                    'database': settings.DB_NAME,
                    'collections': collections
                }
            })
            
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return Response({
                'success': False,
                'data': {
                    'available': False,
                    'connected': False,
                    'error': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)