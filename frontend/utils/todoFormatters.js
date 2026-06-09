// utils/todoFormatters.js

/**
 * 格式化日期
 * @param {string} iso - ISO 格式的日期字符串
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const datePart = `${d.getMonth() + 1}/${d.getDate()}`
  if (d.getHours() === 0 && d.getMinutes() === 0) return datePart
  const h = String(d.getHours()).padStart(2, '0')
  const m = String(d.getMinutes()).padStart(2, '0')
  return `${datePart} ${h}:${m}`
}

/**
 * 格式化重复规则
 * @param {Object} rule - 重复规则对象
 * @returns {string} 格式化后的重复规则字符串
 */
export function formatRecurrence(rule) {
  if (!rule) return ''
  const weekNames = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const freqMap = { daily: '每天', weekly: '每周', monthly: '每月', yearly: '每年' }
  let text = freqMap[rule.frequency] || ''
  if (rule.interval && rule.interval > 1) text = `每${rule.interval}` + text.slice(1)
  if (rule.frequency === 'weekly' && rule.days_of_week?.length) {
    text += rule.days_of_week.map(d => weekNames[d]).join('')
  }
  if (rule.frequency === 'monthly' && rule.day_of_month) {
    text += `${rule.day_of_month}号`
  }
  if (rule.frequency === 'yearly' && rule.month_of_year && rule.day_of_month) {
    text += `${rule.month_of_year}月${rule.day_of_month}日`
  }
  if (rule.time_of_day) {
    text += rule.time_of_day
  }
  return text
}

/**
 * 判断是否为未来日期
 * @param {string} iso - ISO 格式的日期字符串
 * @returns {boolean} 是否为未来日期
 */
export function isFutureDate(iso) {
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
}

/**
 * 获取问候语
 * @returns {string} 根据时间返回问候语
 */
export function getGreeting() {
  const h = new Date().getHours()
  if (h < 6) return '夜深了 🌙'
  if (h < 9) return '早上好 ☀️'
  if (h < 12) return '上午好 ✨'
  if (h < 14) return '中午好 🌤'
  if (h < 18) return '下午好 ☕'
  if (h < 22) return '晚上好 🌆'
  return '夜深了 🌙'
}

/**
 * 获取日期字符串
 * @returns {string} 当前日期字符串
 */
export function getDateString() {
  const d = new Date()
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()} 周${weekdays[d.getDay()]}`
}
