<template>
  <view class="page" :class="{ recording: isRecording, hasResult: transcript }">
    <!-- ==================== Custom Header ==================== -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <view class="back-btn" hover-class="back-hover" @tap="goBack">
          <text class="back-arrow">←</text>
          <text class="back-label">返回</text>
        </view>
        <text class="header-title">语音创建</text>
        <view class="header-spacer" />
      </view>
    </view>

    <!-- ==================== Main Content ==================== -->
    <view class="body">
      <!-- ── Info Hint ── -->
      <view class="hint-area" v-if="!isRecording && !transcript">
        <view class="hint-icon-wrap">
          <text class="hint-icon">🎤</text>
        </view>
        <text class="hint-title">轻触下方按钮开始录音</text>
        <text class="hint-desc">说出待办事项，我们将为你转成文字</text>
      </view>

      <!-- ── Recording Indicator ── -->
      <view class="recording-indicator" v-if="isRecording">
        <view class="indicator-dot" />
        <text class="indicator-text">正在聆听</text>
        <view class="indicator-bars">
          <view
            v-for="n in 5"
            :key="n"
            class="wave-bar"
            :style="{ animationDelay: n * 0.12 + 's' }"
          />
        </view>
      </view>

      <!-- ── Transcription Area ── -->
      <view class="transcript-area" v-if="transcript">
        <view class="transcript-card">
          <text class="transcript-label">转写结果</text>
          <text class="transcript-text">{{ transcript }}</text>
        </view>
      </view>

      <!-- ── Audio Waveform (after recording) ── -->
      <view class="waveform-area" v-if="hasAudio && !isRecording">
        <view class="waveform-container">
          <view
            v-for="(h, idx) in waveformBars"
            :key="idx"
            class="wf-bar"
            :style="{ height: h + '%' }"
          />
        </view>
        <text class="waveform-label">录音 {{ duration }}s</text>
      </view>

      <!-- ── Action Buttons ── -->
      <view class="actions" v-if="transcript && !isRecording">
        <view
          class="action-btn secondary"
          hover-class="action-hover-secondary"
          @tap="resetAll"
        >
          <text>重新录制</text>
        </view>
        <view
          class="action-btn primary"
          hover-class="action-hover-primary"
          :class="{ submitting: isSubmitting }"
          @tap="submitTodo"
        >
          <text>{{ isSubmitting ? '创建中...' : '创建待办' }}</text>
        </view>
      </view>
    </view>

    <!-- ==================== Recording Button ==================== -->
    <view class="record-area">
      <view class="record-btn-wrap">
        <!-- Animated rings (visible during recording) -->
        <template v-if="isRecording">
          <view
            v-for="n in 3"
            :key="'ring-' + n"
            class="record-ring"
            :style="{ animationDelay: n * 0.4 + 's' }"
          />
        </template>

        <!-- The button -->
        <view
          class="record-btn"
          :class="{ idle: !isRecording && !transcript, active: isRecording }"
          @tap="toggleRecord"
          hover-class="record-hover"
        >
          <text class="record-icon">
            {{ isRecording ? '⬤' : '🎤' }}
          </text>
        </view>
      </view>
      <text class="record-hint" v-if="!isRecording && !transcript">
        点击录音
      </text>
      <text class="record-hint rec-hint" v-else-if="isRecording">
        点击停止
      </text>
    </view>
  </view>
</template>

<script>
import { createTodo, uploadAudio } from '@/api/todo'

export default {
  data() {
    return {
      statusBarHeight: 44,
      isRecording: false,
      hasAudio: false,
      duration: 0,
      transcript: '',
      isSubmitting: false,
      recorder: null,
      waveformBars: [30, 50, 70, 45, 60, 80, 35, 55, 75, 40, 65, 50],
    }
  },
  onLoad() {
    try {
      const sys = uni.getSystemInfoSync()
      this.statusBarHeight = sys.statusBarHeight || 44
    } catch (_) {
      this.statusBarHeight = 44
    }
  },
  onHide() {
    this.cleanupRecording({ stopRecorder: true, skipUpload: true })
  },
  onUnload() {
    this.cleanupRecording({ stopRecorder: true, skipUpload: true })
  },
  methods: {
    goBack() {
      uni.navigateBack()
    },

    toggleRecord() {
      if (this.isRecording) {
        this.stopRecord()
      } else {
        this.startRecord()
      }
    },

    startRecord() {
      if (this.isRecording) return
      this.isRecording = true
      this.duration = 0
      this.hasAudio = false
      this._skipNextUpload = false

      // Start timing
      this._timer = setInterval(() => {
        this.duration++
      }, 1000)

      // Start native recorder
      const recorderManager = uni.getRecorderManager()
      this.recorder = recorderManager

      recorderManager.onStop((res) => {
        this.cleanupRecording()
        if (this._skipNextUpload) {
          this._skipNextUpload = false
          return
        }
        this._audioPath = res.tempFilePath
        this.hasAudio = true
        this.uploadAndTranscribe()
      })

      recorderManager.onError((err) => {
        this.cleanupRecording()
        uni.showToast({ title: '录音失败', icon: 'none' })
      })

      recorderManager.start({
        format: 'mp3',
        sampleRate: 16000,
        numberOfChannels: 1,
        encodeBitRate: 48000,
      })
    },

    stopRecord() {
      if (!this.isRecording) return
      this.cleanupRecording()

      if (this.recorder) {
        this.recorder.stop()
      }
    },

    cleanupRecording(options = {}) {
      const { stopRecorder = false, skipUpload = false } = options
      if (skipUpload) {
        this._skipNextUpload = true
      }
      if (this._timer) {
        clearInterval(this._timer)
        this._timer = null
      }
      const shouldStop = stopRecorder && this.isRecording && this.recorder
      this.isRecording = false
      if (shouldStop) {
        try { this.recorder.stop() } catch (_) {}
      }
    },

    async uploadAndTranscribe() {
      if (!this._audioPath) {
        uni.showToast({ title: '没有录音文件', icon: 'none' })
        return
      }

      uni.showLoading({ title: '识别中...' })
      try {
        const result = await uploadAudio(this._audioPath)
        this.transcript = result.text || ''
        if (result.todo) {
          uni.showToast({ title: '创建成功', icon: 'success' })
          setTimeout(() => {
            uni.navigateBack()
          }, 600)
        }
      } catch (e) {
        uni.showToast({ title: '识别失败，请重试', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },

    async submitTodo() {
      if (this.isSubmitting || !this.transcript) return
      this.isSubmitting = true
      try {
        await createTodo({ title: this.transcript, status: 'pending' })
        uni.showToast({ title: '创建成功', icon: 'success' })
        setTimeout(() => {
          uni.navigateBack()
        }, 600)
      } catch (_) {
        uni.showToast({ title: '创建失败', icon: 'none' })
      } finally {
        this.isSubmitting = false
      }
    },

    resetAll() {
      this.transcript = ''
      this.hasAudio = false
      this.duration = 0
      this._audioPath = null
    },
  },
}
</script>

<style lang="scss" scoped>
@import "@/uni.scss";

// =============================================
//  Page
// =============================================
.page {
  height: 100vh;
  overflow: hidden;
  background: $bg-page;
  display: flex;
  flex-direction: column;
  transition: $transition-base;
}

.page.recording {
  background: linear-gradient(180deg, #2D2A26 0%, $bg-page 60%);
}

.page.hasResult {
  background: $bg-page;
}

// =============================================
//  Header
// =============================================
.header {
  background: transparent;
  padding-bottom: $spacing-sm;
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-sm $spacing-xl 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: $spacing-sm 0;
}

.back-arrow {
  font-size: 34rpx;
  color: $text-primary;
  font-weight: 300;
}

.back-label {
  font-size: 26rpx;
  color: $text-secondary;
}

.back-hover {
  opacity: 0.5;
}

.header-title {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.header-spacer {
  width: 100rpx;
}

// =============================================
//  Body Content
// =============================================
.body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 $spacing-xl;
}

// ── Idle Hint ──
.hint-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: fadeUp 0.5s ease-out;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(30rpx); }
  to { opacity: 1; transform: translateY(0); }
}

.hint-icon-wrap {
  width: 140rpx;
  height: 140rpx;
  border-radius: $radius-full;
  background: $primary-light;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: $spacing-lg;
}

.hint-icon {
  font-size: 60rpx;
}

.hint-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: $spacing-sm;
}

.hint-desc {
  font-size: 26rpx;
  color: $text-tertiary;
  text-align: center;
  line-height: 1.6;
}

// ── Recording Indicator ──
.recording-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-md;
  animation: fadeUp 0.3s ease-out;
}

.indicator-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: $radius-full;
  background: $danger;
  animation: blink 1s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.indicator-text {
  font-size: 28rpx;
  color: $text-primary;
  font-weight: 500;
}

.indicator-bars {
  display: flex;
  align-items: center;
  gap: 6rpx;
  height: 48rpx;
}

.wave-bar {
  width: 6rpx;
  border-radius: 3rpx;
  background: $primary;
  animation: waveBounce 0.6s ease-in-out infinite alternate;
}

.wave-bar:nth-child(1) { height: 24rpx; }
.wave-bar:nth-child(2) { height: 40rpx; }
.wave-bar:nth-child(3) { height: 48rpx; }
.wave-bar:nth-child(4) { height: 32rpx; }
.wave-bar:nth-child(5) { height: 20rpx; }

@keyframes waveBounce {
  0% { transform: scaleY(0.5); }
  100% { transform: scaleY(1); }
}

// ── Transcription ──
.transcript-area {
  width: 100%;
  animation: fadeUp 0.4s ease-out;
}

.transcript-card {
  background: $bg-card;
  border-radius: $radius-lg;
  padding: $spacing-lg $spacing-xl;
  border: 1rpx solid $border-light;
  box-shadow: $shadow-sm;
}

.transcript-label {
  font-size: 22rpx;
  color: $text-tertiary;
  margin-bottom: $spacing-md;
  display: block;
  text-transform: uppercase;
  letter-spacing: 2rpx;
}

.transcript-text {
  font-size: 34rpx;
  line-height: 1.6;
  color: $text-primary;
  font-weight: 400;
}

// ── Waveform ──
.waveform-area {
  width: 100%;
  margin-top: $spacing-lg;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-sm;
  animation: fadeUp 0.4s ease-out;
}

.waveform-container {
  display: flex;
  align-items: center;
  gap: 4rpx;
  height: 80rpx;
  width: 80%;
}

.wf-bar {
  flex: 1;
  background: $primary;
  border-radius: 2rpx;
  opacity: 0.6;
  transition: $transition-base;
}

.waveform-label {
  font-size: 22rpx;
  color: $text-tertiary;
}

// ── Action Buttons ──
.actions {
  display: flex;
  gap: $spacing-md;
  margin-top: $spacing-2xl;
  width: 100%;
  animation: fadeUp 0.5s ease-out;
}

.action-btn {
  flex: 1;
  padding: $spacing-md 0;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 500;
  transition: $transition-base;
}

.action-btn.primary {
  background: $primary;
  color: $text-inverse;
  box-shadow: 0 4rpx 16rpx rgba(192, 84, 74, 0.25);
}

.action-btn.secondary {
  background: $bg-page;
  color: $text-secondary;
  border: 1rpx solid $border-light;
}

.action-btn.primary.submitting {
  opacity: 0.7;
}

.action-hover-primary {
  transform: scale(0.97);
  opacity: 0.9;
}

.action-hover-secondary {
  background: $border-light;
}

// =============================================
//  Record Button (bottom)
// =============================================
.record-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-2xl 0 80rpx;
}

.record-btn-wrap {
  position: relative;
  width: 140rpx;
  height: 140rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.record-btn {
  width: 130rpx;
  height: 130rpx;
  border-radius: $radius-full;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: $transition-spring;
  position: relative;
  z-index: 2;
}

.record-btn.idle {
  background: $primary-gradient;
  box-shadow: 0 8rpx 28rpx rgba(192, 84, 74, 0.3);
}

.record-btn.active {
  width: 160rpx;
  height: 160rpx;
  background: $danger;
  box-shadow: 0 0 40rpx rgba(192, 84, 74, 0.4);
}

.record-icon {
  font-size: 48rpx;
  color: $text-inverse;
}

.record-btn.active .record-icon {
  font-size: 42rpx;
  animation: pulseText 0.8s ease-in-out infinite;
}

@keyframes pulseText {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.record-hover {
  transform: scale(0.93);
}

// ── Recording Rings ──
.record-ring {
  position: absolute;
  inset: 0;
  border-radius: $radius-full;
  border: 2rpx solid rgba(192, 84, 74, 0.25);
  animation: rippleOut 1.6s ease-out infinite;
  pointer-events: none;
}

@keyframes rippleOut {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

// ── Hint below button ──
.record-hint {
  font-size: 24rpx;
  color: $text-tertiary;
}

.rec-hint {
  color: $text-secondary;
}
</style>
