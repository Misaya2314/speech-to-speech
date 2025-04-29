/**
 * WebSocket客户端工具类
 * 负责与后端S2S WebSocket服务器通信
 */

// 消息类型定义
export enum MessageType {
  START_LISTENING = 'start_listening',
  STOP_LISTENING = 'stop_listening',
  SET_LANGUAGE = 'set_language',
  SET_MODEL = 'set_model',
  AUDIO_DATA = 'audio_data',
  TRANSCRIPTION = 'transcription',
  RESPONSE = 'response',
  AUDIO_CHUNK = 'audio_chunk',
  STATUS = 'status',
  ERROR = 'error',
  PING = 'ping',
  PONG = 'pong'
}

// 事件类型定义
export enum EventType {
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  MESSAGE = 'message',
  TRANSCRIPTION = 'transcription',
  RESPONSE = 'response',
  AUDIO_CHUNK = 'audio_chunk',
  STATUS_UPDATE = 'status_update',
  ERROR = 'error',
  RECONNECTING = 'reconnecting',
  RECONNECTED = 'reconnected',
  RECONNECT_FAILED = 'reconnect_failed'
}

// 状态类型定义
export enum StatusType {
  IDLE = 'idle',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  LISTENING = 'listening',
  PROCESSING = 'processing',
  ERROR = 'error',
  RECONNECTING = 'reconnecting'
}

// WebSocket客户端配置
export interface WebSocketClientConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  pingInterval?: number;
  autoReconnect?: boolean;
}

// 音频配置
export interface AudioConfig {
  sampleRate?: number;
  channels?: number;
  format?: string;
}

// 事件监听器类型
type EventListener = (data: any) => void;

export class WebSocketClient {
  private socket: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number;
  private maxReconnectAttempts: number;
  private pingInterval: number;
  private autoReconnect: boolean;
  private reconnectAttempts = 0;
  private status: StatusType = StatusType.IDLE;
  private eventListeners: Map<EventType, EventListener[]> = new Map();
  private pingTimer: number | null = null;
  private isManualClose = false;
  private audioContext: AudioContext | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioConfig: AudioConfig = {
    sampleRate: 16000,
    channels: 1,
    format: 'audio/webm'
  };
  
  constructor(config: WebSocketClientConfig) {
    this.url = config.url;
    this.reconnectInterval = config.reconnectInterval || 3000;
    this.maxReconnectAttempts = config.maxReconnectAttempts || 5;
    this.pingInterval = config.pingInterval || 30000;
    this.autoReconnect = config.autoReconnect !== false;
    
    // 初始化事件监听器
    Object.values(EventType).forEach(type => {
      this.eventListeners.set(type as EventType, []);
    });
  }
  
  /**
   * 连接到WebSocket服务器
   */
  public connect(): void {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      console.log('WebSocket已连接或正在连接中');
      return;
    }
    
    this.isManualClose = false;
    this.setStatus(StatusType.CONNECTING);
    
    try {
      this.socket = new WebSocket(this.url);
      
      // 连接打开
      this.socket.onopen = () => {
        console.log('WebSocket连接已建立');
        this.reconnectAttempts = 0;
        this.setStatus(StatusType.CONNECTED);
        this.emit(EventType.CONNECTED, null);
        
        // 启动心跳检测
        this.startPingInterval();
      };
      
      // 接收消息
      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('解析消息失败:', error);
          this.emit(EventType.ERROR, { error: '解析消息失败', details: error });
        }
      };
      
      // 连接关闭
      this.socket.onclose = (event) => {
        console.log(`WebSocket连接已关闭: (${event.code}) ${event.reason}`);
        this.clearPingInterval();
        this.setStatus(StatusType.DISCONNECTED);
        this.emit(EventType.DISCONNECTED, { code: event.code, reason: event.reason });
        
        // 如果不是手动关闭且自动重连开启，则尝试重连
        if (!this.isManualClose && this.autoReconnect) {
          this.attemptReconnect();
        }
      };
      
      // 连接错误
      this.socket.onerror = (error) => {
        console.error('WebSocket连接错误:', error);
        this.setStatus(StatusType.ERROR);
        this.emit(EventType.ERROR, { error: '连接错误', details: error });
      };
      
    } catch (error) {
      console.error('创建WebSocket连接失败:', error);
      this.setStatus(StatusType.ERROR);
      this.emit(EventType.ERROR, { error: '创建连接失败', details: error });
      
      if (this.autoReconnect) {
        this.attemptReconnect();
      }
    }
  }
  
  /**
   * 断开WebSocket连接
   */
  public disconnect(): void {
    this.isManualClose = true;
    this.clearPingInterval();
    
    if (this.socket) {
      this.socket.close(1000, '客户端主动断开连接');
      this.socket = null;
      this.setStatus(StatusType.DISCONNECTED);
    }
    
    this.stopAudioCapture();
  }
  
  /**
   * 发送消息到服务器
   */
  public send(type: MessageType, data: any = {}): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket未连接，无法发送消息');
      this.emit(EventType.ERROR, { error: '连接未建立，无法发送消息' });
      return;
    }
    
    const message = JSON.stringify({
      type,
      data
    });
    
    try {
      this.socket.send(message);
    } catch (error) {
      console.error('发送消息失败:', error);
      this.emit(EventType.ERROR, { error: '发送消息失败', details: error });
    }
  }
  
  /**
   * 开始语音识别
   */
  public async startListening(config: any = {}): Promise<void> {
    try {
      // 合并配置
      if (config.audioConfig) {
        this.audioConfig = { ...this.audioConfig, ...config.audioConfig };
      }
      
      // 发送开始监听命令
      this.send(MessageType.START_LISTENING, config);
      this.setStatus(StatusType.LISTENING);
      
      // 启动音频捕获
      await this.startAudioCapture();
    } catch (error) {
      console.error('启动语音识别失败:', error);
      this.emit(EventType.ERROR, { error: '启动语音识别失败', details: error });
      this.setStatus(StatusType.ERROR);
    }
  }
  
  /**
   * 停止语音识别
   */
  public stopListening(): void {
    this.stopAudioCapture();
    this.send(MessageType.STOP_LISTENING);
    this.setStatus(StatusType.CONNECTED);
  }
  
  /**
   * 设置语言
   */
  public setLanguage(language: string): void {
    this.send(MessageType.SET_LANGUAGE, { language });
  }
  
  /**
   * 设置模型
   */
  public setModel(modelType: string, modelName: string): void {
    this.send(MessageType.SET_MODEL, { model_type: modelType, model_name: modelName });
  }
  
  /**
   * 发送音频数据
   */
  public sendAudioData(audioData: ArrayBuffer | Blob): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket未连接，无法发送音频数据');
      return;
    }
    
    // 性能优化：添加频率限制，避免发送过多数据
    if (audioData instanceof ArrayBuffer) {
      // 检查音频数据大小，如果太小则忽略（噪音）
      if (audioData.byteLength < 100) {
        return;
      }
      
      // 转换为Base64
      const base64 = this.arrayBufferToBase64(audioData);
      this.send(MessageType.AUDIO_DATA, { audio: base64, format: this.audioConfig.format });
    } else if (audioData instanceof Blob) {
      // 检查音频数据大小，如果太小则忽略（噪音）
      if (audioData.size < 100) {
        return;
      }
      
      // 读取Blob并转换为Base64
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = (reader.result as string).split(',')[1];
        this.send(MessageType.AUDIO_DATA, { audio: base64, format: this.audioConfig.format });
      };
      reader.readAsDataURL(audioData);
    }
  }
  
  /**
   * 添加事件监听器
   */
  public on(event: EventType, callback: EventListener): void {
    const listeners = this.eventListeners.get(event) || [];
    listeners.push(callback);
    this.eventListeners.set(event, listeners);
  }
  
  /**
   * 移除事件监听器
   */
  public off(event: EventType, callback: EventListener): void {
    const listeners = this.eventListeners.get(event) || [];
    const index = listeners.indexOf(callback);
    if (index !== -1) {
      listeners.splice(index, 1);
      this.eventListeners.set(event, listeners);
    }
  }
  
  /**
   * 获取当前状态
   */
  public getStatus(): StatusType {
    return this.status;
  }
  
  /**
   * 获取重连尝试信息
   */
  public getReconnectInfo(): { attempts: number, max: number } {
    return {
      attempts: this.reconnectAttempts,
      max: this.maxReconnectAttempts
    };
  }
  
  /**
   * 设置音频配置
   */
  public setAudioConfig(config: AudioConfig): void {
    this.audioConfig = { ...this.audioConfig, ...config };
  }
  
  /**
   * 设置状态
   */
  private setStatus(status: StatusType): void {
    this.status = status;
    
    // 通知状态变化
    this.emit(EventType.STATUS_UPDATE, { status });
  }
  
  /**
   * 触发事件
   */
  private emit(event: EventType, data: any): void {
    const listeners = this.eventListeners.get(event) || [];
    listeners.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`事件监听器错误 (${event}):`, error);
      }
    });
  }
  
  /**
   * 处理接收到的消息
   */
  private handleMessage(message: any): void {
    const { type, data } = message;
    
    // 发出通用消息事件
    this.emit(EventType.MESSAGE, message);
    
    // 根据消息类型处理
    switch (type) {
      case MessageType.TRANSCRIPTION:
        this.emit(EventType.TRANSCRIPTION, data);
        break;
        
      case MessageType.RESPONSE:
        this.emit(EventType.RESPONSE, data);
        break;
        
      case MessageType.AUDIO_CHUNK:
        this.processAudioChunk(data);
        break;
        
      case MessageType.STATUS:
        this.emit(EventType.STATUS_UPDATE, data);
        break;
        
      case MessageType.ERROR:
        this.emit(EventType.ERROR, data);
        break;
        
      case MessageType.PONG:
        // 处理服务器心跳响应，这里可以不做任何处理
        break;
        
      default:
        console.warn('收到未知类型消息:', message);
    }
  }
  
  /**
   * 尝试重新连接
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(`已达到最大重连尝试次数 (${this.maxReconnectAttempts})`);
      this.emit(EventType.RECONNECT_FAILED, { attempts: this.reconnectAttempts });
      return;
    }
    
    this.reconnectAttempts++;
    this.setStatus(StatusType.RECONNECTING);
    console.log(`尝试重新连接 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
    this.emit(EventType.RECONNECTING, { attempt: this.reconnectAttempts, max: this.maxReconnectAttempts });
    
    setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }
  
  /**
   * 启动心跳检测
   */
  private startPingInterval(): void {
    this.clearPingInterval();
    
    this.pingTimer = window.setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.send(MessageType.PING);
      }
    }, this.pingInterval);
  }
  
  /**
   * 清除心跳检测
   */
  private clearPingInterval(): void {
    if (this.pingTimer !== null) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }
  
  /**
   * 处理音频数据块
   */
  private processAudioChunk(data: any): void {
    // 发出原始音频数据事件
    this.emit(EventType.AUDIO_CHUNK, data);
    
    // 解码并播放音频
    if (data && data.audio) {
      try {
        // 转换Base64为ArrayBuffer
        const audioData = this.base64ToArrayBuffer(data.audio);
        
        // 如果有格式信息，则播放音频
        if (data.format) {
          this.playAudio(audioData, data.format);
        }
      } catch (error) {
        console.error('处理音频数据块失败:', error);
      }
    }
  }
  
  /**
   * 启动音频捕获
   */
  private async startAudioCapture(): Promise<void> {
    try {
      // 停止现有音频捕获
      this.stopAudioCapture();
      
      // 获取音频流
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // 创建AudioContext
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      
      // 创建MediaRecorder
      const options = { mimeType: this.audioConfig.format };
      this.mediaRecorder = new MediaRecorder(stream, options);
      
      // 处理音频数据
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.sendAudioData(event.data);
        }
      };
      
      // 启动录音，每100ms发送一次数据
      this.mediaRecorder.start(100);
      
    } catch (error) {
      console.error('启动音频捕获失败:', error);
      this.emit(EventType.ERROR, { error: '启动音频捕获失败', details: error });
      throw error;
    }
  }
  
  /**
   * 停止音频捕获
   */
  private stopAudioCapture(): void {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }
    
    // 释放资源
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    this.mediaRecorder = null;
  }
  
  /**
   * 播放音频
   */
  private async playAudio(audioData: ArrayBuffer, _format: string): Promise<void> {
    try {
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      
      // 解码音频
      const audioBuffer = await this.audioContext.decodeAudioData(audioData);
      
      // 创建音频源
      const source = this.audioContext.createBufferSource();
      source.buffer = audioBuffer;
      
      // 连接到输出设备
      source.connect(this.audioContext.destination);
      
      // 播放音频
      source.start();
      
    } catch (error) {
      console.error('播放音频失败:', error);
      this.emit(EventType.ERROR, { error: '播放音频失败', details: error });
    }
  }
  
  /**
   * ArrayBuffer转Base64
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }
  
  /**
   * Base64转ArrayBuffer
   */
  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = window.atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }
} 