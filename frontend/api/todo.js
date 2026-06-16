import { request, uploadFile } from './request'

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
  return uploadFile('/api/voice/upload', filePath)
}

export function sendChatText(text, extra = {}) {
  return request('/api/chat/text', {
    method: 'POST',
    data: { text, ...extra },
    header: { 'Content-Type': 'application/json' },
  })
}

export function sendChatVoice(filePath) {
  return uploadFile('/api/chat/audio', filePath)
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
