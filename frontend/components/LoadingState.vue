<template>
  <view class="skeleton-wrap">
    <view v-for="n in 5" :key="n" class="skeleton-card">
      <view class="skeleton-row">
        <view class="skeleton-check"></view>
        <view class="skeleton-block w-70"></view>
      </view>
      <view v-if="n === 1" class="skeleton-row">
        <view class="skeleton-block w-40"></view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'LoadingState'
}
</script>

<style lang="scss" scoped>
.skeleton-wrap {
  padding: 0 $spacing-xl;
}

.skeleton-card {
  background: $bg-card;
  border-radius: $radius-md;
  padding: $spacing-md;
  margin-bottom: $spacing-sm;
}

.skeleton-row {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-sm;
}

.skeleton-check {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: linear-gradient(90deg, #F5F1EC 25%, #E8E0D6 50%, #F5F1EC 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-block {
  height: 24rpx;
  border-radius: 12rpx;
  background: linear-gradient(90deg, #F5F1EC 25%, #E8E0D6 50%, #F5F1EC 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-block.w-70 {
  flex: 0 0 70%;
}

.skeleton-block.w-40 {
  flex: 0 0 40%;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
