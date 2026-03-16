"""
赛博算命 - fortune 应用配置
"""
from django.apps import AppConfig


class FortuneConfig(AppConfig):
    """fortune 应用配置"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fortune'
    verbose_name = '命理分析'
    
    def ready(self):
        """应用启动时初始化"""
        # 初始化数据库连接
        try:
            from mongoengine import connect
            from django.conf import settings
            connect(
                db=settings.DB_NAME,
                host=settings.MONGO_URI,
                alias='default'
            )
            print(f"✓ MongoDB 连接成功: {settings.DB_NAME}")
        except Exception as e:
            print(f"✗ MongoDB 连接失败: {e}")