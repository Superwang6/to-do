import { API_BASE_URL } from '@/config/index'
import { getToken } from '@/utils/auth'

function request(path, options = {}) {
  const token = getToken()
  const headers = {
    ...options.header,
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  }
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}${path}`,
      ...options,
      header: headers,
	  timeout: 5000,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data?.message || res.data?.detail || 'Request failed'))
        }
      },
      fail: reject,
    })
  })
}

function uploadFile(path, filePath) {
  const token = getToken()
  const headers = {
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  }
  
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${API_BASE_URL}${path}`,
      filePath,
      name: 'file',
      header: headers,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(res.data).data)
        } else {
          reject(new Error(JSON.parse(res.data)?.message || 'Upload failed'))
        }
      },
      fail: reject,
    })
  })
}

export function login(username, password) {
  return request('/api/auth/login', {
    method: 'POST',
    data: { username, password },
    header: { 'Content-Type': 'application/json' },
  })
}

export function register(username, password) {
  return request('/api/auth/register', {
    method: 'POST',
    data: { username, password },
    header: { 'Content-Type': 'application/json' },
  })
}

export function updateProfile(data) {
  return request('/api/user/profile', {
    method: 'PUT',
    data,
    header: { 'Content-Type': 'application/json' },
  })
}

export function uploadAvatar(filePath) {
  return uploadFile('/api/user/avatar', filePath)
}

export function changePassword(data) {
  return request('/api/user/change-password', {
    method: 'POST',
    data,
    header: { 'Content-Type': 'application/json' },
  })
}

export function getSettings() {
  return request('/api/user/settings', {
    method: 'GET',
  })
}

export function updateSettings(data) {
  return request('/api/user/settings', {
    method: 'PUT',
    data,
    header: { 'Content-Type': 'application/json' },
  })
}
