<template>
  <view class="page">
    <!-- ==================== Header ==================== -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="header-back" @tap="onBack">‹</text>
        <text class="header-title">修改密码</text>
        <view class="header-right"></view>
      </view>
    </view>

    <!-- ==================== Content ==================== -->
    <scroll-view class="content-scroll" scroll-y enhanced show-scrollbar="false">
      <view class="content-inner">
        <!-- ── Form Section ── -->
        <view class="form-section">
          <!-- Current Password -->
          <view class="form-item">
            <text class="form-label">当前密码</text>
            <view class="form-control">
              <input 
                v-model="form.currentPassword" 
                class="form-input" 
                placeholder="请输入当前密码"
                type="password"
                password
              />
            </view>
          </view>

          <view class="form-divider" />

          <!-- New Password -->
          <view class="form-item">
            <text class="form-label">新密码</text>
            <view class="form-control">
              <input 
                v-model="form.newPassword" 
                class="form-input" 
                placeholder="请输入新密码（至少6位）"
                type="password"
                password
              />
            </view>
          </view>

          <view class="form-divider" />

          <!-- Confirm Password -->
          <view class="form-item">
            <text class="form-label">确认密码</text>
            <view class="form-control">
              <input 
                v-model="form.confirmPassword" 
                class="form-input" 
                placeholder="请再次输入新密码"
                type="password"
                password
              />
            </view>
          </view>
        </view>

        <!-- ── Save Button ── -->
        <view class="save-btn" @tap="onSave" :class="{ 'btn-disabled': !isFormValid }" :disabled="!isFormValid">
          <text class="save-text">保存修改</text>
        </view>

        <view class="bottom-spacer" />
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { changePassword } from '@/api/auth'

export default {
  data() {
    return {
      statusBarHeight: 44,
      form: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      },
    }
  },
  computed: {
    isFormValid() {
      return this.form.currentPassword && 
             this.form.newPassword.length >= 6 && 
             this.form.newPassword === this.form.confirmPassword
    },
  },
  onLoad() {
    try {
      const sys = uni.getSystemInfoSync()
      this.statusBarHeight = sys.statusBarHeight || 44
    } catch (_) {
      this.statusBarHeight = 44
    }
  },
  methods: {
    onBack() {
      uni.navigateBack()
    },
    async onSave() {
      if (!this.isFormValid) return

      try {
        uni.showLoading({ title: '保存中...' })
        const response = await changePassword({
          current_password: this.form.currentPassword,
          new_password: this.form.newPassword,
        })
        if (response.success) {
          uni.showToast({ title: '密码修改成功', icon: 'success' })
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        } else {
          uni.showToast({ title: response.message || '修改失败', icon: 'none' })
        }
      } catch (error) {
        console.error('Failed to change password:', error)
        uni.showToast({ title: '修改失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
  },
}
</script>

<style lang="scss" scoped>
// =============================================
//  Page Layout
// =============================================
.page {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  background: $bg-page;
  display: flex;
  flex-direction: column;
}

// =============================================
//  Header
// =============================================
.header {
  background: $bg-card;
  border-bottom: 1rpx solid $border;
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
  padding: 0 $spacing-xl;
}

.header-back {
  font-size: 40rpx;
  color: $text-primary;
  width: 40rpx;
}

.header-title {
  font-size: 34rpx;
  font-weight: 600;
  color: $text-primary;
}

.header-right {
  width: 40rpx;
}

// =============================================
//  Content
// =============================================
.content-scroll {
  flex: 1;
  height: 0;
  overflow: hidden;
}

.content-inner {
  width: 100%;
  box-sizing: border-box;
  padding: $spacing-lg $spacing-xl;
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

// =============================================
//  Form Section
// =============================================
.form-section {
  background: $bg-card;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

.form-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-lg $spacing-xl;
}

.form-label {
  font-size: 30rpx;
  color: $text-primary;
  width: 140rpx;
}

.form-control {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.form-input {
  font-size: 30rpx;
  color: $text-primary;
  text-align: right;
  width: 100%;
  padding: 10rpx 0;
}

.form-divider {
  height: 1rpx;
  background: $border;
  margin-left: 140rpx;
}

// =============================================
//  Save Button
// =============================================
.save-btn {
  background: $primary;
  border-radius: $radius-lg;
  padding: $spacing-lg $spacing-xl;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: $spacing-lg;
  transition: $transition-fast;
}

.save-btn.btn-disabled {
  background: $primary-light;
  opacity: 0.6;
}

.save-text {
  font-size: 30rpx;
  color: #fff;
  font-weight: 500;
}

// =============================================
//  Spacer
// =============================================
.bottom-spacer {
  height: 100rpx;
}
</style>