<template>
  <view class="filter-bar">
    <view
      v-for="stat in stats"
      :key="stat.key"
      class="filter-pill"
      :class="{ active: activeTab === stat.key }"
      hover-class="pill-hover"
      @tap="onStatTap(stat.key)"
    >
      <text class="pill-label">{{ stat.label }}</text>
      <text class="pill-count">{{ stat.value }}</text>
    </view>
    <view
      class="filter-pill star-pill"
      :class="{ on: importantOnly }"
      hover-class="pill-hover"
      @tap="$emit('toggle-important')"
    >
      <text class="pill-star">{{ importantOnly ? '★' : '☆' }}</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'FilterBar',
  props: {
    stats: {
      type: Array,
      default: () => []
    },
    activeTab: {
      type: String,
      default: 'all'
    },
    importantOnly: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    onStatTap(key) {
      this.$emit('tab-change', key)
    }
  }
}
</script>

<style lang="scss" scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  margin-top: $spacing-lg;
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $spacing-xs;
  box-shadow: $shadow-md;
  border: 2rpx solid $border;
}

.filter-pill {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4rpx;
  height: 52rpx;
  padding: 0 $spacing-xs;
  border-radius: $radius-md;
  background: $bg-input;
  transition: $transition-fast;
  white-space: nowrap;
  border: 2rpx solid transparent;
}

.filter-pill.active {
  background: $primary;
  border-color: $primary-dark;
}

.filter-pill.active .pill-label {
  color: $text-inverse;
  font-weight: 700;
}

.filter-pill.active .pill-count {
  color: $text-inverse;
  background: rgba(255, 255, 255, 0.25);
}

.pill-hover {
  transform: scale(0.98);
}

.pill-label {
  font-size: 24rpx;
  color: #4A4540;
  font-weight: 600;
}

.pill-count {
  font-size: 22rpx;
  color: #6B655F;
  background: rgba(0, 0, 0, 0.08);
  padding: 2rpx 8rpx;
  border-radius: 12rpx;
  font-weight: 600;
}

.star-pill {
  flex: 0 0 52rpx;
  padding: 0;
}

.star-pill.on {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
}

.pill-star {
  font-size: 28rpx;
}
</style>
