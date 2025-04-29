<template>
  <div class="knowledge-manager">
    <div class="section-header">
      <h3>本地知识库管理</h3>
      <div class="header-actions">
        <el-button type="primary" @click="showUploadDialog">
          <el-icon><UploadFilled /></el-icon>
          上传文档
        </el-button>
        <el-button type="success" @click="buildIndex" :loading="isBuilding">
          <el-icon><Connection /></el-icon>
          重建索引
        </el-button>
      </div>
    </div>

    <div class="knowledge-stats">
      <div class="stat-item">
        <div class="stat-value">{{ documents.length }}</div>
        <div class="stat-label">文档总数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ totalChunks }}</div>
        <div class="stat-label">文本块数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ indexSize }}</div>
        <div class="stat-label">索引大小</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ lastUpdated }}</div>
        <div class="stat-label">上次更新</div>
      </div>
    </div>

    <div class="document-list">
      <div class="list-header">
        <div class="header-column filename">文件名</div>
        <div class="header-column type">类型</div>
        <div class="header-column size">大小</div>
        <div class="header-column date">上传日期</div>
        <div class="header-column actions">操作</div>
      </div>
      
      <div v-if="documents.length === 0" class="empty-list">
        <el-empty description="暂无文档" />
      </div>
      
      <div v-else class="list-content">
        <div 
          v-for="doc in documents" 
          :key="doc.id" 
          class="document-item"
        >
          <div class="item-column filename">
            <el-icon class="file-icon">
              <Document v-if="doc.type === 'txt'" />
              <Files v-else-if="doc.type === 'pdf'" />
              <Tickets v-else-if="doc.type === 'doc' || doc.type === 'docx'" />
              <Notebook v-else />
            </el-icon>
            <span>{{ doc.name }}</span>
          </div>
          <div class="item-column type">{{ doc.type.toUpperCase() }}</div>
          <div class="item-column size">{{ formatSize(doc.size) }}</div>
          <div class="item-column date">{{ formatDate(doc.date) }}</div>
          <div class="item-column actions">
            <el-button-group size="small">
              <el-button @click="previewDocument(doc)" type="info">
                <el-icon><View /></el-icon>
              </el-button>
              <el-button @click="deleteDocument(doc)" type="danger">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-button-group>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传文档对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文档" width="500px">
      <el-upload
        class="upload-area"
        drag
        action="#"
        multiple
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="uploadFiles"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持PDF、Word、TXT等文档格式
          </div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="uploadDocuments" :loading="isUploading">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 文档预览对话框 -->
    <el-dialog v-model="previewDialogVisible" title="文档预览" width="70%">
      <div v-if="currentPreview" class="preview-content">
        <div class="preview-header">
          <div class="preview-title">{{ currentPreview.name }}</div>
          <div class="preview-info">
            <span>类型: {{ currentPreview.type.toUpperCase() }}</span>
            <span>大小: {{ formatSize(currentPreview.size) }}</span>
            <span>上传日期: {{ formatDate(currentPreview.date) }}</span>
          </div>
        </div>
        <div class="preview-body">
          <div v-if="currentPreview.content" class="text-preview">
            {{ currentPreview.content }}
          </div>
          <div v-else class="preview-placeholder">
            <el-empty description="暂无预览内容" />
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { 
  UploadFilled, 
  Connection, 
  Document, 
  Files, 
  Tickets, 
  Notebook,
  View, 
  Delete 
} from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

// 文档类型接口
interface KnowledgeDocument {
  id: string;
  name: string;
  type: string;
  size: number;
  date: number;
  content?: string;
}

// 状态变量
const documents = ref<KnowledgeDocument[]>([]);
const uploadDialogVisible = ref(false);
const previewDialogVisible = ref(false);
const uploadFiles = ref<any[]>([]);
const isUploading = ref(false);
const isBuilding = ref(false);
const currentPreview = ref<KnowledgeDocument | null>(null);
const totalChunks = ref(0);
const indexSize = ref('0 KB');
const lastUpdated = ref('从未');

// 定义事件
const emit = defineEmits(['update', 'delete', 'build-index']);

// 显示上传对话框
const showUploadDialog = () => {
  uploadDialogVisible.value = true;
  uploadFiles.value = [];
};

// 处理文件选择
const handleFileChange = (file: any) => {
  // 实际项目中可能需要验证文件类型等
  uploadFiles.value.push(file);
};

// 上传文档
const uploadDocuments = async () => {
  if (uploadFiles.value.length === 0) {
    ElMessage.warning('请先选择文件');
    return;
  }

  isUploading.value = true;
  
  try {
    // 模拟上传过程
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // 添加到文档列表
    uploadFiles.value.forEach(file => {
      const doc: KnowledgeDocument = {
        id: Date.now().toString() + Math.random().toString(36).substr(2, 5),
        name: file.name,
        type: file.name.split('.').pop() || 'unknown',
        size: file.size,
        date: Date.now()
      };
      documents.value.push(doc);
    });
    
    ElMessage.success('文档上传成功');
    uploadDialogVisible.value = false;
    emit('update', documents.value);
    
    // 更新统计信息
    totalChunks.value += uploadFiles.value.length * 10;
    indexSize.value = formatSize(parseInt(indexSize.value) + Math.round(Math.random() * 1000000));
    lastUpdated.value = new Date().toLocaleString();
  } catch (error) {
    ElMessage.error('文档上传失败');
    console.error('上传文档失败:', error);
  } finally {
    isUploading.value = false;
  }
};

// 构建索引
const buildIndex = async () => {
  if (documents.value.length === 0) {
    ElMessage.warning('没有文档可供索引');
    return;
  }
  
  isBuilding.value = true;
  
  try {
    // 模拟索引构建过程
    await new Promise(resolve => setTimeout(resolve, 2000));
    ElMessage.success('索引构建完成');
    emit('build-index');
    
    // 更新统计信息
    totalChunks.value = documents.value.length * 10 + Math.floor(Math.random() * 50);
    const calculatedSize = documents.value.reduce((acc, doc) => acc + doc.size, 0) * 0.3;
    indexSize.value = formatSize(calculatedSize);
    lastUpdated.value = new Date().toLocaleString();
  } catch (error) {
    ElMessage.error('索引构建失败');
    console.error('构建索引失败:', error);
  } finally {
    isBuilding.value = false;
  }
};

// 预览文档
const previewDocument = (doc: KnowledgeDocument) => {
  // 在实际项目中，这里应该通过API获取文档内容
  currentPreview.value = {
    ...doc,
    content: doc.content || `这是${doc.name}的示例内容。在实际项目中，这里会显示从后端获取的文档内容预览。`
  };
  previewDialogVisible.value = true;
};

// 删除文档
const deleteDocument = (doc: KnowledgeDocument) => {
  ElMessageBox.confirm(
    `确定要删除文档"${doc.name}"吗？这将同时删除相关索引。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    documents.value = documents.value.filter(d => d.id !== doc.id);
    ElMessage.success('文档已删除');
    emit('delete', doc.id);
    
    // 更新统计信息
    totalChunks.value -= 10;
    if (totalChunks.value < 0) totalChunks.value = 0;
    const newSize = parseInt(indexSize.value) - Math.round(doc.size * 0.3);
    indexSize.value = formatSize(newSize > 0 ? newSize : 0);
    lastUpdated.value = new Date().toLocaleString();
  }).catch(() => {
    // 用户取消操作
  });
};

// 格式化文件大小
const formatSize = (size: number): string => {
  if (size < 1024) return size + ' B';
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB';
  if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(1) + ' MB';
  return (size / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
};

// 格式化日期
const formatDate = (timestamp: number): string => {
  return new Date(timestamp).toLocaleString();
};

// 初始化示例数据
onMounted(() => {
  // 添加一些示例文档
  documents.value = [
    {
      id: '1',
      name: '项目概述.pdf',
      type: 'pdf',
      size: 2458600,
      date: Date.now() - 86400000 * 3
    },
    {
      id: '2',
      name: '技术规范.docx',
      type: 'docx',
      size: 1458600,
      date: Date.now() - 86400000 * 2
    },
    {
      id: '3',
      name: '研究数据.txt',
      type: 'txt',
      size: 345600,
      date: Date.now() - 86400000
    }
  ];
  
  // 初始化统计信息
  totalChunks.value = documents.value.length * 10 + 15;
  const calculatedSize = documents.value.reduce((acc, doc) => acc + doc.size, 0) * 0.3;
  indexSize.value = formatSize(calculatedSize);
  lastUpdated.value = new Date(Date.now() - 86400000).toLocaleString();
});
</script>

<style scoped>
.knowledge-manager {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.knowledge-stats {
  display: flex;
  padding: 16px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #eee;
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 0 16px;
  border-right: 1px solid #eee;
}

.stat-item:last-child {
  border-right: none;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1976d2;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.document-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  display: flex;
  padding: 8px 16px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #eee;
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px;
}

.document-item {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.header-column,
.item-column {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.filename {
  flex: 2;
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #1976d2;
}

.type {
  flex: 0.5;
}

.size {
  flex: 0.5;
}

.date {
  flex: 1;
}

.actions {
  flex: 0.5;
  text-align: center;
}

.empty-list {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}

.upload-area {
  width: 100%;
}

.preview-content {
  display: flex;
  flex-direction: column;
  height: 60vh;
}

.preview-header {
  padding: 16px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #eee;
}

.preview-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.preview-info {
  display: flex;
  gap: 16px;
  color: #666;
  font-size: 14px;
}

.preview-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.text-preview {
  white-space: pre-wrap;
  font-family: monospace;
  line-height: 1.5;
}

.preview-placeholder {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style> 