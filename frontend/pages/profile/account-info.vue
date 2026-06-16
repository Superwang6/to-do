<template>
  <view class="page">
    <!-- ==================== Header ==================== -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="header-back" @tap="onBack">‹</text>
        <text class="header-title">账号信息</text>
        <view class="header-right"></view>
      </view>
    </view>

    <!-- ==================== Content ==================== -->
    <scroll-view class="content-scroll" scroll-y enhanced show-scrollbar="false">
      <view class="content-inner">
        <!-- ── Avatar Section ── -->
        <view class="avatar-section">
          <view class="avatar-container">
            <image v-if="user.avatar" class="avatar" :src="user.avatar" mode="aspectFill" />
            <view v-else class="avatar avatar-placeholder">
              <text class="avatar-text">{{ initial }}</text>
            </view>
            <view class="avatar-edit" @tap="onAvatarClick">
              <text class="avatar-edit-icon">📷</text>
            </view>
          </view>
          <text class="avatar-hint">点击修改头像</text>
        </view>

        <!-- ── Form Section ── -->
        <view class="form-section">
          <!-- Username -->
          <view class="form-item">
            <text class="form-label">用户名</text>
            <view class="form-control">
              <input 
                v-model="form.username" 
                class="form-input" 
                placeholder="请输入用户名"
                maxlength="32"
              />
            </view>
          </view>

          <view class="form-divider" />

          <!-- Email -->
          <view class="form-item">
            <text class="form-label">邮箱</text>
            <view class="form-control">
              <input 
                v-model="form.email" 
                class="form-input" 
                placeholder="请输入邮箱"
                type="email"
              />
            </view>
          </view>

          <view class="form-divider" />

          <!-- Password -->
          <view class="form-item" @tap="onChangePassword">
            <text class="form-label">密码</text>
            <view class="form-control form-control-action">
              <text class="form-value">修改密码</text>
              <text class="form-arrow">›</text>
            </view>
          </view>
        </view>

        <!-- ── Save Button ── -->
        <view class="save-btn" @tap="onSave" :class="{ 'btn-disabled': !isFormChanged }" :disabled="!isFormChanged">
          <text class="save-text">保存修改</text>
        </view>

        <view class="bottom-spacer" />
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { getUser, setUser } from '@/utils/auth'
import { updateProfile, uploadAvatar } from '@/api/auth'

export default {
  data() {
    const user = getUser()
    return {
      statusBarHeight: 44,
      user: {
        username: user?.username || '',
        email: user?.email || '',
        avatar: user?.avatar || '',
      },
      form: {
        username: user?.username || '',
        email: user?.email || '',
      },
      originalForm: {
        username: user?.username || '',
        email: user?.email || '',
      },
    }
  },
  computed: {
    initial() {
      return (this.user.username || '用')[0].toUpperCase()
    },
    isFormChanged() {
      return this.form.username !== this.originalForm.username || 
             this.form.email !== this.originalForm.email
    },
  },
  onLoad() {
    try {
      const sys = uni.getSystemInfoSync()
      this.statusBarHeight = sys.statusBarHeight || 44
    } catch (_) {
      this.statusBarHeight = 44
    }
    this.fetchUserProfile()
  },
  methods: {
    onBack() {
      uni.navigateBack()
    },
    async fetchUserProfile() {
      try {
        // 这里可以调用 API 获取最新的用户信息，并按业务 data 更新本地状态
      } catch (error) {
        console.error('Failed to fetch user profile:', error)
      }
    },
    async onSave() {
      if (!this.isFormChanged) return

      try {
        uni.showLoading({ title: '保存中...' })
        const updatedUserData = await updateProfile(this.form)
        const updatedUser = { ...this.user, ...this.form, ...(updatedUserData || {}) }
        this.user = updatedUser
        this.form = {
          username: updatedUser.username || '',
          email: updatedUser.email || '',
        }
        this.originalForm = { ...this.form }
        setUser(updatedUser)
        uni.showToast({ title: '保存成功', icon: 'success' })
      } catch (error) {
        console.error('Failed to update profile:', error)
        uni.showToast({ title: error.message || '保存失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    onChangePassword() {
      uni.navigateTo({ url: '/pages/profile/change-password' })
    },
    onAvatarClick() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          try {
            uni.showLoading({ title: '上传中...' })
            const tempFilePaths = res.tempFilePaths
            const data = await uploadAvatar(tempFilePaths[0])
            const updatedUser = { ...this.user, avatar: data?.avatar || '' }
            this.user = updatedUser
            setUser(updatedUser)
            uni.showToast({ title: '头像更新成功', icon: 'success' })
          } catch (error) {
            console.error('Failed to upload avatar:', error)
            uni.showToast({ title: '上传失败', icon: 'none' })
          } finally {
            uni.hideLoading()
          }
        },
        fail: (error) => {
          console.error('Failed to choose image:', error)
        }
      })
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
//  Avatar Section
// =============================================
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-xl 0;
}

.avatar-container {
  position: relative;
  width: 160rpx;
  height: 160rpx;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: $radius-full;
  background: $primary-light;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 60rpx;
  font-weight: 700;
  color: $primary;
}

.avatar-edit {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 48rpx;
  height: 48rpx;
  border-radius: $radius-full;
  background: $primary;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4rpx solid #fff;
}

.avatar-edit-icon {
  font-size: 24rpx;
  color: #fff;
}

.avatar-hint {
  font-size: 24rpx;
  color: $text-tertiary;
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
  width: 120rpx;
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

.form-control-action {
  gap: $spacing-xs;
}

.form-value {
  font-size: 26rpx;
  color: $text-tertiary;
}

.form-arrow {
  font-size: 32rpx;
  color: $text-tertiary;
}

.form-divider {
  height: 1rpx;
  background: $border;
  margin-left: 120rpx;
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