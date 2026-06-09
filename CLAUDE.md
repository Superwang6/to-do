# CLAUDE.md

本文件为 Claude Code 在此代码仓库中工作时提供指导。

## 项目概览

这是一个语音驱动的待办事项应用，前端使用 uni-app（Vue 3），后端使用 Python/FastAPI。用户可以通过类似聊天的界面，使用文本或语音输入创建待办事项。

## 技术栈

- **前端**：uni-app（Vue 3）、Vite、SCSS
- **后端**：Python、FastAPI
- **包管理器**：npm（前端）、uv（后端）

## 项目结构

```
to-do/
├── frontend/                  # uni-app 应用
│   ├── pages/
│   │   ├── index/            # 主待办列表
│   │   ├── voice/            # 语音创建页面
│   │   └── chat/             # 聊天/智能创建页面
│   ├── api/                  # API 客户端函数
│   ├── App.vue
│   ├── main.js
│   ├── uni.scss              # 设计系统变量
│   ├── pages.json            # 路由与导航配置
│   └── vite.config.js
├── backend/
│   └── src/                  # FastAPI 后端（三层架构）
│       ├── api/              #   表现层（路由）
│       ├── service/          #   业务逻辑层
│       ├── repository/       #   数据访问层
│       ├── model/            #   ORM 实体
│       ├── schema/           #   跨层 DTO（Pydantic）
│       ├── config.py
│       ├── database.py
│       └── main.py           #   FastAPI 应用入口
└── .claude/
    └── skills/
        └── uni-app-layout/   # 布局模式技能（自动加载）
```

## 后端架构：三层架构（表现层 / 业务逻辑层 / 数据访问层）

依赖方向是单向的：`api → service → repository → model`

### api/ — 表现层

- 每个文件都是一个 FastAPI `APIRouter`，命名为 `*_router.py`
- 职责：接收请求、校验参数、调用 service、返回响应
- 禁止：包含业务逻辑、直接访问数据库
- 文件命名：`{domain}_router.py`

### service/ — 业务逻辑层

- 职责：执行业务规则、编排多个 repository、管理事务
- 每个 service 通过构造函数注入接收其 repository
- 参数命名：`repository: XxxRepository`（不要使用 `dao`）
- 禁止：处理 HTTP 相关逻辑、编写原始 SQL

### repository/ — 数据访问层

- 职责：封装所有数据库 CRUD，返回 ORM model 对象
- 类命名：`{Domain}Repository`（不要使用 `*DAO`）
- 文件命名：`{domain}_repository.py`
- 禁止：包含业务逻辑、引用 HTTP 层

### model/ — ORM 实体

- SQLAlchemy `Base` 子类，映射到数据库表
- **禁止使用外键。** 对引用列使用普通的 `index=True` 列。关联表使用带有 `primary_key=True` 的普通 `Column`（这会自动创建索引）。本项目依赖应用层而非数据库来保证引用完整性。
- 关系定义使用 `backref` 或 `back_populates`。由于没有 `ForeignKey` 约束，每个 `relationship()` 都必须提供显式的 `primaryjoin`（多对多关系还需要 `secondaryjoin`），以便 SQLAlchemy 在无法从外键元数据推断时仍能解析连接关系。
- 多对多关联表在模块级别定义为 `Table()`
- 在 `model/__init__.py` 中导入所有模型，确保 `Base.metadata.create_all()` 能发现所有表

### schema/ — 跨层 DTO

- `common.py`：可复用基础类 — `PageRequest`、`TimeRangeRequest`
- 领域 schema 通过**组合**聚合基础类（不要使用继承）：
  ```python
  class TodoListRequest(BaseModel):
      page: PageRequest = PageRequest()
      time_range: Optional[TimeRangeRequest] = None
  ```
- PageRequest 字段：`page`（int，从 1 开始）、`page_size`（int，最大 200）
- TimeRangeRequest 字段：`start_time`、`end_time`（均为 Optional\[datetime]）
- Controller 层将 `page/page_size` 转换为 DAO 层使用的 `skip/limit`

## API 约定

所有后端 API 必须遵守以下规则：

- **方法**：仅使用 GET 和 POST。GET 用于详情，POST 用于列表 / 创建 / 更新 / 删除。
- **URL 模式**：
  - 创建：`POST /save`
  - 更新：`POST /modify/{id}`
  - 列表：`POST /list`（JSON body 包含 page/time\_range）
  - 详情：`GET /detail/{id}`
  - 删除：`POST /delete/{id}`
  - 聊天消息列表：`POST /messages/list`
- 绝不使用 PUT 或 DELETE 方法。
- 路由中，字面量路径片段必须定义在参数化路径之前，以避免路由被错误劫持（例如 `/list` 要位于 `/detail/{id}` 之前）。
- 后端路由位于 `backend/src/api/`，前端 API 封装位于 `frontend/api/`。路由变更时必须同时更新两端。

## 布局模式

本项目包含 `.claude/skills/uni-app-layout/` 技能，用于记录 uni-app 布局规则，避免滚动条和溢出问题。处理本项目时它会自动加载。关键规则：

1. 页面根元素：使用 `height: 100vh` + `overflow: hidden`（不要使用 `min-height`）
2. 带 `flex: 1` 的 `scroll-view` 必须同时设置 `height: 0`
3. Flex 子元素需要设置 `width: 100%` + `box-sizing: border-box`
4. 不要在父元素和子元素上嵌套设置横向 padding
5. 消息气泡需要设置 `max-width` 约束
6. `index.html` 入口的 `src` 路径必须与实际文件位置一致

## 设计系统

定义于 `frontend/uni.scss`：

- 暖奶油色背景（#F8F6F3）、陶土红主色（#C0544A）
- SCSS 变量：`$bg-page`、`$primary`、`$text-primary`、`$shadow-sm` 等
- 使用 `rpx` 单位进行响应式尺寸设置
- 使用 `$transition-spring` 实现交互动效
