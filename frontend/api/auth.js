import { request, uploadFile } from './request'

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
  return request('/api/user/profile/modify', {
    method: 'POST',
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
  return request('/api/user/settings/modify', {
    method: 'POST',
    data,
    header: { 'Content-Type': 'application/json' },
  })
}
