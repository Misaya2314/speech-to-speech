<template>
  <div class="history-panel">
    <div class="panel-header">
      <h3>对话历史记录</h3>
      <div class="header-actions">
        <el-tooltip content="导出历史记录" placement="top">
          <el-button :icon="Download" size="small" @click="exportHistory" />
        </el-tooltip>
        <el-tooltip content="清空历史记录" placement="top">
          <el-button :icon="Delete" size="small" type="danger" @click="confirmClearHistory" />
        </el-tooltip>
      </div>
    </div>
    
    <div class="history-list">
      <div v-if="conversations.length === 0" class="empty-history">
        <p>暂无历史记录</p>
      </div>
      
      <div
        v-for="(conversation, index) in conversations"
        :key="index"
        :class="['conversation-item', { active: selectedConversation === index }]"
        @click="selectConversation(index)"
      >
        <div class="conversation-header">
          <span class="conversation-title">{{ conversation.title || `对话 ${index + 1}` }}</span>
          <span class="conversation-date">{{ formatDate(conversation.timestamp) }}</span>
        </div>
        
        <div class="conversation-preview">
          {{ truncateText(getPreviewText(conversation), 100) }}
        </div>
        
        <div class="conversation-actions">
          <el-tooltip content="继续对话" placement="top">
            <el-button :icon="VideoPlay" circle size="small" @click.stop="continueConversation(index)" />
          </el-tooltip>
          <el-tooltip content="删除" placement="top">
            <el-button :icon="Delete" circle size="small" @click.stop="deleteConversation(index)" />
          </el-tooltip>
        </div>
      </div>
    </div>
    
    <el-dialog
      v-model="clearConfirmVisible"
      title="确认清空"
      width="300px"
    >
      <span>确定要清空所有历史记录吗？此操作不可恢复。</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="clearConfirmVisible = false">取消</el-button>
          <el-button type="primary" @click="clearHistory">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Download, Delete, VideoPlay } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

interface Message {
  type: 'user' | 'ai';
  text: string;
  timestamp: number;
}

interface Conversation {
  id: string;
  title?: string;
  timestamp: number;
  messages: Message[];
  language: string;
}

// 定义属性
defineProps({
  conversations: {
    type: Array as () => Conversation[],
    default: () => []
  }
});

// 定义事件
const emit = defineEmits(['select', 'delete', 'clear', 'continue', 'export']);

// 选中的对话
const selectedConversation = ref(-1);

// 清空确认对话框
const clearConfirmVisible = ref(false);

// 选择对话
const selectConversation = (index: number) => {
  selectedConversation.value = index;
  emit('select', index);
};

// 继续对话
const continueConversation = (index: number) => {
  emit('continue', index);
};

// 删除对话
const deleteConversation = (index: number) => {
  ElMessageBox.confirm(
    '确定要删除这条对话记录吗？',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    emit('delete', index);
    ElMessage({
      type: 'success',
      message: '删除成功'
    });
  }).catch(() => {
    // 用户取消删除，不做操作
  });
};

// 确认清空历史
const confirmClearHistory = () => {
  clearConfirmVisible.value = true;
};

// 清空历史
const clearHistory = () => {
  emit('clear');
  clearConfirmVisible.value = false;
  ElMessage({
    type: 'success',
    message: '历史记录已清空'
  });
};

// 导出历史
const exportHistory = () => {
  emit('export');
};

// 格式化日期
const formatDate = (timestamp: number): string => {
  const date = new Date(timestamp);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 获取预览文本
const getPreviewText = (conversation: Conversation): string => {
  if (conversation.messages.length === 0) return '无内容';
  const latestMessages = conversation.messages.slice(-2);
  return latestMessages.map(m => `${m.type === 'user' ? '用户: ' : 'AI: '}${m.text}`).join(' | ');
};

// 截断文本
const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};
</script>

<style scoped>
.history-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.empty-history {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: #999;
  font-style: italic;
}

.conversation-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
  border: 1px solid #eee;
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
}

.conversation-item:hover {
  background-color: #f9f9f9;
}

.conversation-item.active {
  background-color: #e3f2fd;
  border-color: #1976d2;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.conversation-title {
  font-weight: 600;
  color: #333;
}

.conversation-date {
  font-size: 12px;
  color: #999;
}

.conversation-preview {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
  line-height: 1.4;
}

.conversation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.conversation-item:hover .conversation-actions {
  opacity: 1;
}
</style> 