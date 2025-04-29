<template>
  <div class="chat-window">
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="empty-chat">
        <p>{{ emptyMessage }}</p>
      </div>
      <transition-group name="message-fade">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.type]"
        >
          <div class="message-avatar">
            <img
              :src="message.type === 'user' ? userIcon : aiIcon"
              :alt="message.type === 'user' ? '用户' : 'AI'"
            />
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-sender">{{
                message.type === "user" ? "用户" : "AI"
              }}</span>
              <span class="message-time">{{
                formatTime(message.timestamp)
              }}</span>
            </div>
            <div class="message-text">
              <TypewriterText 
                v-if="message.type === 'ai' && animateText" 
                :text="message.text" 
                :key="message.timestamp"
                :speed="typewriterSpeed"
              />
              <template v-else>{{ message.text }}</template>
            </div>
          </div>
        </div>
      </transition-group>
      <div v-if="isProcessing" class="processing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <div v-if="showScrollButton" class="scroll-to-bottom" @click="scrollToBottom">
        <div class="scroll-icon">↓</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, h, defineComponent } from "vue";
import userIcon from "@/assets/figma/user_icon.svg";
import aiIcon from "@/assets/figma/ai_icon.svg";

// 导入打字机效果组件
const TypewriterText = defineComponent({
  props: {
    text: { type: String, required: true },
    speed: { type: Number, default: 30 }
  },
  setup(props: { text: string; speed: number }) {
    const displayedText = ref('');
    const isComplete = ref(false);
    
    onMounted(() => {
      let index = 0;
      const interval = setInterval(() => {
        if (index < props.text.length) {
          displayedText.value = props.text.substring(0, index + 1);
          index++;
        } else {
          isComplete.value = true;
          clearInterval(interval);
        }
      }, props.speed);
      
      // 清理工作
      onUnmounted(() => {
        clearInterval(interval);
      });
    });
    
    return () => h('div', { class: { 'typewriter-text': true, 'complete': isComplete.value } }, displayedText.value);
  }
});

interface Message {
  type: "user" | "ai";
  text: string;
  timestamp: number;
}

const props = defineProps({
  messages: {
    type: Array as () => Message[],
    default: () => [],
  },
  isProcessing: {
    type: Boolean,
    default: false,
  },
  emptyMessage: {
    type: String,
    default: "开始一段新的对话...",
  },
  animateText: {
    type: Boolean,
    default: true,
  },
  typewriterSpeed: {
    type: Number,
    default: 30,
  }
});

const messagesContainer = ref<HTMLElement | null>(null);
const isScrolling = ref(false);
const isAtBottom = ref(true);
const showScrollButton = ref(false);

// 检测是否在底部
const checkIfAtBottom = () => {
  if (!messagesContainer.value) return;
  
  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value;
  const scrollBottom = scrollTop + clientHeight;
  // 如果滚动位置在距离底部20px之内，认为是在底部
  isAtBottom.value = scrollBottom >= scrollHeight - 20;
  showScrollButton.value = !isAtBottom.value;
};

// 监听消息变化，自动滚动到底部
watch(
  () => props.messages.length,
  () => {
    if (isAtBottom.value) {
      scrollToBottom();
    } else {
      showScrollButton.value = true;
    }
  }
);

// 监听处理状态变化，自动滚动到底部
watch(
  () => props.isProcessing,
  (newValue) => {
    if (newValue === true) {
      scrollToBottom();
    }
  }
);

// 监听滚动事件
const handleScroll = () => {
  if (isScrolling.value) return;
  isScrolling.value = true;
  
  // 使用requestAnimationFrame优化滚动性能
  requestAnimationFrame(() => {
    checkIfAtBottom();
    isScrolling.value = false;
  });
};

onMounted(() => {
  scrollToBottom();
  
  if (messagesContainer.value) {
    messagesContainer.value.addEventListener('scroll', handleScroll);
  }
  
  // 清理
  onUnmounted(() => {
    if (messagesContainer.value) {
      messagesContainer.value.removeEventListener('scroll', handleScroll);
    }
  });
});

// 格式化时间戳
const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp);
  return `${date.getHours().toString().padStart(2, "0")}:${date
    .getMinutes()
    .toString()
    .padStart(2, "0")}`;
};

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    showScrollButton.value = false;
    isAtBottom.value = true;
  }
};
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f9f9f9;
  border-radius: 8px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  scroll-behavior: smooth;
}

.empty-chat {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
  font-style: italic;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 85%;
  transition: opacity 0.3s, transform 0.3s;
}

.message-fade-enter-active,
.message-fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.message-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-fade-leave-to {
  opacity: 0;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.ai {
  align-self: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  background-color: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-width: 100px;
  word-break: break-word;
}

.message.user .message-content {
  background-color: #1976d2;
  color: white;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 0.85rem;
}

.message.user .message-header {
  color: rgba(255, 255, 255, 0.8);
}

.message-sender {
  font-weight: 600;
}

.message-time {
  font-size: 0.75rem;
  color: #888;
}

.message.user .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.message-text {
  line-height: 1.4;
  white-space: pre-wrap;
}

.processing-indicator {
  align-self: flex-start;
  display: flex;
  gap: 4px;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 12px;
}

.processing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #888;
  border-radius: 50%;
  display: inline-block;
  animation: pulse 1.5s infinite ease-in-out;
}

.processing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.processing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

.scroll-to-bottom {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #1976d2;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s;
  z-index: 10;
}

.scroll-to-bottom:hover {
  transform: scale(1.1);
}

.scroll-icon {
  font-size: 20px;
  font-weight: bold;
}

/* 打字机效果 */
.typewriter-text {
  display: inline;
  position: relative;
}

.typewriter-text.complete::after {
  content: '';
  display: none;
}

.typewriter-text::after {
  content: '|';
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
