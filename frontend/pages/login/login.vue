<template>
  <view class="page">
    <view class="card">
      <view class="header">
        <text class="logo">&#x270D;</text>
        <text class="title">Todo App</text>
        <text class="subtitle">语音智能待办清单</text>
      </view>

      <view class="form">
        <view class="input-group">
          <text class="label">用户名</text>
          <input
            class="input"
            v-model="username"
            placeholder="请输入用户名"
            placeholder-style="color: #C4BCB2"
          />
        </view>

        <view class="input-group">
          <text class="label">密码</text>
          <input
            class="input"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            placeholder-style="color: #C4BCB2"
          />
        </view>

        <view class="input-group" v-if="isRegister">
          <text class="label">确认密码</text>
          <input
            class="input"
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            placeholder-style="color: #C4BCB2"
          />
        </view>

        <view class="btn" @tap="submit">
          <text class="btn-text">{{ isRegister ? '注册' : '登录' }}</text>
        </view>
      </view>

      <view class="toggle" @tap="toggleMode">
        <text class="toggle-text">
          {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
        </text>
      </view>
    </view>
  </view>
</template>

<script>
import { login, register } from '@/api/auth'
import { setToken, setUser, isLoggedIn } from '@/utils/auth'

export default {
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      isRegister: false,
    }
  },
  onLoad() {
    if (isLoggedIn()) {
      uni.reLaunch({ url: '/pages/index/index' })
    }
  },
  methods: {
    toggleMode() {
      this.isRegister = !this.isRegister
      this.username = ''
      this.password = ''
      this.confirmPassword = ''
    },
    async submit() {
      const name = this.username.trim()
      const pass = this.password
      if (!name || !pass) {
        uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
        return
      }
      if (this.isRegister) {
        if (pass !== this.confirmPassword) {
          uni.showToast({ title: '两次密码不一致', icon: 'none' })
          return
        }
        if (pass.length < 6) {
          uni.showToast({ title: '密码至少6位', icon: 'none' })
          return
        }
      }
      try {
        const fn = this.isRegister ? register : login
        const result = await fn(name, pass)
        setToken(result.token)
        setUser({ user_id: result.user_id, username: result.username })
        uni.reLaunch({ url: '/pages/index/index' })
      } catch (e) {
        uni.showToast({ title: e.message || '操作失败', icon: 'none' })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $bg-page;
  padding: 40rpx;
}

.card {
  width: 100%;
  max-width: 600rpx;
  background: #fff;
  border-radius: 28rpx;
  padding: 60rpx 48rpx 40rpx;
  box-shadow: $shadow-md;
}

.header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 48rpx;
}

.logo {
  font-size: 56rpx;
  margin-bottom: 16rpx;
}

.title {
  font-size: 40rpx;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 8rpx;
}

.subtitle {
  font-size: 26rpx;
  color: $text-secondary;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 28rpx;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.label {
  font-size: 26rpx;
  color: $text-secondary;
  padding-left: 4rpx;
}

.input {
  height: 88rpx;
  background: $bg-input;
  border-radius: 18rpx;
  padding: 0 28rpx;
  font-size: 30rpx;
  color: $text-primary;
}

.btn {
  height: 92rpx;
  background: $primary;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 12rpx;
}

.btn-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}

.toggle {
  display: flex;
  justify-content: center;
  margin-top: 36rpx;
}

.toggle-text {
  font-size: 26rpx;
  color: $primary;
}
</style>
