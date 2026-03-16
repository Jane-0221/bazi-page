"""
赛博算命 - fortune 应用 URL 路由
"""

from django.urls import path
from .yviews import (
    QueryView, FortuneView, ConfigDetailView,
    ClearCacheView, KnowledgeSearchView, DatabaseStatusView
)

urlpatterns = [
    # 命理查询
    path('query', QueryView.as_view(), name='query'),
    
    # 大运查询
    path('fortune', FortuneView.as_view(), name='fortune'),
    
    # 配置管理
    path('config/<str:config_type>', ConfigDetailView.as_view(), name='config_detail'),
    
    # 清除缓存
    path('config/clear-cache', ClearCacheView.as_view(), name='clear_cache'),
    
    # 知识库搜索
    path('knowledge/search', KnowledgeSearchView.as_view(), name='knowledge_search'),
    
    # 数据库状态
    path('db/status', DatabaseStatusView.as_view(), name='db_status'),
]