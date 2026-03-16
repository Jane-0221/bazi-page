"""
赛博算命 - DRF 序列化器
"""

from rest_framework import serializers
from datetime import datetime


# ==================== 查询请求序列化器 ====================

class QueryRequestSerializer(serializers.Serializer):
    """查询请求序列化器"""
    name = serializers.CharField(max_length=50, required=True)
    birthday = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=['male', 'female'], default='male')


class FortuneRequestSerializer(serializers.Serializer):
    """大运查询请求序列化器"""
    birthday = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=['male', 'female'], default='male')


# ==================== 配置数据序列化器 ====================

class ConfigSerializer(serializers.Serializer):
    """配置数据序列化器"""
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=50)
    data = serializers.DictField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ConfigUpdateSerializer(serializers.Serializer):
    """配置更新序列化器"""
    name = serializers.CharField(max_length=100, required=False)
    data = serializers.DictField(required=True)


# ==================== 知识库序列化器 ====================

class KnowledgeBaseSerializer(serializers.Serializer):
    """知识库序列化器"""
    id = serializers.CharField(read_only=True)
    material_type = serializers.CharField(max_length=50)
    keywords = serializers.ListField(child=serializers.CharField())
    content = serializers.CharField()
    case_examples = serializers.ListField(child=serializers.CharField(), required=False)
    source = serializers.CharField(max_length=100, required=False)
    audit_status = serializers.CharField(max_length=20)
    hit_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


# ==================== 命理分析结果序列化器 ====================

class PatternSerializer(serializers.Serializer):
    """格局序列化器"""
    title = serializers.CharField()
    pattern = serializers.CharField()
    description = serializers.CharField()


class FiveElementsSerializer(serializers.Serializer):
    """五行序列化器"""
    wood = serializers.FloatField()
    fire = serializers.FloatField()
    earth = serializers.FloatField()
    metal = serializers.FloatField()
    water = serializers.FloatField()
    wood_cai = serializers.CharField()
    fire_guan = serializers.CharField()
    water_shi = serializers.CharField()
    metal_bi = serializers.CharField()
    earth_yin = serializers.CharField()


class LuckyElementsSerializer(serializers.Serializer):
    """喜用神序列化器"""
    title = serializers.CharField()
    labels = serializers.DictField()
    luckyColors = serializers.ListField()
    luckyDirections = serializers.ListField(child=serializers.CharField())
    luckyNumbers = serializers.ListField(child=serializers.CharField())


class ShishenSerializer(serializers.Serializer):
    """十神序列化器"""
    title = serializers.CharField()
    chartTitle = serializers.CharField()
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    colors = serializers.ListField(child=serializers.CharField())


class ShenshaItemSerializer(serializers.Serializer):
    """神煞项序列化器"""
    name = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()
    iconBg = serializers.CharField()
    iconColor = serializers.CharField()


class ShenshaSerializer(serializers.Serializer):
    """神煞序列化器"""
    title = serializers.CharField()
    items = ShenshaItemSerializer(many=True)


class FortunePeriodSerializer(serializers.Serializer):
    """大运周期序列化器"""
    age = serializers.CharField()
    stemBranch = serializers.CharField()
    tag = serializers.CharField()
    score = serializers.IntegerField()


class MatchSerializer(serializers.Serializer):
    """匹配信息序列化器"""
    industry = serializers.DictField()
    partner = serializers.DictField()


class FortuneResultSerializer(serializers.Serializer):
    """命理分析结果序列化器"""
    bazi = serializers.DictField()
    five_elements = FiveElementsSerializer()
    body_type = serializers.CharField()
    lucky = LuckyElementsSerializer()
    pattern = PatternSerializer()
    shishen = ShishenSerializer()
    shensha = ShenshaSerializer()
    fortune_periods = FortunePeriodSerializer(many=True)
    match = MatchSerializer()
    day_zhi = serializers.CharField()
    day_shishen = serializers.CharField()


# ==================== 前端配置序列化器 ====================

class FrontendConfigSerializer(serializers.Serializer):
    """前端配置序列化器"""
    page = serializers.DictField()
    colors = serializers.DictField()
    nav = serializers.DictField()
    pattern = PatternSerializer()
    fiveElements = serializers.DictField()
    lucky = LuckyElementsSerializer()
    match = MatchSerializer()
    fortune = serializers.DictField()
    shishen = ShishenSerializer()
    shensha = ShenshaSerializer()
    disclaimer = serializers.DictField()
    footer = serializers.DictField()


class QueryResponseSerializer(serializers.Serializer):
    """查询响应序列化器"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField()


# ==================== 数据库状态序列化器 ====================

class DatabaseStatusSerializer(serializers.Serializer):
    """数据库状态序列化器"""
    available = serializers.BooleanField()
    connected = serializers.BooleanField()
    collections = serializers.DictField()
    error = serializers.CharField(required=False)