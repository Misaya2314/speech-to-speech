const { contextBridge, ipcRenderer } = require('electron');

// 向渲染进程暴露受限制的API
contextBridge.exposeInMainWorld('electronAPI', {
  // 连接到后端服务器
  connectBackend: (options) => ipcRenderer.invoke('connect-backend', options),
  
  // 断开后端连接
  disconnectBackend: () => ipcRenderer.invoke('disconnect-backend'),
  
  // 监听后端连接请求
  onBackendConnectRequest: (callback) => 
    ipcRenderer.on('backend-connect-request', (event, options) => callback(options)),
  
  // 监听后端断开连接请求
  onBackendDisconnectRequest: (callback) => 
    ipcRenderer.on('backend-disconnect-request', (event) => callback()),
  
  // 发送音频数据
  sendAudioData: (audioData) => ipcRenderer.send('audio-data', audioData),
  
  // 监听转录结果
  onTranscription: (callback) => 
    ipcRenderer.on('transcription', (event, text) => callback(text)),
  
  // 监听响应
  onResponse: (callback) => 
    ipcRenderer.on('response', (event, text) => callback(text)),
  
  // 监听音频响应
  onAudioResponse: (callback) => 
    ipcRenderer.on('audio-response', (event, audioData) => callback(audioData)),
  
  // 监听状态更新
  onStatus: (callback) => 
    ipcRenderer.on('status', (event, status) => callback(status)),
  
  // 监听Python日志
  onPythonLog: (callback) => 
    ipcRenderer.on('python-log', (event, log) => callback(log)),
  
  // 监听Python错误
  onPythonError: (callback) => 
    ipcRenderer.on('python-error', (event, error) => callback(error))
}); 