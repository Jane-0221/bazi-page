#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
赛博算命 - 数据库模型定义
定义 MongoDB 集合结构和验证规则
"""

from datetime import datetime
from bson import ObjectId


class User:
    """
    用户信息模型
    集合名: users
    """
    collection_name = 'users'
    
    @staticmethod
    def schema():
        """返回用户模型结构"""
        return {
            'login_account': '',  # 登录账号（手机号/邮箱）
            'password_hash': '',  # 密码哈希
            'user_profile': {
                'nickname': '',  # 昵称
                'avatar_url': ''  # 头像URL
            },
            'birth_info': {
                'year': 0,  # 出生年
                'month': 0,  # 出生月
                'day': 0,  # 出生日
                'hour': 0  # 出生时
            },
            'life_status': {
                'is_divorced': False,  # 是否离婚
                'has_abortion': False,  # 是否堕胎
                'marriage_detail': '未婚'  # 婚姻状态
            },
            'auth_records': [],  # 授权记录
            'account_status': 'active',  # 账号状态
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    
    @staticmethod
    def validate(data):
        """验证用户数据"""
        required = ['login_account', 'password_hash', 'birth_info']
        for field in required:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")
        
        birth_info = data.get('birth_info', {})
        for field in ['year', 'month', 'day']:
            if field not in birth_info:
                raise ValueError(f"出生信息缺少: {field}")
        
        return True


class FortuneKnowledgeBase:
    """
    算命知识库模型
    集合名: fortune_knowledge_base
    """
    collection_name = 'fortune_knowledge_base'
    
    @staticmethod
    def schema():
        """返回知识库模型结构"""
        return {
            'material_type': '',  # 资料类型（财运/婚姻/事业/健康）
            'keywords': [],  # 检索关键词
            'content': '',  # 资料文本内容
            'case_examples': [],  # 相关案例
            'related_resource_ids': [],  # 关联资源ID
            'source': '',  # 资料来源
            'audit_status': 'draft',  # 审核状态
            'audit_time': None,  # 审核时间
            'hit_count': 0,  # 命中次数
            'created_at': datetime.now()
        }
    
    @staticmethod
    def validate(data):
        """验证知识库数据"""
        required = ['material_type', 'keywords', 'content']
        for field in required:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")
        return True


class FortuneResource:
    """
    展示资源模型
    集合名: fortune_resources
    """
    collection_name = 'fortune_resources'
    
    @staticmethod
    def schema():
        """返回资源模型结构"""
        return {
            'resource_type': '',  # 资源类型（卦象图/特有照片/装饰图）
            'resource_name': '',  # 资源名称
            'resource_url': '',  # 资源URL
            'resource_tags': [],  # 资源标签
            'display_order': 1,  # 展示顺序
            'audit_status': 'draft',  # 审核状态
            'created_at': datetime.now()
        }
    
    @staticmethod
    def validate(data):
        """验证资源数据"""
        required = ['resource_type', 'resource_name', 'resource_url']
        for field in required:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")
        return True


class FortuneQuery:
    """
    用户查询记录模型
    集合名: fortune_queries
    """
    collection_name = 'fortune_queries'
    
    @staticmethod
    def schema():
        """返回查询记录模型结构"""
        return {
            'user_id': None,  # 关联用户ID
            'query_time': datetime.now(),  # 查询时间
            'user_input': {
                'birth_info': {},
                'life_status': {}
            },  # 用户输入快照
            'extracted_keywords': [],  # 提取的关键词
            'matched_kb_ids': [],  # 命中的知识库ID
            'model_call': {
                'api_key_id': None,
                'model_name': '',
                'prompt': '',
                'temperature': 0.7,
                'raw_response': ''
            },  # 大模型调用记录
            'final_result': {
                'text_content': '',
                'display_resource_ids': []
            },  # 最终结果
            'query_status': 'success',  # 查询状态
            'fail_reason': '',  # 失败原因
            'created_at': datetime.now()
        }
    
    @staticmethod
    def validate(data):
        """验证查询记录数据"""
        required = ['user_id', 'user_input']
        for field in required:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")
        return True


class ModelApiKey:
    """
    大模型APIKey管理模型
    集合名: model_api_keys
    """
    collection_name = 'model_api_keys'
    
    @staticmethod
    def schema():
        """返回APIKey模型结构"""
        return {
            'platform': '',  # 平台名称
            'api_key': '',  # API密钥（加密）
            'remaining_quota': 0,  # 剩余额度
            'total_used': 0,  # 累计使用次数
            'status': 'active',  # 密钥状态
            'expire_time': None,  # 过期时间
            'created_at': datetime.now()
        }
    
    @staticmethod
    def validate(data):
        """验证APIKey数据"""
        required = ['platform', 'api_key']
        for field in required:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")
        return True


class AuditLog:
    """
    敏感操作审计模型
    集合名: audit_logs
    """
    collection_name = 'audit_logs'
    
    @staticmethod
    def schema():
        """返回审计日志模型结构"""
        return {
            'operate_type': '',  # 操作类型
            'operate_user': '',  # 操作人
            'operate_time': datetime.now(),  # 操作时间
            'operate_content': '',  # 操作内容
            'operate_ip': '',  # 操作IP
            'operate_result': 'success'  # 操作结果
        }
    
    @staticmethod
    def validate(data):
        """验证审计日志数据"""
        required = ['operate_type', 'operate_user', 'operate_content']
        for field in required:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")
        return True


class DisplayConfig:
    """
    前端展示配置模型
    集合名: display_configs
    """
    collection_name = 'display_configs'
    
    @staticmethod
    def schema():
        """返回展示配置模型结构"""
        return {
            'config_name': '',  # 配置名称
            'config_type': '',  # 配置类型
            'config_content': {},  # 配置内容
            'status': 'active',  # 配置状态
            'created_at': datetime.now()
        }
    
    @staticmethod
    def validate(data):
        """验证展示配置数据"""
        required = ['config_name', 'config_type', 'config_content']
        for field in required:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")
        return True


# ==================== 配置数据模型 ====================

class PatternConfig:
    """
    格局配置模型
    集合名: configs
    用于存储格局模板、五行对应、行业匹配等配置
    """
    collection_name = 'configs'
    
    @staticmethod
    def schema():
        """返回配置模型结构"""
        return {
            'name': '',  # 配置名称
            'type': '',  # 配置类型（pattern/wuxing_mapping/industry_mapping/shensha_config/fortune_tags）
            'data': {},  # 配置数据
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }


# 集合映射
COLLECTIONS = {
    'users': User,
    'fortune_knowledge_base': FortuneKnowledgeBase,
    'fortune_resources': FortuneResource,
    'fortune_queries': FortuneQuery,
    'model_api_keys': ModelApiKey,
    'audit_logs': AuditLog,
    'display_configs': DisplayConfig,
    'configs': PatternConfig
}