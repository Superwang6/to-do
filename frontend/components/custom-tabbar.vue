<template>
  <view class="tabbar-container">
    <view class="tabbar">
      <view
        v-for="(item, index) in tabList"
        :key="item.pagePath"
        class="tab-item"
        :class="{ active: currentIndex === index }"
        @tap="switchTab(item.pagePath, index)"
      >
        <text class="tab-icon">{{ currentIndex === index ? item.selectedIcon : item.icon }}</text>
        <text class="tab-text">{{ item.text }}</text>
      </view>
    </view>
    <view class="safe-area-bottom" />
  </view>
</template>

<script>
export default {
  props: {
    current: {
      type: String,
      default: '/pages/index/index'
    }
  },
  data() {
    return {
      tabList: [
        {
          pagePath: '/pages/index/index',
          text: '待办',
          icon: '📋',
          selectedIcon: '✅'
        },
        {
          pagePath: '/pages/profile/profile',
          text: '我的',
          icon: '👤',
          selectedIcon: '👤'
        }
      ]
    }
  },
  computed: {
    currentIndex() {
      return this.tabList.findIndex(item => item.pagePath === this.current)
    }
  },
  methods: {
    switchTab(pagePath, index) {
      if (this.currentIndex === index) return
      uni.reLaunch({
        url: pagePath
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.tabbar-container {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.tabbar {
  background: #FFFFFF;
  display: flex;
  padding-top: 8rpx;
  box-shadow: 0 -2rpx 12rpx rgba(45, 42, 38, 0.08);
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8rpx 0;
  transition: all 0.2s ease;
}

.tab-icon {
  font-size: 40rpx;
  margin-bottom: 4rpx;
}

.tab-text {
  font-size: 22rpx;
  color: #978E84;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tab-item.active .tab-text {
  color: #C0544A;
  font-weight: 600;
}

.safe-area-bottom {
  height: env(safe-area-inset-bottom);
  background: #FFFFFF;
}
</style>
