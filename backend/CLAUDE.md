# Backend Instructions

本文件为 Claude Code 在 `backend/` 目录中工作时提供后端专属指导。根目录 `CLAUDE.md` 中的项目总览、跨端 API 约定和开发流水线仍然适用。

## 后端概览

后端使用 Python + FastAPI，代码位于 `backend/src/`，采用三层架构：

```text
api → service → repository → model
```

依赖方向必须保持单向：上层可以调用下层，下层不能反向引用上层。

## 目录结构

```text
backend/
├── requirements.txt
├── setup.sql
├── migrations/              # 数据库迁移 SQL
└── src/
    ├── api/                 # 表现层：FastAPI APIRouter
    ├── service/             # 业务逻辑层
    ├── repository/          # 数据访问层
    ├── model/               # SQLAlchemy ORM 实体
    ├── schema/              # Pydantic DTO
    ├── util/                # 工具函数
    ├── config.py
    ├── database.py
    ├── dependencies.py
    └── main.py              # FastAPI 应用入口
```

## 分层规则

### api/ — 表现层

- 每个路由文件都是一个 FastAPI `APIRouter`。
- 文件命名：`{domain}_router.py`。
- 职责：接收请求、校验参数、调用 service、返回响应。
- 禁止：包含业务逻辑、直接访问数据库、直接操作 ORM 查询。
- 字面量路由必须定义在参数化路由之前，避免路由被错误劫持。

### service/ — 业务逻辑层

- 职责：执行业务规则、编排多个 repository、管理事务边界。
- 每个 service 通过构造函数注入接收 repository。
- 参数命名使用 `repository: XxxRepository`，不要使用 `dao`。
- 禁止：处理 HTTP 细节、返回 FastAPI Response、编写原始 SQL。

### repository/ — 数据访问层

- 职责：封装数据库 CRUD，返回 ORM model 对象。
- 类命名：`{Domain}Repository`，不要使用 `*DAO`。
- 文件命名：`{domain}_repository.py`。
- 禁止：包含业务逻辑、引用 HTTP 层、处理请求/响应对象。

### model/ — ORM 实体

- SQLAlchemy `Base` 子类映射数据库表。
- **禁止使用外键。** 对引用列使用普通的 `index=True` 列。
- 关联表使用带有 `primary_key=True` 的普通 `Column`，这会自动创建索引。
- 项目依赖应用层而非数据库来保证引用完整性。
- 关系定义使用 `backref` 或 `back_populates`。
- 因为没有 `ForeignKey`，每个 `relationship()` 必须提供显式 `primaryjoin`；多对多关系还需要 `secondaryjoin`。
- 多对多关联表在模块级别定义为 `Table()`。
- 在 `model/__init__.py` 中导入所有模型，确保 `Base.metadata.create_all()` 能发现所有表。

### schema/ — 跨层 DTO

- 使用 Pydantic schema 表达请求/响应 DTO。
- `common.py` 存放可复用基础类：`PageRequest`、`TimeRangeRequest`。
- 领域 schema 通过组合聚合基础类，不要使用继承：

```python
class TodoListRequest(BaseModel):
    page: PageRequest = PageRequest()
    time_range: Optional[TimeRangeRequest] = None
```

- `PageRequest` 字段：`page`（int，从 1 开始）、`page_size`（int，最大 200）。
- `TimeRangeRequest` 字段：`start_time`、`end_time`（均为 `Optional[datetime]`）。
- Controller/router 层负责把 `page/page_size` 转换为 repository 层使用的 `skip/limit`。

## API 约定

所有后端 API 必须遵守根目录的跨端约定：

- 仅使用 GET 和 POST。
- GET 用于详情。
- POST 用于列表、创建、更新、删除。
- 创建：`POST /save`
- 更新：`POST /modify/{id}`
- 列表：`POST /list`，JSON body 包含 `page` / `time_range`。
- 详情：`GET /detail/{id}`
- 删除：`POST /delete/{id}`
- 聊天消息列表：`POST /messages/list`
- 绝不使用 PUT 或 DELETE。

路由变更时必须同步提醒更新 `frontend/api/`。

## 开发顺序

后端功能开发优先按以下顺序：

```text
schema → model → repository → service → api/router → tests
```

如果只是纯查询或纯接口包装，可以跳过不涉及的层，但不能破坏依赖方向。

## 测试与验证

涉及后端行为变更时，应运行相关测试命令，例如：

```text
pytest
uv run pytest
```

如果测试命令当前不可用或项目缺少测试，最终回复中必须说明未运行原因。

API 变更至少检查：

- method/path 是否符合约定
- request body 是否与 schema 一致
- response 字段是否与前端使用一致
- 分页参数是否正确转换为 `skip/limit`
- 异常路径是否有明确处理

## 禁止事项

- 不要在 router 里写业务逻辑。
- 不要在 service 里处理 HTTP Response。
- 不要在 repository 里引用 FastAPI 或请求对象。
- 不要使用 `dao` 命名。
- 不要新增数据库外键。
- 不要新增 PUT / DELETE 接口。
