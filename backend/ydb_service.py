#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
赛博算命 - 数据库服务层
提供数据库操作的封装接口
"""

import os
import logging
from datetime import datetime
from bson import ObjectId

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB 连接配置
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'cyber_fortune')


class DatabaseService:
    """数据库服务类"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        """连接数据库"""
        if self._client is not None:
            return True
        
        try:
            from pymongo import MongoClient
            self._client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self._db = self._client[DB_NAME]
            self._client.server_info()
            logger.info(f"数据库服务连接成功: {DB_NAME}")
            return True
        except Exception as e:
            logger.warning(f"数据库连接失败: {e}，将使用内存缓存")
            self._client = None
            self._db = None
            return False
    
    def close(self):
        """关闭连接"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
    
    @property
    def db(self):
        """获取数据库实例"""
        if self._db is None:
            self.connect()
        return self._db
    
    def is_connected(self):
        """检查是否已连接"""
        return self._db is not None


# 全局数据库服务实例
db_service = DatabaseService()


# ==================== 配置数据服务 ====================

class ConfigService:
    """配置数据服务"""
    
    def __init__(self):
        self._cache = {}  # 内存缓存
    
    def _get_cache_key(self, config_type, config_name=None):
        """生成缓存键"""
        if config_name:
            return f"{config_type}:{config_name}"
        return config_type
    
    def get_config(self, config_type, config_name=None, use_cache=True):
        """
        获取配置数据
        
        Args:
            config_type: 配置类型 (pattern/wuxing_mapping/industry_mapping/shensha_config/fortune_tags)
            config_name: 配置名称（可选）
            use_cache: 是否使用缓存
        
        Returns:
            dict: 配置数据
        """
        cache_key = self._get_cache_key(config_type, config_name)
        
        # 检查缓存
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        # 从数据库获取
        if db_service.is_connected():
            query = {'type': config_type}
            if config_name:
                query['name'] = config_name
            
            config = db_service.db.configs.find_one(query)
            if config:
                result = config.get('data', {})
                # 缓存结果
                self._cache[cache_key] = result
                return result
        
        # 返回默认配置
        return self._get_default_config(config_type)
    
    def _get_default_config(self, config_type):
        """获取默认配置（当数据库不可用时）"""
        defaults = {
            'pattern': {
                'templates': [
                    {'title': '【乘风破浪】', 'pattern': '正官格·贵气盈门', 'description': '正气凛然，贵人相助，事业顺遂。'},
                    {'title': '【厚积薄发】', 'pattern': '正印格·文华显耀', 'description': '学识渊博，智慧超群，文运亨通。'},
                    {'title': '【柳暗花明】', 'pattern': '偏财格·财源广进', 'description': '财运亨通，投资有道，收益丰厚。'},
                    {'title': '【逆流而上】', 'pattern': '七杀格·威震四方', 'description': '意志坚定，勇往直前，成就非凡。'},
                    {'title': '【静待花开】', 'pattern': '食神格·福禄双全', 'description': '生活安逸，福禄兼得，晚年享福。'}
                ]
            },
            'wuxing_mapping': {
                'colors': {
                    '木': [{'name': '绿色', 'colorClass': 'bg-green-200'}, {'name': '青色', 'colorClass': 'bg-cyan-200'}],
                    '火': [{'name': '红色', 'colorClass': 'bg-red-200'}, {'name': '粉色', 'colorClass': 'bg-pink-200'}],
                    '土': [{'name': '黄色', 'colorClass': 'bg-luckyEarth'}, {'name': '棕色', 'colorClass': 'bg-amber-200'}],
                    '金': [{'name': '白色', 'colorClass': 'bg-luckyMetal'}, {'name': '金色', 'colorClass': 'bg-yellow-100'}],
                    '水': [{'name': '黑色', 'colorClass': 'bg-gray-300'}, {'name': '蓝色', 'colorClass': 'bg-blue-200'}]
                },
                'directions': {
                    '木': ['正东', '东南'],
                    '火': ['正南'],
                    '土': ['家乡', '中部'],
                    '金': ['正西', '西北'],
                    '水': ['正北']
                },
                'numbers': {
                    '木': ['3', '8'],
                    '火': ['2', '7'],
                    '土': ['5', '10'],
                    '金': ['4', '9'],
                    '水': ['1', '6']
                }
            },
            'industry_mapping': {
                'industries': {
                    '木': '文化教育、医疗卫生、艺术设计、农林牧渔',
                    '火': '电子科技、餐饮娱乐、照明电力、美容美发',
                    '土': '房地产、建筑工程、农业种植、政府部门',
                    '金': '金融投资、法律咨询、机械制造、珠宝首饰',
                    '水': '物流运输、旅游酒店、饮料饮品、水产养殖'
                }
            },
            'shensha_config': {
                'items': [
                    {'name': '贵人相助', 'description': '天乙贵人、福星贵人', 'icon': 'fa-star', 'iconBg': 'bg-orange-100', 'iconColor': 'text-orange-500'},
                    {'name': '慧根发达', 'description': '太极贵人', 'icon': 'fa-brain', 'iconBg': 'bg-blue-100', 'iconColor': 'text-blue-500'},
                    {'name': '张力满满', 'description': '桃花', 'icon': 'fa-heart', 'iconBg': 'bg-yellow-100', 'iconColor': 'text-yellow-500'},
                    {'name': '天选领导', 'description': '禄神', 'icon': 'fa-crown', 'iconBg': 'bg-pink-100', 'iconColor': 'text-pink-500'},
                    {'name': '旷世奇才', 'description': '学堂', 'icon': 'fa-graduation-cap', 'iconBg': 'bg-sky-100', 'iconColor': 'text-sky-500'}
                ]
            },
            'fortune_tags': {
                'tags': [
                    {'score_range': [90, 100], 'tags': ['智慧通达 德才并举', '福星高照 万事如意', '鹏程万里 前程似锦']},
                    {'score_range': [80, 89], 'tags': ['根深叶茂 贵人垂青', '福泽绵长 贵人护业', '鸿运当头 吉星拱照']},
                    {'score_range': [70, 79], 'tags': ['稳中求进 渐入佳境', '安守本心 心宽事顺', '柳暗花明 豁然开朗']},
                    {'score_range': [60, 69], 'tags': ['韬光养晦 厚积薄发', '稳扎稳打 步步为营', '循序渐进 稳中求胜']},
                    {'score_range': [0, 59], 'tags': ['否极泰来 转危为安', '韬光养晦 等待时机', '收敛低调 蓄势待发']}
                ]
            }
        }
        
        return defaults.get(config_type, {})
    
    def update_config(self, config_type, config_name, data):
        """
        更新配置数据
        
        Args:
            config_type: 配置类型
            config_name: 配置名称
            data: 新的配置数据
        
        Returns:
            bool: 更新是否成功
        """
        if not db_service.is_connected():
            logger.warning("数据库未连接，无法更新配置")
            return False
        
        try:
            result = db_service.db.configs.update_one(
                {'type': config_type, 'name': config_name},
                {'$set': {'data': data, 'updated_at': datetime.now()}},
                upsert=True
            )
            
            # 清除缓存
            cache_key = self._get_cache_key(config_type, config_name)
            if cache_key in self._cache:
                del self._cache[cache_key]
            
            logger.info(f"配置更新成功: {config_type}/{config_name}")
            return True
        except Exception as e:
            logger.error(f"配置更新失败: {e}")
            return False
    
    def clear_cache(self, config_type=None):
        """清除缓存"""
        if config_type:
            keys_to_remove = [k for k in self._cache if k.startswith(config_type)]
            for key in keys_to_remove:
                del self._cache[key]
        else:
            self._cache.clear()
        logger.info(f"缓存已清除: {config_type or '全部'}")


# 全局配置服务实例
config_service = ConfigService()


# ==================== 知识库服务 ====================

class KnowledgeBaseService:
    """知识库服务"""
    
    def search(self, keywords, material_type=None, limit=10):
        """
        搜索知识库
        
        Args:
            keywords: 关键词列表
            material_type: 资料类型（可选）
            limit: 返回结果数量限制
        
        Returns:
            list: 匹配的知识库记录
        """
        if not db_service.is_connected():
            logger.warning("数据库未连接，无法搜索知识库")
            return []
        
        try:
            query = {
                'keywords': {'$in': keywords},
                'audit_status': 'approved'
            }
            
            if material_type:
                query['material_type'] = material_type
            
            results = list(db_service.db.fortune_knowledge_base.find(
                query,
                limit=limit
            ))
            
            # 更新命中次数
            if results:
                ids = [r['_id'] for r in results]
                db_service.db.fortune_knowledge_base.update_many(
                    {'_id': {'$in': ids}},
                    {'$inc': {'hit_count': 1}}
                )
            
            return results
        except Exception as e:
            logger.error(f"知识库搜索失败: {e}")
            return []
    
    def get_by_type(self, material_type):
        """按类型获取知识库"""
        if not db_service.is_connected():
            return []
        
        try:
            return list(db_service.db.fortune_knowledge_base.find(
                {'material_type': material_type, 'audit_status': 'approved'}
            ))
        except Exception as e:
            logger.error(f"获取知识库失败: {e}")
            return []


# 全局知识库服务实例
knowledge_service = KnowledgeBaseService()


# ==================== 用户服务 ====================

class UserService:
    """用户服务"""
    
    def create_user(self, login_account, password_hash, birth_info, **kwargs):
        """创建用户"""
        if not db_service.is_connected():
            logger.warning("数据库未连接，无法创建用户")
            return None
        
        try:
            user_data = {
                'login_account': login_account,
                'password_hash': password_hash,
                'user_profile': kwargs.get('user_profile', {'nickname': '', 'avatar_url': ''}),
                'birth_info': birth_info,
                'life_status': kwargs.get('life_status', {
                    'is_divorced': False,
                    'has_abortion': False,
                    'marriage_detail': '未婚'
                }),
                'auth_records': [],
                'account_status': 'active',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            result = db_service.db.users.insert_one(user_data)
            logger.info(f"用户创建成功: {login_account}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"用户创建失败: {e}")
            return None
    
    def get_user_by_account(self, login_account):
        """根据账号获取用户"""
        if not db_service.is_connected():
            return None
        
        try:
            return db_service.db.users.find_one({'login_account': login_account})
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户"""
        if not db_service.is_connected():
            return None
        
        try:
            return db_service.db.users.find_one({'_id': ObjectId(user_id)})
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    def update_user(self, user_id, update_data):
        """更新用户信息"""
        if not db_service.is_connected():
            return False
        
        try:
            update_data['updated_at'] = datetime.now()
            result = db_service.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            return False
    
    def add_auth_record(self, user_id, auth_content):
        """添加授权记录"""
        if not db_service.is_connected():
            return False
        
        try:
            auth_record = {
                'auth_time': datetime.now(),
                'auth_content': auth_content
            }
            result = db_service.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$push': {'auth_records': auth_record}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"添加授权记录失败: {e}")
            return False


# 全局用户服务实例
user_service = UserService()


# ==================== 查询记录服务 ====================

class QueryRecordService:
    """查询记录服务"""
    
    def create_record(self, user_id, user_input, extracted_keywords=None, matched_kb_ids=None):
        """创建查询记录"""
        if not db_service.is_connected():
            return None
        
        try:
            record = {
                'user_id': ObjectId(user_id) if user_id else None,
                'query_time': datetime.now(),
                'user_input': user_input,
                'extracted_keywords': extracted_keywords or [],
                'matched_kb_ids': matched_kb_ids or [],
                'model_call': {
                    'api_key_id': None,
                    'model_name': '',
                    'prompt': '',
                    'temperature': 0.7,
                    'raw_response': ''
                },
                'final_result': {
                    'text_content': '',
                    'display_resource_ids': []
                },
                'query_status': 'pending',
                'fail_reason': '',
                'created_at': datetime.now()
            }
            
            result = db_service.db.fortune_queries.insert_one(record)
            return result.inserted_id
        except Exception as e:
            logger.error(f"创建查询记录失败: {e}")
            return None
    
    def update_result(self, record_id, final_result, model_call=None):
        """更新查询结果"""
        if not db_service.is_connected():
            return False
        
        try:
            update_data = {
                'final_result': final_result,
                'query_status': 'success'
            }
            
            if model_call:
                update_data['model_call'] = model_call
            
            result = db_service.db.fortune_queries.update_one(
                {'_id': ObjectId(record_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"更新查询结果失败: {e}")
            return False
    
    def get_user_history(self, user_id, limit=20):
        """获取用户查询历史"""
        if not db_service.is_connected():
            return []
        
        try:
            return list(db_service.db.fortune_queries.find(
                {'user_id': ObjectId(user_id)},
                sort=[('query_time', -1)],
                limit=limit
            ))
        except Exception as e:
            logger.error(f"获取查询历史失败: {e}")
            return []


# 全局查询记录服务实例
query_service = QueryRecordService()


# ==================== 审计日志服务 ====================

class AuditLogService:
    """审计日志服务"""
    
    def log(self, operate_type, operate_user, operate_content, operate_ip='', operate_result='success'):
        """记录审计日志"""
        if not db_service.is_connected():
            return False
        
        try:
            log_entry = {
                'operate_type': operate_type,
                'operate_user': operate_user,
                'operate_time': datetime.now(),
                'operate_content': operate_content,
                'operate_ip': operate_ip,
                'operate_result': operate_result
            }
            
            db_service.db.audit_logs.insert_one(log_entry)
            return True
        except Exception as e:
            logger.error(f"记录审计日志失败: {e}")
            return False


# 全局审计日志服务实例
audit_service = AuditLogService()


# ==================== 展示配置服务 ====================

class DisplayConfigService:
    """展示配置服务"""
    
    _cache = {}
    
    def get_config(self, config_type, config_name=None):
        """获取展示配置"""
        cache_key = f"{config_type}:{config_name}" if config_name else config_type
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if not db_service.is_connected():
            return None
        
        try:
            query = {'config_type': config_type, 'status': 'active'}
            if config_name:
                query['config_name'] = config_name
            
            config = db_service.db.display_configs.find_one(query)
            if config:
                result = config.get('config_content', {})
                self._cache[cache_key] = result
                return result
            return None
        except Exception as e:
            logger.error(f"获取展示配置失败: {e}")
            return None
    
    def get_color_theme(self):
        """获取颜色主题"""
        return self.get_config('color_theme') or {
            'bgMain': '#FFFFF8',
            'bgCard': '#FDF8F3',
            'bgChart': '#FAF5F0',
            'textMain': '#5C3D2E',
            'fire': '#F8C4C4',
            'wood': '#C9A66B',
            'water': '#A8D8EA',
            'metal': '#F5E6CC',
            'earth': '#D4A574'
        }


# 全局展示配置服务实例
display_service = DisplayConfigService()


# ==================== 初始化函数 ====================

def init_database():
    """初始化数据库连接"""
    return db_service.connect()


def check_database():
    """检查数据库状态"""
    if db_service.is_connected():
        try:
            db_service.db.list_collection_names()
            return True
        except:
            return False
    return False