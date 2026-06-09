<template>
  <view class="state-wrap">
    <view class="state-icon empty-icon">
      <text class="state-emoji">📋</text>
    </view>
    <text class="state-title">清单空空的</text>
    <text class="state-desc">用语音快速创建一条待办吧</text>
  </view>
</template>

<script>
export default {
  name: 'EmptyState'
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

.empty-icon {
  background: linear-gradient(135deg, #F5F1EC 0%, #E8E0D6 100%);
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
}

.state-wrap.state-mini {
  padding: $spacing-xl;
}
</style>
