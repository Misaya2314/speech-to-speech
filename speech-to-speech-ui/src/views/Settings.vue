<template>
  <div class="settings-container">
    <div class="header">
      <div class="title">
        <el-button icon="Back" @click="goBack">返回</el-button>
        <h1>系统设置</h1>
      </div>
    </div>

    <div class="settings-content">
      <el-tabs tab-position="left" class="settings-tabs">
        <el-tab-pane label="模型设置">
          <div class="settings-section">
            <h2>模型设置</h2>
            <el-divider />

            <el-form label-position="top">
              <el-form-item label="STT模型 (语音转文本)">
                <el-select
                  v-model="settings.sttModel"
                  placeholder="选择STT模型"
                >
                  <el-option
                    v-for="model in sttModels"
                    :key="model.value"
                    :label="model.label"
                    :value="model.value"
                  />
                </el-select>
                <el-text type="info" size="small"
                  >负责将你的语音转换为文本</el-text
                >
              </el-form-item>

              <el-form-item label="LLM模型 (语言处理)">
                <el-select v-model="settings.lmModel" placeholder="选择LLM模型">
                  <el-option
                    v-for="model in lmModels"
                    :key="model.value"
                    :label="model.label"
                    :value="model.value"
                  />
                </el-select>
                <el-text type="info" size="small"
                  >负责理解文本并生成回复</el-text
                >
              </el-form-item>

              <el-form-item label="TTS模型 (文本转语音)">
                <el-select
                  v-model="settings.ttsModel"
                  placeholder="选择TTS模型"
                >
                  <el-option
                    v-for="model in ttsModels"
                    :key="model.value"
                    :label="model.label"
                    :value="model.value"
                  />
                </el-select>
                <el-text type="info" size="small"
                  >负责将回复文本转换为语音</el-text
                >
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane label="语言设置">
          <div class="settings-section">
            <h2>语言设置</h2>
            <el-divider />

            <el-form label-position="top">
              <el-form-item label="默认语言">
                <el-select
                  v-model="settings.defaultLanguage"
                  placeholder="选择默认语言"
                >
                  <el-option
                    v-for="lang in languages"
                    :key="lang.code"
                    :label="lang.name"
                    :value="lang.code"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="语言检测">
                <el-switch
                  v-model="settings.autoDetectLanguage"
                  active-text="自动检测语言"
                  inactive-text="使用默认语言"
                />
                <el-text type="info" size="small"
                  >启用后，系统将自动检测你说话的语言</el-text
                >
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane label="音频设置">
          <div class="settings-section">
            <h2>音频设置</h2>
            <el-divider />

            <el-form label-position="top">
              <el-form-item label="输入音量">
                <el-slider
                  v-model="settings.inputVolume"
                  :min="0"
                  :max="100"
                  :step="1"
                  show-input
                />
              </el-form-item>

              <el-form-item label="输出音量">
                <el-slider
                  v-model="settings.outputVolume"
                  :min="0"
                  :max="100"
                  :step="1"
                  show-input
                />
              </el-form-item>

              <el-form-item label="静音阈值">
                <el-slider
                  v-model="settings.silenceThreshold"
                  :min="0"
                  :max="100"
                  :step="1"
                  show-input
                />
                <el-text type="info" size="small"
                  >调整系统对安静环境的敏感度</el-text
                >
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane label="连接设置">
          <div class="settings-section">
            <h2>后端连接设置</h2>
            <el-divider />

            <el-form label-position="top">
              <el-form-item label="服务器地址">
                <el-input
                  v-model="settings.serverAddress"
                  placeholder="例如: localhost 或 192.168.1.100"
                />
              </el-form-item>

              <el-form-item label="端口">
                <el-input-number
                  v-model="settings.serverPort"
                  :min="1"
                  :max="65535"
                />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="testConnection"
                  >测试连接</el-button
                >
                <el-text
                  v-if="connectionStatus"
                  :type="connectionStatusType"
                  class="connection-status"
                >
                  {{ connectionStatusText }}
                </el-text>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <div class="actions">
      <el-button type="primary" @click="saveSettings">保存设置</el-button>
      <el-button @click="resetSettings">重置</el-button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { WebSocketClient, EventType } from "@/utils/websocket-client";

export default defineComponent({
  name: "SettingsPage",

  setup() {
    const router = useRouter();
    const connectionStatus = ref("");

    // 状态类型
    const connectionStatusType = computed(() => {
      if (!connectionStatus.value) return "";
      return connectionStatus.value === "连接成功" ? "success" : "danger";
    });

    // 状态文本
    const connectionStatusText = computed(() => {
      return connectionStatus.value;
    });

    // 设置数据
    const settings = reactive({
      sttModel: "whisper-large-v3",
      lmModel: "meta-llama/Llama-2-7b-chat-hf",
      ttsModel: "tts_models/multilingual/multi-dataset/xtts_v2",
      defaultLanguage: "zh",
      autoDetectLanguage: true,
      inputVolume: 80,
      outputVolume: 80,
      silenceThreshold: 30,
      serverAddress: "localhost",
      serverPort: 8766,
    });

    // STT模型列表
    const sttModels = [
      { label: "Whisper Large V3", value: "whisper-large-v3" },
      {
        label: "Distil Whisper Large V3",
        value: "distil-whisper/distil-large-v3",
      },
      { label: "Whisper Medium", value: "openai/whisper-medium" },
    ];

    // LLM模型列表
    const lmModels = [
      { label: "Llama-2-7B", value: "meta-llama/Llama-2-7b-chat-hf" },
      { label: "Phi-3-mini-4k", value: "microsoft/Phi-3-mini-4k-instruct" },
      { label: "Gemma-2B", value: "google/gemma-2b-it" },
    ];

    // TTS模型列表
    const ttsModels = [
      {
        label: "XTTS V2",
        value: "tts_models/multilingual/multi-dataset/xtts_v2",
      },
      { label: "MeloTTS", value: "melo" },
      { label: "Parler TTS", value: "parler" },
    ];

    // 语言列表
    const languages = [
      { code: "zh", name: "中文" },
      { code: "en", name: "英文" },
      { code: "fr", name: "法语" },
      { code: "es", name: "西班牙语" },
      { code: "ja", name: "日语" },
      { code: "ko", name: "韩语" },
    ];

    // 测试连接
    const testConnection = () => {
      connectionStatus.value = "正在连接...";

      const wsUrl = `ws://${settings.serverAddress}:${settings.serverPort}`;
      const wsClient = new WebSocketClient({
        url: wsUrl,
        reconnectInterval: 3000,
        maxReconnectAttempts: 1,
      });

      wsClient.on(EventType.CONNECTED, () => {
        connectionStatus.value = "连接成功";
        setTimeout(() => {
          wsClient.disconnect();
        }, 1000);
      });

      wsClient.on(EventType.ERROR, () => {
        connectionStatus.value = "连接失败";
      });

      wsClient.connect();
    };

    // 保存设置
    const saveSettings = () => {
      // 这里将来可以持久化设置
      // 目前仅显示提示
      ElMessage.success("设置已保存");
    };

    // 重置设置
    const resetSettings = () => {
      // 重置为默认值
      Object.assign(settings, {
        sttModel: "whisper-large-v3",
        lmModel: "meta-llama/Llama-2-7b-chat-hf",
        ttsModel: "tts_models/multilingual/multi-dataset/xtts_v2",
        defaultLanguage: "zh",
        autoDetectLanguage: true,
        inputVolume: 80,
        outputVolume: 80,
        silenceThreshold: 30,
        serverAddress: "localhost",
        serverPort: 8766,
      });

      ElMessage.info("设置已重置");
    };

    // 返回主页
    const goBack = () => {
      router.push("/");
    };

    return {
      settings,
      sttModels,
      lmModels,
      ttsModels,
      languages,
      connectionStatus,
      connectionStatusType,
      connectionStatusText,
      testConnection,
      saveSettings,
      resetSettings,
      goBack,
    };
  },
});
</script>

<style scoped>
.settings-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f7f7f7;
}

.header {
  padding: 15px 20px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.title {
  display: flex;
  align-items: center;
}

.title h1 {
  margin: 0 0 0 15px;
  font-size: 1.5rem;
  color: #333;
}

.settings-content {
  flex: 1;
  padding: 20px;
  overflow: auto;
}

.settings-tabs {
  height: 100%;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.settings-section {
  padding: 0 20px;
}

.settings-section h2 {
  font-size: 1.3rem;
  color: #333;
  margin-top: 10px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  padding: 15px 20px;
  background-color: #ffffff;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
}

.actions .el-button {
  margin-left: 10px;
}

.connection-status {
  margin-left: 10px;
}

:deep(.el-tabs__item) {
  height: 50px;
  line-height: 50px;
}

:deep(.el-tabs__content) {
  padding: 20px 0;
}
</style>
