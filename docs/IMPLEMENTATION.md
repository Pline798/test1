# 个人记账本 — 实现步骤

本文档记录项目的完整开发实现过程，包含技术选型理由、关键实现细节、遇到的问题及解决方案。

## 一、技术选型

### 后端框架：FastAPI

| 对比项 | FastAPI | Flask | Django |
|--------|---------|-------|--------|
| 性能 | 高（异步支持） | 中 | 中 |
| API 文档 | 自动生成 Swagger/Redoc | 需第三方扩展 | 需 DRF + 扩展 |
| 类型校验 | Pydantic 原生集成 | 需手动 | 需 DRF Serializer |
| 学习成本 | 低 | 极低 | 高 |
| 项目规模 | 适合中小型 | 适合微型 | 适合大型 |

记账本属于中小型项目，FastAPI 的自动 API 文档和 Pydantic 类型校验能显著提升开发效率。

### ORM：SQLAlchemy 2.0

SQLAlchemy 是 Python 生态最成熟的 ORM，2.0 版本引入了新的声明式映射语法。相比之下，Tortoise-ORM 生态不够成熟，Django ORM 脱离 Django 后使用不便。

### 数据库：MySQL 8.1

支持 utf8mb4 字符集，可以完整存储 emoji 图标（分类用）。

### 前端框架：Vue 3 + Vite

Vue 3 组合式 API 比选项式 API 更适合组织复杂逻辑。Vite 基于 ES Module 的开发服务器启动速度极快，HMR 几乎即时生效。

## 二、开发环境搭建

### Python 依赖

- fastapi + uvicorn：Web 框架 + ASGI 服务器
- sqlalchemy + pymysql：ORM + MySQL 驱动
- pydantic：数据校验
- alembic：数据库迁移管理
- python-dotenv：环境变量加载
- pytest + httpx：测试框架

### Node.js 依赖

production：vue、vue-router、axios、dayjs、marked
devDependencies：vite、@vitejs/plugin-vue

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
  amount      DECIMAL(10,2) NOT NULL COMMENT '金额',
  type        ENUM('income','expense') NOT NULL COMMENT '收支类型',
  category_id INT NOT NULL COMMENT '分类ID',
  description TEXT COMMENT '备注',
  date        DATE NOT NULL COMMENT '交易日期',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

关键设计决策：
- **amount 使用 DECIMAL(10,2)**：避免 Float 浮点精度丢失。Float 无法精确表示 0.01 这样的十进制小数，做财务累计时会产生舍入误差。
- **created_at 带时区**：使用 `DateTime(timezone=True)` 和 `datetime.now(timezone.utc)` 存储 UTC 时间，避免容器部署时的时区歧义。
- **外键 ON DELETE CASCADE**：删除分类时自动删除关联流水记录。

### 默认分类预设

14 个默认分类，5 个收入 + 9 个支出，配有 emoji 图标和颜色标识。

## 四、后端实现

### 4.1 项目结构演进

项目从最初的单文件结构逐步拆分：

```
早期：app.py + config.py + database.py + models.py + schemas.py + crud.py
当前：按职责拆分为 app/ 包，内含 crud/、routers/、models/、schemas/ 子模块
```

拆分原则：每个文件只负责一个领域（分类/流水/统计），接口清晰，便于测试和维护。

### 4.2 配置管理 (config.py)

从 .env 文件读取数据库连接信息，自动拼装 SQLAlchemy 连接字符串。

### 4.3 数据库连接 (database.py)

使用 `create_engine` 创建数据库引擎，`sessionmaker` 创建会话工厂。定义 `get_db` 生成器配合 FastAPI 的 `Depends` 实现依赖注入。

### 4.4 数据模型 (models/__init__.py)

两个 ORM 模型：Category 和 Transaction，通过 `relationship` 建立双向关联。

### 4.5 Pydantic 校验 (schemas/__init__.py)

采用三层继承结构：

```
Base → Create（全部必填）
     → Update（全部可选）
     → Out（含 id，用于响应）
```

字段别名：Pydantic v2.10 检测到字段名 `date` 与 Python 内置 `datetime.date` 冲突，使用 `Field(alias="date")` 避让。

### 4.6 应用生命周期 (main.py)

使用 FastAPI 的 `lifespan` 上下文管理器管理启动和关闭逻辑：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # 建表
    init_seed_categories()                 # 写入默认分类
    yield
```

将 `create_all` 放在 lifespan 中而非模块导入时执行，避免测试导入时意外建表，同时确保 Docker 容器启动时自动完成初始化。

### 4.7 CRUD 操作

分类和流水各自独立为 crud 模块。交易查询支持以下筛选维度：

- type（收支类型）
- category_id（分类）
- year / month（日期范围）
- amount_min / amount_max（金额范围）
- keyword（备注关键词）

日期查询使用范围过滤（`date >= start AND date < end`）代替 `func.year(date)`，让 MySQL 可以用上 `date` 列索引。

### 4.8 API 路由

路由注册方式：

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

CORS 配置：`allow_origins=["*"]` 配合 `allow_credentials=False`，避免浏览器拒绝响应。

### 4.9 数据库迁移 (Alembic)

配置了 Alembic 迁移框架，env.py 从 Config 读取数据库连接 URL。初始迁移脚本 `001_initial_schema.py` 记录当前表结构。

### 4.10 测试

测试使用 SQLite 文件数据库，无需 MySQL 即可运行：

```python
# conftest.py — 测试前自动切换数据库
import app.config
app.config.Config.DATABASE_URL = "sqlite:///test_account_book.db"
```

每个测试函数前自动清空数据（autouse fixture），避免测试间相互污染。共 39 个测试用例覆盖分类 CRUD、流水 CRUD、金额搜索、分页、统计等场景。

## 五、前端实现

### 5.1 项目结构

前端按功能划分为 views（页面）、components（组件）、composables（组合式逻辑）、api（HTTP 封装）。

### 5.2 API 层 (api/index.js)

使用 Axios 封装 HTTP 请求，添加全局响应拦截器统一处理错误：

```javascript
http.interceptors.response.use(
  res => res,
  error => {
    const msg = error.response?.data?.detail || error.message || '网络请求失败'
    alert('操作失败：' + msg)
    return Promise.reject(error)
  },
)
```

### 5.3 状态管理 (composables/)

使用 Vue 组合式函数（Composables）管理状态而非 Pinia，减少依赖体积：

- `useTransactions.js`：交易列表、CRUD 操作、客户端筛选（关键词 + 金额范围）
- `useCategories.js`：分类列表、CRUD 操作

客户端筛选在 `filteredTxns` 计算属性中实现，与服务端筛选互补。

### 5.4 首页 Home.vue

- 月份切换：`prevMonth()/nextMonth()` 更新年份/月份后自动调用 `loadData()` 刷新
- 结余卡片：从 stats 接口计算 balance = income.total - expense.total
- 分类统计：按分类展示月度汇总
- 加载状态：`loading` 变量控制 "加载中..." 提示
- 近期流水：取最新 5 条，传递 year/month/limit 参数到服务端

### 5.5 流水管理 Transactions.vue

- 搜索栏：关键词搜索备注 + 金额范围搜索（最小值/最大值）
- 筛选 Tab：全部 / 支出 / 收入
- 添加/编辑：模态表单，金额、分类、日期、备注

### 5.6 分类管理 Categories.vue

Tab 切换显示收入和支出分类。3 列网格布局，预置 30 个 emoji 图标和 10 种颜色。

## 六、问题记录

### 1. Pydantic 字段名冲突

现象：运行时报错 PydanticUserError。
原因：Pydantic v2.10 检测到字段名 date 与 datetime.date 类型名冲突。
解决：使用 `Field(alias="date")`，配合 `populate_by_name=True` 和 `response_model_by_alias=True`。

### 2. 金额精度丢失

现象：累计金额出现微小误差。
原因：amount 使用 Float 类型，浮点数无法精确表示十进制小数。
解决：改为 `Numeric(10, 2)`，数据库层面保证精度。

### 3. 首页月份切换无效

现象：点击月份箭头只变了文字，数据不刷新。
原因：`prevMonth/nextMonth` 只更新了响应式变量，没调 `loadData()`。
解决：在切换函数末尾加上 `await loadData()`。

### 4. CORS 配置无效

现象：浏览器拦截 API 响应。
原因：`allow_origins=["*"]` 搭配 `allow_credentials=True` 被浏览器拒绝。
解决：`allow_credentials=False`（通配符域名不能携带凭证）。

### 5. Docker 部署数据库为空

现象：Docker 启动后 API 报错"表不存在"。
原因：`Base.metadata.create_all()` 和 `init_db.py` 都未被调用。
解决：移入 FastAPI lifespan 事件，应用启动时自动执行。

### 6. 日期查询不走索引

现象：交易量增大后查询变慢。
原因：`func.year(date) = X AND func.month(date) = Y` 包裹了 date 列，索引失效。
解决：改为 `date >= start AND date < end` 范围查询。

### 7. 测试无法离线运行

现象：运行 pytest 需要 MySQL 服务。
原因：conftest.py 写死了 MySQL 连接字符串。
解决：在 conftest.py 中动态覆盖 Config.DATABASE_URL 为 SQLite，测试前后自动建表/删表。

### 8. Vue Router 锚点冲突

现象：文档页面点击目录链接页面变白。
原因：Hash 模式下 `#id` 变化被 Vue Router 拦截。
解决：在 marked 渲染器中处理锚点链接。
