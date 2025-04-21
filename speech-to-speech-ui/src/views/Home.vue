<template>
  <div class="flowmind-container">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <div class="logo-section">
        <h1>FlowMind AI testVer1.0</h1>
        <div class="project-title">A: 汽车内饰设计测试3</div>
      </div>
      <div class="menu-bar">
        <div class="menu-item">文件</div>
        <div class="menu-item">模型</div>
        <div class="menu-item">显示</div>
        <div class="menu-item">工具</div>
        <div class="menu-item">多任务</div>
        <div class="menu-item">教程与案例</div>
        <div class="menu-item right-align">问号</div>
      </div>
    </header>

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 左侧边栏 -->
      <div class="left-sidebar">
        <div class="sidebar-section">
          <h3>建模交互</h3>
          <div class="sidebar-item active">语音建模</div>
          <div class="sidebar-item">指令解析</div>
        </div>

        <div class="sidebar-section">
          <h3>物理仿真</h3>
          <div class="sidebar-item">开发中</div>
        </div>

        <div class="sidebar-section">
          <h3>动态知识库</h3>
          <div class="sidebar-item">本地案例</div>
          <div class="sidebar-item">设计查询</div>
          <div class="sidebar-item">专家经验</div>
        </div>

        <div class="sidebar-section">
          <h3>AI辅助决策</h3>
          <div class="sidebar-item">设计优化</div>
          <div class="sidebar-item">决策生成</div>
          <div class="sidebar-item">报告预览</div>
        </div>
      </div>

      <!-- 中间主内容区 -->
      <div class="center-content">
        <div class="main-workspace">
          <!-- 3D设计视图区域 -->
          <div class="design-view">
            <div class="placeholder-3d">
              <span>汽车内饰设计视图</span>
              <p>使用左侧工具栏的语音按钮开始语音控制</p>
            </div>

            <!-- 工具栏组件 -->
            <ToolBar
              :is-listening="isListening"
              @toggle-listening="startListening"
            />
          </div>

          <!-- 语音指令反馈区 -->
          <div class="voice-feedback" v-if="lastCommand">
            <el-alert
              :title="lastCommand"
              type="success"
              :closable="false"
              show-icon
            >
              <template #icon
                ><el-icon><MicrophoneIcon /></el-icon
              ></template>
            </el-alert>
          </div>
        </div>

        <!-- 底部控制台 -->
        <div class="bottom-console">
          <div class="console-section">
            <h3>Graph</h3>
            <div class="placeholder-graph">
              <span>组件依赖关系图</span>
            </div>
          </div>
          <div class="console-section">
            <h3>Data</h3>
            <div class="data-logs">
              <div
                v-for="(log, index) in dataLogs"
                :key="index"
                class="log-item"
              >
                {{ log }}
              </div>
              <div v-if="!dataLogs.length" class="placeholder-data">
                <span>无数据记录</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { Microphone as MicrophoneIcon } from "@element-plus/icons-vue";
import {
  WebSocketClient,
  EventType,
  StatusType,
} from "@/utils/websocket-client";
import ToolBar from "@/components/ToolBar.vue";

// 状态管理
const isListening = ref(false);
const status = ref(StatusType.IDLE);
const messages = ref([]);
const currentLanguage = ref("zh");
const wsClient = ref(null);
const lastCommand = ref("");
const dataLogs = ref([]);

// 添加数据日志
const addDataLog = (message) => {
  const timestamp = new Date().toLocaleTimeString();
  dataLogs.value.push(`[${timestamp}] ${message}`);

  // 保持最大日志数
  if (dataLogs.value.length > 20) {
    dataLogs.value.shift();
  }
};

// 开始/停止监听
const startListening = () => {
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
const handleVoiceCommand = (text) => {
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
      url: "ws://localhost:8765",
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
    });

    wsClient.value.on(EventType.CONNECTED, () => {
      console.log("WebSocket已连接");
      status.value = StatusType.CONNECTED;
      wsClient.value.setLanguage(currentLanguage.value);
      addDataLog("WebSocket连接已建立");
    });

    wsClient.value.on(EventType.DISCONNECTED, () => {
      console.log("WebSocket已断开");
      status.value = StatusType.DISCONNECTED;
      isListening.value = false;
      addDataLog("WebSocket连接已断开");
    });

    wsClient.value.on(EventType.TRANSCRIPTION, (data) => {
      handleVoiceCommand(data.text);
    });

    wsClient.value.connect();

    // 模拟数据日志
    addDataLog("系统初始化完成");
    addDataLog("加载汽车内饰模型...");
    addDataLog("模型加载完成");
  } catch (error) {
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
  font-family: "Microsoft YaHei", Arial, sans-serif;
}

.top-header {
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  padding: 0 20px;
}

.logo-section {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.logo-section h1 {
  font-size: 1.5rem;
  margin: 0;
  margin-right: 20px;
  color: #333;
}

.project-title {
  font-size: 1.2rem;
  color: #666;
}

.menu-bar {
  display: flex;
  border-top: 1px solid #e0e0e0;
  padding: 10px 0;
}

.menu-item {
  padding: 5px 15px;
  cursor: pointer;
}

.menu-item:hover {
  background-color: #f0f0f0;
}

.right-align {
  margin-left: auto;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.left-sidebar {
  width: 200px;
  background-color: #f7f7f7;
  border-right: 1px solid #e0e0e0;
  padding: 15px;
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: 25px;
}

.sidebar-section h3 {
  font-size: 1.1rem;
  margin-bottom: 10px;
  color: #333;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 5px;
}

.sidebar-item {
  padding: 8px 10px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #555;
  border-radius: 4px;
}

.sidebar-item:hover {
  background-color: #e8e8e8;
}

.sidebar-item.active {
  background-color: #ecf5ff;
  color: #409eff;
}

.center-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-workspace {
  flex: 1;
  padding: 0;
  overflow: hidden;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  margin: 10px;
  position: relative;
}

.design-view {
  width: 100%;
  height: 100%;
  position: relative;
  background-color: #f0f0f0;
}

.placeholder-3d {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
}

.placeholder-3d span {
  font-size: 1.5rem;
  margin-bottom: 10px;
}

.voice-feedback {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 300px;
}

.bottom-console {
  height: 200px;
  display: flex;
  border-top: 1px solid #e0e0e0;
  margin: 0 10px 10px 10px;
}

.console-section {
  flex: 1;
  border: 1px solid #e0e0e0;
  margin: 10px 5px;
  padding: 10px;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.console-section h3 {
  margin-top: 0;
  font-size: 1rem;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 5px;
  margin-bottom: 10px;
}

.placeholder-graph,
.placeholder-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
}

.data-logs {
  flex: 1;
  overflow-y: auto;
  font-family: "Consolas", monospace;
  font-size: 0.85rem;
}

.log-item {
  padding: 3px 0;
  border-bottom: 1px dashed #eee;
}
</style>
