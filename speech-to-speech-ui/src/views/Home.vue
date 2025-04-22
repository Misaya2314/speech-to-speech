<template>
  <div class="flowmind-container">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <div class="header-left">
        <h1 class="logo-text">FlowMind testVer1.1</h1>
        <div class="menu-bar">
          <div class="menu-item">文件</div>
          <div class="menu-item">模型</div>
          <div class="menu-item">显示</div>
          <div class="menu-item">语言</div>
        </div>
      </div>
      
      <div class="header-right">
        <div class="menu-item">
          <img :src="infoIcon" alt="使用教程" class="tutorial-icon" />
          <span>使用教程</span>
        </div>
        <div class="window-controls">
          <div class="control-button settings-btn">
            <img :src="settingsIcon" alt="设置" />
          </div>
          <div class="control-button minimize-btn">
            <img :src="minusIcon" alt="最小化" />
          </div>
          <div class="control-button maximize-btn">
            <img :src="squareIcon" alt="最大化" />
          </div>
          <div class="control-button close-btn">
            <img :src="powerIcon" alt="关闭" />
          </div>
        </div>
      </div>
    </header>

    <!-- 主体内容区 -->
    <div class="main-content">
      <!-- 左侧区域 -->
      <div class="left-sidebar">
        <div class="sidebar-item-group">
          <div class="sidebar-icon">
            <img :src="editIcon" alt="编辑" />
          </div>
          <h2>语义建模</h2>
          <div class="sidebar-item active">
            <span>语音建模</span>
          </div>
          <div class="sidebar-item">
            <span>模型调用</span>
          </div>
        </div>
        
        <div class="sidebar-divider"></div>
        
        <div class="sidebar-item-group">
          <div class="sidebar-icon">
            <img :src="toolIcon" alt="工具" />
          </div>
          <h2>物理仿真</h2>
          <div class="sidebar-item">
            <span>流体分析</span>
          </div>
          <div class="sidebar-item">
            <span>结构强度</span>
          </div>
        </div>
        
        <div class="sidebar-divider"></div>
        
        <div class="sidebar-item-group">
          <div class="sidebar-icon">
            <img :src="bookOpenIcon" alt="书籍" />
          </div>
          <h2>知识管理</h2>
          <div class="sidebar-item">
            <span>智能索引</span>
          </div>
          <div class="sidebar-item">
            <span>规则提取</span>
          </div>
          <div class="sidebar-item">
            <span>案例调用</span>
          </div>
        </div>
        
        <div class="sidebar-divider"></div>
        
        <div class="sidebar-item-group">
          <div class="sidebar-icon">
            <img :src="crosshairIcon" alt="决策" />
          </div>
          <h2>决策优化</h2>
          <div class="sidebar-item">
            <span>方案对比</span>
          </div>
          <div class="sidebar-item">
            <span>性能评估</span>
          </div>
          <div class="sidebar-item">
            <span>决策生成</span>
          </div>
          <div class="sidebar-item">
            <span>成本估算</span>
          </div>
          <div class="sidebar-item">
            <span>报告预览</span>
          </div>
        </div>
      </div>

      <!-- 中间主工作区 -->
      <div class="center-content">
        <div class="main-workspace">
          <!-- 内容区域 -->
        </div>
        
        <!-- 底部控制台 -->
        <div class="bottom-console">
          <div class="console-section">
            <h3>Graph</h3>
            <div class="console-content">
              <!-- 图表内容 -->
            </div>
          </div>
          <div class="console-section">
            <h3>Data</h3>
            <div class="console-content data-logs">
              <div
                v-for="(log, index) in dataLogs"
                :key="index"
                class="log-item"
              >
                {{ log }}
              </div>
              <div v-if="!dataLogs.length" class="empty-placeholder">
                <span>无数据记录</span>
              </div>
            </div>
          </div>
          <div class="console-section">
            <h3>System Monitor</h3>
            <div class="console-content">
              <!-- 系统监控内容 -->
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部输入区 -->
    <div class="bottom-input-area">
      <div class="mic-buttons">
        <div
          class="mic-button"
          :class="{ active: isListening }"
          @click="toggleListening"
        >
          <img
            :src="isListening ? micIcon : micOffIcon"
            alt="Microphone"
          />
        </div>
      </div>
      
      <div class="input-field">
        <input type="text" placeholder="输入命令..." />
      </div>
      
      <div class="return-button">
        <img :src="cornerDownLeftIcon" alt="Return" />
      </div>
    </div>

    <!-- 语音命令反馈 -->
    <div v-if="lastCommand" class="voice-feedback">
      <div class="feedback-content">
        <span>{{ lastCommand }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import {
  WebSocketClient,
  EventType,
  StatusType,
} from "@/utils/websocket-client";

// 导入图标
import editIcon from '@/assets/figma/edit_icon.svg';
import toolIcon from '@/assets/figma/tool_icon.svg';
import crosshairIcon from '@/assets/figma/crosshair_icon.svg';
import bookOpenIcon from '@/assets/figma/book_open_icon.svg';
import settingsIcon from '@/assets/figma/settings_icon.svg';
import infoIcon from '@/assets/figma/info_icon.svg';
import cornerDownLeftIcon from '@/assets/figma/corner_down_left_icon.svg';
import minusIcon from '@/assets/figma/minus_icon.svg';
import squareIcon from '@/assets/figma/square_icon.svg';
import powerIcon from '@/assets/figma/power_icon.svg';
import micIcon from '@/assets/figma/mic_icon.svg';
import micOffIcon from '@/assets/figma/mic_off_icon.svg';

// 状态管理
const isListening = ref(false);
const status = ref(StatusType.IDLE);
const currentLanguage = ref("zh");
const wsClient = ref<WebSocketClient | null>(null);
const lastCommand = ref("");
const dataLogs = ref<string[]>([]);

// 添加数据日志
const addDataLog = (message: string) => {
  const timestamp = new Date().toLocaleTimeString();
  dataLogs.value.push(`[${timestamp}] ${message}`);

  // 保持最大日志数
  if (dataLogs.value.length > 20) {
    dataLogs.value.shift();
  }
};

// 开始/停止监听
const toggleListening = () => {
  if (!isListening.value) {
    isListening.value = true;
    if (wsClient.value) {
      wsClient.value.startListening();
      addDataLog("开始语音监听");
    } else {
      addDataLog("错误: WebSocket客户端未初始化");
    }
  } else {
    isListening.value = false;
    if (wsClient.value) {
      wsClient.value.stopListening();
      addDataLog("停止语音监听");
    }
  }
};

// 处理语音命令
const handleVoiceCommand = (text: string) => {
  lastCommand.value = text;
  addDataLog(`接收到命令: ${text}`);

  // 这里可以添加命令解析逻辑
  setTimeout(() => {
    addDataLog(`执行命令: ${text}`);
  }, 500);
};

// 组件挂载时初始化WebSocket连接
onMounted(() => {
  try {
    wsClient.value = new WebSocketClient({
      url: "ws://localhost:3210",
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
    });

    wsClient.value.on(EventType.CONNECTED, () => {
      console.log("WebSocket已连接");
      status.value = StatusType.CONNECTED;
      wsClient.value?.setLanguage(currentLanguage.value);
      addDataLog("WebSocket连接已建立");
    });

    wsClient.value.on(EventType.DISCONNECTED, () => {
      console.log("WebSocket已断开");
      status.value = StatusType.DISCONNECTED;
      isListening.value = false;
      addDataLog("WebSocket连接已断开");
    });

    wsClient.value.on(EventType.TRANSCRIPTION, (data: { text: string }) => {
      handleVoiceCommand(data.text);
    });

    wsClient.value.connect();

    // 模拟数据日志
    addDataLog("系统初始化完成");
    addDataLog("加载模型中...");
    addDataLog("模型加载完成");
  } catch (error: any) {
    console.error("初始化WebSocket客户端失败:", error);
    addDataLog(`错误: ${error.message}`);
  }
});

// 组件卸载时关闭WebSocket连接
onUnmounted(() => {
  if (wsClient.value) {
    wsClient.value.disconnect();
  }
});
</script>

<style scoped>
.flowmind-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f3f3f3;
  font-family: "Inter", "Microsoft YaHei", Arial, sans-serif;
}

/* 顶部导航栏样式 */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  background: linear-gradient(to right, #00205f, #005d8c, #ad2e7c);
  color: white;
  padding: 0 10px;
  -webkit-app-region: drag;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.logo-text {
  font-family: "Nico Moji", sans-serif;
  font-size: 36px;
  color: #f28b93;
  margin: 0 20px 0 0;
  white-space: nowrap;
}

.menu-bar {
  display: flex;
  gap: 15px;
}

.menu-item {
  font-size: 18px;
  color: white;
  cursor: pointer;
  padding: 5px 10px;
  -webkit-app-region: no-drag;
  display: flex;
  align-items: center;
  gap: 5px;
}

.tutorial-icon {
  width: 20px;
  height: 20px;
  filter: invert(1);
}

.window-controls {
  display: flex;
  margin-left: 15px;
}

.control-button {
  width: 32px;
  height: 32px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  -webkit-app-region: no-drag;
  border-radius: 4px;
  margin-left: 5px;
}

.control-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.control-button img {
  width: 16px;
  height: 16px;
  filter: invert(1);
}

.close-btn:hover {
  background-color: rgba(224, 67, 67, 0.8);
}

/* 主内容区样式 */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧菜单样式 */
.left-sidebar {
  width: 230px;
  padding: 15px;
  overflow-y: auto;
  background-color: white;
  border-right: 1px solid #ddd;
}

.sidebar-item-group {
  margin-bottom: 15px;
  position: relative;
}

.sidebar-icon {
  position: absolute;
  left: 0;
  top: 5px;
  width: 20px;
  height: 20px;
}

.sidebar-icon img {
  width: 100%;
  height: 100%;
  opacity: 0.7;
}

.sidebar-item-group h2 {
  font-family: serif;
  font-size: 20px;
  font-weight: normal;
  margin: 0 0 8px 28px;
}

.sidebar-item {
  padding: 6px 6px 6px 28px;
  margin: 2px 0;
  cursor: pointer;
  font-size: 16px;
  border-radius: 4px;
}

.sidebar-item.active {
  background-color: #d9d9d9;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
}

.sidebar-divider {
  height: 1px;
  background-color: #ddd;
  margin: 15px 0;
}

/* 中间内容区样式 */
.center-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 10px;
}

.main-workspace {
  flex: 1;
  background-color: #d9d9d9;
  border-radius: 10px;
  margin-bottom: 10px;
}

.bottom-console {
  height: 200px;
  display: flex;
  gap: 10px;
}

.console-section {
  flex: 1;
  background-color: #d9d9d9;
  border-radius: 5px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.console-section h3 {
  margin: 0;
  padding: 8px 15px;
  font-size: 18px;
  font-weight: normal;
  color: #333;
  border-bottom: 1px solid #ccc;
}

.console-content {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

.data-logs {
  font-family: monospace;
  font-size: 14px;
}

.log-item {
  padding: 3px 0;
  border-bottom: 1px dashed #ccc;
}

.empty-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #777;
}

/* 底部输入区 */
.bottom-input-area {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: white;
  border-top: 1px solid #ddd;
}

.mic-buttons {
  margin-right: 15px;
}

.mic-button {
  width: 40px;
  height: 40px;
  background-color: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.mic-button.active {
  background-color: #4caf50;
}

.mic-button img {
  width: 20px;
  height: 20px;
}

.input-field {
  flex: 1;
}

.input-field input {
  width: 100%;
  height: 36px;
  padding: 0 15px;
  border: 1px solid #ccc;
  border-radius: 18px;
  outline: none;
  font-size: 14px;
}

.return-button {
  width: 40px;
  height: 40px;
  background-color: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  margin-left: 15px;
}

.return-button img {
  width: 20px;
  height: 20px;
}

/* 语音反馈 */
.voice-feedback {
  position: fixed;
  bottom: 80px;
  right: 20px;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  z-index: 100;
  max-width: 300px;
}

.feedback-content {
  display: flex;
  align-items: center;
}
</style>
