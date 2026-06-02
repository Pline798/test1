# 个人记账本

一个基于 Python + Vue 3 的全栈个人记账 Web 应用，支持收支记录、分类管理和月度统计，采用前后端分离架构。

## 技术栈

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12 | 运行时 |
| FastAPI | 0.115.6 | Web 框架，自动生成 OpenAPI 文档 |
| Uvicorn | 0.34.0 | ASGI 服务器，支持热重载 |
| SQLAlchemy | 2.0.36 | ORM 框架，操作 MySQL |
| PyMySQL | 1.1.1 | MySQL Python 驱动 |
| Pydantic | 2.10.3 | 数据校验与序列化 |
| python-dotenv | 1.0.1 | 环境变量管理 |

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.4 | 前端框架 |
| Vite | 5.4 | 构建工具与开发服务器 |
| Pinia | 2.1 | 状态管理 |
| Vue Router | 4.3 | 前端路由 |
| Axios | 1.7 | HTTP 请求 |
| dayjs | 1.11 | 日期格式化 |

### 数据库
| 技术 | 版本 | 用途 |
|------|------|------|
| MySQL | 8.1 | 数据持久化 |

## 项目结构

```
Test/
├── backend/                          # Python 后端项目
│   ├── app.py                        # FastAPI 应用入口
│   ├── config.py                     # 配置管理类
│   ├── database.py                   # 数据库连接与会话
│   ├── models.py                     # ORM 数据模型
│   ├── schemas.py                    # Pydantic 校验模型
│   ├── crud.py                       # 数据库操作函数
│   ├── init_db.py                    # 数据库初始化脚本
│   ├── requirements.txt              # Python 依赖
│   └── .env                          # 数据库连接配置
│
├── frontend/                         # Vue 3 前端项目
│   ├── index.html                    # HTML 入口
│   ├── vite.config.js                # Vite 构建配置
│   ├── package.json                  # npm 依赖
│   ├── public/                       # 静态资源
│   │   ├── vite.svg                  # 网站图标
│   │   ├── README.md                 # 项目文档（同步）
│   │   └── IMPLEMENTATION.md         # 实现文档（同步）
│   └── src/
│       ├── main.js                   # 应用入口
│       ├── App.vue                   # 根组件
│       ├── api/
│       │   └── index.js              # Axios API 封装
│       ├── router/
│       │   └── index.js              # 路由配置
│       ├── views/
│       │   ├── Home.vue              # 首页仪表盘
│       │   ├── Transactions.vue      # 流水管理
│       │   ├── Categories.vue        # 分类管理
│       │   └── AboutDoc.vue          # 项目文档
│       └── components/
│           └── NavBar.vue            # 底部导航栏
│
└── README.md                         # 项目文档（本文件）
```

## 快速开始

### 前置要求

确保已安装以下环境：

```bash
python --version   # >= 3.10
node --version     # >= 18
npm --version      # >= 9
mysql --version    # >= 8.0
```

### 第一步：创建数据库

登录 MySQL 并创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS account_book
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

### 第二步：配置数据库连接

编辑 `backend/.env` 文件，修改为你的数据库信息：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的密码
DB_NAME=account_book
```

### 第三步：初始化后端

```bash
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 初始化数据库（创建表结构和默认分类）
python init_db.py

# 启动后端服务（热重载模式）
python app.py
```

后端启动后：
- API 服务：http://localhost:8000
- API 文档（Swagger UI）：http://localhost:8000/docs

### 第四步：启动前端

新开一个终端：

```bash
cd frontend

# 安装 npm 依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后：
- 页面地址：http://localhost:5173
- Vite 自动将 `/api` 请求代理到后端

## API 文档

### 分类 API

#### 获取分类列表

```
GET /api/categories
```

查询参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| type | string | 筛选类型：income（收入）/ expense（支出），不传则返回全部 |

响应示例：

```json
[
  {
    "id": 1,
    "name": "工资",
    "type": "income",
    "icon": "💰",
    "color": "#67C23A"
  },
  {
    "id": 6,
    "name": "餐饮",
    "type": "expense",
    "icon": "🍜",
    "color": "#F56C6C"
  }
]
```

#### 创建分类

```
POST /api/categories
```

请求体：

```json
{
  "name": "健身",
  "type": "expense",
  "icon": "🏋️",
  "color": "#2ECC71"
}
```

#### 更新分类

```
PUT /api/categories/{id}
```

请求体（支持局部更新，只传需要修改的字段）：

```json
{
  "name": "运动健身",
  "color": "#1ABC9C"
}
```

#### 删除分类

```
DELETE /api/categories/{id}
```

删除分类会同时删除该分类下的所有流水记录。

### 流水 API

#### 获取流水列表

```
GET /api/transactions
```

查询参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| type | string | 筛选类型：income / expense |
| category_id | int | 按分类筛选 |
| year | int | 按年份筛选（如 2026） |
| month | int | 按月份筛选（1-12） |
| skip | int | 分页偏移量，默认 0 |
| limit | int | 每页条数，默认 100，最大 500 |

响应示例：

```json
[
  {
    "id": 1,
    "amount": 35.5,
    "type": "expense",
    "category_id": 6,
    "description": "午餐",
    "date": "2026-06-01",
    "created_at": "2026-06-01T12:00:00",
    "category": {
      "id": 6,
      "name": "餐饮",
      "icon": "🍜",
      "color": "#F56C6C",
      "type": "expense"
    }
  }
]
```

#### 创建流水记录

```
POST /api/transactions
```

请求体：

```json
{
  "amount": 35.50,
  "type": "expense",
  "category_id": 6,
  "description": "午餐",
  "date": "2026-06-01"
}
```

#### 更新流水记录

```
PUT /api/transactions/{id}
```

支持局部更新。

#### 删除流水记录

```
DELETE /api/transactions/{id}
```

### 统计 API

#### 获取统计汇总

```
GET /api/stats
```

查询参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| year | int | 按年份统计 |
| month | int | 按月份统计（需同时传 year） |

响应示例：

```json
{
  "income": {
    "total": 5000.00,
    "count": 1
  },
  "expense": {
    "total": 335.50,
    "count": 3
  },
  "by_category": [
    {
      "category_id": 6,
      "category_name": "餐饮",
      "icon": "🍜",
      "color": "#F56C6C",
      "type": "expense",
      "total": 135.50,
      "count": 2
    }
  ]
}
```

## 功能说明

### 首页仪表盘

月度切换：通过左右箭头切换查看不同月份的账单数据。结余概览卡片展示当月总收入、总支出和结余金额，结余为正时绿色显示，为负时红色显示。分类统计区域按分类展示月度收支明细，每条显示分类图标、名称和金额。近期流水区域展示最近 5 条交易记录，包含分类图标、备注和金额。

### 流水管理

支持快速添加支出或收入记录，通过顶部的「+支出」和「+收入」按钮打开添加表单。表单包含金额输入、分类选择（根据类型动态筛选）、日期选择和备注填写。列表支持按类型筛选（全部/支出/收入），每条记录显示分类图标、名称、备注和金额，支出红色、收入绿色。每条记录提供编辑和删除按钮。

### 分类管理

预设 14 个常用分类（5 个收入、9 个支出），每个分类配有 emoji 图标和颜色标识。支持自定义新增分类，可以从 30 个 emoji 图标和 10 种颜色中选择。分类以 3 列网格展示，顶部颜色条区分。支持切换查看收入分类和支出分类。

## 开发约定

Python 代码遵循 PEP 8 规范。数据库连接等敏感配置使用 .env 文件管理，通过 python-dotenv 加载。所有可调参数集中到 Config 类管理，不硬编码魔数。

## 常见问题

Q：数据库连接失败？
A：检查 .env 中的密码和主机地址是否正确，确认 MySQL 服务已启动且账号有远程访问权限。

Q：前端页面空白？
A：打开浏览器开发者工具（F12）查看 Console 面板的错误信息，确认 npm install 已安装完整依赖。

Q：API 请求提示 404？
A：确认后端已成功启动在 8000 端口，检查前端 vite.config.js 中 proxy 配置是否正确。

Q：初始化数据库报错？
A：确保 MySQL 用户有建库权限，可以先手动执行建库语句后再运行 init_db.py。

## 协议

MIT License