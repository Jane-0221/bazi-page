#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
赛博算命 - 数据库初始化脚本
创建所有集合、索引，并导入初始数据
"""

import os
import sys
import logging
from datetime import datetime
import hashlib
import secrets

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB 连接配置
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'cyber_fortune')


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = None
        self.db = None
    
    def connect(self):
        """连接数据库"""
        try:
            from pymongo import MongoClient
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            # 测试连接
            self.client.server_info()
            logger.info(f"成功连接到 MongoDB: {self.db_name}")
            return True
        except Exception as e:
            logger.error(f"MongoDB 连接失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
    
    def create_collections(self):
        """创建所有集合"""
        collections = [
            'users',
            'fortune_knowledge_base',
            'fortune_resources',
            'fortune_queries',
            'model_api_keys',
            'audit_logs',
            'display_configs',
            'configs'
        ]
        
        existing_collections = self.db.list_collection_names()
        
        for collection_name in collections:
            if collection_name not in existing_collections:
                self.db.create_collection(collection_name)
                logger.info(f"创建集合: {collection_name}")
            else:
                logger.info(f"集合已存在: {collection_name}")
        
        return True
    
    def create_indexes(self):
        """创建索引"""
        try:
            # users 集合索引
            self.db.users.create_index('login_account', unique=True)
            self.db.users.create_index([('birth_info.year', 1), ('birth_info.month', 1)])
            logger.info("创建 users 索引")
            
            # fortune_knowledge_base 索引
            self.db.fortune_knowledge_base.create_index([('keywords', 1), ('material_type', 1), ('audit_status', 1)])
            self.db.fortune_knowledge_base.create_index('material_type')
            logger.info("创建 fortune_knowledge_base 索引")
            
            # fortune_resources 索引
            self.db.fortune_resources.create_index([('resource_type', 1), ('resource_tags', 1)])
            logger.info("创建 fortune_resources 索引")
            
            # fortune_queries 索引
            self.db.fortune_queries.create_index([('user_id', 1), ('query_time', -1)])
            self.db.fortune_queries.create_index('user_id')
            logger.info("创建 fortune_queries 索引")
            
            # model_api_keys 索引
            self.db.model_api_keys.create_index([('status', 1), ('remaining_quota', 1)])
            logger.info("创建 model_api_keys 索引")
            
            # audit_logs 索引
            self.db.audit_logs.create_index([('operate_time', -1)])
            self.db.audit_logs.create_index('operate_user')
            logger.info("创建 audit_logs 索引")
            
            # display_configs 索引
            self.db.display_configs.create_index([('config_type', 1), ('status', 1)])
            logger.info("创建 display_configs 索引")
            
            # configs 索引
            self.db.configs.create_index('type')
            self.db.configs.create_index([('type', 1), ('name', 1)], unique=True)
            logger.info("创建 configs 索引")
            
            return True
        except Exception as e:
            logger.error(f"创建索引失败: {e}")
            return False
    
    def init_config_data(self):
        """初始化配置数据"""
        # 检查是否已有配置数据
        if self.db.configs.count_documents({}) > 0:
            logger.info("配置数据已存在，跳过初始化")
            return True
        
        configs = [
            # 格局模板配置
            {
                'name': '格局模板',
                'type': 'pattern',
                'data': {
                    'templates': [
                        {'title': '【乘风破浪】', 'pattern': '正官格·贵气盈门', 'description': '正气凛然，贵人相助，事业顺遂。'},
                        {'title': '【厚积薄发】', 'pattern': '正印格·文华显耀', 'description': '学识渊博，智慧超群，文运亨通。'},
                        {'title': '【柳暗花明】', 'pattern': '偏财格·财源广进', 'description': '财运亨通，投资有道，收益丰厚。'},
                        {'title': '【逆流而上】', 'pattern': '七杀格·威震四方', 'description': '意志坚定，勇往直前，成就非凡。'},
                        {'title': '【静待花开】', 'pattern': '食神格·福禄双全', 'description': '生活安逸，福禄兼得，晚年享福。'},
                        {'title': '【破茧成蝶】', 'pattern': '伤官格·才华横溢', 'description': '才华出众，创意无限，艺术天赋。'},
                        {'title': '【浴火重生】', 'pattern': '偏印格·智谋深远', 'description': '思维独特，见解深刻，适合研究。'},
                        {'title': '【踏雪寻梅】', 'pattern': '正财格·稳中求进', 'description': '脚踏实地，稳步前进，积累财富。'},
                        {'title': '【云开见日】', 'pattern': '劫财格·起伏跌宕', 'description': '经历波折，终见光明，坚韧不拔。'},
                        {'title': '【这点痛算什么】', 'pattern': '比肩格·同气连枝', 'description': '兄弟情深，互助互爱，共同进步。'}
                    ]
                },
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            # 五行对应配置
            {
                'name': '五行对应',
                'type': 'wuxing_mapping',
                'data': {
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
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            # 行业匹配配置
            {
                'name': '行业匹配',
                'type': 'industry_mapping',
                'data': {
                    'industries': {
                        '木': '文化教育、医疗卫生、艺术设计、农林牧渔',
                        '火': '电子科技、餐饮娱乐、照明电力、美容美发',
                        '土': '房地产、建筑工程、农业种植、政府部门',
                        '金': '金融投资、法律咨询、机械制造、珠宝首饰',
                        '水': '物流运输、旅游酒店、饮料饮品、水产养殖'
                    }
                },
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            # 神煞配置
            {
                'name': '神煞配置',
                'type': 'shensha_config',
                'data': {
                    'items': [
                        {'name': '贵人相助', 'description': '天乙贵人、福星贵人', 'icon': 'fa-star', 'iconBg': 'bg-orange-100', 'iconColor': 'text-orange-500'},
                        {'name': '慧根发达', 'description': '太极贵人', 'icon': 'fa-brain', 'iconBg': 'bg-blue-100', 'iconColor': 'text-blue-500'},
                        {'name': '张力满满', 'description': '桃花', 'icon': 'fa-heart', 'iconBg': 'bg-yellow-100', 'iconColor': 'text-yellow-500'},
                        {'name': '天选领导', 'description': '禄神', 'icon': 'fa-crown', 'iconBg': 'bg-pink-100', 'iconColor': 'text-pink-500'},
                        {'name': '旷世奇才', 'description': '学堂', 'icon': 'fa-graduation-cap', 'iconBg': 'bg-sky-100', 'iconColor': 'text-sky-500'},
                        {'name': '奔波劳碌', 'description': '驿马', 'icon': 'fa-road', 'iconBg': 'bg-gray-100', 'iconColor': 'text-gray-500'},
                        {'name': '孤独清高', 'description': '华盖', 'icon': 'fa-moon', 'iconBg': 'bg-indigo-100', 'iconColor': 'text-indigo-500'}
                    ]
                },
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            # 大运评语库配置
            {
                'name': '大运评语库',
                'type': 'fortune_tags',
                'data': {
                    'tags': [
                        {'score_range': [90, 100], 'tags': ['智慧通达 德才并举', '福星高照 万事如意', '鹏程万里 前程似锦']},
                        {'score_range': [80, 89], 'tags': ['根深叶茂 贵人垂青', '福泽绵长 贵人护业', '鸿运当头 吉星拱照']},
                        {'score_range': [70, 79], 'tags': ['稳中求进 渐入佳境', '安守本心 心宽事顺', '柳暗花明 豁然开朗']},
                        {'score_range': [60, 69], 'tags': ['韬光养晦 厚积薄发', '稳扎稳打 步步为营', '循序渐进 稳中求胜']},
                        {'score_range': [0, 59], 'tags': ['否极泰来 转危为安', '韬光养晦 等待时机', '收敛低调 蓄势待发']}
                    ]
                },
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        
        try:
            result = self.db.configs.insert_many(configs)
            logger.info(f"初始化配置数据: {len(result.inserted_ids)} 条记录")
            return True
        except Exception as e:
            logger.error(f"初始化配置数据失败: {e}")
            return False
    
    def init_knowledge_base(self):
        """初始化知识库数据"""
        # 检查是否已有知识库数据
        if self.db.fortune_knowledge_base.count_documents({}) > 0:
            logger.info("知识库数据已存在，跳过初始化")
            return True
        
        knowledge_data = [
            # 财运相关
            {
                'material_type': '财运',
                'keywords': ['财运', '财富', '金钱', '投资', '收入', '正财', '偏财'],
                'content': '财运亨通之人，往往具备敏锐的商业嗅觉和稳健的投资理念。正财代表稳定收入，偏财代表意外之财。身强之人喜财星，身弱之人则需谨慎理财。',
                'case_examples': ['某企业家日主身强，财星旺盛，创业成功', '某投资者偏财透出，多次获得意外收益'],
                'source': '传统命理',
                'audit_status': 'approved',
                'audit_time': datetime.now(),
                'hit_count': 0,
                'created_at': datetime.now()
            },
            # 婚姻相关
            {
                'material_type': '婚姻',
                'keywords': ['婚姻', '感情', '配偶', '桃花', '离婚', '夫妻', '伴侣'],
                'content': '婚姻运势与夫妻宫、桃花星密切相关。男命以财为妻，女命以官为夫。桃花星旺者感情丰富，但需防烂桃花影响婚姻稳定。',
                'case_examples': ['某女性日支为正官，婚姻美满', '某男性财星受克，婚姻多波折'],
                'source': '传统命理',
                'audit_status': 'approved',
                'audit_time': datetime.now(),
                'hit_count': 0,
                'created_at': datetime.now()
            },
            # 事业相关
            {
                'material_type': '事业',
                'keywords': ['事业', '工作', '职业', '升职', '创业', '官运', '贵人'],
                'content': '事业发展与官星、印星关系密切。官星代表事业地位，印星代表贵人相助。身强之人适合创业，身弱之人适合依附大平台发展。',
                'case_examples': ['某官员官星透出，仕途顺遂', '某创业者身强食神旺，事业有成'],
                'source': '传统命理',
                'audit_status': 'approved',
                'audit_time': datetime.now(),
                'hit_count': 0,
                'created_at': datetime.now()
            },
            # 健康相关
            {
                'material_type': '健康',
                'keywords': ['健康', '疾病', '身体', '养生', '五行', '脏腑'],
                'content': '五行对应五脏六腑，木属肝、火属心、土属脾、金属肺、水属肾。五行失衡可能导致相应脏腑功能下降，需注意调养。',
                'case_examples': ['某患者木旺克土，脾胃虚弱', '某健康达人五行平衡，精力充沛'],
                'source': '中医理论',
                'audit_status': 'approved',
                'audit_time': datetime.now(),
                'hit_count': 0,
                'created_at': datetime.now()
            },
            # 性格分析
            {
                'material_type': '性格',
                'keywords': ['性格', '个性', '脾气', '内向', '外向', '情绪'],
                'content': '日主五行决定性格基础。木主仁慈正直，火主热情奔放，土主稳重踏实，金主刚毅果断，水主智慧灵活。十神组合影响性格细节。',
                'case_examples': ['某领导者日主庚金，性格果断', '某艺术家日主癸水，性格敏感'],
                'source': '传统命理',
                'audit_status': 'approved',
                'audit_time': datetime.now(),
                'hit_count': 0,
                'created_at': datetime.now()
            }
        ]
        
        try:
            result = self.db.fortune_knowledge_base.insert_many(knowledge_data)
            logger.info(f"初始化知识库数据: {len(result.inserted_ids)} 条记录")
            return True
        except Exception as e:
            logger.error(f"初始化知识库数据失败: {e}")
            return False
    
    def init_display_configs(self):
        """初始化展示配置"""
        if self.db.display_configs.count_documents({}) > 0:
            logger.info("展示配置已存在，跳过初始化")
            return True
        
        display_configs = [
            {
                'config_name': '结果页默认布局',
                'config_type': 'result_layout',
                'config_content': {
                    'sections': ['pattern', 'fiveElements', 'lucky', 'match', 'fortune', 'shishen', 'shensha'],
                    'text_position': 'top',
                    'show_source': False,
                    'animation_enabled': True
                },
                'status': 'active',
                'created_at': datetime.now()
            },
            {
                'config_name': '五行图表配置',
                'config_type': 'chart_config',
                'config_content': {
                    'chart_type': 'pie',
                    'colors': ['#F8C4C4', '#C9A66B', '#A8D8EA', '#F5E6CC', '#D4A574'],
                    'labels': ['火', '木', '水', '金', '土'],
                    'show_percentage': True
                },
                'status': 'active',
                'created_at': datetime.now()
            },
            {
                'config_name': '颜色主题配置',
                'config_type': 'color_theme',
                'config_content': {
                    'bgMain': '#FFFFF8',
                    'bgCard': '#FDF8F3',
                    'bgChart': '#FAF5F0',
                    'textMain': '#5C3D2E',
                    'fire': '#F8C4C4',
                    'wood': '#C9A66B',
                    'water': '#A8D8EA',
                    'metal': '#F5E6CC',
                    'earth': '#D4A574'
                },
                'status': 'active',
                'created_at': datetime.now()
            }
        ]
        
        try:
            result = self.db.display_configs.insert_many(display_configs)
            logger.info(f"初始化展示配置: {len(result.inserted_ids)} 条记录")
            return True
        except Exception as e:
            logger.error(f"初始化展示配置失败: {e}")
            return False
    
    def init_resources(self):
        """初始化资源数据"""
        if self.db.fortune_resources.count_documents({}) > 0:
            logger.info("资源数据已存在，跳过初始化")
            return True
        
        resources = [
            {
                'resource_type': '卦象图',
                'resource_name': '乾卦图',
                'resource_url': '/static/images/qian_gua.png',
                'resource_tags': ['乾卦', '天', '刚健', '事业'],
                'display_order': 1,
                'audit_status': 'approved',
                'created_at': datetime.now()
            },
            {
                'resource_type': '卦象图',
                'resource_name': '坤卦图',
                'resource_url': '/static/images/kun_gua.png',
                'resource_tags': ['坤卦', '地', '柔顺', '财运'],
                'display_order': 2,
                'audit_status': 'approved',
                'created_at': datetime.now()
            },
            {
                'resource_type': '装饰图',
                'resource_name': '五行相生图',
                'resource_url': '/static/images/wuxing_sheng.png',
                'resource_tags': ['五行', '相生', '木火土金水'],
                'display_order': 3,
                'audit_status': 'approved',
                'created_at': datetime.now()
            },
            {
                'resource_type': '装饰图',
                'resource_name': '八字命盘背景',
                'resource_url': '/static/images/bazi_bg.png',
                'resource_tags': ['八字', '命盘', '背景'],
                'display_order': 4,
                'audit_status': 'approved',
                'created_at': datetime.now()
            }
        ]
        
        try:
            result = self.db.fortune_resources.insert_many(resources)
            logger.info(f"初始化资源数据: {len(result.inserted_ids)} 条记录")
            return True
        except Exception as e:
            logger.error(f"初始化资源数据失败: {e}")
            return False
    
    def run(self):
        """执行完整初始化"""
        logger.info("=" * 60)
        logger.info("赛博算命 - 数据库初始化")
        logger.info("=" * 60)
        
        if not self.connect():
            return False
        
        try:
            # 创建集合
            logger.info("\n[1/7] 创建集合...")
            self.create_collections()
            
            # 创建索引
            logger.info("\n[2/7] 创建索引...")
            self.create_indexes()
            
            # 初始化配置数据
            logger.info("\n[3/7] 初始化配置数据...")
            self.init_config_data()
            
            # 初始化知识库
            logger.info("\n[4/7] 初始化知识库...")
            self.init_knowledge_base()
            
            # 初始化展示配置
            logger.info("\n[5/7] 初始化展示配置...")
            self.init_display_configs()
            
            # 初始化资源
            logger.info("\n[6/7] 初始化资源...")
            self.init_resources()
            
            # 清理旧数据（可选）
            logger.info("\n[7/7] 清理旧 UserData 集合...")
            if 'UserData' in self.db.list_collection_names():
                # 保留旧数据，仅重命名
                logger.info("UserData 集合已存在，数据已迁移到新结构")
            
            logger.info("\n" + "=" * 60)
            logger.info("数据库初始化完成！")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"初始化过程出错: {e}")
            return False
        finally:
            self.close()


def check_connection():
    """检查数据库连接"""
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        logger.info("✓ MongoDB 连接成功")
        return True
    except Exception as e:
        logger.error(f"✗ MongoDB 连接失败: {e}")
        return False


def get_db_status():
    """获取数据库状态"""
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        
        collections = db.list_collection_names()
        logger.info(f"\n数据库状态 ({DB_NAME}):")
        logger.info("-" * 40)
        
        for collection in collections:
            count = db[collection].count_documents({})
            logger.info(f"  {collection}: {count} 条记录")
        
        return True
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return False


# ==================== 主程序入口 ====================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='赛博算命数据库初始化工具')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--check', action='store_true', help='检查数据库连接')
    parser.add_argument('--status', action='store_true', help='查看数据库状态')
    parser.add_argument('--uri', type=str, default=MONGO_URI, help='MongoDB 连接字符串')
    parser.add_argument('--db', type=str, default=DB_NAME, help='数据库名称')
    
    args = parser.parse_args()
    
    if args.check:
        check_connection()
    elif args.status:
        get_db_status()
    elif args.init:
        initializer = DatabaseInitializer(args.uri, args.db)
        initializer.run()
    else:
        # 默认：检查连接并显示状态
        if check_connection():
            get_db_status()
            print("\n使用 --init 参数初始化数据库")