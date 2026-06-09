<template>
  <view class="page">
    <!-- 搜索栏 -->
    <view class="search-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="search-input-wrapper">
        <text class="search-icon">🔍</text>
        <input
          v-model="keyword"
          class="search-input"
          placeholder="搜索待办..."
          confirm-type="search"
          @confirm="onSearch"
          @input="onInput"
        />
        <text
          v-if="keyword"
          class="clear-icon"
          @tap="onClear"
        >✕</text>
      </view>
      <view class="search-btn" v-if="keyword" @tap="onSearch">搜索</view>
      <view class="cancel-btn" @tap="onCancel">取消</view>
    </view>

    <!-- 搜索结果 -->
    <view class="content">
      <LoadingState v-if="loading" />

      <view v-else-if="keyword && results.length === 0" class="empty-state">
        <text class="empty-text">没有找到 "{{ keyword }}"</text>
        <text class="empty-hint">试试换个关键词吧</text>
      </view>

      <scroll-view
        v-else
        class="result-list"
        scroll-y
        enhanced
        show-scrollbar="false"
      >
        <view class="list-inner">
          <TodoCard
            v-for="(item, idx) in results"
            :key="item.id"
            :todo="item"
            :index="idx"
            @toggle="toggleStatus"
            @edit="openEdit"
            @delete="removeTodo"
          />
          <view class="list-bottom" v-if="hasMore" />
        </view>
      </scroll-view>
    </view>

    <todo-edit-sheet
      :visible="showEditSheet"
      :todo="editingTodo || {}"
      @close="onEditClose"
      @saved="onTodoSaved"
    />
  </view>
</template>

<script>
import { searchTodos, updateTodo, completeTodo, deleteTodo, revertTodo } from '@/api/todo'
import TodoEditSheet from '@/components/todo-edit-sheet.vue'
import TodoCard from '@/components/TodoCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'

export default {
  name: 'SearchPage',
  components: {
    TodoCard,
    TodoEditSheet,
    EmptyState,
    LoadingState,
    ErrorState,
  },
  data() {
    return {
      keyword: '',
      results: [],
      loading: false,
      loadingMore: false,
      hasMore: true,
      currentPage: 1,
      pageSize: 50,
      statusBarHeight: 44,
      showEditSheet: false,
      editingTodo: null,
      _toggling: false,
    }
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
    // 自动聚焦搜索框
    if (this.keyword === '') {
      setTimeout(() => {
        uni.createSelectorQuery().select('.search-input input').exec((res) => {
          if (res[0] && res[0].node) {
            res[0].node.focus()
          }
        })
      }, 300)
    }
  },
  methods: {
    onInput() {
      // 输入空了清空结果
      if (!this.keyword.trim()) {
        this.results = []
        this.hasMore = false
      }
    },
    onClear() {
      this.keyword = ''
      this.results = []
      this.hasMore = false
    },
    onCancel() {
      uni.navigateBack()
    },
    async onSearch() {
      const kw = this.keyword.trim()
      if (!kw) {
        uni.showToast({ title: '请输入关键词', icon: 'none' })
        return
      }
      this.loading = true
      this.currentPage = 1
      this.results = []
      try {
        const data = await searchTodos(kw, this.currentPage, this.pageSize)
        // API 返回格式是 data 是列表，total 在顶层
        this.results = Array.isArray(data) ? data : []
        this.hasMore = this.results.length >= this.pageSize
      } catch (e) {
        uni.showToast({ title: e.message || '搜索失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    async loadMore() {
      if (this.loadingMore || !this.hasMore) return
      this.loadingMore = true
      this.currentPage++
      try {
        const data = await searchTodos(this.keyword.trim(), this.currentPage, this.pageSize)
        const newResults = Array.isArray(data) ? data : []
        this.results.push(...newResults)
        this.hasMore = newResults.length >= this.pageSize
      } catch (e) {
        uni.showToast({ title: e.message || '加载失败', icon: 'none' })
        this.currentPage--
      } finally {
        this.loadingMore = false
      }
    },
    async toggleStatus(item) {
      if (this._toggling) return

      const status = item.status === 'completed' ? 'completed' : 'pending'
      this._toggling = true

      try {
        if (status === 'completed') {
          await completeTodo(item.id)
        } else {
          await revertTodo(item.id)
        }
        // 刷新搜索结果
        this.onSearch()
      } catch (e) {
        uni.showToast({ title: e.message || '操作失败', icon: 'none' })
      }

      this._toggling = false
    },
    async removeTodo(item) {
      const confirmed = await this.showConfirmDialog('确认删除', `删除「${item.title}」？`)
      if (confirmed) {
        try {
          await deleteTodo(item.id)
          uni.showToast({ title: '已删除', icon: 'none' })
          this.results = this.results.filter(t => t.id !== item.id)
        } catch (_) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
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
      this.onSearch()
    },
    showConfirmDialog(title, content) {
      return new Promise((resolve) => {
        uni.showModal({
          title,
          content,
          confirmColor: '#C0544A',
          success: (res) => resolve(res.confirm),
          fail: () => resolve(false),
        })
      })
    },
  },
  onReachBottom() {
    if (this.keyword.trim() && this.hasMore && !this.loading) {
      this.loadMore()
    }
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

.search-bar {
  background: $bg-card;
  padding-bottom: $spacing-md;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding-left: $spacing-xl;
  padding-right: $spacing-xl;
}

.search-input-wrapper {
  flex: 1;
  height: 64rpx;
  background: $bg-input;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  padding: 0 $spacing-md;
}

.search-icon {
  font-size: 28rpx;
  color: $text-secondary;
  margin-right: $spacing-xs;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: $text-primary;
  line-height: 1;

  &::placeholder {
    color: $text-tertiary;
  }
}

.clear-icon {
  font-size: 24rpx;
  color: $text-tertiary;
  padding: $spacing-xs;
  flex-shrink: 0;
}

.search-btn {
  font-size: 28rpx;
  color: $primary;
  font-weight: 500;
  flex-shrink: 0;
  padding: $spacing-xs 0;
}

.cancel-btn {
  font-size: 28rpx;
  color: $text-primary;
  flex-shrink: 0;
}

.content {
  flex: 1;
  height: 0;
  overflow: hidden;
  padding: 0 $spacing-xl;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 200rpx;
  gap: 8rpx;
}

.empty-text {
  font-size: 28rpx;
  color: $text-secondary;
}

.empty-hint {
  font-size: 24rpx;
  color: $text-tertiary;
}

.result-list {
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
</style>
