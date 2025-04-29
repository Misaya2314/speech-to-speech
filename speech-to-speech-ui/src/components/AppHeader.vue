<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo">
        <img :src="logoImage" alt="Logo" class="logo-image" />
        <span class="logo-text">Speech-to-Speech</span>
      </div>
      
      <div class="main-menu">
        <div 
          v-for="item in menuItems" 
          :key="item.id"
          :class="['menu-item', { active: activeMenuItem === item.id }]"
          @click="setActiveMenuItem(item.id)"
        >
          {{ item.label }}
        </div>
      </div>
    </div>
    
    <div class="header-right">
      <el-tooltip content="帮助文档" placement="bottom">
        <el-button :icon="QuestionFilled" circle class="header-button" @click="openHelp" />
      </el-tooltip>
      
      <el-tooltip content="设置" placement="bottom">
        <el-button :icon="Setting" circle class="header-button" @click="openSettings" />
      </el-tooltip>
      
      <div class="window-controls">
        <div class="control-button minimize-btn" @click="minimizeWindow">
          <el-icon><Minus /></el-icon>
        </div>
        
        <div class="control-button maximize-btn" @click="maximizeWindow">
          <el-icon><FullScreen /></el-icon>
        </div>
        
        <div class="control-button close-btn" @click="closeWindow">
          <el-icon><Close /></el-icon>
        </div>
      </div>
    </div>
  </header>
</template>

<script lang="ts">
// 先添加全局类型声明
declare global {
  interface Window {
    electron?: {
      minimizeWindow: () => void;
      maximizeWindow: () => void;
      closeWindow: () => void;
    };
  }
}
</script>

<script setup lang="ts">
import { ref } from 'vue';
import { Setting, QuestionFilled, Minus, FullScreen, Close } from '@element-plus/icons-vue';
import logoImage from '@/assets/figma/logo.svg';

// 菜单项定义
const menuItems = [
  { id: 'home', label: '主页' },
  { id: 'history', label: '历史记录' },
  { id: 'models', label: '模型' },
  { id: 'language', label: '语言' }
];

// 当前活动菜单项
const activeMenuItem = ref('home');

// 定义事件
const emit = defineEmits(['open-settings', 'open-help', 'menu-change']);

// 设置当前活动菜单项
const setActiveMenuItem = (id: string) => {
  activeMenuItem.value = id;
  emit('menu-change', id);
};

// 打开设置
const openSettings = () => {
  emit('open-settings');
};

// 打开帮助
const openHelp = () => {
  emit('open-help');
};

// 窗口控制函数
const minimizeWindow = () => {
  if (typeof window !== 'undefined' && window.electron) {
    window.electron.minimizeWindow();
  }
};

const maximizeWindow = () => {
  if (typeof window !== 'undefined' && window.electron) {
    window.electron.maximizeWindow();
  }
};

const closeWindow = () => {
  if (typeof window !== 'undefined' && window.electron) {
    window.electron.closeWindow();
  }
};
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 16px;
  background-color: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  -webkit-app-region: drag; /* 允许拖动窗口 */
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  -webkit-app-region: no-drag; /* 禁止在按钮上拖动窗口 */
}

.logo {
  display: flex;
  align-items: center;
  margin-right: 24px;
}

.logo-image {
  width: 32px;
  height: 32px;
  margin-right: 8px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.main-menu {
  display: flex;
  gap: 16px;
}

.menu-item {
  padding: 0 12px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  height: 60px;
  display: flex;
  align-items: center;
  transition: all 0.3s;
  position: relative;
}

.menu-item:hover {
  color: #1976d2;
}

.menu-item.active {
  color: #1976d2;
  font-weight: 500;
}

.menu-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #1976d2;
}

.header-button {
  margin-left: 8px;
}

.window-controls {
  display: flex;
  margin-left: 16px;
}

.control-button {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.control-button:hover {
  background-color: #f0f0f0;
}

.close-btn:hover {
  background-color: #f44336;
  color: white;
}
</style> 