#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
赛博算命 - Flask 后端主程序
初始化 Web 服务、整合路由与业务逻辑
支持 MongoDB 数据库
"""

import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入业务模块
from yFiveMat import FiveElementsCalculator
from yurls import register_routes

# 导入数据库服务
try:
    from ydb_service import (
        db_service, config_service, user_service, 
        query_service, knowledge_service, audit_service,
        display_service, init_database, check_database
    )
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# 创建 Flask 应用
app = Flask(__name__)

# 配置
app.config['JSON_AS_ASCII'] = False  # 支持中文 JSON
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cyber-fortune-2024')

# 启用跨域支持
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 配置日志
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== 路由定义 ====================

@app.route('/')
def index():
    """首页 - 返回 API 信息"""
    return jsonify({
        'name': '赛博算命 API',
        'version': '1.0.0',
        'description': '基于五行理论的命理分析系统',
        'endpoints': {
            'query': '/api/query - POST - 查询命理信息',
            'fortune': '/api/fortune - GET - 获取大运信息',
            'health': '/api/health - GET - 健康检查'
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'cyber-fortune-api'
    })


@app.route('/api/query', methods=['POST', 'OPTIONS'])
def query_handler():
    """
    主查询接口
    接收用户姓名、生日、性别，返回命理分析结果
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        name = data.get('name', '').strip()
        birthday = data.get('birthday', '')
        gender = data.get('gender', 'male')
        
        # 参数验证
        if not name:
            return jsonify({
                'success': False,
                'message': '请输入姓名'
            }), 400
        
        if not birthday:
            return jsonify({
                'success': False,
                'message': '请选择出生日期'
            }), 400
        
        # 验证日期格式
        try:
            birth_date = datetime.strptime(birthday, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'success': False,
                'message': '日期格式不正确，请使用 YYYY-MM-DD 格式'
            }), 400
        
        logger.info(f"查询请求: 姓名={name}, 生日={birthday}, 性别={gender}")
        
        # 调用业务逻辑计算
        calculator = FiveElementsCalculator(birth_date, gender)
        result = calculator.calculate()
        
        # 构建前端配置数据
        config = build_frontend_config(name, birth_date, result)
        
        logger.info(f"查询成功: 姓名={name}")
        
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': {
                'name': name,
                'birthday': birthday,
                'gender': gender,
                'config': config
            }
        })
        
    except Exception as e:
        logger.error(f"查询出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/fortune', methods=['GET'])
def fortune_handler():
    """
    大运查询接口
    根据生日计算大运周期
    """
    try:
        birthday = request.args.get('birthday', '')
        gender = request.args.get('gender', 'male')
        
        if not birthday:
            return jsonify({
                'success': False,
                'message': '请提供出生日期'
            }), 400
        
        birth_date = datetime.strptime(birthday, '%Y-%m-%d')
        
        calculator = FiveElementsCalculator(birth_date, gender)
        fortune_data = calculator.calculate_fortune_periods()
        
        return jsonify({
            'success': True,
            'data': fortune_data
        })
        
    except Exception as e:
        logger.error(f"大运查询出错: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 辅助函数 ====================

def build_frontend_config(name, birth_date, result):
    """
    构建前端渲染所需的配置数据
    """
    # 计算年龄
    today = datetime.now()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    # 五行数据
    five_elements = result.get('five_elements', {})
    elements_data = [
        {"label": f"火（{five_elements.get('fire_guan', '七杀正官')}）", "percentage": five_elements.get('fire', 0), "colorClass": "bg-fire"},
        {"label": f"木（{five_elements.get('wood_cai', '偏财正财')}）", "percentage": five_elements.get('wood', 0), "colorClass": "bg-wood"},
        {"label": f"水（{five_elements.get('water_shi', '食神')}）", "percentage": five_elements.get('water', 0), "colorClass": "bg-water"},
        {"label": f"金（{five_elements.get('metal_bi', '比肩劫财，日主')}）", "percentage": five_elements.get('metal', 0), "colorClass": "bg-metal"},
        {"label": f"土（{five_elements.get('earth_yin', '偏印正印')}）", "percentage": five_elements.get('earth', 0), "colorClass": "bg-earth/50"}
    ]
    
    config = {
        "page": {
            "title": f"命理分析 - {name}"
        },
        "colors": {
            "bgMain": "#FFFFF8",
            "bgCard": "#FDF8F3",
            "bgChart": "#FAF5F0",
            "textMain": "#5C3D2E",
            "fire": "#F8C4C4",
            "wood": "#C9A66B",
            "water": "#A8D8EA",
            "metal": "#F5E6CC",
            "earth": "#D4A574",
            "luckyEarth": "#F5E6CC",
            "luckyMetal": "#FFFFFF",
            "halo": "rgba(248, 196, 196, 0.3)",
            "tagBg": "#F5EDE4"
        },
        "nav": {
            "title": name,
            "tabs": [
                {"name": "沙盘", "active": True},
                {"name": "星座", "active": False},
                {"name": "生辰", "active": False},
                {"name": "星宿", "active": False},
                {"name": "紫微", "active": False}
            ],
            "buttons": [
                {"icon": "fa-share-alt", "text": "分享完整内容"},
                {"icon": "fa-calendar", "text": "查看生辰历"}
            ]
        },
        "pattern": result.get('pattern', {
            "title": "【命格分析】",
            "pattern": "格局待定",
            "description": "根据您的生辰八字分析，您的命格具有独特的特征。"
        }),
        "fiveElements": {
            "title": f"【{result.get('body_type', '身弱型')}】",
            "chartTitle": "五行占比",
            "elements": elements_data,
            "chartColors": ["#F8C4C4", "#C9A66B", "#A8D8EA", "#F5E6CC", "#D4A574"]
        },
        "lucky": result.get('lucky', {
            "title": "【喜用神】",
            "labels": {
                "luckyColor": "幸运颜色",
                "luckyDirection": "幸运方向",
                "luckyNumber": "幸运数字"
            },
            "luckyColors": [
                {"name": "黄色", "colorClass": "bg-luckyEarth"},
                {"name": "白色", "colorClass": "bg-luckyMetal"}
            ],
            "luckyDirections": ["家乡", "正西"],
            "luckyNumbers": ["15", "8"]
        }),
        "match": result.get('match', {
            "industry": {
                "title": "适配行业",
                "content": "适合从事与五行属性相符的行业"
            },
            "partner": {
                "title": "匹配伴侣",
                "content": "根据八字分析配偶特征"
            }
        }),
        "fortune": {
            "title": "大运分析",
            "chartTitle": "大运评分",
            "periods": result.get('fortune_periods', [])
        },
        "shishen": result.get('shishen', {
            "title": "十神占比",
            "chartTitle": "十神占比",
            "labels": ["正官", "七杀", "正财", "偏财", "食神", "伤官", "正印", "偏印", "比肩", "劫财"],
            "data": [8, 12, 5, 10, 3, 2, 0, 0, 15, 15],
            "colors": ['#F8C4C4', '#E8A0A0', '#C9A66B', '#B89565', '#A8D8EA', '#98C8DA', '#F5E6CC', '#E5D6BC', '#D4A574', '#C49564']
        }),
        "shensha": result.get('shensha', {
            "title": "神煞解析",
            "items": [
                {"name": "贵人相助", "description": "天乙贵人、福星贵人", "icon": "fa-star", "iconBg": "bg-orange-100", "iconColor": "text-orange-500"},
                {"name": "慧根发达", "description": "太极贵人", "icon": "fa-brain", "iconBg": "bg-blue-100", "iconColor": "text-blue-500"}
            ]
        }),
        "disclaimer": {
            "content": "当前内容为免费内容，仅供您在娱乐中探索自我，不等于专业测评，不代表价值评判，无任何现实指导意义。"
        },
        "footer": {
            "title": result.get('day_zhi', '日支') + "·" + result.get('day_shishen', '正官')
        }
    }
    
    return config


# 注册额外路由
register_routes(app)


# ==================== 配置管理 API ====================

@app.route('/api/config/<config_type>', methods=['GET'])
def get_config(config_type):
    """
    获取配置数据
    
    Args:
        config_type: 配置类型 (pattern/wuxing_mapping/industry_mapping/shensha_config/fortune_tags)
    """
    if not DB_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '数据库服务不可用'
        }), 503
    
    try:
        config_data = config_service.get_config(config_type)
        
        return jsonify({
            'success': True,
            'data': config_data
        })
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/config/<config_type>', methods=['POST'])
def update_config(config_type):
    """
    更新配置数据
    
    Args:
        config_type: 配置类型
    """
    if not DB_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '数据库服务不可用'
        }), 503
    
    try:
        data = request.get_json()
        config_name = data.get('name', config_type)
        config_data = data.get('data', {})
        
        if not config_data:
            return jsonify({
                'success': False,
                'message': '配置数据不能为空'
            }), 400
        
        success = config_service.update_config(config_type, config_name, config_data)
        
        if success:
            # 记录审计日志
            audit_service.log(
                operate_type='config_update',
                operate_user=request.remote_addr,
                operate_content=f'更新配置: {config_type}/{config_name}',
                operate_ip=request.remote_addr
            )
            
            return jsonify({
                'success': True,
                'message': '配置更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '配置更新失败'
            }), 500
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/config/clear-cache', methods=['POST'])
def clear_config_cache():
    """清除配置缓存"""
    if not DB_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '数据库服务不可用'
        }), 503
    
    try:
        config_type = request.args.get('type', None)
        config_service.clear_cache(config_type)
        
        return jsonify({
            'success': True,
            'message': f'缓存已清除: {config_type or "全部"}'
        })
    except Exception as e:
        logger.error(f"清除缓存失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 知识库 API ====================

@app.route('/api/knowledge/search', methods=['GET'])
def search_knowledge():
    """搜索知识库"""
    if not DB_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '数据库服务不可用'
        }), 503
    
    try:
        keywords = request.args.get('keywords', '').split(',')
        material_type = request.args.get('type', None)
        limit = int(request.args.get('limit', 10))
        
        results = knowledge_service.search(keywords, material_type, limit)
        
        # 转换 ObjectId
        for result in results:
            result['_id'] = str(result['_id'])
            if 'related_resource_ids' in result:
                result['related_resource_ids'] = [str(rid) for rid in result['related_resource_ids']]
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results)
        })
    except Exception as e:
        logger.error(f"搜索知识库失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 数据库状态 API ====================

@app.route('/api/db/status', methods=['GET'])
def db_status():
    """获取数据库状态"""
    status = {
        'available': DB_AVAILABLE,
        'connected': False,
        'collections': {}
    }
    
    if DB_AVAILABLE:
        status['connected'] = db_service.is_connected()
        
        if status['connected']:
            try:
                collections = db_service.db.list_collection_names()
                for collection in collections:
                    status['collections'][collection] = db_service.db[collection].count_documents({})
            except Exception as e:
                status['error'] = str(e)
    
    return jsonify({
        'success': True,
        'data': status
    })


@app.route('/api/db/init', methods=['POST'])
def init_db():
    """初始化数据库"""
    if not DB_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '数据库服务不可用'
        }), 503
    
    try:
        from ydb_init import DatabaseInitializer
        
        initializer = DatabaseInitializer()
        success = initializer.run()
        
        if success:
            return jsonify({
                'success': True,
                'message': '数据库初始化成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '数据库初始化失败'
            }), 500
    except Exception as e:
        logger.error(f"初始化数据库失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 应用启动初始化 ====================

def init_app():
    """应用启动时初始化"""
    logger.info("初始化应用...")
    
    # 初始化数据库连接
    if DB_AVAILABLE:
        if init_database():
            logger.info("数据库连接成功")
        else:
            logger.warning("数据库连接失败，将使用内存缓存")


# 在应用启动时调用初始化
init_app()


# ==================== 主程序入口 ====================

if __name__ == '__main__':
    # 开发模式运行
    logger.info("启动赛博算命后端服务...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
