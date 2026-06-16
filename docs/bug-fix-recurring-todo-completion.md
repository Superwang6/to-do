# 周期事项完成逻辑 Bug 修复总结

## 问题现象

2026-06-16 发现以下 6 个关联 Bug：

| 序号 | 问题 | 现象 |
|-----|------|------|
| 1 | 分类错误 | 完成过期的周期事项后，模板仍停留在「今天」分类 |
| 2 | 历史记录缺失 | 已完成列表看不到周期事项的完成记录 |
| 3 | 计数不准确 | 已完成数量不包含周期历史实例 |
| 4 | 硬编码显示 | 周期事项卡片永远显示「今天」，不显示实际下次截止日期 |
| 5 | 历史日期错误 | 周期历史实例的 due_date 是过期日期，不是完成日期 |
| 6 | 时区不一致 | 本地日期 vs UTC 日期比较导致跨天判断错误 |

---

## 根因分析

### Bug 1 & 6：顺延逻辑 + 时区问题

**位置**：`backend/src/service/todo_service.py`

**原代码问题**：
```python
# 1. 时区不一致
def _is_today_or_past(d: datetime) -> bool:
    today = date.today()  # ❌ 本地日期
    return due_date <= today  # due_date 是 UTC 存储的

# 2. 顺延基准错误
next_due = calculate_next_due_date(todo.due_date, rule)  # ❌ 基于原截止日期
```

**影响**：
- 今天 6/16，due_date 6/15（昨天），每天重复
- 原逻辑：6/15 + 1 = 6/16 → 仍满足 `<= today` → **还在今天分类**

---

### Bug 2 & 3：过滤条件错误

**位置**：`backend/src/repository/todo_repository.py`

**原代码问题**：
```python
.filter(
    Todo.recurring_template_id.is_(None),  # ❌ 过滤掉了历史实例！
    Todo.status == "completed",
)
```

**影响**：
- 周期历史实例正是通过 `recurring_template_id` 关联到模板的
- 这个条件导致所有周期完成记录都被过滤掉了

---

### Bug 4：硬编码显示

**位置**：`frontend/components/TodoCard.vue`

**原代码问题**：
```vue
<text class="sub-next">今天</text>  <!-- ❌ 硬编码 -->
```

---

### Bug 5：历史 due_date 错误

**位置**：`backend/src/service/todo_service.py`

**原代码问题**：
```python
history = Todo(
    due_date=todo.due_date,  # ❌ 原模板的过期日期
    ...
)
```

---

## 修复方案

### 1. 时区统一 + 顺延逻辑修正

**文件**：`backend/src/service/todo_service.py:_is_today_or_past`

```python
def _is_today_or_past(d: datetime) -> bool:
    """Check if a datetime is today or past, using UTC time for consistency."""
    if d is None:
        return False
    today_utc = datetime.now(timezone.utc).date()  # ✅ UTC 日期
    due_date = d.date() if isinstance(d, datetime) else d
    return due_date <= today_utc
```

### 2. 顺延基准修正

**文件**：`backend/src/service/todo_service.py:complete`

```python
today = datetime.now(timezone.utc).date()
current_due_date = todo.due_date.date()

if current_due_date < today:
    # 截止日期已过期，从今天开始计算下一次
    next_due = calculate_next_due_date(
        datetime.combine(today, todo.due_date.time()),  # ✅ 今天日期 + 原时间
        todo.recurrence_rule
    )
else:
    # 截止日期是今天或未来，正常顺延
    next_due = calculate_next_due_date(todo.due_date, todo.recurrence_rule)
```

### 3. 历史 due_date 记录完成日期

```python
# 历史实例的截止日期 = 今天日期 + 原时间
completed_due_date = datetime.combine(today, todo.due_date.time())
```

### 4. 移除过滤条件

**文件**：`backend/src/repository/todo_repository.py`

```python
# ❌ 旧代码
.filter(
    Todo.recurring_template_id.is_(None),
    Todo.status == "completed",
)

# ✅ 新代码
.filter(Todo.status == "completed")
```

### 5. 动态显示下次截止日期

**文件**：`frontend/components/TodoCard.vue`

```vue
<!-- ❌ 旧代码 -->
<text class="sub-next">今天</text>

<!-- ✅ 新代码 -->
<text class="sub-next">{{ formatNextDue(todo.due_date) }}</text>
```

```javascript
function formatNextDue(iso) {
  // 今天 → "今天"
  // 明天 → "明天"
  // 其他 → "6/18"
}
```

---

## 修复效果验证

| 场景 | 修复前 | 修复后 |
|------|--------|--------|
| 今天 6/16<br>模板 due_date 6/15（昨天）<br>每天 16:00<br>点击完成 | | |
| 历史 due_date | 6/15 16:00 ❌ | 6/16 16:00 ✅ |
| 模板新 due_date | 6/16 16:00（仍在今天）❌ | 6/17 16:00（移到周期）✅ |
| 已完成列表 | 看不到这条记录 ❌ | 显示这条记录 ✅ |
| 已完成计数 | 不变 ❌ | +1 ✅ |
| 周期卡片显示 | 每天 · 今天 ❌ | 每天 · 明天 ✅ |

---

## 经验教训

### 1. 时区处理
- **永远不要混用本地时间和 UTC 时间**
- 所有日期比较都应该使用同一时区（建议统一用 UTC）
- `date.today()` 是本地日期，数据库存储的是 UTC，比较会出问题

### 2. 外键/关联字段的语义
- 新增关联字段后，一定要检查所有查询条件
- `recurring_template_id IS NULL` 的语义是「是模板」，这个条件不能随便加
- 查询前想清楚：**我要查什么？模板还是实例？**

### 3. 不要硬编码
- 显示状态信息时，永远基于数据动态计算，不要硬编码
- "今天"这种看起来合理的假设，在时间变化时就会出错

### 4. 历史记录的语义
- 历史快照应该记录**发生时的状态**，而不是原状态
- 完成日期应该是「今天」，不是「原定截止日期」

### 5. 关联 Bug 检查
- 发现一个 Bug 时，应该想想：**还有哪里有类似的问题？**
- 本次 6 个 Bug 都是互相关联的，只修一个会导致其他问题更隐蔽

---

## 代码位置速查

| 修复项 | 文件 | 行号 |
|--------|------|------|
| UTC 日期比较 | `backend/src/service/todo_service.py` | 26-31 |
| 顺延逻辑修正 | `backend/src/service/todo_service.py` | 150-164 |
| 历史 due_date 修正 | `backend/src/service/todo_service.py` | 129-148 |
| get_completed 移除过滤 | `backend/src/repository/todo_repository.py` | 117-134 |
| count_completed 移除过滤 | `backend/src/repository/todo_repository.py` | 106-115 |
| 动态显示下次截止 | `frontend/components/TodoCard.vue` | 18, 41-84 |
