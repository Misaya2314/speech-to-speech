<template>
  <div class="settings-panel">
    <div class="section-header">
      <h3>模型设置</h3>
    </div>

    <div class="settings-section">
      <div class="section-title">语音转文本 (STT)</div>
      <div class="setting-item">
        <span class="setting-label">模型选择</span>
        <el-select v-model="sttModel" @change="updateSettings('stt', sttModel)">
          <el-option
            v-for="model in sttModels"
            :key="model.value"
            :label="model.label"
            :value="model.value"
          />
        </el-select>
      </div>
      
      <div v-if="showAdvancedSettings" class="setting-item">
        <span class="setting-label">参数配置</span>
        <el-button size="small" @click="openAdvancedSettings('stt')">高级参数</el-button>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-title">语言模型 (LLM)</div>
      <div class="setting-item">
        <span class="setting-label">模型选择</span>
        <el-select v-model="llmModel" @change="updateSettings('llm', llmModel)">
          <el-option
            v-for="model in llmModels"
            :key="model.value"
            :label="model.label"
            :value="model.value"
          />
        </el-select>
      </div>
      
      <div v-if="showAdvancedSettings" class="setting-item">
        <span class="setting-label">参数配置</span>
        <el-button size="small" @click="openAdvancedSettings('llm')">高级参数</el-button>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-title">文本转语音 (TTS)</div>
      <div class="setting-item">
        <span class="setting-label">模型选择</span>
        <el-select v-model="ttsModel" @change="updateSettings('tts', ttsModel)">
          <el-option
            v-for="model in ttsModels"
            :key="model.value"
            :label="model.label"
            :value="model.value"
          />
        </el-select>
      </div>
      
      <div class="setting-item">
        <span class="setting-label">声音选择</span>
        <el-select v-model="ttsVoice" @change="updateSettings('voice', ttsVoice)">
          <el-option
            v-for="voice in ttsVoices"
            :key="voice.value"
            :label="voice.label"
            :value="voice.value"
          />
        </el-select>
      </div>
      
      <div v-if="showAdvancedSettings" class="setting-item">
        <span class="setting-label">参数配置</span>
        <el-button size="small" @click="openAdvancedSettings('tts')">高级参数</el-button>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-title">音频设置</div>
      <div class="setting-item">
        <span class="setting-label">麦克风设备</span>
        <el-select v-model="microphoneDevice" @change="updateSettings('microphone', microphoneDevice)">
          <el-option
            v-for="device in audioInputDevices"
            :key="device.value"
            :label="device.label"
            :value="device.value"
          />
        </el-select>
      </div>
      
      <div class="setting-item">
        <span class="setting-label">输出设备</span>
        <el-select v-model="outputDevice" @change="updateSettings('output', outputDevice)">
          <el-option
            v-for="device in audioOutputDevices"
            :key="device.value"
            :label="device.label"
            :value="device.value"
          />
        </el-select>
      </div>
      
      <div class="setting-item">
        <span class="setting-label">输入音量</span>
        <el-slider
          v-model="inputVolume"
          :min="0"
          :max="100"
          @change="updateSettings('inputVolume', inputVolume)"
        />
      </div>
      
      <div class="setting-item">
        <span class="setting-label">输出音量</span>
        <el-slider
          v-model="outputVolume"
          :min="0"
          :max="100"
          @change="updateSettings('outputVolume', outputVolume)"
        />
      </div>
    </div>

    <div class="settings-section">
      <div class="section-title">本地知识库</div>
      <div class="setting-item">
        <span class="setting-label">启用本地知识库</span>
        <el-switch v-model="useLocalKnowledge" @change="updateSettings('useLocalKnowledge', useLocalKnowledge)" />
      </div>
      
      <div class="setting-item" v-if="useLocalKnowledge">
        <span class="setting-label">知识库路径</span>
        <div class="file-selector">
          <el-input v-model="localKnowledgePath" placeholder="选择知识库目录" readonly />
          <el-button size="small" @click="selectKnowledgePath">浏览</el-button>
        </div>
      </div>
      
      <div class="setting-item" v-if="useLocalKnowledge">
        <span class="setting-label">相关度阈值</span>
        <el-slider
          v-model="relevanceThreshold"
          :min="0"
          :max="1"
          :step="0.01"
          :format-tooltip="(value: number) => (value * 100).toFixed(0) + '%'"
          @change="updateSettings('relevanceThreshold', relevanceThreshold)"
        />
      </div>
      
      <div class="setting-item" v-if="useLocalKnowledge">
        <span class="setting-label">最大引用文档数</span>
        <el-input-number
          v-model="maxDocuments"
          :min="1"
          :max="10"
          @change="updateSettings('maxDocuments', maxDocuments)"
        />
      </div>
    </div>

    <div class="settings-section">
      <div class="section-title">显示设置</div>
      <div class="setting-item">
        <span class="setting-label">显示高级设置</span>
        <el-switch v-model="showAdvancedSettings" />
      </div>
      
      <div class="setting-item">
        <span class="setting-label">语音文本实时显示</span>
        <el-switch v-model="showRealtimeText" @change="updateSettings('showRealtimeText', showRealtimeText)" />
      </div>
    </div>

    <div class="settings-actions">
      <el-button type="primary" @click="saveSettings">保存设置</el-button>
      <el-button @click="resetSettings">重置</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

// 定义属性
const props = defineProps({
  savedSettings: {
    type: Object,
    default: () => ({})
  }
});

// 定义事件
const emit = defineEmits(['update-settings', 'save-settings']);

// STT模型
const sttModels = [
  { label: 'Whisper Large V3', value: 'whisper-large-v3' },
  { label: 'Whisper Medium', value: 'whisper-medium' },
  { label: 'Faster Whisper', value: 'faster-whisper' },
  { label: 'Paraformer', value: 'paraformer' }
];
const sttModel = ref('whisper-large-v3');

// LLM模型
const llmModels = [
  { label: 'Llama-2-7b-chat', value: 'meta-llama/Llama-2-7b-chat-hf' },
  { label: 'Mixtral-8x7B', value: 'mistralai/Mixtral-8x7B-Instruct-v0.1' },
  { label: 'Vicuna-13B', value: 'lmsys/vicuna-13b-v1.5' },
  { label: 'OpenAI API (需要API Key)', value: 'openai' }
];
const llmModel = ref('meta-llama/Llama-2-7b-chat-hf');

// TTS模型
const ttsModels = [
  { label: 'XTTS V2', value: 'tts_models/multilingual/multi-dataset/xtts_v2' },
  { label: 'MELO TTS', value: 'melo' },
  { label: 'Facebook MMS', value: 'facebook-mms' },
  { label: 'Parler TTS', value: 'parler' }
];
const ttsModel = ref('tts_models/multilingual/multi-dataset/xtts_v2');

// TTS声音
const ttsVoices = [
  { label: '默认声音', value: 'default' },
  { label: '男声-1', value: 'male-1' },
  { label: '女声-1', value: 'female-1' },
  { label: '男声-2', value: 'male-2' },
  { label: '女声-2', value: 'female-2' }
];
const ttsVoice = ref('default');

// 音频设备
const audioInputDevices = ref([
  { label: '默认麦克风', value: 'default' }
]);
const audioOutputDevices = ref([
  { label: '默认扬声器', value: 'default' }
]);
const microphoneDevice = ref('default');
const outputDevice = ref('default');

// 音量设置
const inputVolume = ref(100);
const outputVolume = ref(100);

// 显示设置
const showAdvancedSettings = ref(false);
const showRealtimeText = ref(true);

// 本地知识库设置
const useLocalKnowledge = ref(true);
const localKnowledgePath = ref('');
const relevanceThreshold = ref(0.7);
const maxDocuments = ref(3);

// 获取音频设备
const getAudioDevices = async () => {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    
    const inputs = devices
      .filter(device => device.kind === 'audioinput')
      .map(device => ({
        label: device.label || `麦克风 ${device.deviceId.substring(0, 5)}...`,
        value: device.deviceId
      }));
    
    const outputs = devices
      .filter(device => device.kind === 'audiooutput')
      .map(device => ({
        label: device.label || `扬声器 ${device.deviceId.substring(0, 5)}...`,
        value: device.deviceId
      }));
    
    audioInputDevices.value = [
      { label: '默认麦克风', value: 'default' },
      ...inputs
    ];
    
    audioOutputDevices.value = [
      { label: '默认扬声器', value: 'default' },
      ...outputs
    ];
  } catch (error) {
    console.error('获取音频设备失败:', error);
  }
};

// 更新设置
const updateSettings = (key: string, value: any) => {
  emit('update-settings', { key, value });
};

// 保存所有设置
const saveSettings = () => {
  const settings = {
    stt: sttModel.value,
    llm: llmModel.value,
    tts: ttsModel.value,
    voice: ttsVoice.value,
    microphone: microphoneDevice.value,
    output: outputDevice.value,
    inputVolume: inputVolume.value,
    outputVolume: outputVolume.value,
    showRealtimeText: showRealtimeText.value,
    useLocalKnowledge: useLocalKnowledge.value,
    localKnowledgePath: localKnowledgePath.value,
    relevanceThreshold: relevanceThreshold.value,
    maxDocuments: maxDocuments.value
  };
  
  emit('save-settings', settings);
};

// 重置设置
const resetSettings = () => {
  sttModel.value = 'whisper-large-v3';
  llmModel.value = 'meta-llama/Llama-2-7b-chat-hf';
  ttsModel.value = 'tts_models/multilingual/multi-dataset/xtts_v2';
  ttsVoice.value = 'default';
  microphoneDevice.value = 'default';
  outputDevice.value = 'default';
  inputVolume.value = 100;
  outputVolume.value = 100;
  showRealtimeText.value = true;
  useLocalKnowledge.value = true;
  localKnowledgePath.value = '';
  relevanceThreshold.value = 0.7;
  maxDocuments.value = 3;
};

// 打开高级设置
const openAdvancedSettings = (type: string) => {
  // 实际项目中可以打开一个对话框让用户配置更多参数
  console.log(`打开${type}的高级设置`);
};

// 选择知识库路径
const selectKnowledgePath = () => {
  // 在实际环境中，这里应该调用Electron的dialog.showOpenDialog
  // 这里仅做模拟
  console.log('选择知识库路径');
  // 模拟选择了一个路径
  localKnowledgePath.value = 'C:/Knowledge';
  updateSettings('localKnowledgePath', localKnowledgePath.value);
};

// 初始化时加载设置
onMounted(async () => {
  // 加载音频设备
  await getAudioDevices();
  
  // 如果有保存的设置，则使用保存的设置
  if (props.savedSettings) {
    const settings = props.savedSettings;
    
    if (settings.stt) sttModel.value = settings.stt;
    if (settings.llm) llmModel.value = settings.llm;
    if (settings.tts) ttsModel.value = settings.tts;
    if (settings.voice) ttsVoice.value = settings.voice;
    if (settings.microphone) microphoneDevice.value = settings.microphone;
    if (settings.output) outputDevice.value = settings.output;
    if (settings.inputVolume) inputVolume.value = settings.inputVolume;
    if (settings.outputVolume) outputVolume.value = settings.outputVolume;
    if (settings.showRealtimeText !== undefined) showRealtimeText.value = settings.showRealtimeText;
    if (settings.useLocalKnowledge !== undefined) useLocalKnowledge.value = settings.useLocalKnowledge;
    if (settings.localKnowledgePath) localKnowledgePath.value = settings.localKnowledgePath;
    if (settings.relevanceThreshold !== undefined) relevanceThreshold.value = settings.relevanceThreshold;
    if (settings.maxDocuments !== undefined) maxDocuments.value = settings.maxDocuments;
  }
});
</script>

<style scoped>
.settings-panel {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.section-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.section-header h3 {
  margin: 0;
  color: #1976d2;
  font-size: 18px;
  font-weight: 600;
}

.settings-section {
  margin-bottom: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 12px;
  color: #333;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.setting-label {
  font-size: 14px;
  color: #666;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

:deep(.el-select) {
  width: 240px;
}

:deep(.el-slider) {
  width: 240px;
}

.file-selector {
  display: flex;
  gap: 10px;
  width: 240px;
}
</style> 