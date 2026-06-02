# 个人记账本

一个基于 Python + Vue 3 的全栈个人记账 Web 应用，支持收支记录、分类管理、月度统计和金额搜索，采用前后端分离架构。

## 技术栈

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12 | 运行时 |
| FastAPI | 0.115+ | Web 框架，自动生成 OpenAPI 文档 |
| Uvicorn | 0.34+ | ASGI 服务器，支持热重载 |
| SQLAlchemy | 2.0+ | ORM 框架，操作 MySQL |
| PyMySQL | 1.1+ | MySQL Python 驱动 |
| Pydantic | 2.10+ | 数据校验与序列化 |
| Alembic | — | 数据库迁移管理 |
| python-dotenv | — | 环境变量管理 |

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.4 | 前端框架 |
| Vite | 5.4 | 构建工具与开发服务器 |
| Vue Router | 4.3 | 前端路由 |
| Axios | 1.7 | HTTP 请求 |
| dayjs | — | 日期格式化 |
| marked | — | Markdown 渲染 |

### 数据库
| 技术 | 版本 | 用途 |
|------|------|------|
| MySQL | 8.1 | 数据持久化 |

## 项目结构

```
个人记账本/
├── backend/                          # Python 后端项目
│   ├── app/
│   │   ├── main.py                   # FastAPI 应用入口（lifespan 事件管理生命周期）
│   │   ├── config.py                 # 配置管理类（从 .env 读取）
│   │   ├── database.py               # 数据库连接与会话
│   │   ├── models/__init__.py        # ORM 数据模型
│   │   ├── schemas/__init__.py       # Pydantic 校验模型（含别名处理）
│   │   ├── crud/
│   │   │   ├── category.py           # 分类 CRUD 操作
│   │   │   └── transaction.py        # 流水 CRUD + 统计查询
│   │   ├── routers/
│   │   │   ├── categories.py         # 分类 API 路由
│   │   │   ├── transactions.py       # 流水 API 路由
│   │   │   └── stats.py              # 统计 API 路由
│   │   ├── services/                 # 业务逻辑层（预留扩展）
│   │   └── init_db.py                # 数据库初始化脚本
│   ├── alembic/                      # 数据库迁移
│   │   ├── env.py                    # Alembic 环境配置
│   │   └── versions/                 # 迁移脚本
│   ├── requirements/
│   │   ├── prod.txt                  # 生产依赖
│   │   └── dev.txt                   # 开发依赖
│   ├── tests/
│   │   ├── conftest.py               # 测试配置（SQLite 内存模式）
│   │   ├── test_categories.py        # 分类 API 测试
│   │   └── test_transactions.py      # 流水 API + 统计测试
│   ├── Dockerfile                    # 后端 Docker 镜像
│   └── .env                          # 数据库连接配置
│
├── frontend/                         # Vue 3 前端项目
│   ├── index.html                    # HTML 入口
│   ├── vite.config.js                # Vite 构建配置
│   ├── package.json                  # npm 依赖
│   ├── public/                       # 静态资源
│   └── src/
│       ├── main.js                   # 应用入口
│       ├── App.vue                   # 根组件
│       ├── api/
│       │   └── index.js              # Axios API 封装（含全局错误拦截器）
│       ├── router/
│       │   └── index.js              # Hash 模式路由配置
│       ├── composables/
│       │   ├── useTransactions.js    # 流水状态管理（含搜索/过滤）
│       │   └── useCategories.js      # 分类状态管理
│       ├── views/
│       │   ├── Home.vue              # 首页仪表盘
│       │   ├── Transactions.vue      # 流水管理（含金额搜索）
│       │   ├── Categories.vue        # 分类管理
│       │   └── AboutDoc.vue          # 项目文档
│       └── components/
│           ├── NavBar.vue            # 底部导航栏
│           ├── MonthPicker.vue       # 月份切换组件
│           ├── TransactionForm.vue   # 交易表单弹窗
│           └── CategoryForm.vue      # 分类表单弹窗
│
├── desktop/                          # CustomTkinter 桌面客户端
│   ├── main.py                       # 入口
│   ├── gui_app.py                    # GUI 界面
│   ├── app_manager.py                # 进程管理
│   └── utils.py                      # 工具函数
│
├── scripts/                          # 开发辅助脚本
│   └── dev.py
│
├── docs/
│   ├── README.md                     # 项目文档（本文件）
│   └── IMPLEMENTATION.md             # 实现文档
│
└── docker-compose.yml                # Docker 编排（MySQL + Backend）
```

## 快速开始

### 前置要求

```bash
python --version   # >= 3.10
node --version     # >= 18
npm --version      # >= 9
mysql --version    # >= 8.0
```

### 第一步：创建数据库

```sql
CREATE DATABASE IF NOT EXISTS account_book
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

### 第二步：配置数据库连接

编辑 `backend/.env` 文件：

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
pip install -r requirements/prod.txt

# 应用启动时会自动建表和写入默认分类
# 也可手动执行初始化：
python -c "from app.init_db import init_seed_categories; init_seed_categories()"

# 启动后端服务（热重载模式）
python -m app.main
```

后端启动后：
- API 服务：http://localhost:8000
- API 文档（Swagger UI）：http://localhost:8000/docs

### 第四步：启动前端

```bash
cd frontend
npm install
npm run dev
```

前端启动后：
- 页面地址：http://localhost:5173
- Vite 自动将 `/api` 请求代理到后端

### 使用 Docker 部署

```bash
docker-compose up -d
```

## API 文档

### 分类 API

#### 获取分类列表

```
GET /api/categories
```

| 参数 | 类型 | 说明 |
|------|------|------|
| type | string | 筛选：income / expense，不传则返回全部 |

#### 创建分类

```
POST /api/categories
```

```json
{"name": "健身", "type": "expense", "icon": "🏋️", "color": "#2ECC71"}
```

#### 更新分类

```
PUT /api/categories/{id}
```

支持局部更新，只传需要修改的字段。

#### 删除分类

```
DELETE /api/categories/{id}
```

分类下有流水记录时会返回 400 错误提示。

### 流水 API

#### 获取流水列表

```
GET /api/transactions
```

| 参数 | 类型 | 说明 |
|------|------|------|
| type | string | 筛选：income / expense |
| category_id | int | 按分类筛选 |
| year | int | 按年份筛选 |
| month | int | 按月份筛选（1-12） |
| amount_min | float | 金额下限 |
| amount_max | float | 金额上限 |
| keyword | string | 搜索备注关键词 |
| skip | int | 分页偏移，默认 0 |
| limit | int | 每页条数，默认 100，最大 500 |

#### 创建流水记录

```
POST /api/transactions
```

```json
{"amount": 35.50, "type": "expense", "category_id": 6, "description": "午餐", "date": "2026-06-01"}
```

#### 更新/删除流水

```
PUT   /api/transactions/{id}
DELETE /api/transactions/{id}
```

### 统计 API

#### 获取统计汇总

```
GET /api/stats
```

| 参数 | 类型 | 说明 |
|------|------|------|
| year | int | 按年份统计 |
| month | int | 按月份统计 |

## 功能说明

### 首页仪表盘
月度切换查看账单，展示当月结余、收入/支出汇总、分类统计和最近 5 条流水。

### 流水管理
支持添加/编辑/删除流水记录，可按收支类型、金额范围、备注关键词筛选。金额输入使用精确的 Decimal 存储，避免浮点误差。

### 分类管理
预设 14 个常用分类（5 收入 + 9 支出），支持自定义新增和编辑。

### 金额搜索
搜索栏下方提供金额范围输入框（最小值 — 最大值），与服务端筛选联动。

## 开发约定

- Python 代码遵循 PEP 8 规范
- 敏感配置使用 .env 文件管理
- 所有可调参数集中到 Config 类管理
- 测试使用 SQLite 文件数据库，无需 MySQL 即可运行

## 常见问题

Q：数据库连接失败？
A：检查 .env 中的密码和主机地址，确认 MySQL 服务已启动。

Q：金额显示不对？
A：金额使用 `Numeric(10,2)` 精确存储，若数据库是旧版 `Float` 结构，需手动 `ALTER TABLE transactions MODIFY amount DECIMAL(10,2);`
