<template>
  <div class="control-panel">
    <div class="status-indicator" :class="{ active: isListening }">
      <div class="status-icon">
        <div class="mic-icon" :class="{ 'pulse': isListening }">
          <svg :class="{ 'hidden': isListening }" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 15c1.66 0 3-1.34 3-3V6c0-1.66-1.34-3-3-3S9 4.34 9 6v6c0 1.66 1.34 3 3 3z" />
            <path d="M17 12c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-2.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
          <svg :class="{ 'hidden': !isListening }" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 15c1.66 0 3-1.34 3-3V6c0-1.66-1.34-3-3-3S9 4.34 9 6v6c0 1.66 1.34 3 3 3z" />
            <path d="M17 12c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-2.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
        </div>
      </div>
      <div class="status-text">{{ statusText }}</div>
    </div>
    
    <div class="controls">
      <el-button
        type="primary"
        :icon="isListening ? CircleClose : Microphone"
        :class="{ 'listening-active': isListening }"
        @click="toggleListening"
      >
        {{ isListening ? '停止' : '开始对话' }}
      </el-button>
      
      <div class="language-selector">
        <el-select v-model="selectedLanguage" :disabled="isListening">
          <el-option
            v-for="language in languages"
            :key="language.code"
            :label="language.name"
            :value="language.code"
          />
        </el-select>
      </div>
    </div>
    
    <div class="audio-indicator" v-if="isListening">
      <div 
        v-for="bar in 10" 
        :key="bar" 
        class="audio-bar"
        :style="{ height: `${getRandomHeight()}px` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, watch } from 'vue';
import { Microphone, CircleClose } from '@element-plus/icons-vue';

// 定义属性
const props = defineProps({
  isListening: {
    type: Boolean,
    default: false
  },
  status: {
    type: String,
    default: 'idle' // idle, listening, processing, error
  }
});

// 定义事件
const emit = defineEmits(['toggle-listening', 'language-change']);

// 语言选项
const languages = [
  { code: 'zh', name: '中文' },
  { code: 'en', name: '英文' },
  { code: 'fr', name: '法语' },
  { code: 'es', name: '西班牙语' },
  { code: 'ja', name: '日语' },
  { code: 'ko', name: '韩语' }
];

// 选中的语言
const selectedLanguage = ref('zh');

// 监听语言变化
watch(selectedLanguage, (newValue: string) => {
  emit('language-change', newValue);
});

// 状态文本
const statusText = computed(() => {
  if (props.status === 'idle') return '准备就绪';
  if (props.status === 'listening') return '正在聆听...';
  if (props.status === 'processing') return '正在处理...';
  if (props.status === 'error') return '发生错误';
  return '准备就绪';
});

// 切换监听状态
const toggleListening = () => {
  emit('toggle-listening');
};

// 为音频指示器生成随机高度
let animationFrame: number | null = null;
const getRandomHeight = () => Math.floor(Math.random() * 20) + 5;

// 清理动画帧
onUnmounted(() => {
  if (animationFrame !== null) {
    cancelAnimationFrame(animationFrame);
  }
});
</script>

<style scoped>
.control-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background-color: #f5f5f5;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.status-indicator.active {
  background-color: #e3f2fd;
}

.status-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mic-icon {
  width: 24px;
  height: 24px;
  fill: #666;
  transition: fill 0.3s;
}

.mic-icon.pulse {
  fill: #1976d2;
}

.mic-icon svg {
  width: 100%;
  height: 100%;
  transition: opacity 0.3s;
}

.mic-icon svg.hidden {
  opacity: 0;
  position: absolute;
}

.status-text {
  font-size: 14px;
  color: #333;
}

.controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.listening-active {
  background-color: #f44336;
  border-color: #f44336;
}

.language-selector {
  width: 120px;
}

.audio-indicator {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 2px;
  height: 30px;
  padding: 0 16px;
}

.audio-bar {
  width: 3px;
  background-color: #1976d2;
  border-radius: 1px;
  transition: height 0.1s ease;
}
</style> 