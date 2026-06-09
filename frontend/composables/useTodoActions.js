// composables/useTodoActions.js
import { completeTodo, updateTodo, deleteTodo } from '@/api/todo'
import { isFutureDate } from '@/utils/todoFormatters'

/**
 * 待办事项操作逻辑
 * @param {Object} context - 组件上下文
 * @returns {Object} 操作方法
 */
export function useTodoActions(context) {
  return {
    methods: {
      /**
       * 切换待办状态
       * @param {Object} item - 待办对象
       */
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

      /**
       * 处理周期事项完成
       * @param {Object} item - 待办对象
       */
      async handleRecurringPending(item) {
        this._toggling = true
        const isFuture = item.due_date && isFutureDate(item.due_date)
        
        const title = isFuture ? '提前完成周期事项' : '完成周期事项'
        const content = isFuture
          ? `「${item.title}」的下次截止日期还未到，确认提前完成吗？完成将自动顺延到下一个周期。`
          : `确认完成「${item.title}」？完成将自动顺延到下一个周期。`
        
        const confirmed = await this.showConfirmDialog(title, content)
        
        if (confirmed) {
          try {
            await completeTodo(item.id)
            await context.loadTodos?.()
          } catch (e) {
            uni.showToast({ title: e.message || '操作失败', icon: 'none' })
          }
        }
        
        this._toggling = false
      },

      /**
       * 处理周期事项已完成（不可取消）
       */
      handleRecurringCompleted() {
        uni.showToast({ title: '周期事项请通过模板完成', icon: 'none' })
      },

      /**
       * 处理单次事项取消完成
       * @param {Object} item - 待办对象
       */
      async handleOnceUncomplete(item) {
        this._toggling = true
        try {
          await updateTodo(item.id, { status: 'pending' })
          item.status = 'pending'
          context.completedCount = Math.max(0, context.completedCount - 1)
          context.removeFromCompleted?.(item.id)
          await context.loadTodos?.()
        } catch (e) {
          uni.showToast({ title: e.message || '操作失败', icon: 'none' })
        } finally {
          this._toggling = false
        }
      },

      /**
       * 处理单次事项完成
       * @param {Object} item - 待办对象
       */
      async handleOnceComplete(item) {
        this._toggling = true
        const isFuture = item.due_date && isFutureDate(item.due_date)
        
        const title = isFuture ? '提前完成' : '完成待办'
        const content = isFuture
          ? `「${item.title}」的截止日期还未到，确认提前完成吗？`
          : `确认完成「${item.title}」？`
        
        const confirmed = await this.showConfirmDialog(title, content)
        
        if (confirmed) {
          await this.doCompleteOnce(item)
        }
        
        this._toggling = false
      },

      /**
       * 执行单次事项完成
       * @param {Object} item - 待办对象
       */
      async doCompleteOnce(item) {
        try {
          await updateTodo(item.id, { status: 'completed' })
          item.status = 'completed'
          context.completedCount = (context.completedCount || 0) + 1
          context.removeFromActive?.(item.id)
        } catch (e) {
          uni.showToast({ title: e.message || '操作失败', icon: 'none' })
        }
      },

      /**
       * 删除待办
       * @param {Object} item - 待办对象
       */
      async removeTodo(item) {
        const confirmed = await this.showConfirmDialog('确认删除', `删除「${item.title}」？`)
        
        if (confirmed) {
          try {
            await deleteTodo(item.id)
            context.removeFromActive?.(item.id)
            context.removeFromCompleted?.(item.id)
            if (item.status === 'completed') {
              context.completedCount = Math.max(0, (context.completedCount || 0) - 1)
            }
            uni.showToast({ title: '已删除', icon: 'none' })
          } catch (_) {
            uni.showToast({ title: '删除失败', icon: 'none' })
          }
        }
      },

      /**
       * 显示确认对话框
       * @param {string} title - 标题
       * @param {string} content - 内容
       * @returns {Promise<boolean>} 是否确认
       */
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
      }
    },
    data() {
      return {
        _toggling: false
      }
    }
  }
}
