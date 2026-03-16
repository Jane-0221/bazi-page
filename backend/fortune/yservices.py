"""
赛博算命 - 业务服务层
封装核心业务逻辑
"""

import random
import logging
from datetime import datetime

logger = logging.getLogger('fortune')


class FiveElementsCalculator:
    """
    五行命理计算器
    根据出生日期计算八字、五行、大运、神煞等信息
    支持从数据库读取配置数据
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
    
    # 五行相生相克
    WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    WUXING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
    
    # 默认格局描述库
    PATTERN_TITLES = [
        "【乘风破浪】", "【厚积薄发】", "【柳暗花明】", "【逆流而上】",
        "【静待花开】", "【破茧成蝶】", "【浴火重生】", "【踏雪寻梅】",
        "【云开见日】", "【这点痛算什么】"
    ]
    
    PATTERN_TYPES = [
        "正官格·贵气盈门", "偏财格·损根破格", "正印格·文华显耀",
        "食神格·福禄双全", "七杀格·威震四方", "伤官格·才华横溢",
        "偏印格·智谋深远", "正财格·稳中求进", "劫财格·起伏跌宕",
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
    
    FORTUNE_TAGS = [
        "智慧通达 德才并举", "根深叶茂 贵人垂青", "福泽绵长 贵人护业",
        "捷足先登 气贯长虹", "安守本心 心宽事顺", "韬光养晦 厚积薄发",
        "柳暗花明 豁然开朗", "乘风破浪 扬帆起航", "稳中求进 渐入佳境",
        "否极泰来 转危为安"
    ]
    
    def __init__(self, birth_date, gender='male'):
        """
        初始化计算器
        
        Args:
            birth_date: datetime 对象或日期字符串，出生日期
            gender: 性别，'male' 或 'female'
        """
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
        
        # 如果只有日期没有时间，转换为 datetime
        if hasattr(birth_date, 'hour'):
            self.birth_date = birth_date
        else:
            # date 对象转换为 datetime，默认小时为 12
            self.birth_date = datetime(birth_date.year, birth_date.month, birth_date.day, 12)
        self.gender = gender
        self.day_master = None
        self.day_master_element = None
    
    def calculate(self):
        """执行完整的命理计算"""
        bazi = self._calculate_bazi()
        five_elements = self._calculate_five_elements(bazi)
        body_type = self._determine_body_type(five_elements)
        lucky = self._calculate_lucky_elements(five_elements, body_type)
        pattern = self._determine_pattern(bazi, five_elements)
        shishen = self._calculate_shishen(bazi)
        shensha = self._calculate_shensha(bazi)
        fortune_periods = self.calculate_fortune_periods()
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
        """计算八字（四柱）"""
        year = self.birth_date.year
        month = self.birth_date.month
        day = self.birth_date.day
        hour = self.birth_date.hour
        
        # 年柱
        year_gan = self.TIAN_GAN[(year - 4) % 10]
        year_zhi = self.DI_ZHI[(year - 4) % 12]
        
        # 月柱
        month_gan = self.TIAN_GAN[(year * 12 + month + 13) % 10]
        month_zhi = self.DI_ZHI[(month + 1) % 12]
        
        # 日柱
        base_date = datetime(1900, 1, 31)
        days_diff = (self.birth_date - base_date).days
        day_gan = self.TIAN_GAN[days_diff % 10]
        day_zhi = self.DI_ZHI[days_diff % 12]
        
        # 时柱
        hour_zhi_idx = ((hour + 1) // 2) % 12
        hour_zhi = self.DI_ZHI[hour_zhi_idx]
        day_gan_value = self.TIAN_GAN.index(day_gan)
        hour_gan = self.TIAN_GAN[(day_gan_value % 5 * 2 + hour_zhi_idx) % 10]
        
        self.day_master = day_gan
        self.day_master_element = self.TIAN_GAN_WUXING[day_gan]
        
        return {
            'year_gan': year_gan, 'year_zhi': year_zhi,
            'month_gan': month_gan, 'month_zhi': month_zhi,
            'day_gan': day_gan, 'day_zhi': day_zhi,
            'hour_gan': hour_gan, 'hour_zhi': hour_zhi,
            'year_ganzhi': year_gan + year_zhi,
            'month_ganzhi': month_gan + month_zhi,
            'day_ganzhi': day_gan + day_zhi,
            'hour_ganzhi': hour_gan + hour_zhi
        }
    
    def _calculate_five_elements(self, bazi):
        """计算五行占比"""
        elements_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        
        for key in ['year_gan', 'month_gan', 'day_gan', 'hour_gan']:
            element = self.TIAN_GAN_WUXING[bazi[key]]
            elements_count[element] += 1
        
        for key in ['year_zhi', 'month_zhi', 'day_zhi', 'hour_zhi']:
            element = self.DI_ZHI_WUXING[bazi[key]]
            elements_count[element] += 1
            for gan in self.DI_ZHI_CANG_GAN[bazi[key]]:
                elements_count[self.TIAN_GAN_WUXING[gan]] += 0.3
        
        total = sum(elements_count.values())
        percentages = {k: round(v / total * 100, 1) for k, v in elements_count.items()}
        shishen_names = self._get_shishen_names(self.day_master_element)
        
        return {
            'wood': percentages['木'], 'fire': percentages['火'],
            'earth': percentages['土'], 'metal': percentages['金'],
            'water': percentages['水'],
            'wood_cai': shishen_names.get('木', '偏财正财'),
            'fire_guan': shishen_names.get('火', '七杀正官'),
            'water_shi': shishen_names.get('水', '食神伤官'),
            'metal_bi': shishen_names.get('金', '比肩劫财'),
            'earth_yin': shishen_names.get('土', '偏印正印'),
            'raw_count': elements_count
        }
    
    def _get_shishen_names(self, day_element):
        """根据日主五行获取其他五行的十神名称"""
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
        """判断身强身弱"""
        day_element = self.day_master_element
        same_party = five_elements['raw_count'].get(day_element, 0)
        
        sheng_wo = [k for k, v in self.WUXING_SHENG.items() if v == day_element]
        for element in sheng_wo:
            same_party += five_elements['raw_count'].get(element, 0) * 0.5
        
        total = sum(five_elements['raw_count'].values())
        return '身强型' if same_party / total > 0.35 else '身弱型'
    
    def _get_wuxing_mapping(self):
        """从数据库获取五行映射配置"""
        try:
            from .models import Config
            config = Config.objects(type='wuxing_mapping').first()
            if config:
                return config.data
        except:
            pass
        
        return {
            'colors': {
                '木': [{'name': '绿色', 'colorClass': 'bg-green-200'}, {'name': '青色', 'colorClass': 'bg-cyan-200'}],
                '火': [{'name': '红色', 'colorClass': 'bg-red-200'}, {'name': '粉色', 'colorClass': 'bg-pink-200'}],
                '土': [{'name': '黄色', 'colorClass': 'bg-luckyEarth'}, {'name': '棕色', 'colorClass': 'bg-amber-200'}],
                '金': [{'name': '白色', 'colorClass': 'bg-luckyMetal'}, {'name': '金色', 'colorClass': 'bg-yellow-100'}],
                '水': [{'name': '黑色', 'colorClass': 'bg-gray-300'}, {'name': '蓝色', 'colorClass': 'bg-blue-200'}]
            },
            'directions': {'木': ['正东', '东南'], '火': ['正南'], '土': ['家乡', '中部'], '金': ['正西', '西北'], '水': ['正北']},
            'numbers': {'木': ['3', '8'], '火': ['2', '7'], '土': ['5', '10'], '金': ['4', '9'], '水': ['1', '6']}
        }
    
    def _calculate_lucky_elements(self, five_elements, body_type):
        """计算喜用神"""
        day_element = self.day_master_element
        
        if body_type == '身强型':
            wo_sheng = self.WUXING_SHENG[day_element]
            ke_wo = [k for k, v in self.WUXING_KE.items() if v == day_element][0]
            wo_ke = self.WUXING_KE[day_element]
            lucky_elements = [wo_sheng, ke_wo, wo_ke]
        else:
            sheng_wo = [k for k, v in self.WUXING_SHENG.items() if v == day_element][0]
            lucky_elements = [sheng_wo, day_element]
        
        lucky_elements = list(set(lucky_elements))[:2]
        wuxing_mapping = self._get_wuxing_mapping()
        
        element_colors = wuxing_mapping.get('colors', {})
        element_directions = wuxing_mapping.get('directions', {})
        element_numbers = wuxing_mapping.get('numbers', {})
        
        lucky_colors, lucky_directions, lucky_numbers = [], [], []
        
        for element in lucky_elements:
            lucky_colors.extend(element_colors.get(element, [{'name': '白色', 'colorClass': 'bg-white'}]))
            lucky_directions.extend(element_directions.get(element, []))
            lucky_numbers.extend(element_numbers.get(element, []))
        
        return {
            'title': f'【喜用{"、".join(lucky_elements)}】',
            'labels': {'luckyColor': '幸运颜色', 'luckyDirection': '幸运方向', 'luckyNumber': '幸运数字'},
            'luckyColors': lucky_colors[:3],
            'luckyDirections': lucky_directions[:3],
            'luckyNumbers': lucky_numbers[:3]
        }
    
    def _get_pattern_config(self):
        """从数据库获取格局配置"""
        try:
            from .models import Config
            config = Config.objects(type='pattern').first()
            if config:
                return config.data
        except:
            pass
        return {'templates': []}
    
    def _determine_pattern(self, bazi, five_elements):
        """判断命格格局"""
        seed = hash(f"{bazi['year_ganzhi']}{bazi['month_ganzhi']}{bazi['day_ganzhi']}") % 1000
        random.seed(seed)
        
        pattern_config = self._get_pattern_config()
        templates = pattern_config.get('templates', [])
        
        if templates:
            idx = seed % len(templates)
            template = templates[idx]
            return {
                'title': template.get('title', self.PATTERN_TITLES[0]),
                'pattern': template.get('pattern', self.PATTERN_TYPES[0]),
                'description': template.get('description', self.PATTERN_DESCRIPTIONS[0])
            }
        
        return {
            'title': self.PATTERN_TITLES[seed % len(self.PATTERN_TITLES)],
            'pattern': self.PATTERN_TYPES[(seed // 10) % len(self.PATTERN_TYPES)],
            'description': self.PATTERN_DESCRIPTIONS[(seed // 100) % len(self.PATTERN_DESCRIPTIONS)]
        }
    
    def _calculate_shishen(self, bazi):
        """计算十神占比"""
        shishen_count = dict.fromkeys(['正官', '七杀', '正财', '偏财', '食神', '伤官', '正印', '偏印', '比肩', '劫财'], 0)
        
        day_gan = bazi['day_gan']
        day_element = self.TIAN_GAN_WUXING[day_gan]
        day_yin_yang = self.TIAN_GAN.index(day_gan) % 2
        
        for key in ['year_gan', 'month_gan', 'hour_gan']:
            gan = bazi[key]
            element = self.TIAN_GAN_WUXING[gan]
            yin_yang = self.TIAN_GAN.index(gan) % 2
            shishen = self._get_shishen(day_element, element, day_yin_yang == yin_yang)
            if shishen in shishen_count:
                shishen_count[shishen] += 1
        
        for key in ['year_zhi', 'month_zhi', 'hour_zhi']:
            zhi = bazi[key]
            for i, gan in enumerate(self.DI_ZHI_CANG_GAN[zhi]):
                element = self.TIAN_GAN_WUXING[gan]
                yin_yang = self.TIAN_GAN.index(gan) % 2
                shishen = self._get_shishen(day_element, element, day_yin_yang == yin_yang)
                weight = 1.0 if i == 0 else 0.3
                if shishen in shishen_count:
                    shishen_count[shishen] += weight
        
        total = sum(shishen_count.values())
        shishen_data = [round(shishen_count[k] / total * 100, 1) for k in shishen_count.keys()]
        
        return {
            'title': '十神占比',
            'chartTitle': '十神占比',
            'labels': list(shishen_count.keys()),
            'data': shishen_data,
            'colors': ['#F8C4C4', '#E8A0A0', '#C9A66B', '#B89565', '#A8D8EA', '#98C8DA', '#F5E6CC', '#E5D6BC', '#D4A574', '#C49564']
        }
    
    def _get_shishen(self, day_element, other_element, same_yinyang):
        """根据日主五行和其他五行获取十神"""
        element_order = ['木', '火', '土', '金', '水']
        diff = (element_order.index(other_element) - element_order.index(day_element)) % 5
        
        if diff == 0:
            return '比肩' if same_yinyang else '劫财'
        elif diff == 1:
            return '食神' if same_yinyang else '伤官'
        elif diff == 2:
            return '偏财' if same_yinyang else '正财'
        elif diff == 3:
            return '七杀' if same_yinyang else '正官'
        else:
            return '偏印' if same_yinyang else '正印'
    
    def _get_shensha_config(self):
        """从数据库获取神煞配置"""
        try:
            from .models import Config
            config = Config.objects(type='shensha_config').first()
            if config:
                return config.data
        except:
            pass
        return {'items': []}
    
    def _calculate_shensha(self, bazi):
        """计算神煞"""
        shensha_config = self._get_shensha_config()
        config_items = shensha_config.get('items', [])
        items = []
        
        # 天乙贵人
        tianyi_guis = self._get_tianyi_gui(bazi['day_gan'])
        if tianyi_guis:
            gui_item = next((item for item in config_items if '贵人' in item.get('name', '')), None)
            items.append(gui_item if gui_item else {'name': '贵人相助', 'description': '天乙贵人、福星贵人', 'icon': 'fa-star', 'iconBg': 'bg-orange-100', 'iconColor': 'text-orange-500'})
        
        # 太极贵人
        taiji_item = next((item for item in config_items if '慧根' in item.get('name', '')), None)
        items.append(taiji_item if taiji_item else {'name': '慧根发达', 'description': '太极贵人', 'icon': 'fa-brain', 'iconBg': 'bg-blue-100', 'iconColor': 'text-blue-500'})
        
        # 桃花
        taohua = self._get_taohua(bazi)
        if taohua:
            taohua_item = next((item for item in config_items if '桃花' in item.get('description', '')), None)
            items.append(taohua_item if taohua_item else {'name': '张力满满', 'description': '桃花', 'icon': 'fa-heart', 'iconBg': 'bg-yellow-100', 'iconColor': 'text-yellow-500'})
        
        # 禄神
        lu_item = next((item for item in config_items if '禄神' in item.get('description', '')), None)
        items.append(lu_item if lu_item else {'name': '天选领导', 'description': '禄神', 'icon': 'fa-crown', 'iconBg': 'bg-pink-100', 'iconColor': 'text-pink-500'})
        
        # 学堂
        xuetang_item = next((item for item in config_items if '学堂' in item.get('description', '')), None)
        items.append(xuetang_item if xuetang_item else {'name': '旷世奇才', 'description': '学堂', 'icon': 'fa-graduation-cap', 'iconBg': 'bg-sky-100', 'iconColor': 'text-sky-500'})
        
        return {'title': '神煞解析', 'items': items}
    
    def _get_tianyi_gui(self, day_gan):
        """获取天乙贵人"""
        tianyi_map = {
            '甲': ['丑', '未'], '乙': ['子', '申'], '丙': ['亥', '酉'], '丁': ['亥', '酉'],
            '戊': ['丑', '未'], '己': ['子', '申'], '庚': ['丑', '未'], '辛': ['寅', '午'],
            '壬': ['卯', '巳'], '癸': ['卯', '巳']
        }
        return tianyi_map.get(day_gan, [])
    
    def _get_taohua(self, bazi):
        """获取桃花"""
        taohua_map = {
            '寅': '卯', '午': '卯', '戌': '卯', '申': '酉', '子': '酉', '辰': '酉',
            '巳': '午', '酉': '午', '丑': '午', '亥': '子', '卯': '子', '未': '子'
        }
        return taohua_map.get(bazi['year_zhi'], '')
    
    def _get_fortune_tags(self):
        """从数据库获取大运评语配置"""
        try:
            from .models import Config
            config = Config.objects(type='fortune_tags').first()
            if config:
                return config.data
        except:
            pass
        return {'tags': []}
    
    def _get_fortune_tag_by_score(self, score, seed):
        """根据评分获取大运评语"""
        fortune_config = self._get_fortune_tags()
        tags_list = fortune_config.get('tags', [])
        
        for tag_group in tags_list:
            score_range = tag_group.get('score_range', [0, 100])
            if score_range[0] <= score <= score_range[1]:
                tags = tag_group.get('tags', [])
                if tags:
                    return tags[seed % len(tags)]
        
        return self.FORTUNE_TAGS[seed % len(self.FORTUNE_TAGS)]
    
    def calculate_fortune_periods(self):
        """计算大运周期"""
        seed = hash(f"{self.birth_date.year}{self.birth_date.month}{self.birth_date.day}") % 1000
        random.seed(seed)
        
        start_age = 10 + (seed % 10)
        periods = []
        gan_idx = self.TIAN_GAN.index(self.day_master) if self.day_master else 0
        zhi_idx = seed % 12
        
        for i in range(6):
            age_start = start_age + i * 10
            age_str = f"{age_start}-{age_start + 9}岁"
            
            fortune_gan = self.TIAN_GAN[(gan_idx + i + 1) % 10]
            fortune_zhi = self.DI_ZHI[(zhi_idx + i + 1) % 12]
            
            score = 50 + random.randint(0, 50)
            tag = self._get_fortune_tag_by_score(score, seed + i * 7)
            
            periods.append({
                'age': age_str,
                'stemBranch': fortune_gan + fortune_zhi,
                'tag': tag,
                'score': score
            })
        
        return periods
    
    def _get_industry_mapping(self):
        """从数据库获取行业映射配置"""
        try:
            from .models import Config
            config = Config.objects(type='industry_mapping').first()
            if config:
                return config.data
        except:
            pass
        return {
            'industries': {
                '木': '文化教育、医疗卫生、艺术设计、农林牧渔',
                '火': '电子科技、餐饮娱乐、照明电力、美容美发',
                '土': '房地产、建筑工程、农业种植、政府部门',
                '金': '金融投资、法律咨询、机械制造、珠宝首饰',
                '水': '物流运输、旅游酒店、饮料饮品、水产养殖'
            }
        }
    
    def _calculate_match(self, five_elements, body_type):
        """计算适配匹配"""
        day_element = self.day_master_element
        industry_config = self._get_industry_mapping()
        industry_map = industry_config.get('industries', {})
        
        elements_sorted = sorted(
            [('木', five_elements['wood']), ('火', five_elements['fire']),
             ('土', five_elements['earth']), ('金', five_elements['metal']),
             ('水', five_elements['water'])],
            key=lambda x: x[1], reverse=True
        )
        
        dominant_element = elements_sorted[0][0]
        spouse_element = self.WUXING_KE[day_element]
        
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
        """获取日支对应的十神"""
        day_element = self.TIAN_GAN_WUXING[bazi['day_gan']]
        zhi_element = self.DI_ZHI_WUXING[bazi['day_zhi']]
        same_yinyang = self.TIAN_GAN.index(bazi['day_gan']) % 2 == self.DI_ZHI.index(bazi['day_zhi']) % 2
        return self._get_shishen(day_element, zhi_element, same_yinyang)


# ==================== 配置服务 ====================

class ConfigService:
    """配置数据服务"""
    
    _cache = {}
    
    @classmethod
    def get_config(cls, config_type, use_cache=True):
        """获取配置数据"""
        if use_cache and config_type in cls._cache:
            return cls._cache[config_type]
        
        try:
            from .models import Config
            config = Config.objects(type=config_type).first()
            if config:
                cls._cache[config_type] = config.data
                return config.data
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
        
        return {}
    
    @classmethod
    def update_config(cls, config_type, config_name, data):
        """更新配置数据"""
        try:
            from .models import Config
            config = Config.objects(type=config_type, name=config_name).first()
            if config:
                config.data = data
                config.save()
            else:
                Config(name=config_name, type=config_type, data=data).save()
            
            # 清除缓存
            if config_type in cls._cache:
                del cls._cache[config_type]
            
            return True
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return False
    
    @classmethod
    def clear_cache(cls, config_type=None):
        """清除缓存"""
        if config_type:
            cls._cache.pop(config_type, None)
        else:
            cls._cache.clear()


# ==================== 知识库服务 ====================

class KnowledgeService:
    """知识库服务"""
    
    @classmethod
    def search(cls, keywords, material_type=None, limit=10):
        """搜索知识库"""
        try:
            from .models import FortuneKnowledgeBase
            query = {'keywords__in': keywords, 'audit_status': 'approved'}
            if material_type:
                query['material_type'] = material_type
            
            results = FortuneKnowledgeBase.objects(**query).limit(limit)
            
            # 更新命中次数
            for result in results:
                result.hit_count += 1
                result.save()
            
            return results
        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            return []


# ==================== 前端配置构建器 ====================

def build_frontend_config(name, birth_date, result):
    """构建前端渲染所需的配置数据"""
    today = datetime.now()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    five_elements = result.get('five_elements', {})
    elements_data = [
        {"label": f"火（{five_elements.get('fire_guan', '七杀正官')}）", "percentage": five_elements.get('fire', 0), "colorClass": "bg-fire"},
        {"label": f"木（{five_elements.get('wood_cai', '偏财正财')}）", "percentage": five_elements.get('wood', 0), "colorClass": "bg-wood"},
        {"label": f"水（{five_elements.get('water_shi', '食神')}）", "percentage": five_elements.get('water', 0), "colorClass": "bg-water"},
        {"label": f"金（{five_elements.get('metal_bi', '比肩劫财，日主')}）", "percentage": five_elements.get('metal', 0), "colorClass": "bg-metal"},
        {"label": f"土（{five_elements.get('earth_yin', '偏印正印')}）", "percentage": five_elements.get('earth', 0), "colorClass": "bg-earth/50"}
    ]
    
    return {
        "page": {"title": f"命理分析 - {name}"},
        "colors": {
            "bgMain": "#FFFFF8", "bgCard": "#FDF8F3", "bgChart": "#FAF5F0", "textMain": "#5C3D2E",
            "fire": "#F8C4C4", "wood": "#C9A66B", "water": "#A8D8EA", "metal": "#F5E6CC", "earth": "#D4A574",
            "luckyEarth": "#F5E6CC", "luckyMetal": "#FFFFFF", "halo": "rgba(248, 196, 196, 0.3)", "tagBg": "#F5EDE4"
        },
        "nav": {
            "title": name,
            "tabs": [{"name": "沙盘", "active": True}, {"name": "星座", "active": False}, {"name": "生辰", "active": False}, {"name": "星宿", "active": False}, {"name": "紫微", "active": False}],
            "buttons": [{"icon": "fa-share-alt", "text": "分享完整内容"}, {"icon": "fa-calendar", "text": "查看生辰历"}]
        },
        "pattern": result.get('pattern', {"title": "【命格分析】", "pattern": "格局待定", "description": "根据您的生辰八字分析您的命格特征"}),
        "fiveElements": {"title": f"【{result.get('body_type', '身弱型')}】", "chartTitle": "五行占比", "elements": elements_data, "chartColors": ["#F8C4C4", "#C9A66B", "#A8D8EA", "#F5E6CC", "#D4A574"]},
        "lucky": result.get('lucky', {"title": "【喜用神】", "labels": {"luckyColor": "幸运颜色", "luckyDirection": "幸运方向", "luckyNumber": "幸运数字"}, "luckyColors": [{"name": "黄色", "colorClass": "bg-luckyEarth"}, {"name": "白色", "colorClass": "bg-luckyMetal"}], "luckyDirections": ["家乡", "正西"], "luckyNumbers": ["15", "8"]}),
        "match": result.get('match', {"industry": {"title": "适配行业", "content": "适合从事与五行属性相符的行业"}, "partner": {"title": "匹配伴侣", "content": "根据八字分析配偶特征"}}),
        "fortune": {"title": "大运分析", "chartTitle": "大运评分", "periods": result.get('fortune_periods', [])},
        "shishen": result.get('shishen', {"title": "十神占比", "chartTitle": "十神占比", "labels": ["正官", "七杀", "正财", "偏财", "食神", "伤官", "正印", "偏印", "比肩", "劫财"], "data": [8, 12, 5, 10, 3, 2, 0, 0, 15, 15], "colors": ['#F8C4C4', '#E8A0A0', '#C9A66B', '#B89565', '#A8D8EA', '#98C8DA', '#F5E6CC', '#E5D6BC', '#D4A574', '#C49564']}),
        "shensha": result.get('shensha', {"title": "神煞解析", "items": [{"name": "贵人相助", "description": "天乙贵人、福星贵人", "icon": "fa-star", "iconBg": "bg-orange-100", "iconColor": "text-orange-500"}, {"name": "慧根发达", "description": "太极贵人", "icon": "fa-brain", "iconBg": "bg-blue-100", "iconColor": "text-blue-500"}]}),
        "disclaimer": {"content": "当前内容为免费内容，仅供您在娱乐中探索自我，不等于专业测评，不代表价值评判，无任何现实指导意义。"},
        "footer": {"title": result.get('day_zhi', '日支') + "·" + result.get('day_shishen', '正官')}
    }