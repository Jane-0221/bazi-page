#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
赛博算命 - 数据库初始化脚本
将 Excel 数据源导入 MongoDB 数据库
"""

import os
import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def import_from_excel(excel_path, mongo_uri='mongodb://localhost:27017/', db_name='cyber_fortune'):
    """
    从 Excel 文件导入数据到 MongoDB
    
    Args:
        excel_path: Excel 文件路径
        mongo_uri: MongoDB 连接字符串
        db_name: 数据库名称
    """
    try:
        import pandas as pd
        from pymongo import MongoClient
        
        # 连接 MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db['UserData']
        
        # 读取 Excel 文件
        logger.info(f"读取 Excel 文件: {excel_path}")
        
        if not os.path.exists(excel_path):
            logger.warning(f"Excel 文件不存在: {excel_path}")
            logger.info("创建示例数据...")
            return create_sample_data(collection)
        
        # 读取所有工作表
        excel_data = pd.ExcelFile(excel_path)
        
        total_records = 0
        for sheet_name in excel_data.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            records = df.to_dict('records')
            
            # 添加元数据
            for record in records:
                record['imported_at'] = datetime.now()
                record['source_sheet'] = sheet_name
            
            if records:
                result = collection.insert_many(records)
                total_records += len(result.inserted_ids)
                logger.info(f"导入工作表 '{sheet_name}': {len(records)} 条记录")
        
        logger.info(f"导入完成，共 {total_records} 条记录")
        return True
        
    except ImportError as e:
        logger.error(f"缺少依赖包: {e}")
        logger.info("请安装: pip install pandas pymongo openpyxl")
        return False
    except Exception as e:
        logger.error(f"导入失败: {e}")
        return False


def create_sample_data(collection):
    """
    创建示例数据
    
    Args:
        collection: MongoDB 集合
    """
    sample_data = [
        {
            "name": "格局模板",
            "type": "pattern",
            "templates": [
                {"title": "【乘风破浪】", "pattern": "正官格·贵气盈门", "description": "正气凛然，贵人相助，事业顺遂。"},
                {"title": "【厚积薄发】", "pattern": "正印格·文华显耀", "description": "学识渊博，智慧超群，文运亨通。"},
                {"title": "【柳暗花明】", "pattern": "偏财格·财源广进", "description": "财运亨通，投资有道，收益丰厚。"},
                {"title": "【逆流而上】", "pattern": "七杀格·威震四方", "description": "意志坚定，勇往直前，成就非凡。"},
                {"title": "【静待花开】", "pattern": "食神格·福禄双全", "description": "生活安逸，福禄兼得，晚年享福。"}
            ],
            "created_at": datetime.now()
        },
        {
            "name": "五行对应",
            "type": "wuxing_mapping",
            "colors": {
                "木": ["绿色", "青色"],
                "火": ["红色", "粉色"],
                "土": ["黄色", "棕色"],
                "金": ["白色", "金色"],
                "水": ["黑色", "蓝色"]
            },
            "directions": {
                "木": ["正东", "东南"],
                "火": ["正南"],
                "土": ["家乡", "中部"],
                "金": ["正西", "西北"],
                "水": ["正北"]
            },
            "numbers": {
                "木": [3, 8],
                "火": [2, 7],
                "土": [5, 10],
                "金": [4, 9],
                "水": [1, 6]
            },
            "created_at": datetime.now()
        },
        {
            "name": "行业匹配",
            "type": "industry_mapping",
            "industries": {
                "木": "文化教育、医疗卫生、艺术设计、农林牧渔",
                "火": "电子科技、餐饮娱乐、照明电力、美容美发",
                "土": "房地产、建筑工程、农业种植、政府部门",
                "金": "金融投资、法律咨询、机械制造、珠宝首饰",
                "水": "物流运输、旅游酒店、饮料饮品、水产养殖"
            },
            "created_at": datetime.now()
        },
        {
            "name": "神煞配置",
            "type": "shensha_config",
            "items": [
                {"name": "贵人相助", "description": "天乙贵人、福星贵人", "icon": "fa-star", "effect": "positive"},
                {"name": "慧根发达", "description": "太极贵人", "icon": "fa-brain", "effect": "positive"},
                {"name": "张力满满", "description": "桃花", "icon": "fa-heart", "effect": "neutral"},
                {"name": "天选领导", "description": "禄神", "icon": "fa-crown", "effect": "positive"},
                {"name": "旷世奇才", "description": "学堂", "icon": "fa-graduation-cap", "effect": "positive"},
                {"name": "奔波劳碌", "description": "驿马", "icon": "fa-road", "effect": "neutral"},
                {"name": "孤独清高", "description": "华盖", "icon": "fa-moon", "effect": "neutral"}
            ],
            "created_at": datetime.now()
        },
        {
            "name": "大运评语库",
            "type": "fortune_tags",
            "tags": [
                {"score_range": [90, 100], "tags": ["智慧通达 德才并举", "福星高照 万事如意", "鹏程万里 前程似锦"]},
                {"score_range": [80, 89], "tags": ["根深叶茂 贵人垂青", "福泽绵长 贵人护业", "鸿运当头 吉星拱照"]},
                {"score_range": [70, 79], "tags": ["稳中求进 渐入佳境", "安守本心 心宽事顺", "柳暗花明 豁然开朗"]},
                {"score_range": [60, 69], "tags": ["韬光养晦 厚积薄发", "稳扎稳打 步步为营", "循序渐进 稳中求胜"]},
                {"score_range": [0, 59], "tags": ["否极泰来 转危为安", "韬光养晦 等待时机", "收敛低调 蓄势待发"]}
            ],
            "created_at": datetime.now()
        }
    ]
    
    try:
        result = collection.insert_many(sample_data)
        logger.info(f"创建示例数据: {len(result.inserted_ids)} 条记录")
        return True
    except Exception as e:
        logger.error(f"创建示例数据失败: {e}")
        return False


def init_database(mongo_uri='mongodb://localhost:27017/', db_name='cyber_fortune'):
    """
    初始化数据库
    
    Args:
        mongo_uri: MongoDB 连接字符串
        db_name: 数据库名称
    """
    try:
        from pymongo import MongoClient
        
        # 连接 MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # 创建集合
        if 'UserData' not in db.list_collection_names():
            db.create_collection('UserData')
            logger.info("创建集合: UserData")
        
        # 创建索引
        db.UserData.create_index([('type', 1)])
        db.UserData.create_index([('name', 1)])
        logger.info("创建索引完成")
        
        # 检查是否有数据
        if db.UserData.count_documents({}) == 0:
            logger.info("数据库为空，创建示例数据...")
            create_sample_data(db.UserData)
        
        logger.info("数据库初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        logger.info("请确保 MongoDB 已启动并可以访问")
        return False


def check_mongodb_connection(mongo_uri='mongodb://localhost:27017/'):
    """
    检查 MongoDB 连接
    
    Args:
        mongo_uri: MongoDB 连接字符串
    """
    try:
        from pymongo import MongoClient
        
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        logger.info("MongoDB 连接成功")
        return True
    except Exception as e:
        logger.error(f"MongoDB 连接失败: {e}")
        return False


# ==================== 主程序入口 ====================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='赛博算命数据库初始化工具')
    parser.add_argument('--excel', type=str, help='Excel 文件路径')
    parser.add_argument('--uri', type=str, default='mongodb://localhost:27017/', help='MongoDB 连接字符串')
    parser.add_argument('--db', type=str, default='cyber_fortune', help='数据库名称')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--check', action='store_true', help='检查数据库连接')
    
    args = parser.parse_args()
    
    if args.check:
        check_mongodb_connection(args.uri)
    elif args.init:
        init_database(args.uri, args.db)
    elif args.excel:
        import_from_excel(args.excel, args.uri, args.db)
    else:
        # 默认：检查连接并初始化
        logger.info("=" * 50)
        logger.info("赛博算命 - 数据库初始化工具")
        logger.info("=" * 50)
        
        if check_mongodb_connection(args.uri):
            init_database(args.uri, args.db)
        else:
            logger.warning("MongoDB 未启动，应用仍可运行（使用内存数据）")