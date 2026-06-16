import { API_BASE_URL } from '@/config/index'
import { getToken, removeToken } from '@/utils/auth'

function buildHeader(header = {}) {
  const token = getToken()
  return {
    ...header,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

function parseUploadBody(data) {
  if (!data) return {}
  if (typeof data === 'object') return data
  try {
    return JSON.parse(data)
  } catch (_) {
    throw new Error('服务响应格式异常')
  }
}

function getErrorMessage(body, fallback) {
  return body?.message || body?.detail || fallback
}

function handleUnauthorized(reject) {
  removeToken()
  uni.reLaunch({ url: '/pages/login/login' })
  reject(new Error('登录已过期，请重新登录'))
}

export function request(path, options = {}) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}${path}`,
      ...options,
      header: buildHeader(options.header),
      success: (res) => {
        if (res.statusCode === 401) {
          handleUnauthorized(reject)
          return
        }

        const body = res.data || {}
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(body.data)
          return
        }

        reject(new Error(getErrorMessage(body, 'Request failed')))
      },
      fail: reject,
    })
  })
}

export function uploadFile(path, filePath, options = {}) {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${API_BASE_URL}${path}`,
      filePath,
      name: options.name || 'file',
      header: buildHeader(options.header),
      formData: options.formData,
      success: (res) => {
        if (res.statusCode === 401) {
          handleUnauthorized(reject)
          return
        }

        let body
        try {
          body = parseUploadBody(res.data)
        } catch (error) {
          reject(error)
          return
        }

        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(body.data)
          return
        }

        reject(new Error(getErrorMessage(body, 'Upload failed')))
      },
      fail: reject,
    })
  })
}
