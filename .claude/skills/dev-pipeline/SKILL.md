---
name: dev-pipeline
description: "Use this skill whenever the user wants to implement a new feature, change behavior, plan a requirement, create test plans, define acceptance criteria, run a development workflow, or says phrases like '流程化开发', '按开发流水线', '先整理需求', '需求评审', '测试计划', '验收标准', or 'Definition of Done'. This skill turns a vague request into a controlled requirement → design → implementation → verification pipeline. It should be used before coding non-trivial changes so the work has clear acceptance criteria, test coverage, and a stopping rule."
---

# Development Pipeline Skill

本技能用于把一个需求从“想法”推进到“可验证完成”。目标不是增加形式主义，而是让每次开发都有明确入口、出口、测试和失败回退策略，避免边写边猜、漏测、前后端契约不一致。

## 使用时机

当用户提出以下类型任务时，使用本技能：

- 新功能、行为变更、接口变更、数据库结构变更
- “帮我实现 xxx”，但需求还不够具体
- “按开发流水线处理 xxx”
- “先整理需求 / 验收标准 / 测试计划”
- “帮我拆任务 / 做技术方案 / 做回归测试”
- 当前修改会影响前端、后端、API、数据结构或核心流程中的任意两个以上部分

简单修 typo、单行 bugfix、纯解释问题时不需要完整流水线；但仍可使用其中的检查清单。

## 核心原则

1. **没有验收标准，不进入实现。** 否则无法判断完成。
2. **先定 API 契约，再分别实现前后端。** 避免两边字段和路径漂移。
3. **小步交付。** 优先把需求拆成可独立验证的阶段。
4. **测试失败即停止推进。** 回到最近的上游阶段修正，不带病进入下一步。
5. **每次结束都说明状态。** 明确 Done / Blocked / Risk / Next。

## 标准流程

### 1. 需求澄清

输出需求理解，必要时向用户提问。不要为了形式提问；只有当答案会改变实现方案时才问。

固定检查：

- 用户是谁？
- 触发入口在哪里？
- 成功状态是什么？
- 失败/空状态是什么？
- 是否影响 API、数据库、前端页面、路由、权限或布局？
- 明确“不做什么”。

如果需求足够明确，直接进入验收标准；如果不明确，先给出合理默认假设，并标注需要用户确认的点。

### 2. 验收标准

用可测试的语言写验收标准。优先使用列表：

```md
## 验收标准
- [ ] 在 <条件> 下，用户执行 <操作>，系统应 <结果>
- [ ] 当 <异常情况> 时，系统应 <错误处理>
- [ ] 原有 <关键流程> 不受影响
```

每条标准应该能被测试或手动验证。避免“体验更好”“性能更高”这种不可验收表述，除非同时给出指标。

### 3. 影响范围与设计

列出预计修改点：

```md
## 影响范围
### 后端
- schema:
- model:
- repository:
- service:
- api/router:
- tests:

### 前端
- api:
- pages/components:
- state:
- styles/layout:

### 文档/配置
- docs:
- env/config:
```

本项目后端必须遵守三层架构：`api → service → repository → model`。

本项目 API 必须遵守：

- 只使用 GET 和 POST
- 创建：`POST /save`
- 更新：`POST /modify/{id}`
- 列表：`POST /list`
- 详情：`GET /detail/{id}`
- 删除：`POST /delete/{id}`
- 字面量路由必须放在参数路由前
- 路由变更必须同步更新 `frontend/api/`

涉及 uni-app 页面或布局时，同时应用 `uni-app-layout` 规则：根元素 `height: 100vh` + `overflow: hidden`，`scroll-view` 的 `flex: 1` 搭配 `height: 0`。

### 4. 实现计划

把工作拆成 3-7 个可执行步骤。每一步都应该有验证方式。

示例：

```md
## 实现计划
1. 更新后端 schema，定义请求/响应字段
   - 验证：schema 能被 router 引用
2. 实现 repository/service 逻辑
   - 验证：单元或接口测试覆盖成功和失败路径
3. 更新 router
   - 验证：接口测试通过
4. 更新前端 api 封装和页面状态
   - 验证：手动创建/修改流程通过
5. 跑测试并执行回归清单
   - 验证：记录命令和结果
```

对非平凡代码修改，在写代码前应让用户确认计划。若用户明确要求“直接实现”，可跳过等待，但仍要在内部遵循计划。

### 5. 开发执行

执行时保持分层：

后端顺序：

```text
schema → model → repository → service → api/router → tests
```

前端顺序：

```text
api 封装 → 页面状态 → UI/交互 → 样式布局 → 联调
```

不要在 router 写业务逻辑；不要让 repository 引用 HTTP 层；不要使用 `dao` 命名。

### 6. 验证与测试

根据改动范围选择测试：

- 后端改动：运行相关 `pytest` / `uv run pytest`
- 前端改动：运行构建、类型检查或项目已有检查命令
- API 改动：至少验证前后端路径、方法、请求体、响应字段一致
- UI 改动：手测主流程、空状态、加载状态、错误状态、布局溢出
- 数据改动：验证创建、读取、更新、删除及边界数据

最终必须如实报告：

```md
## 验证结果
- 命令：...
- 结果：通过 / 失败 / 未运行
- 失败原因：...
- 未运行原因：...
```

不要把未运行的测试说成通过。

### 7. 完成定义

只有满足以下条件，才建议标记为完成：

- 验收标准逐条有结果
- 相关自动化测试通过，或明确说明未运行原因
- 主流程手测通过，或明确说明阻塞点
- API 变更已同步前后端
- 没有引入违反项目架构/API/布局约定的实现
- 最终总结包含已完成、测试结果、风险和下一步

## 失败回退策略

| 失败点 | 处理方式 |
|---|---|
| 需求不清 | 停止实现，回到需求澄清 |
| 验收标准不可测试 | 重写验收标准 |
| API 字段不一致 | 回到 API 契约设计 |
| 后端测试失败 | 暂停前端联调，先修后端 |
| 前端联调失败 | 检查路径、方法、请求体、响应字段 |
| 布局溢出 | 使用 `uni-app-layout` 规则修复 |
| 回归失败 | 暂停完成结论，记录影响并修复 |

## 输出模板

### 开发前

```md
## 需求理解
...

## 验收标准
- [ ] ...

## 影响范围
...

## 实现计划
1. ...

## 测试计划
- 后端：...
- 前端：...
- 联调：...
- 回归：...
```

### 开发后

```md
## 完成情况
- ...

## 修改文件
- path/to/file: 说明

## 验证结果
- 命令：...
- 结果：...

## 验收标准结果
- [x] ...
- [ ] ...（原因）

## 风险与下一步
- ...
```

## 项目文档约定

若用户要求落地需求文档，优先使用：

- `docs/feature-template.md`
- `docs/test-checklist.md`
- `docs/api-change-checklist.md`
- `docs/definition-of-done.md`
- `docs/development-flow.md`

具体需求文档放在：

- `docs/requirements/NNN-feature-name.md`
- `docs/test-plans/NNN-feature-name-test-plan.md`
