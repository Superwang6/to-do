# API 变更检查清单

所有后端路由变更都必须同步检查本清单。

## 项目 API 约定

- [ ] 只使用 GET 和 POST。
- [ ] 创建接口使用 `POST /save`。
- [ ] 更新接口使用 `POST /modify/{id}`。
- [ ] 列表接口使用 `POST /list`。
- [ ] 详情接口使用 `GET /detail/{id}`。
- [ ] 删除接口使用 `POST /delete/{id}`。
- [ ] 聊天消息列表使用 `POST /messages/list`。
- [ ] 没有使用 PUT。
- [ ] 没有使用 DELETE。

## 路由顺序

- [ ] 字面量路径片段定义在参数化路径之前。
- [ ] `/list` 不会被 `/{id}` 或 `/detail/{id}` 错误劫持。
- [ ] `/messages/list` 等具体路径位于更宽泛路径之前。

## 后端实现

- [ ] router 文件位于 `backend/src/api/`。
- [ ] router 命名为 `*_router.py`。
- [ ] router 只处理请求、校验、调用 service、返回响应。
- [ ] 业务逻辑位于 service。
- [ ] 数据访问位于 repository。
- [ ] 请求/响应 DTO 位于 `backend/src/schema/`。

## 前端同步

- [ ] `frontend/api/` 已同步新增或修改封装。
- [ ] method 一致。
- [ ] path 一致。
- [ ] request body 一致。
- [ ] response 字段一致。
- [ ] 页面调用点已更新。

## 测试

- [ ] 成功请求测试。
- [ ] 参数缺失/非法测试。
- [ ] 数据不存在测试。
- [ ] 分页测试（列表接口）。
- [ ] 时间范围测试（如涉及）。
- [ ] 前端联调验证。

## API 记录

| Method | Path | Request | Response | 说明 |
|---|---|---|---|---|
|  |  |  |  |  |
