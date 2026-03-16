# 赛博算命

基于五行理论的命理分析系统，采用前后端分离架构。

## 📁 项目结构

```
suanming/
├── index.html              # 前端入口页面
├── data.js                 # 前端配置数据
├── style.css               # 样式文件
├── script.js               # 前端交互脚本
├── backend/                # 后端目录
│   ├── App.py              # Flask 主程序
│   ├── FiveMat.py          # 五行计算核心模块
│   ├── urls.py             # 路由配置
│   ├── db_import.py        # 数据库导入脚本
│   ├── requirements.txt    # Python 依赖
│   ├── mongod.conf         # MongoDB 配置
│   ├── DBData.xlsx.csv     # 数据源文件
│   └── logs/               # 日志目录
│       └── app.log
└── README.md               # 说明文档
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- MongoDB 4.4+（可选，不启动也可运行）
- 现代浏览器

### 2. 安装依赖

```bash
# 进入后端目录
cd backend

# 安装 Python 依赖
pip install -r requirements.txt
```

### 3. 启动服务

```bash
# 启动后端服务（默认端口 5000）
python App.py
```

### 4. 访问应用

打开浏览器访问：
- 前端页面：直接打开 `index.html` 文件
- API 文档：http://localhost:5000/

## 📡 API 接口

### 主查询接口

**POST** `/api/query`

请求示例：
```json
{
    "name": "张三",
    "birthday": "1990-05-15",
    "gender": "male"
}
```

响应示例：
```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "name": "张三",
        "birthday": "1990-05-15",
        "config": { ... }
    }
}
```

### 其他接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/fortune` | GET | 大运查询 |
| `/api/bazi` | POST | 八字计算 |
| `/api/elements` | POST | 五行分析 |
| `/api/test` | GET | API 测试 |

## 🔧 配置说明

### 前端配置

编辑 `data.js` 文件修改默认显示数据，编辑 `script.js` 中的 `API_CONFIG` 修改后端地址。

### 后端配置

在 `App.py` 中可修改：
- 端口号（默认 5000）
- 跨域设置
- 日志级别

### MongoDB 配置

1. 安装 MongoDB
2. 运行初始化脚本：
```bash
python db_import.py --init
```

## 🎨 功能特性

### 命理分析
- 八字排盘（年柱、月柱、日柱、时柱）
- 五行占比分析
- 身强身弱判断
- 喜用神推导

### 命格解读
- 十种命格类型
- 个性化命格描述
- 幸运颜色、方向、数字

### 大运分析
- 六步大运周期
- 大运评分
- 运势评语

### 神煞解析
- 天乙贵人
- 太极贵人
- 桃花
- 禄神
- 学堂

## 📊 数据库（可选）

项目支持 MongoDB 存储，用于：
- 用户查询历史
- 自定义格局模板
- 数据统计分析

不启动 MongoDB 时，程序仍可正常运行。

## 🌐 部署说明

### Apache 部署（前端）

1. 将前端文件复制到 Web 服务器目录
```
C:\ApacheWeb\blog\
```

2. 配置 `httpd.conf`：
```apache
Listen 8080
<VirtualHost *:8080>
    DocumentRoot "C:/ApacheWeb/blog"
    <Directory "C:/ApacheWeb/blog">
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

### Flask 部署（后端）

生产环境建议使用 Gunicorn：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 App:app
```

## ⚠️ 免责声明

本系统仅供娱乐和学习参考，分析结果不具有任何现实指导意义，不代表价值评判。请理性看待，切勿迷信。

## 📝 开发说明

### 技术栈
- 前端：HTML5 + CSS3 + JavaScript + Tailwind CSS + Chart.js
- 后端：Python + Flask
- 数据库：MongoDB（可选）

### 扩展开发
1. 新增命理算法：编辑 `FiveMat.py`
2. 新增 API 接口：编辑 `urls.py`
3. 修改前端样式：编辑 `style.css`

## 📜 版本历史

- v1.0.0 (2024-03-16)
  - 初始版本发布
  - 完整的命理分析功能
  - 前后端分离架构

## 📧 联系方式

如有问题或建议，欢迎反馈。