# CLAUDE.md

本文件为 Claude Code 在此代码仓库中工作时提供项目级指导。更细的后端/前端规则分别位于：

- `backend/CLAUDE.md`
- `frontend/CLAUDE.md`

## 项目概览

这是一个语音驱动的待办事项应用。用户可以通过类似聊天的界面，使用文本或语音输入创建待办事项。

## 技术栈

- **前端**：uni-app（Vue 3）、Vite、SCSS；当前主要通过 HBuilderX 运行/构建，npm 仅用于依赖管理
- **后端**：Python、FastAPI、uv

## 顶层结构

```text
to-do/
├── frontend/                 # uni-app 前端，详见 frontend/CLAUDE.md
├── backend/                  # FastAPI 后端，详见 backend/CLAUDE.md
├── docs/                     # 需求、测试、API 变更和完成定义模板
├── .claude/skills/           # 项目技能
└── CLAUDE.md                 # 项目级指导
```

## 跨端 API 约定

所有后端 API 与前端封装必须遵守以下规则：

- **方法**：仅使用 GET 和 POST。
- **GET**：用于详情查询。
- **POST**：用于列表、创建、更新、删除。
- **创建**：`POST /save`
- **更新**：`POST /modify/{id}`
- **列表**：`POST /list`，JSON body 包含分页和可选筛选条件。
- **详情**：`GET /detail/{id}`
- **删除**：`POST /delete/{id}`
- **聊天消息列表**：`POST /messages/list`
- 绝不使用 PUT 或 DELETE。
- 后端路由位于 `backend/src/api/`，前端 API 封装位于 `frontend/api/`。
- 路由变更时必须同时更新后端 router、前端 API 封装和相关调用点。
- 字面量路径片段必须定义在参数化路径之前，避免 `/list` 被 `/{id}` 或类似参数路由劫持。

## 需求开发流水线

本项目包含 `.claude/skills/dev-pipeline/` 技能，用于将新需求按以下流程推进：

```text
需求 → 验收标准 → 影响范围 → 实现计划 → 开发 → 测试 → 验收总结
```

处理非平凡功能、行为变更、API 变更、前后端联调或测试计划时，应优先使用该技能。

### 流程要求

1. **先计划，后实现。** 非平凡需求在修改代码前，必须先输出需求理解、验收标准、影响范围、实现计划和测试计划。
2. **没有验收标准不进入开发。** 验收标准必须可测试、可手动验证。
3. **API 契约先行。** 涉及接口时，先明确 method、path、request、response，再分别修改后端和前端。
4. **测试失败即停止推进。** 不得把失败或未运行的测试描述为通过。
5. **结果如实报告。** 最终回复必须包含已完成内容、验证命令、测试结果、未运行项原因、风险与下一步。

## 项目文档

开发流程和模板位于 `docs/`：

- `docs/development-flow.md`：完整开发流水线
- `docs/feature-template.md`：需求文档模板
- `docs/test-checklist.md`：测试检查清单
- `docs/api-change-checklist.md`：API 变更检查清单
- `docs/definition-of-done.md`：完成定义
- `docs/requirements/`：需求文档目录
- `docs/test-plans/`：测试计划目录

## 最小执行规则

即使是小需求，也至少遵守：

1. 写清验收标准。
2. 说明影响范围。
3. 开发后运行相关测试，或明确说明未运行原因。
4. 输出风险和下一步。
