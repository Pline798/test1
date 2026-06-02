# 个人记账本 — 实现步骤

本文档从零开始记录项目的完整开发实现过程，包含技术选型理由、每一步的详细实现逻辑、遇到的所有问题及解决方案。

## 一、技术选型

### 后端框架：FastAPI

选择 FastAPI 而非 Flask 或 Django 的原因：

| 对比项 | FastAPI | Flask | Django |
|--------|---------|-------|--------|
| 性能 | 高（异步支持） | 中 | 中 |
| API 文档 | 自动生成 Swagger/Redoc | 需第三方扩展 | 需 DRF + 扩展 |
| 类型校验 | Pydantic 原生集成 | 需手动 | 需 DRF Serializer |
| 学习成本 | 低 | 极低 | 高 |
| 项目规模 | 适合中小型 | 适合微型 | 适合大型 |

记账本属于中小型项目，FastAPI 的自动 API 文档和 Pydantic 类型校验能显著提升开发效率。

### ORM：SQLAlchemy 2.0

SQLAlchemy 是 Python 生态最成熟的 ORM，2.0 版本引入了新的声明式映射语法，代码更简洁。相比之下， Tortoise-ORM 生态不够成熟，Django ORM 脱离 Django 后使用不便。

### 数据库：MySQL 8.1

项目运行环境的 MySQL 版本为 8.1，支持 utf8mb4 字符集，可以完整存储 emoji 图标（分类用）。如果追求更轻量，可以考虑 SQLite，但 MySQL 更适合实际部署。

### 前端框架：Vue 3 + Vite

Vue 3 组合式 API（Composition API）比选项式 API 更适合组织复杂逻辑。Vite 基于 ES Module 的开发服务器启动速度极快，HMR（热模块替换）几乎即时生效。Pinia 作为 Vue 3 官方推荐的状态管理方案，比 Vuex 更简洁，TypeScript 支持更好。

## 二、开发环境搭建

### Python 依赖

requirements.txt 包含以下依赖：

- fastapi：Web 框架
- uvicorn：ASGI 服务器，--reload 参数支持热重载
- sqlalchemy：ORM 框架
- pymysql：MySQL 驱动
- pydantic：FastAPI 内置的数据校验库
- python-dotenv：从 .env 文件加载环境变量

安装命令：`pip install -r requirements.txt`

### Node.js 依赖

package.json 中的依赖分为两类：

production 依赖：
- vue：核心框架
- vue-router：前端路由
- pinia：状态管理
- axios：HTTP 客户端
- dayjs：日期格式化
- marked：Markdown 渲染

devDependencies：
- vite：构建工具
- @vitejs/plugin-vue：Vue 单文件组件编译插件

安装命令：`npm install`

### MySQL 准备

在 MySQL 中创建数据库，指定 utf8mb4 字符集以支持 emoji：

```sql
CREATE DATABASE IF NOT EXISTS account_book
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

## 三、数据库设计

### categories 表

```sql
CREATE TABLE categories (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  name        VARCHAR(50) NOT NULL COMMENT '分类名称',
  type        ENUM('income','expense') NOT NULL COMMENT '收支类型',
  icon        VARCHAR(20) DEFAULT '📁' COMMENT '图标',
  color       VARCHAR(7)  DEFAULT '#409EFF' COMMENT '颜色'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### transactions 表

```sql
CREATE TABLE transactions (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  amount      FLOAT NOT NULL COMMENT '金额',
  type        ENUM('income','expense') NOT NULL COMMENT '收支类型',
  category_id INT NOT NULL COMMENT '分类ID',
  description TEXT COMMENT '备注',
  date        DATE NOT NULL COMMENT '交易日期',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 默认分类预设

初始化 14 个分类，方便用户直接使用：

```python
DEFAULT_CATEGORIES = [
    # 收入分类
    {"name": "工资", "type": "income", "icon": "💰", "color": "#67C23A"},
    {"name": "兼职", "type": "income", "icon": "💼", "color": "#409EFF"},
    {"name": "投资收益", "type": "income", "icon": "📈", "color": "#E6A23C"},
    {"name": "红包", "type": "income", "icon": "🧧", "color": "#F56C6C"},
    {"name": "其他收入", "type": "income", "icon": "💵", "color": "#909399"},
    # 支出分类
    {"name": "餐饮", "type": "expense", "icon": "🍜", "color": "#F56C6C"},
    {"name": "交通", "type": "expense", "icon": "🚌", "color": "#E6A23C"},
    {"name": "购物", "type": "expense", "icon": "🛒", "color": "#409EFF"},
    {"name": "住房", "type": "expense", "icon": "🏠", "color": "#67C23A"},
    {"name": "娱乐", "type": "expense", "icon": "🎮", "color": "#9B59B6"},
    {"name": "医疗", "type": "expense", "icon": "💊", "color": "#E74C3C"},
    {"name": "教育", "type": "expense", "icon": "📚", "color": "#3498DB"},
    {"name": "通讯", "type": "expense", "icon": "📱", "color": "#1ABC9C"},
    {"name": "其他支出", "type": "expense", "icon": "📦", "color": "#95A5A6"},
]
```

## 四、后端实现

### 4.1 配置管理 (config.py)

创建 Config 类集中管理所有可调参数。从 .env 文件读取数据库连接信息，自动拼装 SQLAlchemy 连接字符串。这样做的好处是：数据库密码等敏感信息不硬编码在代码中，不同环境（开发/生产）只需要替换 .env 文件即可。

主要配置项：

```python
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"
```

charset=utf8mb4 参数确保 emoji 图标在数据库中正常存储。

### 4.2 数据库连接 (database.py)

使用 SQLAlchemy 的 create_engine 创建数据库引擎，sessionmaker 创建会话工厂。定义 DeclarativeBase 基类供后续数据模型继承。定义 get_db 生成器函数，配合 FastAPI 的 Depends 实现依赖注入，确保每个请求使用独立的数据库会话，请求结束后自动关闭。

关键代码结构：

```python
engine = create_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4.3 数据模型 (models.py)

定义两个 ORM 模型类：

Category 模型：
- id：自增主键
- name：分类名称，最长 50 字符
- type：枚举类型，限制为 income 或 expense
- icon：emoji 图标
- color：hex 颜色值

Transaction 模型：
- id：自增主键
- amount：金额，Float 类型
- type：枚举类型，收支标识
- category_id：外键关联 Category
- description：文本类型，可空
- date：交易日期
- created_at：记录创建时间，自动填充

两个模型通过 relationship 建立双向关联，方便序列化时携带关联对象信息。

### 4.4 数据校验 (schemas.py)

Pydantic 模型用于 API 请求的接收和响应的序列化。这里采用了三层继承结构：

```
CategoryBase → CategoryCreate, CategoryUpdate
             → CategoryOut
```

Transaction 同理。这样做的好处是：
- CategoryBase 定义公共字段的校验规则（如 name 最长 50 字符）
- Create 继承所有公共规则，用于接收新建请求
- Update 将所有字段设为 Optional，支持局部更新
- Out 额外包含 id，用于响应序列化

处理字段名冲突：Pydantic v2.10 中，字段名 date 与 Python 内置 datetime.date 类型名冲突。解决方案是使用 alias 别名机制，将字段声明为 record_date，同时设置 alias="date"，并配置 populate_by_name=True 和 response_model_by_alias=True。

处理日期类型：ORM 返回的 created_at 是 Python datetime 对象，在 TransactionOut 中声明为 Optional[datetime] 而不是 Optional[str]，让 Pydantic 自动序列化为 ISO 格式字符串。

### 4.5 CRUD 操作 (crud.py)

按照单一职责原则，将数据库操作函数独立到 crud.py 中，每个函数只负责一个数据库操作。

分类操作包含四个函数：
- get_categories：支持按 type 参数筛选，返回分类列表
- create_category：创建分类并刷新对象
- update_category：只更新传入的字段，其他字段保持不变
- delete_category：删除分类，返回是否成功的布尔值

流水操作包含五个函数：
- get_transactions：支持 type、category_id、year、month 四个筛选条件，以及 skip/limit 分页参数，按日期降序排列
- create_transaction：创建流水记录，返回完整对象（含关联的分类信息）
- update_transaction：局部更新，逻辑同分类更新
- delete_transaction：按 ID 删除
- get_stats：统计函数，使用 SQLAlchemy 的 func.sum 和 func.count 聚合函数，按 type 分组计算总额和笔数。同时按分类分组统计，返回分类维度明细

### 4.6 API 路由 (app.py)

注册所有路由端点，配置 CORS 中间件允许跨域请求。每个路由函数使用 Depends(get_db) 自动获取数据库会话。

路由组织方式：

```
GET    /api/categories        # 列表查询
POST   /api/categories        # 创建
PUT    /api/categories/{id}   # 更新
DELETE /api/categories/{id}   # 删除

GET    /api/transactions      # 列表查询（支持筛选分页）
POST   /api/transactions      # 创建
PUT    /api/transactions/{id} # 更新
DELETE /api/transactions/{id} # 删除

GET    /api/stats             # 统计汇总
```

每个路由配置 response_model 和 response_model_by_alias=True，确保响应使用正确的字段名（如 type 而非 record_type）。

### 4.7 数据库初始化 (init_db.py)

脚本在首次运行时执行以下操作：

1. 创建所有表结构（Base.metadata.create_all）
2. 检查数据库是否已有分类记录
3. 如果没有，插入 14 条默认分类数据
4. 如果已有，跳过初始化

这种设计确保多次运行 init_db.py 不会重复插入数据。

## 五、前端实现

### 5.1 Vite 配置 (vite.config.js)

配置开发服务器端口为 5173，设置 /api 代理到后端 8000 端口。使用代理而不是直接请求后端地址，可以避免跨域问题，也不需要后端配置具体的 allow_origins。

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

### 5.2 API 层 (api/index.js)

使用 Axios 创建 HTTP 实例，统一 baseURL 为 /api。每个后端接口对应一个 async 函数：

- fetchCategories / createCategory / updateCategory / deleteCategory
- fetchTransactions / createTransaction / updateTransaction / deleteTransaction
- fetchStats

此外封装了 formatDate 工具函数，使用 dayjs 格式化日期。

### 5.3 路由配置 (router/index.js)

使用 Vue Router 的 createWebHashHistory 模式。选择 hash 模式而非 history 模式的原因：hash 模式不需要服务端配置，部署到任意静态文件服务器都能工作。

四个路由：
- /：首页仪表盘
- /transactions：流水管理
- /categories：分类管理
- /about：项目文档（使用 marked 渲染 Markdown）

### 5.4 首页 Home.vue

月度导航组件：使用 currentYear 和 currentMonth 两个响应式变量，通过 prevMonth/nextMonth 函数切换月份。当月份跨年时自动调整年份。

结余概览卡片：调用 fetchStats 获取月度数据，计算 balance = income.total - expense.total。使用动态 CSS class 切换正负颜色。

分类统计区域：遍历 stats.by_category 数组，展示每个分类的图标、名称和汇总金额。

近期流水区域：调用 fetchTransactions 获取最新 5 条记录，展示分类图标、备注和金额。

所有数据在 onMounted 生命周期中通过 Promise.all 并行加载。

### 5.5 流水管理 Transactions.vue

筛选功能：三个 Tab 按钮控制 filterType 变量。使用计算属性 filteredTxns 对本地 transactions 数组进行过滤，避免重复请求后端。

添加/编辑流程：
- 点击「+支出」或「+收入」按钮，打开模态框
- 表单自动根据选择的类型筛选可用的分类
- 保存时根据 editingId 判断是新增还是更新
- 操作完成后关闭模态框并刷新列表

表单验证：金额必须大于 0，分类必须选择，否则提交按钮禁用。

删除操作：调用 deleteTransaction 前先 confirm 确认。

### 5.6 分类管理 Categories.vue

Tab 切换：两个 Tab 分别显示收入分类和支出分类。数据在两个 Tab 间切换时不会重复请求，因为 categories 对象同时存储 income 和 expense 两个数组。

分类卡片：3 列网格布局，每张卡片显示图标、名称，顶部颜色条通过 borderTopColor 绑定。悬停样式的添加卡片用虚线边框表示。

分类编辑：
- 预置 30 个常用 emoji 图标和 10 种颜色
- 选中态用高亮边框标识
- 新增时自动继承当前 Tab 的类型

删除分类前提示用户该操作会同时删除关联的流水记录。

### 5.7 底部导航栏 NavBar.vue

固定在页面底部，使用 position: fixed + bottom: 0。四个导航项通过 router-link 实现页面跳转。使用 route.name 匹配当前路由，高亮对应的 Tab。导航图标用 emoji 展示，简洁直观。

### 5.8 文档页面 AboutDoc.vue

通过 fetch 加载 public 目录下的 README.md 和 IMPLEMENTATION.md 文件。使用 marked 库将 Markdown 文本解析为 HTML。通过 v-html 指令渲染到页面。Tab 切换功能允许用户在项目文档和实现文档之间切换。

## 六、API 测试

编写自动化测试脚本 test_all.py 覆盖所有 API 端点，共测试 36 个场景：

分类测试（14 项）：获取全部分类、按类型筛选、创建分类、更新分类、删除分类、操作不存在分类返回 404、验证删除后数量恢复。

流水测试（16 项）：创建支出记录、创建收入记录、获取流水列表、按类型筛选、按分类筛选、按年月筛选、分页查询、更新流水、删除流水、操作不存在流水返回 404。

统计测试（6 项）：获取全量统计、按年月统计、验证金额正确性、按分类统计明细。

## 七、运行方式

开发模式需要同时启动两个终端：

```bash
# 终端 1：后端
cd backend
python app.py
# 输出：Uvicorn running on http://0.0.0.0:8000

# 终端 2：前端
cd frontend
npm run dev
# 输出：Local: http://localhost:5173/
```

生产构建：

```bash
cd frontend
npm run build
# 构建产物在 frontend/dist/ 目录
# 可将 dist 目录部署到 Nginx 或任意静态文件服务器
```

## 八、问题记录

### 1. Pydantic 字段名冲突

现象：运行 python app.py 时立即报错 PydanticUserError。

原因：Pydantic v2.10 在构建模型时检测到字段名 date 与 Python 标准库 datetime.date 类型名冲突，触发保护机制。

解决：使用 Field 的 alias 参数重命名字段。将模型中的字段声明为 record_date，同时设置 alias="date"。配置 model_dump(by_alias=True) 和 response_model_by_alias=True 确保序列化时使用原始字段名。

### 2. API 响应 500 错误

现象：调用 GET /api/transactions 时返回 500 状态码。

原因：TransactionOut 中 created_at 字段声明为 Optional[str]，但 SQLAlchemy ORM 返回的是 Python datetime 对象。FastAPI 在序列化响应时进行 Pydantic 校验，发现类型不匹配抛出 ResponseValidationError。

解决：将 created_at 字段类型改为 Optional[datetime]，Pydantic 会自动将 datetime 对象序列化为 ISO 格式字符串。

### 3. 热重载干扰测试

现象：在 backend 目录下创建测试脚本后，Uvicorn 自动重启导致测试中断。

原因：Uvicorn 启动时使用了 --reload 参数，会监控整个 backend 目录的文件变化。在目录内创建新文件会触发热重载。

解决：将测试脚本放在 backend 目录之外，或在启动命令中添加 reload_excludes 配置排除测试文件。

### 4. Vue Router 锚点冲突

现象：在文档页面中点击 Markdown 渲染出的目录链接，页面变空白。

原因：前端使用 createWebHashHistory 模式，Markdown 中 `[text](#id)` 链接的 hash 变化被 Vue Router 拦截为路由导航，找不到匹配的路由导致页面白屏。

解决：在 marked 渲染器中通过自定义 link renderer 将锚点链接改为 href="javascript:void(0)" 并添加 data-anchor 属性，再通过事件代理手动控制滚动。最终的解决方案是文档中不再使用目录链接。