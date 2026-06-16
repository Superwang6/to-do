<template>
  <view class="todo-card" :class="cardClass" :style="{ '--delay': delay }">
    <view class="card-left-bar" :class="leftBarClass"></view>
    <view class="card-body">
      <view class="card-left">
        <view class="check-circle" :class="{ checked: todo.status === 'completed' }" @tap="onToggle" hover-class="check-hover">
          <text v-if="todo.status === 'completed'" class="check-icon">✓</text>
        </view>
      </view>
      <view class="card-content" @tap="onEdit">
        <view class="card-title-row">
          <text v-if="todo.type === 'recurring'" class="type-icon">🔄</text>
          <text class="card-title">{{ todo.title }}</text>
        </view>
        <view class="card-sub">
          <text v-if="showRecurrence" class="sub-recurrence">{{ formatRecurrence(todo.recurrence_rule) }}</text>
          <text v-if="showRecurrence && todo.type === 'recurring'" class="sub-dot">·</text>
          <text v-if="showRecurrence && todo.type === 'recurring'" class="sub-next">{{ formatNextDue(todo.due_date) }}</text>
          <text v-else-if="showDueDate" class="sub-date">截止 {{ formatDate(todo.due_date) }}</text>
          <text v-if="showCompletedDate" class="sub-completed">完成于 {{ formatDate(todo.updated_at) }}</text>
          <text v-if="todo.priority === 'high'" class="sub-important">!! 重要</text>
        </view>
      </view>
      <view class="card-delete" @tap.stop="onDelete" hover-class="delete-hover">
        <text class="delete-icon">✕</text>
      </view>
    </view>
  </view>
</template>

<script>
import { formatDate, formatRecurrence } from '@/utils/todoFormatters'

/**
 * 格式化周期事项的下次截止日期
 * @param {string} iso - ISO 格式日期
 * @returns {string} 格式化后的下次截止描述
 */
function formatNextDue(iso) {
  if (!iso) return ''

  const match = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})/)
  if (!match) return ''

  const dueYear = parseInt(match[1], 10)
  const dueMonth = parseInt(match[2], 10)
  const dueDay = parseInt(match[3], 10)

  const today = new Date()
  const todayYear = today.getFullYear()
  const todayMonth = today.getMonth() + 1
  const todayDay = today.getDate()

  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  const tomorrowYear = tomorrow.getFullYear()
  const tomorrowMonth = tomorrow.getMonth() + 1
  const tomorrowDay = tomorrow.getDate()

  if (dueYear === todayYear && dueMonth === todayMonth && dueDay === todayDay) {
    return '今天'
  }
  if (dueYear === tomorrowYear && dueMonth === tomorrowMonth && dueDay === tomorrowDay) {
    return '明天'
  }

  // 显示日期
  return `${dueMonth}/${dueDay}`
}

export default {
  name: 'TodoCard',
  props: {
    todo: {
      type: Object,
      required: true
    },
    section: {
      type: String,
      default: ''
    },
    index: {
      type: Number,
      default: 0
    }
  },
  computed: {
    delay() {
      return this.index * 0.04 + 's'
    },
    cardClass() {
      const cls = []
      if (this.todo.priority === 'high') cls.push('high')
      if (this.section === 'today' && this.todo.type === 'recurring') cls.push('today-recurring')
      if (this.todo.status === 'completed') cls.push('done')
      return cls
    },
    leftBarClass() {
      if (this.todo.type === 'recurring') return 'recurring-bar'
      if (this.todo.priority === 'high') return 'high-bar'
      if (this.todo.status === 'completed') return 'done-bar'
      return ''
    },
    showRecurrence() {
      return this.todo.type === 'recurring' && this.todo.recurrence_rule && this.todo.status !== 'completed'
    },
    showDueDate() {
      return this.todo.due_date && this.todo.type !== 'recurring' && this.todo.status !== 'completed'
    },
    showCompletedDate() {
      return this.todo.status === 'completed'
    }
  },
  methods: {
    formatDate,
    formatRecurrence,
    formatNextDue,
    onToggle() {
      this.$emit('toggle', this.todo)
    },
    onEdit() {
      this.$emit('edit', this.todo)
    },
    onDelete() {
      this.$emit('delete', this.todo)
    }
  }
}
</script>

<style lang="scss" scoped>
.todo-card {
  display: flex;
  align-items: stretch;
  background: $bg-card;
  border-radius: $radius-md;
  margin-bottom: $spacing-sm;
  overflow: hidden;
  box-shadow: $shadow-sm;
  border: 2rpx solid $border;
  transform: translateY(20rpx);
  opacity: 0;
  animation: cardIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards var(--delay, 0s);
  transition: all $transition-base;
}

@keyframes cardIn {
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.todo-card.done {
  opacity: 0.65;
}

.todo-card.done .card-title {
  text-decoration: line-through;
  color: $text-tertiary;
}

.todo-card.high {
  background: linear-gradient(90deg, rgba(192, 84, 74, 0.05) 0%, $bg-card 100%);
}

.todo-card.today-recurring {
  background: linear-gradient(90deg, rgba(74, 156, 156, 0.05) 0%, $bg-card 100%);
}

.card-left-bar {
  width: 6rpx;
  background: $border-light;
  flex-shrink: 0;
}

.card-left-bar.recurring-bar {
  background: #4A9C9C;
}

.card-left-bar.high-bar {
  background: $primary;
}

.card-left-bar.done-bar {
  background: $text-tertiary;
}

.card-body {
  flex: 1;
  display: flex;
  align-items: center;
  padding: $spacing-md $spacing-md;
  min-width: 0;
}

.card-left {
  width: 44rpx;
  height: 44rpx;
  margin-right: $spacing-md;
  flex-shrink: 0;
  flex-grow: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-circle {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  border: 3rpx solid $text-tertiary;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all $transition-fast;
  cursor: pointer;
}

.check-circle.checked {
  background: $success;
  border-color: $success;
}

.check-hover {
  transform: scale(0.92);
}

.check-icon {
  color: white;
  font-weight: bold;
  font-size: 26rpx;
  line-height: 1;
}

.card-content {
  flex: 1;
  min-width: 0;
  margin-right: $spacing-sm;
  /* 保证内容不会挤压左侧复选框 */
  overflow: hidden;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 6rpx;
}

.type-icon {
  font-size: 24rpx;
  flex-shrink: 0;
}

.card-title {
  font-size: 30rpx;
  font-weight: 500;
  color: $text-primary;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
  transition: all $transition-base;
}

.card-sub {
  display: flex;
  align-items: center;
  gap: 8rpx;
  flex-wrap: wrap;
}

.sub-recurrence,
.sub-date,
.sub-next,
.sub-completed {
  font-size: 24rpx;
  color: $text-secondary;
  font-weight: 400;
  line-height: 1.3;
}

.sub-next {
  color: #4A9C9C;
  font-weight: 500;
}

.sub-dot {
  font-size: 24rpx;
  color: $text-tertiary;
}

.sub-important {
  font-size: 22rpx;
  color: $primary;
  font-weight: 500;
  padding: 2rpx 8rpx;
  border-radius: 8rpx;
  background: $primary-light;
}

.card-delete {
  padding: $spacing-xs;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $radius-sm;
  transition: all $transition-fast;
}

.card-delete:active {
  background: $danger-light;
}

.delete-icon {
  font-size: 28rpx;
  color: $text-tertiary;
  line-height: 1;
  transition: all $transition-fast;
}

.card-delete:active .delete-icon {
  color: $danger;
}

.delete-hover {
  transform: scale(0.9);
}
</style>
