<template>
  <view class="page">
    <!-- ==================== Header ==================== -->
    <view class="header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="header-inner">
        <view class="back-btn" hover-class="back-hover" @tap="goBack">
          <text class="back-arrow">←</text>
          <text class="back-label">返回</text>
        </view>
        <view class="header-center">
          <text class="header-title">智能创建</text>
          <text class="header-sub">语音或文字 · 自动解析待办</text>
        </view>
        <view class="header-spacer" />
      </view>
    </view>

    <!-- ==================== Message List ==================== -->
    <scroll-view
      class="msg-scroll"
      :class="{ 'msg-scroll-ready': scrollReady }"
      scroll-y
      :scroll-top="scrollTop"
      :scroll-with-animation="animateScroll"
      enhanced
      show-scrollbar="false"
      @touchmove="onScrollTouch"
    >
      <view class="msg-list">
        <!-- Welcome message -->
        <view class="msg-row bot-row">
          <view class="bot-avatar">
            <text class="bot-avatar-text">🤖</text>
          </view>
          <view class="bot-bubble welcome-bubble">
            <text class="bot-name">智能助手</text>
            <text class="bot-text">你好！发送文字或语音给我，我会自动解析内容，帮你创建待办事项。</text>
            <view class="hint-chips">
              <view class="hint-chip" @tap="quickSend('每天跑步')">
                <text>每天跑步</text>
              </view>
              <view class="hint-chip" @tap="quickSend('买牛奶和面包')">
                <text>买牛奶和面包</text>
              </view>
              <view class="hint-chip" @tap="quickSend('下午三点开会')">
                <text>下午三点开会</text>
              </view>
              <view class="hint-chip" @tap="quickSend('明天上午去健身房')">
                <text>明天上午去健身房</text>
              </view>
            </view>
          </view>
        </view>

        <!-- Messages -->
        <view
          v-for="(msg, idx) in messages"
          :key="msg.id"
          :id="'msg-' + msg.id"
          class="msg-row"
          :class="msg.role + '-row'"
        >
          <!-- Bot avatar -->
          <view v-if="msg.role === 'bot'" class="bot-avatar">
            <text class="bot-avatar-text">🤖</text>
          </view>

          <!-- User text message -->
          <view v-if="msg.role === 'user'" class="user-bubble">
            <text class="user-text">{{ msg.content }}</text>
          </view>

          <!-- Voice message -->
          <view v-else-if="msg.role === 'voice'" class="user-bubble voice-bubble">
            <text class="voice-icon">🎤</text>
            <text class="voice-dur">{{ msg.duration }}s</text>
            <text v-if="msg.transcribed_text" class="voice-text">{{ msg.transcribed_text }}</text>
          </view>

          <!-- Bot response -->
          <view v-else-if="msg.role === 'bot'" class="bot-bubble">
            <text class="bot-name">{{ msg.todo_created ? '✅ 已创建' : '💬 已记录' }}</text>
            <text class="bot-text">{{ msg.content }}</text>
            <view v-if="msg.todos && msg.todos.length > 0" class="bot-todo-section">
              <view
                v-for="t in msg.todos"
                :key="t.id"
                class="bot-todo-card"
                hover-class="bot-todo-card-hover"
                @tap="openEdit(t)"
              >
                <view class="bot-todo-check">✓</view>
                <text class="bot-todo-title">{{ t.title }}</text>
              </view>
            </view>
          </view>

          <!-- System notification -->
          <view v-else-if="msg.role === 'system'" class="sys-msg">
            <view class="sys-line" />
            <text class="sys-text">{{ msg.content }}</text>
            <view class="sys-line" />
          </view>

          <!-- Right spacer for user messages (no avatar) -->
          <view v-if="msg.role === 'user' || msg.role === 'voice'" class="msg-spacer" />
        </view>

        <!-- Typing indicator -->
        <view v-if="isTyping" id="msg-typing" class="msg-row bot-row">
          <view class="bot-avatar">
            <text class="bot-avatar-text">🤖</text>
          </view>
          <view class="bot-bubble typing-bubble">
            <view class="typing-dots">
              <view class="typing-dot" />
              <view class="typing-dot" />
              <view class="typing-dot" />
            </view>
          </view>
          <view class="msg-spacer" />
        </view>

        <!-- Bottom spacer -->
        <view class="msg-bottom" />
      </view>
    </scroll-view>

    <!-- ==================== Edit Sheet ==================== -->
    <todo-edit-sheet
      :visible="showEditSheet"
      :todo="editingTodo || {}"
      @close="showEditSheet = false"
      @saved="onTodoSaved"
    />

    <!-- ==================== Recording Overlay ==================== -->
    <view class="recording-overlay" v-if="isRecording">
      <view class="recording-indicator" :class="{ 'cancelling': _cancelRecord }">
        <view class="record-ring-pulse" :class="{ 'cancelling': _cancelRecord }" />
        <view class="record-ring-inner" :class="{ 'cancelling': _cancelRecord }">
          <text class="record-icon">{{ _cancelRecord ? '✕' : '🎤' }}</text>
        </view>
        <text class="record-dur">{{ recordDuration }}s</text>
        <text class="record-hint">{{ _cancelRecord ? '松开取消' : '松开发送 · 上滑取消' }}</text>
      </view>
    </view>

    <!-- ==================== Input Bar ==================== -->
    <view class="input-bar" :class="{ 'has-record': isRecording }">
      <view class="input-inner">
        <!-- Text input -->
        <view class="input-field">
          <input
            v-model="inputText"
            type="text"
            :disabled="isRecording"
            placeholder="输入待办内容..."
            placeholder-class="input-placeholder"
            confirm-type="send"
            @confirm="sendText"
            @focus="onInputFocus"
          />
        </view>

        <!-- Mic / Send -->
        <view
          class="input-btn"
          :class="{ 'is-send': inputText.trim() }"
          hover-class="input-btn-hover"
          @touchstart.stop="onMicTouchStart"
          @touchend.stop="onMicTouchEnd"
          @touchmove.stop.prevent="onMicTouchMove"
          @click.stop="handleInputAction"
        >
          <text v-if="inputText.trim()" class="btn-icon send-icon">↑</text>
          <text v-else class="btn-icon mic-icon">🎤</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { fetchChatMessages, saveChatMessage, sendChatText, sendChatVoice, fetchTodoDetail } from '@/api/todo'
import TodoEditSheet from '@/components/todo-edit-sheet.vue'

let msgIdCounter = 100

export default {
  components: { TodoEditSheet },
  data() {
    return {
      statusBarHeight: 44,
      animateScroll: false,
      inputText: '',
      messages: [],
      isTyping: false,
      isRecording: false,
      recordDuration: 0,
      recordTimer: null,
      recorder: null,
      audioPath: null,
      scrollTop: 0,
      scrollReady: false,
      showEditSheet: false,
      editingTodo: null,
      _recordingStartY: 0,
      _cancelRecord: false,
    }
  },
  onLoad() {
    try {
      const sys = uni.getSystemInfoSync()
      this.statusBarHeight = sys.statusBarHeight || 44
    } catch (_) {
      this.statusBarHeight = 44
    }
    this.loadMessages()
  },
  methods: {
    // ── Navigation ──
    goBack() {
      uni.navigateBack()
    },

    // ── Edit ──
    async openEdit(todo) {
      if (!todo || !todo.id) return
      try {
        const detail = await fetchTodoDetail(todo.id)
        this.editingTodo = detail
        this.showEditSheet = true
      } catch (_) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },

    onTodoSaved() {
      this.showEditSheet = false
      this.editingTodo = null
    },

    async loadMessages() {
      try {
        const res = await fetchChatMessages()
        if (res && res.length > 0) {
          this.messages = res.map(m => ({
            id: m.id,
            role: m.role,
            content: m.content || '',
            duration: m.duration,
            todo_created: m.todo_created,
            todos: m.todos || [],
          }))
          const maxId = Math.max(...this.messages.map(m => m.id))
          msgIdCounter = Math.max(msgIdCounter, maxId + 1)
        }
      } catch (_) {
        // No history loaded, start fresh
      }
      // Position at bottom while still hidden, then reveal
      await this.$nextTick()
      this.scrollTop = 999999
      await this.$nextTick()
      this.scrollReady = true
      this.animateScroll = true
    },

    // ── Quick Send ──
    quickSend(text) {
      this.inputText = text
      this.sendText()
    },

    // ── Send Text ──
    async sendText() {
      const text = this.inputText.trim()
      if (!text || this.isTyping) return
      this.inputText = ''

      // 1. Save user message
      this.addMessage('user', text)
      saveChatMessage({ role: 'user', content: text })
      this.scrollToBottom()

      // 2. Get bot reply
      this.isTyping = true
      try {
        const res = await sendChatText(text)
        this.isTyping = false
        this.addBotMessage(res)
      } catch (_) {
        this.isTyping = false
        this.addMessage('bot', '抱歉，出了点问题，请稍后再试。')
      }
      this.scrollToBottom()
    },

    // ── Mic handling ──
    onMicTouchStart(e) {
      if (this.inputText.trim()) return
      this._recordingStartY = e.touches ? e.touches[0].clientY : 0
      this._cancelRecord = false
      this.startRecord()
    },

    onMicTouchMove(e) {
      if (!this.isRecording) return
      
      // Prevent default behavior to avoid rubberband effect
      if (e.preventDefault) {
        e.preventDefault()
      } else if (e.changedTouches && e.changedTouches[0]) {
        // For some platforms
        e.changedTouches[0].preventDefault?.()
      }
      
      const clientY = e.touches ? e.touches[0].clientY : (e.changedTouches ? e.changedTouches[0].clientY : 0)
      const dy = this._recordingStartY - clientY
      if (dy > 80) {
        this._cancelRecord = true
      } else {
        this._cancelRecord = false
      }
    },

    onMicTouchEnd() {
      if (!this.isRecording) return
      if (this._cancelRecord) {
        this.cancelRecord()
      } else {
        this.stopRecord()
      }
    },

    handleInputAction() {
      if (this.inputText.trim()) {
        this.sendText()
      }
    },

    // ── Recording ──
    startRecord() {
      this.isRecording = true
      this.recordDuration = 0
      this.audioPath = null
      this._recordingTimer = setInterval(() => {
        this.recordDuration++
      }, 1000)
      
      const recorderManager = uni.getRecorderManager()

      this._stopPromise = new Promise((resolve, reject) => {
        recorderManager.onStop((res) => {
          this.audioPath = res.tempFilePath
          resolve(res.tempFilePath)
        })
        recorderManager.onError((err) => {
          reject(err)
        })
      })

      recorderManager.start({
        format: 'mp3',
        sampleRate: 16000,
        numberOfChannels: 1,
        encodeBitRate: 48000,
      })
    },

    async stopRecord() {
      if (!this.isRecording) return
      const duration = this.recordDuration
      this.isRecording = false
      clearInterval(this._recordingTimer)

      const recorderManager = uni.getRecorderManager()
      recorderManager.stop()

      let filePath = null
      try {
        filePath = await this._stopPromise
      } catch (e) {
        return
      }

      if (!filePath) {
        return
      }

      // Add voice message bubble
      const voiceMsg = this.addMessage('voice', '', { duration })
      this.scrollToBottom()

      // Upload and transcribe, then process
      this.isTyping = true
      try {
        const audioRes = await sendChatVoice(filePath)
        
        // Update voice message with transcribed text
        voiceMsg.transcribed_text = audioRes.transcribed_text
        
        const textRes = await sendChatText(audioRes.transcribed_text)
        this.isTyping = false
        this.addBotMessage(textRes)
      } catch (e) {
        this.isTyping = false
        this.addMessage('bot', '抱歉，语音解析失败了，请重试。')
      }
      this.scrollToBottom()
    },

    cancelRecord() {
      this.isRecording = false
      clearInterval(this._recordingTimer)
      const recorderManager = uni.getRecorderManager()
      try { recorderManager.stop() } catch (_) {}
    },

    // ── Message Helpers ──
    addMessage(role, content, extra = {}) {
      const id = ++msgIdCounter
      const msg = { id, role, content, ...extra }
      this.messages.push(msg)
      return msg
    },

    addBotMessage(res) {
      const botMsg = res.bot_message || {}
      const todos = botMsg.todos || []
      const msg = this.addMessage('bot', res.response || '已记录。', {
        todo_created: res.todo_created || false,
        todos,
      })
      if (msg.todo_created && todos.length > 0) {
        const titles = todos.map(t => `「${t.title}」`).join('、')
        this.addMessage('system', `已创建待办${titles}`)
      }
      return msg
    },

    scrollToBottom() {
      this.$nextTick(() => {
        this.scrollTop = this.scrollTop === 999999 ? 999998 : 999999
      })
    },

    onInputFocus() {
      setTimeout(() => this.scrollToBottom(), 300)
    },

    onScrollTouch() {
      uni.hideKeyboard()
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
}

// =============================================
//  Header
// =============================================
.header {
  background: $bg-card;
  border-bottom: 1rpx solid $border-light;
  padding-bottom: $spacing-sm;
}

.header-inner {
  display: flex;
  align-items: center;
  padding: $spacing-sm $spacing-xl 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: $spacing-sm 0;
  flex-shrink: 0;
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

.header-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-title {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.header-sub {
  font-size: 20rpx;
  color: $text-tertiary;
  margin-top: 2rpx;
}

.header-spacer {
  width: 100rpx;
  flex-shrink: 0;
}

// =============================================
//  Message List
// =============================================
.msg-scroll {
  flex: 1;
  height: 0;
  padding: 0 $spacing-xl;
  overflow: hidden;
  opacity: 0;
  transition: opacity 0.15s ease-out;
}

.msg-scroll-ready {
  opacity: 1;
}

.msg-list {
  display: flex;
  flex-direction: column;
  padding: $spacing-lg 0;
  gap: $spacing-lg;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.msg-row {
  display: flex;
  align-items: flex-start;
  gap: $spacing-md;
  animation: msgIn 0.35s ease-out;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(16rpx); }
  to { opacity: 1; transform: translateY(0); }
}

// ── User messages (right-aligned) ──
.user-row,
.voice-row {
  justify-content: flex-end;
}

.user-bubble {
  max-width: 75%;
  background: $primary-gradient;
  padding: $spacing-md $spacing-lg;
  border-radius: 20rpx 20rpx 4rpx 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(192, 84, 74, 0.15);
}

.user-text {
  font-size: 28rpx;
  color: $text-inverse;
  line-height: 1.5;
  word-break: break-word;
}

// ── Voice bubble ──
.voice-bubble {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

.voice-icon {
  font-size: 32rpx;
}

.voice-dur {
  font-size: 26rpx;
  color: $text-inverse;
  font-weight: 500;
}

.voice-text {
  width: 100%;
  font-size: 26rpx;
  color: $text-inverse;
  line-height: 1.4;
  margin-top: $spacing-sm;
  word-break: break-word;
}

// ── Bot messages (left-aligned) ──
.bot-avatar {
  width: 56rpx;
  height: 56rpx;
  border-radius: $radius-full;
  background: $primary-light;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 4rpx;
}

.bot-avatar-text {
  font-size: 28rpx;
}

.bot-bubble {
  max-width: 68%;
  background: $bg-card;
  padding: $spacing-md $spacing-lg;
  border-radius: 4rpx 20rpx 20rpx 20rpx;
  box-shadow: $shadow-sm;
  border: 1rpx solid $border-light;
}

.bot-name {
  font-size: 20rpx;
  color: $text-tertiary;
  margin-bottom: $spacing-sm;
  display: block;
  letter-spacing: 1rpx;
}

.bot-text {
  font-size: 28rpx;
  color: $text-primary;
  line-height: 1.6;
  word-break: break-word;
}

// ── Bot todo card ──
.bot-todo-section {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
  margin-top: $spacing-md;
}

.bot-todo-card {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-md;
  background: $success-light;
  border-radius: $radius-sm;
}

.bot-todo-card-hover {
  opacity: 0.7;
}

.bot-todo-check {
  width: 36rpx;
  height: 36rpx;
  border-radius: $radius-full;
  background: $success;
  color: $text-inverse;
  font-size: 20rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bot-todo-title {
  font-size: 26rpx;
  color: $success;
  font-weight: 500;
}

// ── Welcome bubble ──
.welcome-bubble {
  background: linear-gradient(135deg, $bg-card, lighten($primary-light, 1%));
}

.hint-chips {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
  margin-top: $spacing-md;
}

.hint-chip {
  padding: $spacing-xs 18rpx;
  border-radius: 24rpx;
  background: $primary-light;
  border: 1rpx solid lighten($primary, 40%);
}

.hint-chip text {
  font-size: 22rpx;
  color: $primary;
}

// ── System message ──
.sys-msg {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  width: 100%;
  box-sizing: border-box;
}

.sys-line {
  flex: 1;
  height: 1rpx;
  background: $border;
}

.sys-text {
  font-size: 22rpx;
  color: $text-tertiary;
  white-space: nowrap;
}

// ── Typing ──
.typing-bubble {
  padding: $spacing-lg $spacing-xl;
}

.typing-dots {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.typing-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: $radius-full;
  background: $text-tertiary;
  animation: typingBounce 1.2s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-12rpx); opacity: 1; }
}

// ── Spacer (balances bot avatar on user rows) ──
.msg-spacer {
  width: 56rpx;
  flex-shrink: 0;
}

// ── Bottom ──
.msg-bottom {
  height: 20rpx;
}

// =============================================
//  Recording Overlay
// =============================================
.recording-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: rgba(45, 42, 38, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.recording-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-lg;
  position: relative;
}

.record-ring-pulse {
  width: 180rpx;
  height: 180rpx;
  border-radius: $radius-full;
  background: rgba(255, 255, 255, 0.1);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: recPulse 1.2s ease-out infinite;
}

@keyframes recPulse {
  0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.6; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

.record-ring-inner {
  width: 140rpx;
  height: 140rpx;
  border-radius: $radius-full;
  background: $danger;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 60rpx rgba(192, 84, 74, 0.4);
  position: relative;
}

.record-icon {
  font-size: 56rpx;
}

// Cancelling state
.recording-indicator.cancelling .record-ring-pulse {
  background: rgba(255, 69, 69, 0.3);
  animation: cancelPulse 1s ease-out infinite;
}

.recording-indicator.cancelling .record-ring-inner {
  background: #FF4545;
  box-shadow: 0 0 60rpx rgba(255, 69, 69, 0.6);
  animation: cancelShake 0.5s ease-in-out;
}

.recording-indicator.cancelling .record-icon {
  font-size: 48rpx;
  color: #FFFFFF;
}

.recording-indicator.cancelling .record-hint {
  color: #FF4545;
  font-weight: 600;
}

@keyframes cancelPulse {
  0% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.8; }
  100% { transform: translate(-50%, -50%) scale(1.6); opacity: 0; }
}

@keyframes cancelShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8rpx); }
  75% { transform: translateX(8rpx); }
}

.record-dur {
  font-size: 56rpx;
  color: $text-inverse;
  font-weight: 300;
  font-variant-numeric: tabular-nums;
}

.record-hint {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
}

// =============================================
//  Input Bar
// =============================================
.input-bar {
  background: $bg-card;
  border-top: 1rpx solid $border-light;
  padding: $spacing-md $spacing-xl;
  padding-bottom: calc($spacing-md + env(safe-area-inset-bottom, 0rpx));
  width: 100%;
  box-sizing: border-box;
}

.input-inner {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  width: 100%;
}

.input-field {
  flex: 1;
  background: $bg-input;
  border-radius: 40rpx;
  padding: $spacing-sm $spacing-lg;
}

.input-field input {
  font-size: 28rpx;
  color: $text-primary;
  height: 48rpx;
  line-height: 48rpx;
}

.input-placeholder {
  color: $text-tertiary;
  font-size: 28rpx;
}

.input-btn {
  width: 80rpx;
  height: 80rpx;
  border-radius: $radius-full;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-input;
  transition: $transition-base;
  flex-shrink: 0;
}

.input-btn.is-send {
  background: $primary;
  box-shadow: 0 4rpx 16rpx rgba(192, 84, 74, 0.25);
}

.btn-icon {
  font-size: 32rpx;
}

.send-icon {
  color: $text-inverse;
  font-size: 36rpx;
  font-weight: 700;
}

.mic-icon {
  font-size: 36rpx;
}

.input-btn-hover {
  transform: scale(0.9);
}

.input-btn.is-send.input-btn-hover {
  opacity: 0.85;
}
</style>
