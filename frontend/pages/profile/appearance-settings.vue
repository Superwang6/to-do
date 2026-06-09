<template>
  <view class="page">
    <!-- ==================== Header ==================== -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <text class="header-back" @tap="onBack">‹</text>
        <text class="header-title">外观设置</text>
        <view class="header-right"></view>
      </view>
    </view>

    <!-- ==================== Content ==================== -->
    <scroll-view class="content-scroll" scroll-y enhanced show-scrollbar="false">
      <view class="content-inner">
        <!-- ── Theme Section ── -->
        <view class="settings-card">
          <view class="setting-item">
            <view class="setting-left">
              <text class="setting-icon">🎨</text>
              <text class="setting-label">主题</text>
            </view>
            <view class="setting-right">
              <radio-group @change="onThemeChange">
                <radio value="light" :checked="theme === 'light'" />
                <text class="radio-label">浅色</text>
                <radio value="dark" :checked="theme === 'dark'" />
                <text class="radio-label">深色</text>
              </radio-group>
            </view>
          </view>
        </view>

        <!-- ── Font Size Section ── -->
        <view class="settings-card">
          <view class="setting-item">
            <view class="setting-left">
              <text class="setting-icon">📝</text>
              <text class="setting-label">字体大小</text>
            </view>
            <view class="setting-right">
              <text class="font-size-value">{{ fontSize }}px</text>
            </view>
          </view>
          <view class="slider-container">
            <slider 
              :value="fontSize" 
              min="14" 
              max="20" 
              step="1" 
              @change="onFontSizeChange"
              activeColor="#C0544A"
            />
            <view class="font-size-labels">
              <text class="font-size-min">小</text>
              <text class="font-size-max">大</text>
            </view>
          </view>
        </view>

        <!-- ── Layout Section ── -->
        <view class="settings-card">
          <view class="setting-item">
            <view class="setting-left">
              <text class="setting-icon">📱</text>
              <text class="setting-label">界面布局</text>
            </view>
            <view class="setting-right">
              <picker @change="onLayoutChange" :value="layoutIndex" :range="layoutOptions">
                <view class="picker-value">{{ layoutOptions[layoutIndex] }}</view>
              </picker>
            </view>
          </view>
        </view>

        <view class="bottom-spacer" />
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { getSettings, updateSettings } from '@/api/auth'

export default {
  data() {
    return {
      statusBarHeight: 44,
      theme: 'light',
      fontSize: 16,
      layoutOptions: ['默认布局', '紧凑布局', '舒适布局'],
      layoutIndex: 0,
    }
  },
  onLoad() {
    try {
      const sys = uni.getSystemInfoSync()
      this.statusBarHeight = sys.statusBarHeight || 44
    } catch (_) {
      this.statusBarHeight = 44
    }
    this.loadSettings()
  },
  methods: {
    onBack() {
      uni.navigateBack()
    },
    async loadSettings() {
      try {
        // 从本地存储加载设置
        const savedTheme = uni.getStorageSync('theme')
        const savedFontSize = uni.getStorageSync('fontSize')
        const savedLayout = uni.getStorageSync('layout')
        
        if (savedTheme) this.theme = savedTheme
        if (savedFontSize) this.fontSize = parseInt(savedFontSize)
        if (savedLayout) this.layoutIndex = parseInt(savedLayout)
        
        // 应用设置
        this.applyTheme()
        this.applyFontSize()
      } catch (error) {
        console.error('Failed to load settings:', error)
      }
    },
    async saveSettings() {
      try {
        // 保存到本地存储
        uni.setStorageSync('theme', this.theme)
        uni.setStorageSync('fontSize', this.fontSize.toString())
        uni.setStorageSync('layout', this.layoutIndex.toString())
        
        // 保存到服务器
        const settings = {
          theme: this.theme,
          fontSize: this.fontSize.toString(),
          layout: this.layoutIndex.toString(),
        }
        await updateSettings(settings)
      } catch (error) {
        console.error('Failed to save settings:', error)
      }
    },
    onThemeChange(e) {
      this.theme = e.detail.value
      this.applyTheme()
      this.saveSettings()
    },
    onFontSizeChange(e) {
      this.fontSize = e.detail.value
      this.applyFontSize()
      this.saveSettings()
    },
    onLayoutChange(e) {
      this.layoutIndex = e.detail.value
      this.saveSettings()
    },
    applyTheme() {
      // 应用主题
      if (this.theme === 'dark') {
        // 这里可以实现深色主题的逻辑
        console.log('Dark theme applied')
      } else {
        // 这里可以实现浅色主题的逻辑
        console.log('Light theme applied')
      }
    },
    applyFontSize() {
      // 应用字体大小
      uni.setStorageSync('fontSize', this.fontSize.toString())
      console.log('Font size applied:', this.fontSize)
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
  gap: $spacing-md;
}

// =============================================
//  Radio Group
// =============================================
radio-group {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

radio {
  transform: scale(0.8);
}

.radio-label {
  font-size: 26rpx;
  color: $text-primary;
}

// =============================================
//  Font Size Section
// =============================================
.font-size-value {
  font-size: 26rpx;
  color: $text-tertiary;
  min-width: 60rpx;
  text-align: right;
}

.slider-container {
  padding: 0 $spacing-xl $spacing-lg;
}

.font-size-labels {
  display: flex;
  justify-content: space-between;
  margin-top: $spacing-sm;
}

.font-size-min,
.font-size-max {
  font-size: 24rpx;
  color: $text-tertiary;
}

// =============================================
//  Picker
// =============================================
.picker-value {
  font-size: 26rpx;
  color: $text-tertiary;
  min-width: 120rpx;
  text-align: right;
}

// =============================================
//  Spacer
// =============================================
.bottom-spacer {
  height: 100rpx;
}
</style>