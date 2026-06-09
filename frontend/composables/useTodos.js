// composables/useTodos.js
import { fetchTodos, fetchCompletedTodos } from '@/api/todo'

/**
 * 待办事项状态管理
 * @returns {Object} 待办状态和方法
 */
export function useTodos() {
  return {
    data() {
      return {
        todayTodos: [],
        recurringTodos: [],
        onceTodos: [],
        completedTodos: [],
        completedCount: 0,
        completedExpanded: false,
        completedLoading: false,
        loading: false,
        error: false
      }
    },
    computed: {
      totalActive() {
        return this.todayTodos.length + this.recurringTodos.length + this.onceTodos.length
      },
      displayedCompletedTodos() {
        // importantOnly 需要从外部传入，这里先留空，在主组件中实现
        return this.completedTodos
      }
    },
    methods: {
      /**
       * 加载待办事项列表
       * @param {string|null} priority - 优先级筛选
       * @param {string} activeTab - 当前标签
       */
      async loadTodos(priority = null, activeTab = 'all') {
        this.loading = true
        this.error = false
        try {
          const data = await fetchTodos(priority)
          let today = data.today || []
          let recurring = data.recurring || []
          let once = data.once || []
          
          // 客户端筛选周期事项
          if (activeTab === 'recurring') {
            today = today.filter(t => t.type === 'recurring')
            once = []
          }
          
          this.todayTodos = today
          this.recurringTodos = recurring
          this.onceTodos = once
          this.completedCount = data.completed_count || 0
          this.completedExpanded = false
          this.completedTodos = []
        } catch (_) {
          this.error = true
        } finally {
          this.loading = false
        }
      },

      /**
       * 加载已完成事项
       */
      async loadCompletedTodos() {
        if (this.completedLoading) return
        this.completedLoading = true
        try {
          this.completedTodos = await fetchCompletedTodos()
        } catch (_) {
          uni.showToast({ title: '加载失败', icon: 'none' })
        } finally {
          this.completedLoading = false
        }
      },

      /**
       * 切换已完成列表展开/收起
       */
      async toggleCompleted() {
        this.completedExpanded = !this.completedExpanded
        if (this.completedExpanded && this.completedTodos.length === 0) {
          await this.loadCompletedTodos()
        }
      },

      /**
       * 从活跃列表移除待办
       * @param {string|number} id - 待办 ID
       */
      removeFromActive(id) {
        this.todayTodos = this.todayTodos.filter(t => t.id !== id)
        this.recurringTodos = this.recurringTodos.filter(t => t.id !== id)
        this.onceTodos = this.onceTodos.filter(t => t.id !== id)
      },

      /**
       * 从已完成列表移除待办
       * @param {string|number} id - 待办 ID
       */
      removeFromCompleted(id) {
        this.completedTodos = this.completedTodos.filter(t => t.id !== id)
      }
    }
  }
}
