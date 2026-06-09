<script>
export default {
  onLaunch: function () {
    console.log('App Launch')
  }
}
</script>

<style lang="scss">
page {
  background-color: $bg-page;
  font-family: $font-cn;
  color: $text-primary;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Smooth page transitions */
.page-enter {
  opacity: 0;
  transform: translateY(10rpx);
}

/* Hide scrollbar for H5 */
::-webkit-scrollbar {
  width: 0;
  background: transparent;
}

/* Selection color */
::selection {
  background: $primary-light;
  color: $primary-dark;
}
</style>
