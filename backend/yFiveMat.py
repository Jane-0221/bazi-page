#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
赛博算命 - 五行命理计算核心模块
实现基于生辰八字的五行分析、大运计算、神煞判定等功能
支持从数据库读取配置数据
"""

from datetime import datetime, timedelta
import random
import math
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入数据库服务
try:
    from ydb_service import config_service, knowledge_service, display_service
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


class FiveElementsCalculator:
    """
    五行命理计算器
    根据出生日期计算八字、五行、大运、神煞等信息
    """
    
    # 天干
    TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    # 地支
    DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 天干五行
    TIAN_GAN_WUXING = {
        '甲': '木', '乙': '木',
        '丙': '火', '丁': '火',
        '戊': '土', '己': '土',
        '庚': '金', '辛': '金',
        '壬': '水', '癸': '水'
    }
    
    # 地支五行
    DI_ZHI_WUXING = {
        '子': '水', '丑': '土',
        '寅': '木', '卯': '木',
        '辰': '土', '巳': '火',
        '午': '火', '未': '土',
        '申': '金', '酉': '金',
        '戌': '土', '亥': '水'
    }
    
    # 地支藏干
    DI_ZHI_CANG_GAN = {
        '子': ['癸'],
        '丑': ['己', '癸', '辛'],
        '寅': ['甲', '丙', '戊'],
        '卯': ['乙'],
        '辰': ['戊', '乙', '癸'],
        '巳': ['丙', '戊', '庚'],
        '午': ['丁', '己'],
        '未': ['己', '丁', '乙'],
        '申': ['庚', '壬', '戊'],
        '酉': ['辛'],
        '戌': ['戊', '辛', '丁'],
        '亥': ['壬', '甲']
    }
    
    # 十神定义（以日主为基准）
    SHISHEN_MAP = {
        ('木', '木', 'same'): '比肩',
        ('木', '木', 'diff'): '劫财',
        ('木', '火', 'same'): '食神',
        ('木', '火', 'diff'): '伤官',
        ('木', '土', 'same'): '偏财',
        ('木', '土', 'diff'): '正财',
        ('木', '金', 'same'): '七杀',
        ('木', '金', 'diff'): '正官',
        ('木', '水', 'same'): '偏印',
        ('木', '水', 'diff'): '正印',
    }
    
    # 五行相生相克
    WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    WUXING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
    
    # 格局描述库
    PATTERN_TITLES = [
        "【乘风破浪】",
        "【厚积薄发】",
        "【柳暗花明】",
        "【逆流而上】",
        "【静待花开】",
        "【破茧成蝶】",
        "【浴火重生】",
        "【踏雪寻梅】",
        "【云开见日】",
        "【这点痛算什么】"
    ]
    
    PATTERN_TYPES = [
        "正官格·贵气盈门",
        "偏财格·损根破格",
        "正印格·文华显耀",
        "食神格·福禄双全",
        "七杀格·威震四方",
        "伤官格·才华横溢",
        "偏印格·智谋深远",
        "正财格·稳中求进",
        "劫财格·起伏跌宕",
        "比肩格·同气连枝"
    ]
    
    PATTERN_DESCRIPTIONS = [
        "起起伏伏坚韧如你，独自向前的你好似那孤胆英雄，总有一天能突破重围。",
        "沉稳内敛是你的特质，不急不躁，终将迎来属于你的辉煌时刻。",
        "天生聪慧，悟性极高，善于在困境中寻找出路，前途不可限量。",
        "性格刚毅，不服输的精神让你在逆境中更显锋芒。",
        "温和谦逊，人缘极佳，贵人相助让你一路顺遂。",
        "创意无限，思维活跃，独特的视角让你脱颖而出。",
        "稳重踏实，一步一个脚印，最终必能登顶高峰。",
        "命途多舛却从不言弃，坚韧的意志是你最大的财富。",
        "天生好运，常有意外之喜，但也需脚踏实地。",
        "独立自主，不依赖他人，靠自己的双手创造未来。"
    ]
    
    # 大运评语库
    FORTUNE_TAGS = [
        "智慧通达 德才并举",
        "根深叶茂 贵人垂青",
        "福泽绵长 贵人护业",
        "捷足先登 气贯长虹",
        "安守本心 心宽事顺",
        "韬光养晦 厚积薄发",
        "柳暗花明 豁然开朗",
        "乘风破浪 扬帆起航",
        "稳中求进 渐入佳境",
        "否极泰来 转危为安"
    ]
    
    def __init__(self, birth_date, gender='male'):
        """
        初始化计算器
        
        Args:
            birth_date: datetime 对象，出生日期
            gender: 性别，'male' 或 'female'
        """
        self.birth_date = birth_date
        self.gender = gender
        self.year_ganzhi = None
        self.month_ganzhi = None
        self.day_ganzhi = None
        self.hour_ganzhi = None
        self.day_master = None  # 日主（日干）
        self.day_master_element = None  # 日主五行
        
    def calculate(self):
        """
        执行完整的命理计算
        
        Returns:
            dict: 包含所有命理分析结果的字典
        """
        # 计算八字
        bazi = self._calculate_bazi()
        
        # 计算五行占比
        five_elements = self._calculate_five_elements(bazi)
        
        # 判断身强身弱
        body_type = self._determine_body_type(five_elements)
        
        # 计算喜用神
        lucky = self._calculate_lucky_elements(five_elements, body_type)
        
        # 计算格局
        pattern = self._determine_pattern(bazi, five_elements)
        
        # 计算十神
        shishen = self._calculate_shishen(bazi)
        
        # 计算神煞
        shensha = self._calculate_shensha(bazi)
        
        # 计算大运
        fortune_periods = self.calculate_fortune_periods()
        
        # 计算适配信息
        match = self._calculate_match(five_elements, body_type)
        
        return {
            'bazi': bazi,
            'five_elements': five_elements,
            'body_type': body_type,
            'lucky': lucky,
            'pattern': pattern,
            'shishen': shishen,
            'shensha': shensha,
            'fortune_periods': fortune_periods,
            'match': match,
            'day_zhi': bazi['day_zhi'],
            'day_shishen': self._get_day_shishen(bazi)
        }
    
    def _calculate_bazi(self):
        """
        计算八字（四柱）
        
        Returns:
            dict: 包含年、月、日、时四柱的天干地支
        """
        year = self.birth_date.year
        month = self.birth_date.month
        day = self.birth_date.day
        hour = self.birth_date.hour
        
        # 计算年柱
        year_gan_idx = (year - 4) % 10
        year_zhi_idx = (year - 4) % 12
        year_gan = self.TIAN_GAN[year_gan_idx]
        year_zhi = self.DI_ZHI[year_zhi_idx]
        
        # 计算月柱（简化计算）
        month_gan_idx = (year * 12 + month + 13) % 10
        month_zhi_idx = (month + 1) % 12
        month_gan = self.TIAN_GAN[month_gan_idx]
        month_zhi = self.DI_ZHI[month_zhi_idx]
        
        # 计算日柱（使用简化公式）
        base_date = datetime(1900, 1, 31)  # 基准日：庚子日
        days_diff = (self.birth_date - base_date).days
        day_gan_idx = days_diff % 10
        day_zhi_idx = days_diff % 12
        day_gan = self.TIAN_GAN[day_gan_idx]
        day_zhi = self.DI_ZHI[day_zhi_idx]
        
        # 计算时柱
        hour_zhi_idx = ((hour + 1) // 2) % 12
        hour_zhi = self.DI_ZHI[hour_zhi_idx]
        # 时干根据日干推算
        day_gan_value = self.TIAN_GAN.index(day_gan)
        hour_gan_idx = (day_gan_value % 5 * 2 + hour_zhi_idx) % 10
        hour_gan = self.TIAN_GAN[hour_gan_idx]
        
        # 保存日主信息
        self.day_master = day_gan
        self.day_master_element = self.TIAN_GAN_WUXING[day_gan]
        
        self.year_ganzhi = year_gan + year_zhi
        self.month_ganzhi = month_gan + month_zhi
        self.day_ganzhi = day_gan + day_zhi
        self.hour_ganzhi = hour_gan + hour_zhi
        
        return {
            'year_gan': year_gan,
            'year_zhi': year_zhi,
            'month_gan': month_gan,
            'month_zhi': month_zhi,
            'day_gan': day_gan,
            'day_zhi': day_zhi,
            'hour_gan': hour_gan,
            'hour_zhi': hour_zhi,
            'year_ganzhi': year_gan + year_zhi,
            'month_ganzhi': month_gan + month_zhi,
            'day_ganzhi': day_gan + day_zhi,
            'hour_ganzhi': hour_gan + hour_zhi
        }
    
    def _calculate_five_elements(self, bazi):
        """
        计算五行占比
        
        Args:
            bazi: 八字信息
            
        Returns:
            dict: 五行占比及十神对应
        """
        elements_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        
        # 统计天干五行
        for key in ['year_gan', 'month_gan', 'day_gan', 'hour_gan']:
            element = self.TIAN_GAN_WUXING[bazi[key]]
            elements_count[element] += 1
        
        # 统计地支五行
        for key in ['year_zhi', 'month_zhi', 'day_zhi', 'hour_zhi']:
            element = self.DI_ZHI_WUXING[bazi[key]]
            elements_count[element] += 1
            # 考虑藏干
            cang_gan = self.DI_ZHI_CANG_GAN[bazi[key]]
            for gan in cang_gan:
                elements_count[self.TIAN_GAN_WUXING[gan]] += 0.3
        
        # 计算百分比
        total = sum(elements_count.values())
        percentages = {k: round(v / total * 100, 1) for k, v in elements_count.items()}
        
        # 根据日主五行确定十神名称
        day_element = self.day_master_element
        
        # 计算十神对应关系
        shishen_names = self._get_shishen_names(day_element)
        
        return {
            'wood': percentages['木'],
            'fire': percentages['火'],
            'earth': percentages['土'],
            'metal': percentages['金'],
            'water': percentages['水'],
            'wood_cai': shishen_names.get('木', '偏财正财'),
            'fire_guan': shishen_names.get('火', '七杀正官'),
            'water_shi': shishen_names.get('水', '食神伤官'),
            'metal_bi': shishen_names.get('金', '比肩劫财'),
            'earth_yin': shishen_names.get('土', '偏印正印'),
            'raw_count': elements_count
        }
    
    def _get_shishen_names(self, day_element):
        """
        根据日主五行获取其他五行的十神名称
        """
        element_order = ['木', '火', '土', '金', '水']
        day_idx = element_order.index(day_element)
        
        names = {}
        for i, element in enumerate(element_order):
            diff = (i - day_idx) % 5
            if diff == 0:
                names[element] = '比肩劫财'
            elif diff == 1:
                names[element] = '食神伤官'
            elif diff == 2:
                names[element] = '偏财正财'
            elif diff == 3:
                names[element] = '七杀正官'
            else:
                names[element] = '偏印正印'
        
        return names
    
    def _determine_body_type(self, five_elements):
        """
        判断身强身弱
        
        Args:
            five_elements: 五行信息
            
        Returns:
            str: '身强型' 或 '身弱型'
        """
        day_element = self.day_master_element
        
        # 获取同党（比肩、劫财、正印、偏印）的力量
        same_party = five_elements['raw_count'].get(day_element, 0)
        
        # 获取生我者（印星）的力量
        sheng_wo = [k for k, v in self.WUXING_SHENG.items() if v == day_element]
        for element in sheng_wo:
            same_party += five_elements['raw_count'].get(element, 0) * 0.5
        
        # 简单判断：同党力量大于某个阈值则为身强
        total = sum(five_elements['raw_count'].values())
        
        if same_party / total > 0.35:
            return '身强型'
        else:
            return '身弱型'
    
    def _get_wuxing_mapping(self):
        """
        从数据库获取五行映射配置
        
        Returns:
            dict: 五行映射配置（颜色、方向、数字）
        """
        if DB_AVAILABLE:
            return config_service.get_config('wuxing_mapping')
        
        # 默认配置
        return {
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
        }
    
    def _calculate_lucky_elements(self, five_elements, body_type):
        """
        计算喜用神
        
        Args:
            five_elements: 五行信息
            body_type: 身强身弱
            
        Returns:
            dict: 喜用神信息
        """
        day_element = self.day_master_element
        
        # 根据身强身弱确定喜用神
        if body_type == '身强型':
            # 身强喜克泄耗
            wo_sheng = self.WUXING_SHENG[day_element]  # 我生
            ke_wo = [k for k, v in self.WUXING_KE.items() if v == day_element][0]  # 克我
            wo_ke = self.WUXING_KE[day_element]  # 我克
            lucky_elements = [wo_sheng, ke_wo, wo_ke]
        else:
            # 身弱喜生扶
            sheng_wo = [k for k, v in self.WUXING_SHENG.items() if v == day_element][0]  # 生我
            lucky_elements = [sheng_wo, day_element]
        
        # 去重
        lucky_elements = list(set(lucky_elements))[:2]
        
        # 从数据库获取五行映射配置
        wuxing_mapping = self._get_wuxing_mapping()
        
        element_colors = wuxing_mapping.get('colors', {})
        element_directions = wuxing_mapping.get('directions', {})
        element_numbers = wuxing_mapping.get('numbers', {})
        
        lucky_colors = []
        lucky_directions = []
        lucky_numbers = []
        
        for element in lucky_elements:
            lucky_colors.extend(element_colors.get(element, [{'name': '白色', 'colorClass': 'bg-white'}]))
            lucky_directions.extend(element_directions.get(element, []))
            lucky_numbers.extend(element_numbers.get(element, []))
        
        # 限制数量
        lucky_colors = lucky_colors[:3]
        lucky_directions = lucky_directions[:3]
        lucky_numbers = lucky_numbers[:3]
        
        element_names = '、'.join(lucky_elements)
        
        return {
            'title': f'【喜用{element_names}】',
            'labels': {
                'luckyColor': '幸运颜色',
                'luckyDirection': '幸运方向',
                'luckyNumber': '幸运数字'
            },
            'luckyColors': lucky_colors,
            'luckyDirections': lucky_directions,
            'luckyNumbers': lucky_numbers
        }
    
    def _get_pattern_config(self):
        """
        从数据库获取格局配置
        
        Returns:
            dict: 格局模板配置
        """
        if DB_AVAILABLE:
            return config_service.get_config('pattern')
        
        # 默认配置
        return {
            'templates': [
                {'title': '【乘风破浪】', 'pattern': '正官格·贵气盈门', 'description': '正气凛然，贵人相助，事业顺遂。'},
                {'title': '【厚积薄发】', 'pattern': '正印格·文华显耀', 'description': '学识渊博，智慧超群，文运亨通。'},
                {'title': '【柳暗花明】', 'pattern': '偏财格·财源广进', 'description': '财运亨通，投资有道，收益丰厚。'},
                {'title': '【逆流而上】', 'pattern': '七杀格·威震四方', 'description': '意志坚定，勇往直前，成就非凡。'},
                {'title': '【静待花开】', 'pattern': '食神格·福禄双全', 'description': '生活安逸，福禄兼得，晚年享福。'}
            ]
        }
    
    def _determine_pattern(self, bazi, five_elements):
        """
        判断命格格局
        
        Args:
            bazi: 八字信息
            five_elements: 五行信息
            
        Returns:
            dict: 格局信息
        """
        # 基于出生信息生成确定性的随机选择
        seed = hash(f"{bazi['year_ganzhi']}{bazi['month_ganzhi']}{bazi['day_ganzhi']}") % 1000
        random.seed(seed)
        
        # 从数据库获取格局模板
        pattern_config = self._get_pattern_config()
        templates = pattern_config.get('templates', [])
        
        if templates:
            # 使用数据库中的模板
            idx = seed % len(templates)
            template = templates[idx]
            return {
                'title': template.get('title', self.PATTERN_TITLES[0]),
                'pattern': template.get('pattern', self.PATTERN_TYPES[0]),
                'description': template.get('description', self.PATTERN_DESCRIPTIONS[0])
            }
        
        # 回退到默认配置
        title_idx = seed % len(self.PATTERN_TITLES)
        type_idx = (seed // 10) % len(self.PATTERN_TYPES)
        desc_idx = (seed // 100) % len(self.PATTERN_DESCRIPTIONS)
        
        return {
            'title': self.PATTERN_TITLES[title_idx],
            'pattern': self.PATTERN_TYPES[type_idx],
            'description': self.PATTERN_DESCRIPTIONS[desc_idx]
        }
    
    def _calculate_shishen(self, bazi):
        """
        计算十神占比
        """
        shishen_count = {
            '正官': 0, '七杀': 0, '正财': 0, '偏财': 0,
            '食神': 0, '伤官': 0, '正印': 0, '偏印': 0,
            '比肩': 0, '劫财': 0
        }
        
        day_gan = bazi['day_gan']
        day_element = self.TIAN_GAN_WUXING[day_gan]
        day_yin_yang = self.TIAN_GAN.index(day_gan) % 2  # 0为阳，1为阴
        
        # 分析其他干支的十神
        for key in ['year_gan', 'month_gan', 'hour_gan']:
            gan = bazi[key]
            element = self.TIAN_GAN_WUXING[gan]
            yin_yang = self.TIAN_GAN.index(gan) % 2
            shishen = self._get_shishen(day_element, element, day_yin_yang == yin_yang)
            if shishen in shishen_count:
                shishen_count[shishen] += 1
        
        # 地支藏干分析
        for key in ['year_zhi', 'month_zhi', 'hour_zhi']:
            zhi = bazi[key]
            cang_gan = self.DI_ZHI_CANG_GAN[zhi]
            for i, gan in enumerate(cang_gan):
                element = self.TIAN_GAN_WUXING[gan]
                yin_yang = self.TIAN_GAN.index(gan) % 2
                shishen = self._get_shishen(day_element, element, day_yin_yang == yin_yang)
                weight = 1.0 if i == 0 else 0.3
                if shishen in shishen_count:
                    shishen_count[shishen] += weight
        
        # 计算百分比
        total = sum(shishen_count.values())
        shishen_data = [round(shishen_count[k] / total * 100, 1) for k in 
                       ['正官', '七杀', '正财', '偏财', '食神', '伤官', '正印', '偏印', '比肩', '劫财']]
        
        return {
            'title': '十神占比',
            'chartTitle': '十神占比',
            'labels': ['正官', '七杀', '正财', '偏财', '食神', '伤官', '正印', '偏印', '比肩', '劫财'],
            'data': shishen_data,
            'colors': ['#F8C4C4', '#E8A0A0', '#C9A66B', '#B89565', '#A8D8EA', '#98C8DA', '#F5E6CC', '#E5D6BC', '#D4A574', '#C49564']
        }
    
    def _get_shishen(self, day_element, other_element, same_yinyang):
        """
        根据日主五行和其他五行获取十神
        """
        element_order = ['木', '火', '土', '金', '水']
        day_idx = element_order.index(day_element)
        other_idx = element_order.index(other_element)
        
        diff = (other_idx - day_idx) % 5
        
        if diff == 0:
            return '比肩' if same_yinyang else '劫财'
        elif diff == 1:
            return '食神' if same_yinyang else '伤官'
        elif diff == 2:
            return '偏财' if same_yinyang else '正财'
        elif diff == 3:
            return '七杀' if same_yinyang else '正官'
        else:  # diff == 4
            return '偏印' if same_yinyang else '正印'
    
    def _get_shensha_config(self):
        """
        从数据库获取神煞配置
        
        Returns:
            dict: 神煞配置
        """
        if DB_AVAILABLE:
            return config_service.get_config('shensha_config')
        
        # 默认配置
        return {
            'items': [
                {'name': '贵人相助', 'description': '天乙贵人、福星贵人', 'icon': 'fa-star', 'iconBg': 'bg-orange-100', 'iconColor': 'text-orange-500'},
                {'name': '慧根发达', 'description': '太极贵人', 'icon': 'fa-brain', 'iconBg': 'bg-blue-100', 'iconColor': 'text-blue-500'},
                {'name': '张力满满', 'description': '桃花', 'icon': 'fa-heart', 'iconBg': 'bg-yellow-100', 'iconColor': 'text-yellow-500'},
                {'name': '天选领导', 'description': '禄神', 'icon': 'fa-crown', 'iconBg': 'bg-pink-100', 'iconColor': 'text-pink-500'},
                {'name': '旷世奇才', 'description': '学堂', 'icon': 'fa-graduation-cap', 'iconBg': 'bg-sky-100', 'iconColor': 'text-sky-500'}
            ]
        }
    
    def _calculate_shensha(self, bazi):
        """
        计算神煞
        
        Args:
            bazi: 八字信息
            
        Returns:
            dict: 神煞信息
        """
        # 从数据库获取神煞配置
        shensha_config = self._get_shensha_config()
        config_items = shensha_config.get('items', [])
        
        items = []
        
        # 天乙贵人
        tianyi_guis = self._get_tianyi_gui(bazi['day_gan'])
        if tianyi_guis:
            # 从配置中查找对应的神煞项
            gui_item = next((item for item in config_items if '贵人' in item.get('name', '')), None)
            if gui_item:
                items.append(gui_item)
            else:
                items.append({
                    'name': '贵人相助',
                    'description': '天乙贵人、福星贵人',
                    'icon': 'fa-star',
                    'iconBg': 'bg-orange-100',
                    'iconColor': 'text-orange-500'
                })
        
        # 太极贵人
        taiji_item = next((item for item in config_items if '慧根' in item.get('name', '')), None)
        if taiji_item:
            items.append(taiji_item)
        else:
            items.append({
                'name': '慧根发达',
                'description': '太极贵人',
                'icon': 'fa-brain',
                'iconBg': 'bg-blue-100',
                'iconColor': 'text-blue-500'
            })
        
        # 桃花
        taohua = self._get_taohua(bazi)
        if taohua:
            taohua_item = next((item for item in config_items if '桃花' in item.get('description', '')), None)
            if taohua_item:
                items.append(taohua_item)
            else:
                items.append({
                    'name': '张力满满',
                    'description': '桃花',
                    'icon': 'fa-heart',
                    'iconBg': 'bg-yellow-100',
                    'iconColor': 'text-yellow-500'
                })
        
        # 禄神
        lu_item = next((item for item in config_items if '禄神' in item.get('description', '')), None)
        if lu_item:
            items.append(lu_item)
        else:
            items.append({
                'name': '天选领导',
                'description': '禄神',
                'icon': 'fa-crown',
                'iconBg': 'bg-pink-100',
                'iconColor': 'text-pink-500'
            })
        
        # 学堂
        xuetang_item = next((item for item in config_items if '学堂' in item.get('description', '')), None)
        if xuetang_item:
            items.append(xuetang_item)
        else:
            items.append({
                'name': '旷世奇才',
                'description': '学堂',
                'icon': 'fa-graduation-cap',
                'iconBg': 'bg-sky-100',
                'iconColor': 'text-sky-500'
            })
        
        return {
            'title': '神煞解析',
            'items': items
        }
    
    def _get_tianyi_gui(self, day_gan):
        """
        获取天乙贵人
        """
        tianyi_map = {
            '甲': ['丑', '未'],
            '乙': ['子', '申'],
            '丙': ['亥', '酉'],
            '丁': ['亥', '酉'],
            '戊': ['丑', '未'],
            '己': ['子', '申'],
            '庚': ['丑', '未'],
            '辛': ['寅', '午'],
            '壬': ['卯', '巳'],
            '癸': ['卯', '巳']
        }
        return tianyi_map.get(day_gan, [])
    
    def _get_taohua(self, bazi):
        """
        获取桃花
        """
        taohua_map = {
            '寅': '卯', '午': '卯', '戌': '卯',
            '申': '酉', '子': '酉', '辰': '酉',
            '巳': '午', '酉': '午', '丑': '午',
            '亥': '子', '卯': '子', '未': '子'
        }
        return taohua_map.get(bazi['year_zhi'], '')
    
    def _get_industry_mapping(self):
        """
        从数据库获取行业映射配置
        
        Returns:
            dict: 行业映射配置
        """
        if DB_AVAILABLE:
            return config_service.get_config('industry_mapping')
        
        # 默认配置
        return {
            'industries': {
                '木': '文化教育、医疗卫生、艺术设计、农林牧渔',
                '火': '电子科技、餐饮娱乐、照明电力、美容美发',
                '土': '房地产、建筑工程、农业种植、政府部门',
                '金': '金融投资、法律咨询、机械制造、珠宝首饰',
                '水': '物流运输、旅游酒店、饮料饮品、水产养殖'
            }
        }
    
    def _get_fortune_tags(self):
        """
        从数据库获取大运评语配置
        
        Returns:
            dict: 大运评语配置
        """
        if DB_AVAILABLE:
            return config_service.get_config('fortune_tags')
        
        # 默认配置
        return {
            'tags': [
                {'score_range': [90, 100], 'tags': ['智慧通达 德才并举', '福星高照 万事如意', '鹏程万里 前程似锦']},
                {'score_range': [80, 89], 'tags': ['根深叶茂 贵人垂青', '福泽绵长 贵人护业', '鸿运当头 吉星拱照']},
                {'score_range': [70, 79], 'tags': ['稳中求进 渐入佳境', '安守本心 心宽事顺', '柳暗花明 豁然开朗']},
                {'score_range': [60, 69], 'tags': ['韬光养晦 厚积薄发', '稳扎稳打 步步为营', '循序渐进 稳中求胜']},
                {'score_range': [0, 59], 'tags': ['否极泰来 转危为安', '韬光养晦 等待时机', '收敛低调 蓄势待发']}
            ]
        }
    
    def _get_fortune_tag_by_score(self, score, seed):
        """
        根据评分获取大运评语
        
        Args:
            score: 评分
            seed: 随机种子
        
        Returns:
            str: 大运评语
        """
        fortune_config = self._get_fortune_tags()
        tags_list = fortune_config.get('tags', [])
        
        # 根据评分查找对应的评语组
        for tag_group in tags_list:
            score_range = tag_group.get('score_range', [0, 100])
            if score_range[0] <= score <= score_range[1]:
                tags = tag_group.get('tags', [])
                if tags:
                    idx = seed % len(tags)
                    return tags[idx]
        
        # 回退到默认评语
        idx = seed % len(self.FORTUNE_TAGS)
        return self.FORTUNE_TAGS[idx]
    
    def calculate_fortune_periods(self):
        """
        计算大运周期
        
        Returns:
            list: 大运周期列表
        """
        # 基于出生日期生成确定性的大运
        seed = hash(f"{self.birth_date.year}{self.birth_date.month}{self.birth_date.day}") % 1000
        random.seed(seed)
        
        # 计算起运年龄（简化为10-20岁之间）
        start_age = 10 + (seed % 10)
        
        periods = []
        gan_idx = self.TIAN_GAN.index(self.day_master) if self.day_master else 0
        zhi_idx = seed % 12
        
        for i in range(6):
            age_start = start_age + i * 10
            age_end = age_start + 9
            age_str = f"{age_start}-{age_end}岁"
            
            # 大运干支
            fortune_gan = self.TIAN_GAN[(gan_idx + i + 1) % 10]
            fortune_zhi = self.DI_ZHI[(zhi_idx + i + 1) % 12]
            stem_branch = fortune_gan + fortune_zhi
            
            # 评分（基于某些规则生成）
            score = 50 + random.randint(0, 50)
            
            # 从数据库获取评语
            tag = self._get_fortune_tag_by_score(score, seed + i * 7)
            
            periods.append({
                'age': age_str,
                'stemBranch': stem_branch,
                'tag': tag,
                'score': score
            })
        
        return periods
    
    def _calculate_match(self, five_elements, body_type):
        """
        计算适配匹配
        """
        day_element = self.day_master_element
        
        # 从数据库获取行业映射
        industry_config = self._get_industry_mapping()
        industry_map = industry_config.get('industries', {
            '木': '文化教育、医疗卫生、艺术设计、农林牧渔',
            '火': '电子科技、餐饮娱乐、照明电力、美容美发',
            '土': '房地产、建筑工程、农业种植、政府部门',
            '金': '金融投资、法律咨询、机械制造、珠宝首饰',
            '水': '物流运输、旅游酒店、饮料饮品、水产养殖'
        })
        
        # 找出最旺的五行
        elements_sorted = sorted(
            [('木', five_elements['wood']), ('火', five_elements['fire']),
             ('土', five_elements['earth']), ('金', five_elements['metal']),
             ('水', five_elements['water'])],
            key=lambda x: x[1],
            reverse=True
        )
        
        dominant_element = elements_sorted[0][0]
        
        # 配偶星五行
        spouse_element = self.WUXING_KE[day_element]  # 我克者为财（配偶星）
        
        return {
            'industry': {
                'title': '适配行业',
                'content': industry_map.get(dominant_element, '适合从事与五行属性相符的行业')
            },
            'partner': {
                'title': '匹配伴侣',
                'content': f'配偶星属{spouse_element}（日主为{day_element}/五行能量最高为{dominant_element}）'
            }
        }
    
    def _get_day_shishen(self, bazi):
        """
        获取日支对应的十神
        """
        day_element = self.TIAN_GAN_WUXING[bazi['day_gan']]
        zhi_element = self.DI_ZHI_WUXING[bazi['day_zhi']]
        same_yinyang = self.TIAN_GAN.index(bazi['day_gan']) % 2 == self.DI_ZHI.index(bazi['day_zhi']) % 2
        
        return self._get_shishen(day_element, zhi_element, same_yinyang)


# ==================== 测试代码 ====================

if __name__ == '__main__':
    # 测试计算
    test_date = datetime(1990, 5, 15, 10, 30)
    calculator = FiveElementsCalculator(test_date, 'male')
    result = calculator.calculate()
    
    print("=" * 50)
    print("赛博算命 - 测试结果")
    print("=" * 50)
    print(f"出生日期: {test_date}")
    print(f"八字: {result['bazi']['year_ganzhi']} {result['bazi']['month_ganzhi']} {result['bazi']['day_ganzhi']} {result['bazi']['hour_ganzhi']}")
    print(f"日主: {calculator.day_master} ({calculator.day_master_element})")
    print(f"身型: {result['body_type']}")
    print(f"格局: {result['pattern']['title']} - {result['pattern']['pattern']}")
    print(f"五行占比: 木{result['five_elements']['wood']}% 火{result['five_elements']['fire']}% 土{result['five_elements']['earth']}% 金{result['five_elements']['metal']}% 水{result['five_elements']['water']}%")
    print("=" * 50)