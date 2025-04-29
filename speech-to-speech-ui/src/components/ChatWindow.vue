<template>
  <div class="chat-window">
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="empty-chat">
        <p>{{ emptyMessage }}</p>
      </div>
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
          <div class="message-text">{{ message.text }}</div>
        </div>
      </div>
      <div v-if="isProcessing" class="processing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from "vue";
import userIcon from "@/assets/figma/user_icon.svg";
import aiIcon from "@/assets/figma/ai_icon.svg";

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
});

const messagesContainer = ref<HTMLElement | null>(null);

// 监听消息变化，自动滚动到底部
watch(
  () => props.messages.length,
  () => {
    scrollToBottom();
  }
);

// 监听处理状态变化，自动滚动到底部
watch(
  () => props.isProcessing,
  () => {
    scrollToBottom();
  }
);

onMounted(() => {
  scrollToBottom();
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
</style>
