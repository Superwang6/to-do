import { API_BASE_URL } from '@/config/index'
import { getToken } from '@/utils/auth'

function request(path, options = {}) {
  const token = getToken()
  const header = { ...(options.header || {}) }
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}${path}`,
      ...options,
      header,
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync('auth_token')
          uni.removeStorageSync('auth_user')
          uni.reLaunch({ url: '/pages/login/login' })
          return
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data?.detail || res.data?.message || 'Request failed'))
        }
      },
      fail: reject,
    })
  })
}

export function fetchTodos(priority = null) {
  return request('/api/todos/list', {
    method: 'POST',
    data: { page: { page: 1, page_size: 200 }, priority },
    header: { 'Content-Type': 'application/json' },
  })
}

export function fetchCompletedTodos(page = 1, pageSize = 50) {
  return request('/api/todos/list', {
    method: 'POST',
    data: { page: { page, page_size: pageSize }, status: 'completed' },
    header: { 'Content-Type': 'application/json' },
  })
}

export function createTodo(data) {
  return request('/api/todos/save', {
    method: 'POST',
    data,
    header: { 'Content-Type': 'application/json' },
  })
}

export function updateTodo(id, data) {
  return request(`/api/todos/modify/${id}`, {
    method: 'POST',
    data,
    header: { 'Content-Type': 'application/json' },
  })
}

export function completeTodo(id) {
  return request(`/api/todos/complete/${id}`, {
    method: 'POST',
  })
}

export function revertTodo(id) {
  return request(`/api/todos/revert/${id}`, {
    method: 'POST',
  })
}

export function fetchTodoDetail(id) {
  return request(`/api/todos/detail/${id}`)
}

export function deleteTodo(id) {
  return request(`/api/todos/delete/${id}`, {
    method: 'POST',
  })
}

export function uploadAudio(filePath) {
  const token = getToken()
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${API_BASE_URL}/api/voice/upload`,
      filePath,
      name: 'file',
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync('auth_token')
          uni.removeStorageSync('auth_user')
          uni.reLaunch({ url: '/pages/login/login' })
          return
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          const body = JSON.parse(res.data)
          resolve(body.data)
        } else {
          reject(new Error(res.data?.detail || 'Upload failed'))
        }
      },
      fail: reject,
    })
  })
}

export function sendChatText(text, extra = {}) {
  return request('/api/chat/text', {
    method: 'POST',
    data: { text, ...extra },
    header: { 'Content-Type': 'application/json' },
  })
}

export function sendChatVoice(filePath) {
  const token = getToken()
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${API_BASE_URL}/api/chat/audio`,
      filePath,
      name: 'file',
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync('auth_token')
          uni.removeStorageSync('auth_user')
          uni.reLaunch({ url: '/pages/login/login' })
          return
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const body = JSON.parse(res.data)
            resolve(body.data)
          } catch (e) {
            reject(new Error('Invalid response format'))
          }
        } else {
          let detail = 'Upload failed'
          try {
            const parsed = JSON.parse(res.data)
            detail = parsed.detail || parsed.message || detail
          } catch (_) {}
          reject(new Error(detail))
        }
      },
      fail: (err) => {
        reject(err)
      },
    })
  })
}

export function fetchChatMessages(page = 1, pageSize = 200) {
  return request('/api/chat/messages/list', {
    method: 'POST',
    data: { page: { page, page_size: pageSize } },
    header: { 'Content-Type': 'application/json' },
  })
}

export function saveChatMessage(data) {
  return request('/api/chat/messages/save', {
    method: 'POST',
    data,
    header: { 'Content-Type': 'application/json' },
  })
}

export function searchTodos(keyword, page = 1, pageSize = 50) {
  return request('/api/todos/list', {
    method: 'POST',
    data: {
      keyword,
      page: { page, page_size: pageSize },
    },
    header: { 'Content-Type': 'application/json' },
  })
}
