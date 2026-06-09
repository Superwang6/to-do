<template>
  <view class="state-wrap">
    <view class="state-icon error-icon">
      <text class="state-emoji">☹️</text>
    </view>
    <text class="state-title">加载失败了</text>
    <text class="state-desc">网络不太稳定，请检查后重试</text>
    <view class="state-btn" hover-class="btn-hover" @tap="$emit('retry')">
      <text class="state-btn-text">重新加载</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'ErrorState'
}
</script>

<style lang="scss" scoped>
.state-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-xl * 2 $spacing-xl;
}

.state-icon {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: $spacing-md;
}

.error-icon {
  background: linear-gradient(135deg, #FFE5E5 0%, #FFCCCC 100%);
}

.state-emoji {
  font-size: 60rpx;
}

.state-title {
  font-size: 32rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: $spacing-xs;
}

.state-desc {
  font-size: 26rpx;
  color: $text-secondary;
  text-align: center;
  margin-bottom: $spacing-lg;
}

.state-btn {
  background: $primary;
  padding: $spacing-sm $spacing-xl;
  border-radius: $radius-lg;
}

.btn-hover {
  transform: scale(0.98);
  opacity: 0.9;
}

.state-btn-text {
  color: $text-inverse;
  font-size: 28rpx;
  font-weight: 500;
}
</style>
