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
  ERROR = 'error'
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
  ERROR = 'error'
}

// 状态类型定义
export enum StatusType {
  IDLE = 'idle',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  LISTENING = 'listening',
  PROCESSING = 'processing',
  ERROR = 'error'
}

// WebSocket客户端配置
export interface WebSocketClientConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

// 事件监听器类型
type EventListener = (data: any) => void;

export class WebSocketClient {
  private socket: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number;
  private maxReconnectAttempts: number;
  private reconnectAttempts = 0;
  private status: StatusType = StatusType.IDLE;
  private eventListeners: Map<EventType, EventListener[]> = new Map();
  
  constructor(config: WebSocketClientConfig) {
    this.url = config.url;
    this.reconnectInterval = config.reconnectInterval || 3000;
    this.maxReconnectAttempts = config.maxReconnectAttempts || 5;
    
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
    
    this.setStatus(StatusType.CONNECTING);
    
    try {
      this.socket = new WebSocket(this.url);
      
      // 连接打开
      this.socket.onopen = () => {
        console.log('WebSocket连接已建立');
        this.reconnectAttempts = 0;
        this.setStatus(StatusType.CONNECTED);
        this.emit(EventType.CONNECTED, null);
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
      this.socket.onclose = () => {
        console.log('WebSocket连接已关闭');
        this.setStatus(StatusType.DISCONNECTED);
        this.emit(EventType.DISCONNECTED, null);
        this.attemptReconnect();
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
      this.attemptReconnect();
    }
  }
  
  /**
   * 断开WebSocket连接
   */
  public disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.setStatus(StatusType.DISCONNECTED);
    }
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
    
    this.socket.send(message);
  }
  
  /**
   * 开始语音识别
   */
  public startListening(config: any = {}): void {
    this.send(MessageType.START_LISTENING, config);
    this.setStatus(StatusType.LISTENING);
  }
  
  /**
   * 停止语音识别
   */
  public stopListening(): void {
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
  public sendAudioData(audioData: any): void {
    this.send(MessageType.AUDIO_DATA, { audio: audioData });
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
   * 设置状态
   */
  private setStatus(status: StatusType): void {
    this.status = status;
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
        this.emit(EventType.AUDIO_CHUNK, data);
        break;
        
      case MessageType.STATUS:
        this.emit(EventType.STATUS_UPDATE, data);
        break;
        
      case MessageType.ERROR:
        this.emit(EventType.ERROR, data);
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
      return;
    }
    
    this.reconnectAttempts++;
    console.log(`尝试重新连接 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
    
    setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }
} 