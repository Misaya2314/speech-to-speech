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
        <div class="menu-item" @click="openHelp">
          <el-icon><QuestionFilled /></el-icon>
          <span>使用教程</span>
        </div>
        <div class="window-controls">
          <div class="control-button settings-btn" @click="openSettings">
            <el-icon><Setting /></el-icon>
          </div>
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

    <!-- 主体内容区 -->
    <div class="main-content">
      <!-- 左侧区域 -->
      <div class="left-sidebar">
        <div class="sidebar-item-group">
          <div class="sidebar-icon">
            <el-icon><EditPen /></el-icon>
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
            <el-icon><Tools /></el-icon>
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
            <el-icon><Reading /></el-icon>
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
          <div class="sidebar-item" @click="showKnowledgeManager = true">
            <span>本地知识库</span>
          </div>
        </div>
        
        <div class="sidebar-divider"></div>
        
        <div class="sidebar-item-group">
          <div class="sidebar-icon">
            <el-icon><Aim /></el-icon>
          </div>
          <h2>决策优化</h2>
          <div class="sidebar-item" @click="showComparison = true">
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
          <!-- 知识库管理视图 -->
          <div v-if="showKnowledgeManager" class="knowledge-view">
            <KnowledgeManager 
              @update="updateKnowledgeBase"
              @delete="handleDocumentDelete"
              @build-index="handleIndexBuild"
            />
          </div>
          
          <!-- 方案对比视图 -->
          <div v-else-if="showComparison" class="comparison-view">
            <h3>方案对比视图</h3>
            <div class="comparison-content">
              <!-- 这里放方案对比的具体内容 -->
              <div class="chat-area" v-if="showChatArea">
                <ChatWindow 
                  :messages="messages" 
                  :is-processing="isProcessing"
                  :empty-message="emptyMessage"
                />
              </div>
            </div>
          </div>
          
          <!-- 默认内容区域 -->
          <div v-else class="default-content">
            <div class="chat-area">
              <ChatWindow 
                :messages="messages" 
                :is-processing="isProcessing"
                :empty-message="emptyMessage"
              />
            </div>
          </div>
        </div>
        
        <!-- 底部控制台 -->
        <div class="bottom-console">
          <div class="console-section">
            <h3>Graph</h3>
            <div class="console-content">
              <!-- 图表内容 -->
              <div class="empty-placeholder" v-if="!graphData.length">
                <span>无图表数据</span>
              </div>
              <div v-else class="graph-container">
                <!-- 这里将来放置图表组件 -->
                <div v-for="(graph, index) in graphData" :key="index" class="graph-item">
                  {{ graph }}
                </div>
              </div>
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
              <div class="system-resource">
                <div class="resource-label">CPU:</div>
                <div class="resource-value">{{ systemResources.cpu }}%</div>
                <div class="resource-bar">
                  <div class="resource-progress" :style="{ width: systemResources.cpu + '%' }"></div>
                </div>
              </div>
              <div class="system-resource">
                <div class="resource-label">内存:</div>
                <div class="resource-value">{{ systemResources.memory }}%</div>
                <div class="resource-bar">
                  <div class="resource-progress" :style="{ width: systemResources.memory + '%' }"></div>
                </div>
              </div>
              <div class="system-resource">
                <div class="resource-label">模型:</div>
                <div class="resource-value">{{ systemResources.model }}%</div>
                <div class="resource-bar">
                  <div class="resource-progress" :style="{ width: systemResources.model + '%' }"></div>
                </div>
              </div>
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
          <el-icon v-if="isListening"><Microphone /></el-icon>
          <el-icon v-else><MuteNotification /></el-icon>
        </div>
      </div>
      
      <div class="input-field">
        <input type="text" placeholder="输入命令..." v-model="inputCommand" @keyup.enter="sendCommand" />
      </div>
      
      <div class="return-button" @click="sendCommand">
        <el-icon><Back /></el-icon>
      </div>
    </div>

    <!-- 语音命令反馈 -->
    <div v-if="lastCommand" class="voice-feedback">
      <div class="feedback-content">
        <span>{{ lastCommand }}</span>
      </div>
    </div>
    
    <!-- 设置对话框 -->
    <el-dialog
      v-model="settingsVisible"
      title="设置"
      width="70%"
      destroy-on-close
    >
      <SettingsPanel 
        :saved-settings="settings"
        @update-settings="updateSettings"
        @save-settings="saveSettings"
      />
    </el-dialog>
    
    <!-- 帮助对话框 -->
    <el-dialog
      v-model="helpVisible"
      title="使用帮助"
      width="70%"
    >
      <div class="help-content">
        <h3>FlowMind 使用指南</h3>
        <p>这是一个语音对话应用程序，您可以通过语音与AI进行自然交流，同时支持本地知识库。</p>
        
        <h4>基本使用</h4>
        <ol>
          <li>点击底部麦克风按钮开始录音</li>
          <li>对着麦克风说话，您的语音将被实时转换为文字</li>
          <li>说完后再次点击麦克风按钮，AI将处理您的语音并回复</li>
          <li>AI的回复将以语音形式播放出来</li>
        </ol>
        
        <h4>本地知识库</h4>
        <p>在"知识管理">"本地知识库"中，您可以：</p>
        <ul>
          <li>上传文档到知识库</li>
          <li>构建文档索引</li>
          <li>在对话中引用知识库内容</li>
        </ul>
        
        <h4>界面说明</h4>
        <p>主界面包含以下部分：</p>
        <ul>
          <li><strong>左侧功能栏</strong>：包含各种功能模块</li>
          <li><strong>中间工作区</strong>：显示对话内容和工作视图</li>
          <li><strong>右侧控制台</strong>：显示图表、数据日志和系统资源</li>
          <li><strong>底部输入区</strong>：语音输入和文本输入</li>
        </ul>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { 
  Setting, 
  QuestionFilled, 
  Minus, 
  FullScreen, 
  Close, 
  EditPen, 
  Tools, 
  Reading, 
  Aim,
  Microphone,
  MuteNotification,
  Back
} from '@element-plus/icons-vue';
import ChatWindow from '@/components/ChatWindow.vue';
import SettingsPanel from '@/components/SettingsPanel.vue';
import KnowledgeManager from '@/components/KnowledgeManager.vue';
import { WebSocketClient, EventType, MessageType } from '@/utils/websocket-client';

// 对话消息
interface Message {
  type: 'user' | 'ai';
  text: string;
  timestamp: number;
}

// 知识库文档接口
interface KnowledgeDocument {
  id: string;
  name: string;
  type: string;
  size: number;
  date: number;
  content?: string;
}

// 应用状态
const isListening = ref(false);
const isProcessing = ref(false);
const status = ref('idle');
const messages = ref<Message[]>([]);
const settingsVisible = ref(false);
const helpVisible = ref(false);
const emptyMessage = ref('点击下方麦克风按钮开始对话...');
const lastCommand = ref('');
const dataLogs = ref<string[]>([]);
const graphData = ref<string[]>([]);
const showComparison = ref(false);
const showChatArea = ref(true);
const inputCommand = ref('');
const showKnowledgeManager = ref(false);
const knowledgeDocuments = ref<KnowledgeDocument[]>([]);

// 系统资源监控
const systemResources = ref({
  cpu: 15,
  memory: 32,
  model: 45
});

// WebSocket客户端
let wsClient: WebSocketClient | null = null;

// 应用设置
const settings = ref({
  stt: 'whisper-large-v3',
  llm: 'meta-llama/Llama-2-7b-chat-hf',
  tts: 'tts_models/multilingual/multi-dataset/xtts_v2',
  voice: 'default',
  language: 'zh',
  microphone: 'default',
  output: 'default',
  inputVolume: 100,
  outputVolume: 100,
  showRealtimeText: true,
  useLocalKnowledge: true, // 新增：是否使用本地知识库
  localKnowledgePath: '', // 新增：本地知识库路径
});

// 添加数据日志
const addDataLog = (message: string) => {
  const timestamp = new Date().toLocaleTimeString();
  dataLogs.value.push(`[${timestamp}] ${message}`);

  // 保持最大日志数
  if (dataLogs.value.length > 20) {
    dataLogs.value.shift();
  }
};

// 初始化WebSocket客户端
const initWebSocketClient = () => {
  wsClient = new WebSocketClient({
    url: 'ws://localhost:8765'
  });
  
  // 注册事件监听器
  wsClient.on(EventType.CONNECTED, () => {
    status.value = 'connected';
    addDataLog('WebSocket连接已建立');
  });
  
  wsClient.on(EventType.DISCONNECTED, () => {
    status.value = 'disconnected';
    addDataLog('WebSocket连接已断开');
  });
  
  wsClient.on(EventType.TRANSCRIPTION, (data) => {
    if (settings.value.showRealtimeText) {
      // 更新当前用户输入的文本
      if (messages.value.length > 0 && messages.value[messages.value.length - 1].type === 'user') {
        messages.value[messages.value.length - 1].text = data.text;
      } else {
        messages.value.push({
          type: 'user',
          text: data.text,
          timestamp: Date.now()
        });
      }
      lastCommand.value = data.text;
    }
  });
  
  wsClient.on(EventType.RESPONSE, (data) => {
    // 添加AI回复消息
    messages.value.push({
      type: 'ai',
      text: data.text,
      timestamp: Date.now()
    });
    
    isProcessing.value = false;
    addDataLog('接收到AI响应');
    
    // 模拟图表数据生成
    if (Math.random() > 0.7) {
      graphData.value.push('生成的图表 ' + new Date().toLocaleTimeString());
    }
  });
  
  wsClient.on(EventType.STATUS_UPDATE, (data) => {
    status.value = data.status;
    
    if (data.status === 'processing') {
      isProcessing.value = true;
      addDataLog('处理中...');
    }
  });
  
  wsClient.on(EventType.ERROR, (error) => {
    console.error('WebSocket错误:', error);
    status.value = 'error';
    addDataLog('错误: ' + (error.message || '未知错误'));
  });
  
  // 连接到服务器
  wsClient.connect();
};

// 切换监听状态
const toggleListening = () => {
  if (!wsClient) return;
  
  if (isListening.value) {
    // 停止监听
    wsClient.stopListening();
    isListening.value = false;
    
    // 提交完整的用户输入，开始处理
    isProcessing.value = true;
    addDataLog('停止语音监听');
  } else {
    // 开始监听
    wsClient.startListening({
      language: settings.value.language,
      useLocalKnowledge: settings.value.useLocalKnowledge // 传递是否使用本地知识库
    });
    isListening.value = true;
    addDataLog('开始语音监听');
    
    // 添加新的用户消息占位符
    if (!settings.value.showRealtimeText) {
      messages.value.push({
        type: 'user',
        text: '...',
        timestamp: Date.now()
      });
    }
  }
};

// 发送文本命令
const sendCommand = () => {
  if (!inputCommand.value.trim()) return;
  
  // 添加用户消息
  messages.value.push({
    type: 'user',
    text: inputCommand.value,
    timestamp: Date.now()
  });
  
  lastCommand.value = inputCommand.value;
  addDataLog(`发送命令: ${inputCommand.value}`);
  
  // 清空输入
  inputCommand.value = '';
  
  // 模拟处理
  isProcessing.value = true;
  setTimeout(() => {
    messages.value.push({
      type: 'ai',
      text: '收到您的命令，正在处理...',
      timestamp: Date.now()
    });
    isProcessing.value = false;
    addDataLog('接收到AI响应');
  }, 1000);
};

// 更新设置
const updateSettings = ({ key, value }: { key: string, value: any }) => {
  if (settings.value.hasOwnProperty(key)) {
    // @ts-ignore
    settings.value[key] = value;
  }
};

// 保存设置
const saveSettings = () => {
  localStorage.setItem('flowmind-settings', JSON.stringify(settings.value));
  
  // 如果已连接，更新WebSocket客户端设置
  if (wsClient) {
    // 设置语言
    wsClient.setLanguage(settings.value.language);
    
    // 设置模型
    wsClient.setModel('stt', settings.value.stt);
    wsClient.setModel('llm', settings.value.llm);
    wsClient.setModel('tts', settings.value.tts);
  }
  
  addDataLog('设置已保存');
};

// 加载设置
const loadSettings = () => {
  const savedSettings = localStorage.getItem('flowmind-settings');
  if (savedSettings) {
    try {
      const parsedSettings = JSON.parse(savedSettings);
      settings.value = { ...settings.value, ...parsedSettings };
    } catch (error) {
      console.error('解析设置失败:', error);
    }
  }
};

// 打开设置
const openSettings = () => {
  settingsVisible.value = true;
};

// 打开帮助
const openHelp = () => {
  helpVisible.value = true;
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

// 模拟系统资源变化
const updateSystemResources = () => {
  systemResources.value.cpu = Math.floor(10 + Math.random() * 20);
  systemResources.value.memory = Math.floor(25 + Math.random() * 15);
  systemResources.value.model = Math.floor(40 + Math.random() * 20);
};

// 知识库管理功能
const updateKnowledgeBase = (documents: KnowledgeDocument[]) => {
  knowledgeDocuments.value = documents;
  addDataLog(`知识库更新: ${documents.length} 个文档`);
  
  if (documents.length > 0) {
    // 模拟图表数据生成
    graphData.value.push('知识库文档分布 ' + new Date().toLocaleTimeString());
  }
};

const handleDocumentDelete = (documentId: string) => {
  addDataLog(`删除文档: ${documentId}`);
};

const handleIndexBuild = () => {
  addDataLog('重建知识库索引完成');
  // 通知WebSocket客户端知识库已更新
  if (wsClient) {
    wsClient.send(MessageType.STATUS, {
      type: 'knowledge_base_updated',
      documentCount: knowledgeDocuments.value.length
    });
  }
};

// 组件挂载
onMounted(() => {
  // 加载设置
  loadSettings();
  
  // 初始化WebSocket客户端
  initWebSocketClient();
  
  // 添加初始日志
  addDataLog('系统初始化完成');
  addDataLog('加载模型中...');
  addDataLog('模型加载完成');
  
  // 启动模拟系统资源更新
  const resourceInterval = setInterval(updateSystemResources, 5000);
  
  // 清理定时器
  onUnmounted(() => {
    clearInterval(resourceInterval);
    
    // 断开WebSocket连接
    if (wsClient) {
      wsClient.disconnect();
      wsClient = null;
    }
  });
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
  padding: 0 20px;
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
  font-size: 24px;
  margin: 0 20px 0 0;
  white-space: nowrap;
}

.menu-bar {
  display: flex;
  gap: 15px;
}

.menu-item {
  font-size: 16px;
  color: white;
  cursor: pointer;
  padding: 5px 10px;
  -webkit-app-region: no-drag;
  display: flex;
  align-items: center;
  gap: 5px;
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
  display: flex;
  justify-content: center;
  align-items: center;
}

.sidebar-item-group h2 {
  font-size: 18px;
  font-weight: normal;
  margin: 0 0 8px 28px;
}

.sidebar-item {
  padding: 6px 6px 6px 28px;
  margin: 2px 0;
  cursor: pointer;
  font-size: 14px;
  border-radius: 4px;
}

.sidebar-item.active {
  background-color: #e9eef5;
  color: #1976d2;
}

.sidebar-item:hover {
  background-color: #f5f5f5;
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
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 10px;
}

.comparison-view, .default-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.comparison-view h3 {
  margin-top: 0;
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.comparison-content {
  flex: 1;
  overflow: auto;
}

.chat-area {
  flex: 1;
  overflow: hidden;
}

.bottom-console {
  height: 200px;
  display: flex;
  gap: 10px;
}

.console-section {
  flex: 1;
  background-color: white;
  border-radius: 5px;
  border: 1px solid #eee;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.console-section h3 {
  margin: 0;
  padding: 8px 15px;
  font-size: 16px;
  font-weight: normal;
  color: #333;
  background-color: #f5f5f5;
  border-bottom: 1px solid #eee;
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
  border-bottom: 1px dashed #eee;
}

.empty-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #aaa;
  font-style: italic;
}

.system-resource {
  margin-bottom: 12px;
}

.resource-label {
  font-size: 14px;
  margin-bottom: 4px;
}

.resource-value {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.resource-bar {
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.resource-progress {
  height: 100%;
  background-color: #1976d2;
  border-radius: 4px;
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
  background-color: #f44336;
  color: white;
}

.input-field {
  flex: 1;
}

.input-field input {
  width: 100%;
  height: 36px;
  padding: 0 15px;
  border: 1px solid #ddd;
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

.help-content {
  line-height: 1.6;
}

.help-content h3 {
  margin-top: 0;
  color: #1976d2;
}

.help-content h4 {
  margin-top: 16px;
  margin-bottom: 8px;
}

.help-content p, .help-content li {
  color: #333;
}

/* 知识库视图 */
.knowledge-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
