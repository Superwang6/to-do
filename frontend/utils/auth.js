const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

export function getToken() {
  return uni.getStorageSync(TOKEN_KEY) || ''
}

export function setToken(token) {
  uni.setStorageSync(TOKEN_KEY, token)
}

export function removeToken() {
  uni.removeStorageSync(TOKEN_KEY)
  uni.removeStorageSync(USER_KEY)
}

export function getUser() {
  return uni.getStorageSync(USER_KEY) || null
}

export function setUser(user) {
  uni.setStorageSync(USER_KEY, user)
}

export function isLoggedIn() {
  return !!getToken()
}
