<template>
  <view v-if="items.length > 0" class="section">
    <view class="section-header" @tap="onHeaderTap">
      <text class="section-icon">{{ icon }}</text>
      <text class="section-label">{{ title }}</text>
      <text class="section-count">{{ items.length }}</text>
      <text v-if="collapsible" class="expand-arrow">{{ expanded ? '▾' : '▸' }}</text>
    </view>
    <view v-if="!collapsible || expanded">
      <TodoCard
        v-for="(item, idx) in items"
        :key="item.id"
        :todo="item"
        :section="section"
        :index="idx"
        @toggle="$emit('toggle', item)"
        @edit="$emit('edit', item)"
        @delete="$emit('delete', item)"
      />
    </view>
  </view>
</template>

<script>
import TodoCard from './TodoCard.vue'

export default {
  name: 'TodoSection',
  components: { TodoCard },
  props: {
    title: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      default: ''
    },
    items: {
      type: Array,
      default: () => []
    },
    section: {
      type: String,
      default: ''
    },
    collapsible: {
      type: Boolean,
      default: false
    },
    expanded: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    onHeaderTap() {
      if (this.collapsible) {
        this.$emit('header-tap')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.section {
  margin-bottom: $spacing-lg;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: $spacing-md 0;
}

.section-header.completed-header {
  cursor: pointer;
}

.section-icon {
  font-size: 32rpx;
}

.section-label {
  font-size: 28rpx;
  font-weight: 500;
  color: $text-primary;
  flex: 1;
}

.section-count {
  font-size: 24rpx;
  color: $text-tertiary;
  background: $bg-input;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
}

.expand-arrow {
  font-size: 24rpx;
  color: $text-tertiary;
  margin-left: 8rpx;
}
</style>
