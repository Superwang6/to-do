<template>
  <view class="page">
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <view class="header-top">
          <view class="header-left">
            <text class="greeting">{{ greeting }}</text>
            <text class="date-label">{{ dateStr }}</text>
          </view>
          <view class="header-right">
            <view class="search-btn" @tap="goSearch" hover-class="search-btn-hover">
              <text class="search-icon">🔍</text>
            </view>
          </view>
        </view>
        <FilterBar
          :stats="stats"
          :active-tab="activeTab"
          :important-only="importantOnly"
          @tab-change="switchTab"
          @toggle-important="toggleImportant"
        />
      </view>
    </view>

    <view class="content">
      <LoadingState v-if="loading" />

      <ErrorState v-else-if="error" @retry="onRetry" />

      <scroll-view
        v-else-if="activeTab !== 'completed' && totalActive > 0"
        class="list-scroll"
        scroll-y
        enhanced
        show-scrollbar="false"
      >
        <view class="list-inner">
          <TodoSection
            title="今天"
            icon="📍"
            :items="todayTodos"
            section="today"
            @toggle="toggleStatus"
            @edit="openEdit"
            @delete="removeTodo"
          />
          <TodoSection
            title="单次待办"
            icon="📋"
            :items="onceTodos"
            section="once"
            @toggle="toggleStatus"
            @edit="openEdit"
            @delete="removeTodo"
          />
          <TodoSection
            title="周期待办"
            icon="🔄"
            :items="recurringTodos"
            section="recurring"
            @toggle="toggleStatus"
            @edit="openEdit"
            @delete="removeTodo"
          />

          <TodoSection
            title="已完成"
            icon="✅"
            :items="displayedCompletedTodos"
            :collapsible="true"
            :expanded="completedExpanded"
            @toggle="toggleStatus"
            @edit="openEdit"
            @delete="removeTodo"
            @header-tap="toggleCompleted"
          />

          <view class="list-bottom" />
        </view>
      </scroll-view>

      <scroll-view
        v-else-if="activeTab === 'completed'"
        class="list-scroll"
        scroll-y
        enhanced
        show-scrollbar="false"
      >
        <view class="list-inner">
          <TodoCard
            v-for="(item, idx) in displayedCompletedTodos"
            :key="item.id"
            :todo="item"
            :index="idx"
            @toggle="toggleStatus"
            @edit="openEdit"
            @delete="removeTodo"
          />
          <view v-if="displayedCompletedTodos.length === 0 && !completedLoading" class="state-wrap state-mini">
            <text class="state-desc">暂无已完成事项</text>
          </view>
          <view class="list-bottom" />
        </view>
      </scroll-view>

      <EmptyState v-else />
    </view>

    <view class="fab" @tap="goChat" hover-class="fab-hover">
      <view class="fab-pulse" />
      <view class="fab-pulse fab-pulse-2" />
      <view class="fab-inner">
        <text class="fab-icon">💬</text>
      </view>
    </view>

    <todo-edit-sheet
      :visible="showEditSheet"
      :todo="editingTodo || {}"
      @close="onEditClose"
      @saved="onTodoSaved"
    />

    <custom-tabbar current="/pages/index/index" />
  </view>
</template>

<script>
import { fetchTodos, fetchCompletedTodos, updateTodo, completeTodo, deleteTodo, revertTodo } from '@/api/todo'
import TodoEditSheet from '@/components/todo-edit-sheet.vue'
import FilterBar from '@/components/FilterBar.vue'
import TodoCard from '@/components/TodoCard.vue'
import TodoSection from '@/components/TodoSection.vue'
import EmptyState from '@/components/EmptyState.vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import CustomTabbar from '@/components/custom-tabbar.vue'
import { getGreeting, getDateString } from '@/utils/todoFormatters'
import { useTodos } from '@/composables/useTodos'
import { useTodoActions } from '@/composables/useTodoActions'

export default {
  components: {
    TodoEditSheet,
    FilterBar,
    TodoCard,
    TodoSection,
    EmptyState,
    LoadingState,
    ErrorState,
    CustomTabbar
  },
  mixins: [useTodos()],
  data() {
    return {
      activeTab: 'all',
      importantOnly: false,
      statusBarHeight: 44,
      showEditSheet: false,
      editingTodo: null,
      _toggling: false
    }
  },
  computed: {
    greeting() {
      return getGreeting()
    },
    dateStr() {
      return getDateString()
    },
    stats() {
      const active = this.totalActive
      const recurring = this.todayTodos.filter(t => t.type === 'recurring').length +
        this.recurringTodos.length
      return [
        { key: 'all', label: '全部', value: active + this.completedCount },
        { key: 'pending', label: '待完成', value: active },
        { key: 'completed', label: '已完成', value: this.completedCount },
        { key: 'recurring', label: '周期', value: recurring },
      ]
    },
    displayedCompletedTodos() {
      if (this.importantOnly) {
        return this.completedTodos.filter(t => t.priority === 'high')
      }
      return this.completedTodos
    },
  },
  onLoad() {
    try {
      const sys = uni.getSystemInfoSync()
      this.statusBarHeight = sys.statusBarHeight || 44
    } catch (_) {
      this.statusBarHeight = 44
    }
  },
  onShow() {
    if (this.activeTab === 'completed') {
      this.loadCompletedTodos()
    } else {
      this.loadTodos(this.importantOnly ? 'high' : null, this.activeTab)
    }
  },
  methods: {
    async toggleStatus(item) {
      if (this._toggling) return

      const status = item.status === 'completed' ? 'completed' : 'pending'
      const key = `${item.type}-${status}`

      const strategies = {
        'recurring-pending': this.handleRecurringPending,
        'recurring-completed': this.handleRecurringCompleted,
        'once-completed': this.handleOnceUncomplete,
        'once-pending': this.handleOnceComplete
      }

      const handler = strategies[key]
      if (handler) {
        await handler.call(this, item)
      }
    },

    async handleRecurringPending(item) {
      const isFuture = item.due_date && this.isFutureDate(item.due_date)
      this._toggling = true

      const confirmed = await this.showConfirmDialog(
        isFuture ? '提前完成周期事项' : '完成周期事项',
        isFuture
          ? `「${item.title}」的下次截止日期还未到，确认提前完成吗？完成将自动顺延到下一个周期。`
          : `确认完成「${item.title}」？完成将自动顺延到下一个周期。`
      )

      if (confirmed) {
        try {
          await completeTodo(item.id)
          await this.loadTodos(this.importantOnly ? 'high' : null, this.activeTab)
        } catch (e) {
          uni.showToast({ title: e.message || '操作失败', icon: 'none' })
        }
      }

      this._toggling = false
    },

    handleRecurringCompleted() {
      uni.showToast({ title: '周期事项请通过模板完成', icon: 'none' })
    },

    async handleOnceUncomplete(item) {
      this._toggling = true
      try {
        await revertTodo(item.id)
        item.status = 'pending'
        this.completedCount = Math.max(0, this.completedCount - 1)
        this.removeFromCompleted(item.id)
        await this.loadTodos(this.importantOnly ? 'high' : null, this.activeTab)
      } catch (e) {
        uni.showToast({ title: e.message || '操作失败', icon: 'none' })
      } finally {
        this._toggling = false
      }
    },

    async handleOnceComplete(item) {
      const isFuture = item.due_date && this.isFutureDate(item.due_date)
      this._toggling = true

      const confirmed = await this.showConfirmDialog(
        isFuture ? '提前完成' : '完成待办',
        isFuture
          ? `「${item.title}」的截止日期还未到，确认提前完成吗？`
          : `确认完成「${item.title}」？`
      )

      if (confirmed) {
        await this.doCompleteOnce(item)
      }

      this._toggling = false
    },

    async doCompleteOnce(item) {
      try {
        await updateTodo(item.id, { status: 'completed' })
        item.status = 'completed'
        this.completedCount++
        this.removeFromActive(item.id)
      } catch (e) {
        uni.showToast({ title: e.message || '操作失败', icon: 'none' })
      }
    },

    async removeTodo(item) {
      const confirmed = await this.showConfirmDialog('确认删除', `删除「${item.title}」？`)
      if (confirmed) {
        try {
          await deleteTodo(item.id)
          this.removeFromActive(item.id)
          this.removeFromCompleted(item.id)
          if (item.status === 'completed') {
            this.completedCount = Math.max(0, this.completedCount - 1)
          }
          uni.showToast({ title: '已删除', icon: 'none' })
        } catch (_) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    },

    isFutureDate(iso) {
      if (!iso) return false
      const match = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})/)
      if (!match) return false
      const isoYear = parseInt(match[1], 10)
      const isoMonth = parseInt(match[2], 10)
      const isoDay = parseInt(match[3], 10)
      const today = new Date()
      if (isoYear !== today.getFullYear()) return isoYear > today.getFullYear()
      if (isoMonth !== today.getMonth() + 1) return isoMonth > today.getMonth() + 1
      return isoDay > today.getDate()
    },

    showConfirmDialog(title, content) {
      return new Promise((resolve) => {
        uni.showModal({
          title,
          content,
          confirmColor: '#C0544A',
          success: (res) => resolve(res.confirm),
          fail: () => resolve(false)
        })
      })
    },

    switchTab(key) {
      if (this.activeTab === key) return
      this.activeTab = key
      if (key === 'completed') {
        this.loadCompletedTodos()
      } else {
        this.loadTodos(this.importantOnly ? 'high' : null, key)
      }
    },

    toggleImportant() {
      this.importantOnly = !this.importantOnly
      if (this.activeTab === 'completed') {
        this.loadCompletedTodos()
      } else {
        this.loadTodos(this.importantOnly ? 'high' : null, this.activeTab)
      }
    },

    onRetry() {
      this.loadTodos(this.importantOnly ? 'high' : null, this.activeTab)
    },

    goChat() {
      uni.navigateTo({ url: '/pages/chat/chat' })
    },

    goSearch() {
      uni.navigateTo({ url: '/pages/search/search' })
    },

    openEdit(todo) {
      this.editingTodo = todo
      this.showEditSheet = true
    },

    onEditClose() {
      this.showEditSheet = false
      this.editingTodo = null
    },

    onTodoSaved() {
      this.showEditSheet = false
      this.editingTodo = null
      this.loadTodos(this.importantOnly ? 'high' : null, this.activeTab)
      if (this.activeTab === 'completed') {
        this.loadCompletedTodos()
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.page {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: $bg-page;
}

.header {
  background: linear-gradient(180deg, $bg-page 0%, $bg-card 120%);
  padding-bottom: $spacing-lg;
}

.header-inner {
  width: 100%;
  box-sizing: border-box;
  padding: 0 $spacing-xl;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: $spacing-md;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.greeting {
  font-size: 34rpx;
  font-weight: 600;
  color: $text-primary;
  letter-spacing: 1rpx;
}

.date-label {
  font-size: 24rpx;
  color: $text-secondary;
  letter-spacing: 0.5rpx;
}

.header-right {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  width: 72rpx;
}

.search-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: $bg-input;
  transition: all $transition-fast;
}

.search-btn-hover {
  transform: scale(0.92);
}

.search-icon {
  font-size: 32rpx;
}

.content {
  flex: 1;
  height: 0;
  overflow: hidden;
  padding: 0 $spacing-xl;
}

.list-scroll {
  height: 100%;
  overflow: hidden;
}

.list-inner {
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  padding: $spacing-sm 0;
}

.list-bottom {
  height: 200rpx;
}

.state-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 200rpx;
  animation: stateFadeIn 0.4s ease-out;
}

.state-wrap.state-mini {
  padding-top: 40rpx;
}

@keyframes stateFadeIn {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: translateY(0); }
}

.state-desc {
  font-size: 26rpx;
  color: $text-tertiary;
  text-align: center;
}

.fab {
  position: fixed;
  right: 40rpx;
  bottom: calc(16rpx + 100rpx + env(safe-area-inset-bottom, 0rpx));
  width: 108rpx;
  height: 108rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.fab-inner {
  width: 108rpx;
  height: 108rpx;
  border-radius: $radius-full;
  background: $primary-gradient;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 28rpx rgba(192, 84, 74, 0.35);
  position: relative;
  z-index: 2;
  transition: $transition-spring;
}

.fab-icon {
  font-size: 40rpx;
}

.fab-hover .fab-inner {
  transform: scale(0.92);
}

.fab-pulse {
  position: absolute;
  inset: 0;
  border-radius: $radius-full;
  background: rgba(192, 84, 74, 0.2);
  z-index: 1;
  animation: pulseRing 2.5s ease-out infinite;
}

.fab-pulse-2 {
  animation-delay: 1.25s;
}

@keyframes pulseRing {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}
</style>
