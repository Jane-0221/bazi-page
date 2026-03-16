"""
赛博算命 - Django 模型定义
使用 MongoEngine ODM
"""

from datetime import datetime
from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField,
    StringField, IntField, BooleanField, ListField,
    DictField, DateTimeField, ObjectIdField, FloatField
)


# ==================== 用户相关模型 ====================

class UserProfile(EmbeddedDocument):
    """用户资料（非敏感信息）"""
    nickname = StringField(max_length=50, default='')
    avatar_url = StringField(max_length=500, default='')


class BirthInfo(EmbeddedDocument):
    """出生信息"""
    year = IntField(required=True)
    month = IntField(required=True, min_value=1, max_value=12)
    day = IntField(required=True, min_value=1, max_value=31)
    hour = IntField(default=0, min_value=0, max_value=23)


class LifeStatus(EmbeddedDocument):
    """生活状态（敏感信息）"""
    is_divorced = BooleanField(default=False)
    has_abortion = BooleanField(default=False)
    marriage_detail = StringField(default='未婚')


class AuthRecord(EmbeddedDocument):
    """授权记录"""
    auth_time = DateTimeField(default=datetime.now)
    auth_content = StringField()


class User(Document):
    """用户信息"""
    meta = {'collection': 'users'}
    
    login_account = StringField(required=True, unique=True, max_length=100)
    password_hash = StringField(required=True)
    user_profile = EmbeddedDocumentField(UserProfile, default=UserProfile)
    birth_info = EmbeddedDocumentField(BirthInfo, required=True)
    life_status = EmbeddedDocumentField(LifeStatus, default=LifeStatus)
    auth_records = ListField(EmbeddedDocumentField(AuthRecord), default=list)
    account_status = StringField(default='active', choices=['active', 'inactive', 'banned'])
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)


# ==================== 配置数据模型 ====================

class Config(Document):
    """配置数据"""
    meta = {'collection': 'configs'}
    
    name = StringField(required=True, max_length=100)
    type = StringField(required=True, max_length=50)
    data = DictField(default=dict)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'configs',
        'indexes': [
            {'fields': ('type', 'name'), 'unique': True}
        ]
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)


# ==================== 知识库模型 ====================

class FortuneKnowledgeBase(Document):
    """算命知识库"""
    meta = {'collection': 'fortune_knowledge_base'}
    
    material_type = StringField(required=True, max_length=50)
    keywords = ListField(StringField(), default=list)
    content = StringField(required=True)
    case_examples = ListField(StringField(), default=list)
    related_resource_ids = ListField(ObjectIdField(), default=list)
    source = StringField(max_length=100, default='')
    audit_status = StringField(default='draft', choices=['draft', 'approved', 'rejected'])
    audit_time = DateTimeField()
    hit_count = IntField(default=0)
    created_at = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'fortune_knowledge_base',
        'indexes': [
            {'fields': ('keywords', 'material_type', 'audit_status')}
        ]
    }


# ==================== 资源模型 ====================

class FortuneResource(Document):
    """展示资源"""
    meta = {'collection': 'fortune_resources'}
    
    resource_type = StringField(required=True, max_length=50)
    resource_name = StringField(required=True, max_length=100)
    resource_url = StringField(required=True, max_length=500)
    resource_tags = ListField(StringField(), default=list)
    display_order = IntField(default=1)
    audit_status = StringField(default='draft', choices=['draft', 'approved', 'rejected'])
    created_at = DateTimeField(default=datetime.now)


# ==================== 查询记录模型 ====================

class ModelCall(EmbeddedDocument):
    """大模型调用记录"""
    api_key_id = ObjectIdField()
    model_name = StringField(max_length=100)
    prompt = StringField()
    temperature = FloatField(default=0.7)
    raw_response = StringField()


class FinalResult(EmbeddedDocument):
    """最终结果"""
    text_content = StringField()
    display_resource_ids = ListField(ObjectIdField(), default=list)


class FortuneQuery(Document):
    """查询记录"""
    meta = {'collection': 'fortune_queries'}
    
    user_id = ObjectIdField()
    query_time = DateTimeField(default=datetime.now)
    user_input = DictField(default=dict)
    extracted_keywords = ListField(StringField(), default=list)
    matched_kb_ids = ListField(ObjectIdField(), default=list)
    model_call = EmbeddedDocumentField(ModelCall, default=ModelCall)
    final_result = EmbeddedDocumentField(FinalResult, default=FinalResult)
    query_status = StringField(default='pending', choices=['pending', 'success', 'failed'])
    fail_reason = StringField()
    created_at = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'fortune_queries',
        'indexes': [
            {'fields': ('user_id', '-query_time')}
        ]
    }


# ==================== API Key 模型 ====================

class ModelApiKey(Document):
    """大模型 API Key 管理"""
    meta = {'collection': 'model_api_keys'}
    
    platform = StringField(required=True, max_length=100)
    api_key = StringField(required=True)  # 加密存储
    remaining_quota = IntField(default=0)
    total_used = IntField(default=0)
    status = StringField(default='active', choices=['active', 'inactive', 'expired'])
    expire_time = DateTimeField()
    created_at = DateTimeField(default=datetime.now)


# ==================== 审计日志模型 ====================

class AuditLog(Document):
    """审计日志"""
    meta = {'collection': 'audit_logs'}
    
    operate_type = StringField(required=True, max_length=50)
    operate_user = StringField(required=True, max_length=100)
    operate_time = DateTimeField(default=datetime.now)
    operate_content = StringField(required=True)
    operate_ip = StringField(max_length=50)
    operate_result = StringField(default='success', choices=['success', 'failed'])


# ==================== 展示配置模型 ====================

class DisplayConfig(Document):
    """前端展示配置"""
    meta = {'collection': 'display_configs'}
    
    config_name = StringField(required=True, max_length=100)
    config_type = StringField(required=True, max_length=50)
    config_content = DictField(default=dict)
    status = StringField(default='active', choices=['active', 'inactive'])
    created_at = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'display_configs',
        'indexes': [
            {'fields': ('config_type', 'status')}
        ]
    }