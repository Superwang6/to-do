<template>
  <view class="page">
    <!-- ==================== Header ==================== -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="header-title">我的</text>
      </view>
    </view>

    <!-- ==================== Content ==================== -->
    <scroll-view class="content-scroll" scroll-y enhanced show-scrollbar="false">
      <view class="content-inner">
        <!-- ── User Card ── -->
        <view class="user-card">
          <view class="avatar">
            <text class="avatar-text">{{ initial }}</text>
          </view>
          <view class="user-info">
            <text class="username">{{ username }}</text>
            <text class="user-sub">用户设置</text>
          </view>
        </view>

        <!-- ── Settings List ── -->
        <view class="settings-card">
          <view class="setting-item" hover-class="item-hover" @tap="onAccount">
            <view class="setting-left">
              <text class="setting-icon">👤</text>
              <text class="setting-label">账号信息</text>
            </view>
            <view class="setting-right">
              <text class="setting-value">{{ username }}</text>
              <text class="setting-arrow">›</text>
            </view>
          </view>

          <view class="setting-divider" />

          <view class="setting-item" hover-class="item-hover" @tap="onData">
            <view class="setting-left">
              <text class="setting-icon">📊</text>
              <text class="setting-label">数据管理</text>
            </view>
            <view class="setting-right">
              <text class="setting-arrow">›</text>
            </view>
          </view>

          <view class="setting-divider" />

          <view class="setting-item" hover-class="item-hover" @tap="onAppearance">
            <view class="setting-left">
              <text class="setting-icon">🎨</text>
              <text class="setting-label">外观设置</text>
            </view>
            <view class="setting-right">
              <text class="setting-arrow">›</text>
            </view>
          </view>

          <view class="setting-divider" />

          <view class="setting-item" hover-class="item-hover" @tap="onAbout">
            <view class="setting-left">
              <text class="setting-icon">ℹ️</text>
              <text class="setting-label">关于</text>
            </view>
            <view class="setting-right">
              <text class="setting-value">v1.0.0</text>
              <text class="setting-arrow">›</text>
            </view>
          </view>
        </view>

        <!-- ── Logout ── -->
        <view class="logout-btn" @tap="onLogout" hover-class="logout-hover">
          <text class="logout-text">退出登录</text>
        </view>

        <view class="bottom-spacer" />
      </view>
    </scroll-view>

    <custom-tabbar current="/pages/profile/profile" />
  </view>
</template>

<script>
import { removeToken, getUser } from '@/utils/auth'
import CustomTabbar from '@/components/custom-tabbar.vue'

export default {
  components: {
    CustomTabbar
  },
  data() {
    const user = getUser()
    return {
      username: user?.username || '用户',
      statusBarHeight: 44,
    }
  },
  computed: {
    initial() {
      return (this.username || '用')[0].toUpperCase()
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
    onAccount() {
      uni.navigateTo({ url: '/pages/profile/account-info' })
    },
    onData() {
      uni.showToast({ title: '数据管理', icon: 'none' })
    },
    onAppearance() {
      uni.navigateTo({ url: '/pages/profile/appearance-settings' })
    },
    onAbout() {
      uni.showModal({
        title: '关于',
        content: 'Todo App v1.0.0\n语音智能待办清单',
        showCancel: false,
        confirmColor: '#C0544A',
      })
    },
    onLogout() {
      uni.showModal({
        title: '退出登录',
        content: '确定要退出当前账号吗？',
        confirmColor: '#C0544A',
        success: (res) => {
          if (res.confirm) {
            removeToken()
            uni.reLaunch({ url: '/pages/login/login' })
          }
        },
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
  justify-content: center;
  height: 88rpx;
  padding: 0 $spacing-xl;
}

.header-title {
  font-size: 34rpx;
  font-weight: 600;
  color: $text-primary;
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
//  User Card
// =============================================
.user-card {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $spacing-xl;
  display: flex;
  align-items: center;
  gap: $spacing-lg;
  box-shadow: $shadow-sm;
}

.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: $radius-full;
  background: $primary-light;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-text {
  font-size: 40rpx;
  font-weight: 700;
  color: $primary;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.username {
  font-size: 34rpx;
  font-weight: 600;
  color: $text-primary;
}

.user-sub {
  font-size: 24rpx;
  color: $text-tertiary;
}

// =============================================
//  Settings Card
// =============================================
.settings-card {
  background: $bg-card;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-lg $spacing-xl;
  transition: $transition-fast;
}

.setting-left {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.setting-icon {
  font-size: 36rpx;
}

.setting-label {
  font-size: 30rpx;
  color: $text-primary;
}

.setting-right {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.setting-value {
  font-size: 26rpx;
  color: $text-tertiary;
}

.setting-arrow {
  font-size: 32rpx;
  color: $text-tertiary;
}

.setting-divider {
  height: 1rpx;
  background: $border;
  margin-left: 80rpx;
}

.item-hover {
  background: $bg-input;
}

// =============================================
//  Logout Button
// =============================================
.logout-btn {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $spacing-lg $spacing-xl;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $shadow-sm;
  transition: $transition-fast;
}

.logout-text {
  font-size: 30rpx;
  color: $danger;
  font-weight: 500;
}

.logout-hover {
  background: $danger-light;
}

// =============================================
//  Spacer
// =============================================
.bottom-spacer {
  height: 140rpx;
}
</style>
