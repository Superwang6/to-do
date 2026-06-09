<template>
  <view v-if="visible" class="sheet-root">
    <!-- Overlay -->
    <view class="sheet-overlay" @tap="cancel" @touchmove.stop.prevent />

    <!-- Panel -->
    <view class="sheet-panel" :class="{ 'sheet-open': animOpen }">
      <view class="sheet-handle" />
      <text class="sheet-title">编辑待办</text>

      <scroll-view class="sheet-body" scroll-y enhanced show-scrollbar="false">
        <!-- Title -->
        <view class="field">
          <text class="field-label">标题</text>
          <input
            v-model="form.title"
            class="field-input"
            placeholder="待办事项名称"
            placeholder-class="ph"
          />
        </view>

        <!-- Priority -->
        <view class="field">
          <text class="field-label">优先级</text>
          <view class="priority-row">
            <view
              v-for="p in priorities"
              :key="p.key"
              class="priority-pill"
              :class="{ active: form.priority === p.key, [p.key]: true }"
              @tap="form.priority = p.key"
            >
              <text>{{ p.label }}</text>
            </view>
          </view>
        </view>

        <!-- Description -->
        <view class="field">
          <text class="field-label">备注</text>
          <textarea
            v-model="form.description"
            class="field-textarea"
            placeholder="添加备注..."
            placeholder-class="ph"
            :auto-height="true"
            :maxlength="500"
          />
        </view>

        <!-- Due Date (once only) -->
        <view v-if="todo.type === 'once'" class="field">
          <text class="field-label">截止日期</text>
          <picker
            mode="date"
            :value="form.due_date || ''"
            :start="minDateStr"
            @change="onDateChange"
          >
            <view class="field-picker">
              <text :class="{ selected: form.due_date }">
                {{ form.due_date ? formatDisplayDate(form.due_date) : '选择日期' }}
              </text>
              <text class="picker-arrow">📅</text>
            </view>
          </picker>
          <view v-if="form.due_date" class="field-clear" @tap="form.due_date = ''">
            <text>清除日期</text>
          </view>
        </view>

        <!-- Recurrence Rule (recurring only) -->
        <view v-if="todo.type === 'recurring'" class="field">
          <text class="field-label">重复规则</text>
          <!-- Frequency -->
          <view class="freq-row">
            <view
              v-for="f in frequencies"
              :key="f.key"
              class="freq-pill"
              :class="{ active: form.recurrence_rule.frequency === f.key }"
              @tap="onFreqChange(f.key)"
            >
              <text>{{ f.label }}</text>
            </view>
          </view>
          <!-- Interval -->
          <view class="sub-row">
            <text class="sub-label">间隔</text>
            <input
              v-model.number="form.recurrence_rule.interval"
              class="field-input interval-input"
              type="number"
              placeholder="1"
              placeholder-class="ph"
            />
            <text class="sub-unit">{{ intervalUnit }}</text>
          </view>
          <!-- Days of week (weekly) -->
          <view v-if="form.recurrence_rule.frequency === 'weekly'" class="sub-row">
            <text class="sub-label">重复日</text>
            <view class="dow-row">
              <view
                v-for="d in weekDays"
                :key="d.value"
                class="dow-dot"
                :class="{ on: form.recurrence_rule.days_of_week.includes(d.value) }"
                @tap="toggleDow(d.value)"
              >
                <text>{{ d.label }}</text>
              </view>
            </view>
          </view>
          <!-- Day of month (monthly) -->
          <view v-if="form.recurrence_rule.frequency === 'monthly'" class="sub-row">
            <text class="sub-label">每月几号</text>
            <input
              v-model.number="form.recurrence_rule.day_of_month"
              class="field-input interval-input"
              type="number"
              placeholder="1"
              placeholder-class="ph"
              :min="1"
              :max="28"
            />
          </view>
          <!-- Month + Day (yearly) -->
          <view v-if="form.recurrence_rule.frequency === 'yearly'" class="sub-row">
            <text class="sub-label">月份</text>
            <input
              v-model.number="form.recurrence_rule.month_of_year"
              class="field-input interval-input"
              type="number"
              placeholder="1"
              placeholder-class="ph"
              :min="1"
              :max="12"
            />
            <text class="sub-label" style="margin-left: 16rpx;">日期</text>
            <input
              v-model.number="form.recurrence_rule.day_of_month"
              class="field-input interval-input"
              type="number"
              placeholder="1"
              placeholder-class="ph"
              :min="1"
              :max="28"
            />
          </view>
          <!-- Time of day -->
          <view class="sub-row">
            <text class="sub-label">提醒时间</text>
            <picker
              mode="time"
              :value="form.recurrence_rule.time_of_day || ''"
              @change="onTimeChange"
            >
              <view class="field-picker time-picker">
                <text :class="{ selected: form.recurrence_rule.time_of_day }">
                  {{ form.recurrence_rule.time_of_day || '不设置' }}
                </text>
                <text class="picker-arrow">🕐</text>
              </view>
            </picker>
          </view>
        </view>
      </scroll-view>

      <!-- Actions -->
      <view class="sheet-actions">
        <view class="btn-cancel" hover-class="btn-hover" @tap="cancel">
          <text>取消</text>
        </view>
        <view
          class="btn-save"
          :class="{ loading: submitting }"
          hover-class="btn-hover"
          @tap="save"
        >
          <text>{{ submitting ? '保存中...' : '保存' }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { updateTodo } from '@/api/todo'

const PRIORITIES = [
  { key: 'low', label: '低' },
  { key: 'medium', label: '中' },
  { key: 'high', label: '高' },
]

const FREQUENCIES = [
  { key: 'daily', label: '每天' },
  { key: 'weekly', label: '每周' },
  { key: 'monthly', label: '每月' },
  { key: 'yearly', label: '每年' },
]

const WEEK_DAYS = [
  { value: 1, label: '一' },
  { value: 2, label: '二' },
  { value: 3, label: '三' },
  { value: 4, label: '四' },
  { value: 5, label: '五' },
  { value: 6, label: '六' },
  { value: 7, label: '日' },
]

export default {
  props: {
    visible: { type: Boolean, default: false },
    todo: { type: Object, default: () => ({}) },
  },
  data() {
    return {
      animOpen: false,
      submitting: false,
      form: { title: '', priority: 'medium', description: '', due_date: '', recurrence_rule: {} },
      priorities: PRIORITIES,
      frequencies: FREQUENCIES,
      weekDays: WEEK_DAYS,
      minDateStr: '',
    }
  },
  computed: {
    intervalUnit() {
      const map = { daily: '天', weekly: '周', monthly: '月', yearly: '年' }
      return map[this.form.recurrence_rule.frequency] || ''
    },
  },
  watch: {
    visible(val) {
      if (val) {
        this.initForm()
        this.$nextTick(() => { this.animOpen = true })
      } else {
        this.animOpen = false
      }
    },
  },
  created() {
    const d = new Date()
    this.minDateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  },
  methods: {
    initForm() {
      const t = this.todo || {}
      this.form.title = t.title || ''
      this.form.priority = t.priority || 'medium'
      this.form.description = t.description || ''
      this.form.due_date = t.due_date ? t.due_date.slice(0, 10) : ''

      const rule = t.recurrence_rule || {}
      this.form.recurrence_rule = {
        frequency: rule.frequency || 'daily',
        interval: rule.interval || 1,
        days_of_week: rule.days_of_week ? [...rule.days_of_week] : [],
        day_of_month: rule.day_of_month || null,
        month_of_year: rule.month_of_year || null,
        time_of_day: rule.time_of_day || '',
      }
    },

    resetForm() {
      this.form = {
        title: '',
        priority: 'medium',
        description: '',
        due_date: '',
        recurrence_rule: {
          frequency: 'daily',
          interval: 1,
          days_of_week: [],
          day_of_month: null,
          month_of_year: null,
          time_of_day: '',
        },
      }
    },

    onFreqChange(freq) {
      this.form.recurrence_rule.frequency = freq
      // Reset conditional fields
      this.form.recurrence_rule.days_of_week = []
      this.form.recurrence_rule.day_of_month = null
      this.form.recurrence_rule.month_of_year = null
    },

    toggleDow(val) {
      const arr = this.form.recurrence_rule.days_of_week
      const idx = arr.indexOf(val)
      if (idx >= 0) {
        arr.splice(idx, 1)
      } else {
        arr.push(val)
      }
    },

    onDateChange(e) {
      this.form.due_date = e.detail.value
    },

    onTimeChange(e) {
      this.form.recurrence_rule.time_of_day = e.detail.value
    },

    formatDisplayDate(iso) {
      if (!iso) return ''
      const parts = iso.split('-')
      return `${parts[0]}年${parseInt(parts[1])}月${parseInt(parts[2])}日`
    },

    cancel() {
      this.animOpen = false
      setTimeout(() => {
        this.resetForm()
        this.$emit('close')
      }, 250)
    },

    async save() {
      if (this.submitting) return
      const title = this.form.title.trim()
      if (!title) {
        uni.showToast({ title: '标题不能为空', icon: 'none' })
        return
      }

      this.submitting = true
      try {
        const payload = {
          title,
          priority: this.form.priority,
          description: this.form.description || null,
        }

        if (this.todo.type === 'once') {
          payload.due_date = this.form.due_date
            ? this.form.due_date + 'T00:00:00'
            : null
        }

        if (this.todo.type === 'recurring') {
          const rule = { ...this.form.recurrence_rule }
          if (!rule.time_of_day) delete rule.time_of_day
          if (rule.frequency !== 'weekly') delete rule.days_of_week
          if (rule.frequency !== 'monthly') delete rule.day_of_month
          if (rule.frequency !== 'yearly') {
            delete rule.month_of_year
            delete rule.day_of_month
          }
          payload.recurrence_rule = rule
        }

        await updateTodo(this.todo.id, payload)
        uni.showToast({ title: '已保存', icon: 'success' })
        this.submitting = false
        this.animOpen = false
        setTimeout(() => {
          this.resetForm()
          this.$emit('saved')
          this.$emit('close')
        }, 250)
      } catch (e) {
        this.submitting = false
        uni.showToast({ title: e.message || '保存失败', icon: 'none' })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
// ── Root ──
.sheet-root {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99999;
  width: 100vw;
  box-sizing: border-box;
}

// ── Overlay ──
.sheet-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(45, 42, 38, 0.4);
  animation: fadeIn 0.25s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

// ── Panel ──
.sheet-panel {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100%;
  max-width: 100vw;
  box-sizing: border-box;
  max-height: 80vh;
  background: #FFFFFF;
  border-radius: 28rpx 28rpx 0 0;
  display: flex;
  flex-direction: column;
  transform: translateY(100%);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  padding-bottom: calc(env(safe-area-inset-bottom) + 16rpx);
  overflow: hidden;
}

.sheet-panel.sheet-open {
  transform: translateY(0);
}

// ── Handle ──
.sheet-handle {
  width: 56rpx;
  height: 6rpx;
  border-radius: 3rpx;
  background: #E0DCD5;
  margin: 16rpx auto 0;
}

// ── Title ──
.sheet-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #2D2A26;
  text-align: center;
  padding: 20rpx 0 16rpx;
  display: block;
}

// ── Body ──
.sheet-body {
  flex: 1;
  height: 0;
  padding: 0 32rpx;
  overflow-y: auto;
  width: 100%;
  box-sizing: border-box;
  max-width: 100vw;
}

// ── Field ──
.field {
  margin-bottom: 24rpx;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.field-label {
  font-size: 24rpx;
  color: #978E84;
  margin-bottom: 10rpx;
  display: block;
  font-weight: 500;
}

.field-input {
  width: 100%;
  height: 80rpx;
  background: #F3F0EC;
  border-radius: 14rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #2D2A26;
  box-sizing: border-box;
  max-width: 100%;
}

.field-textarea {
  width: 100%;
  min-height: 80rpx;
  background: #F3F0EC;
  border-radius: 14rpx;
  padding: 16rpx 20rpx;
  font-size: 28rpx;
  color: #2D2A26;
  box-sizing: border-box;
  max-width: 100%;
}

.ph {
  color: #C4BCB2;
  font-size: 28rpx;
}

// ── Priority ──
.priority-row {
  display: flex;
  gap: 12rpx;
}

.priority-pill {
  flex: 1;
  height: 64rpx;
  border-radius: 14rpx;
  background: #F3F0EC;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  color: #978E84;
  transition: all 0.2s ease;
}

.priority-pill.active {
  color: #FFFFFF;
  font-weight: 500;
}

.priority-pill.active.low { background: #6A8F6A; }
.priority-pill.active.medium { background: #C4905C; }
.priority-pill.active.high { background: #C0544A; }

// ── Date picker ──
.field-picker {
  height: 80rpx;
  background: #F3F0EC;
  border-radius: 14rpx;
  padding: 0 20rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 28rpx;
  color: #C4BCB2;
}

.field-picker .selected {
  color: #2D2A26;
}

.picker-arrow {
  font-size: 28rpx;
}

.field-clear {
  margin-top: 8rpx;
  text-align: right;
  font-size: 22rpx;
  color: #C0544A;
}

// ── Frequency ──
.freq-row {
  display: flex;
  gap: 10rpx;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.freq-pill {
  flex: 1;
  height: 60rpx;
  border-radius: 14rpx;
  background: #F3F0EC;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #978E84;
  transition: all 0.2s ease;
  min-width: 0;
}

.freq-pill.active {
  background: #C0544A;
  color: #FFFFFF;
  font-weight: 500;
}

// ── Sub rows ──
.sub-row {
  display: flex;
  align-items: center;
  margin-top: 16rpx;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  flex-wrap: wrap;
}

.sub-label {
  font-size: 24rpx;
  color: #978E84;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.sub-unit {
  font-size: 24rpx;
  color: #978E84;
  margin-left: 12rpx;
  flex-shrink: 0;
}

.interval-input {
  width: 120rpx;
  height: 64rpx;
  text-align: center;
  flex-shrink: 0;
}

// ── Days of week ──
.dow-row {
  display: flex;
  gap: 8rpx;
  flex-wrap: wrap;
}

.dow-dot {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F3F0EC;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  color: #978E84;
  transition: all 0.2s ease;
}

.dow-dot.on {
  background: #C0544A;
  color: #FFFFFF;
}

.time-picker {
  flex: 1;
}

// ── Actions ──
.sheet-actions {
  display: flex;
  gap: 20rpx;
  padding: 20rpx 32rpx;
  border-top: 1rpx solid #F5F1EC;
  margin-top: 8rpx;
  width: 100%;
  box-sizing: border-box;
}

.btn-cancel, .btn-save {
  flex: 1;
  height: 88rpx;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: #F3F0EC;
  color: #978E84;
}

.btn-save {
  background: #C0544A;
  color: #FFFFFF;
}

.btn-save.loading {
  opacity: 0.7;
}

.btn-hover {
  opacity: 0.75;
  transform: scale(0.97);
}
</style>
