<template>
  <div class="tool-bar">
    <div class="tool-group">
      <el-tooltip content="选择" placement="bottom" effect="light">
        <el-button :icon="Select" circle></el-button>
      </el-tooltip>
      <el-tooltip content="移动" placement="bottom" effect="light">
        <el-button :icon="DArrowRight" circle></el-button>
      </el-tooltip>
      <el-tooltip content="旋转" placement="bottom" effect="light">
        <el-button :icon="Refresh" circle></el-button>
      </el-tooltip>
    </div>

    <div class="tool-group">
      <el-tooltip content="缩放" placement="bottom" effect="light">
        <el-button :icon="ZoomIn" circle></el-button>
      </el-tooltip>
      <el-tooltip content="测量" placement="bottom" effect="light">
        <el-button :icon="Odometer" circle></el-button>
      </el-tooltip>
    </div>

    <div class="tool-group">
      <el-tooltip content="语音命令" placement="bottom" effect="light">
        <el-button
          :icon="Microphone"
          type="primary"
          circle
          :class="{ active: isListening }"
          @click="toggleListening"
        ></el-button>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import {
  Select,
  DArrowRight,
  Refresh,
  ZoomIn,
  Odometer,
  Microphone,
} from "@element-plus/icons-vue";

const props = defineProps({
  isListening: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["toggle-listening"]);

const toggleListening = () => {
  emit("toggle-listening");
};
</script>

<style scoped>
.tool-bar {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  z-index: 100;
}

.tool-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: white;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.active {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
  }
}
</style>
