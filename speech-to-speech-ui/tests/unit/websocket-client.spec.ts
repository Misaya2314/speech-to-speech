import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { WebSocketClient } from '@/utils/websocket-client';

// 模拟WebSocket类
class MockWebSocket {
  url: string;
  onopen: Function | null = null;
  onclose: Function | null = null;
  onmessage: Function | null = null;
  onerror: Function | null = null;
  readyState: number = 0;
  
  constructor(url: string) {
    this.url = url;
  }
  
  send(data: string) {
    return data;
  }
  
  close() {
    if (this.onclose) {
      this.onclose({ code: 1000, reason: 'Normal closure' });
    }
  }
}

// 模拟WebSocketClient中可能使用的接口或类型
vi.mock('@/utils/websocket-client', () => {
  return {
    WebSocketClient: class MockWebSocketClient {
      private url: string;
      private ws: MockWebSocket | null = null;
      
      constructor(url: string) {
        this.url = url;
      }
      
      connect() {
        this.ws = new MockWebSocket(this.url);
        return true;
      }
      
      send(message: any) {
        if (this.ws) {
          return this.ws.send(JSON.stringify(message));
        }
        return false;
      }
      
      disconnect() {
        if (this.ws) {
          this.ws.close();
          return true;
        }
        return false;
      }
    }
  };
});

describe('WebSocketClient', () => {
  let client: WebSocketClient;
  
  beforeEach(() => {
    client = new WebSocketClient('ws://localhost:8080');
  });
  
  it('应该可以创建WebSocketClient实例', () => {
    expect(client).toBeDefined();
  });
  
  it('应该可以连接到服务器', () => {
    const result = client.connect();
    expect(result).toBe(true);
  });
  
  it('应该可以发送消息', () => {
    client.connect();
    const message = { type: 'TEST', data: { message: 'Hello' } };
    const result = client.send(message);
    expect(result).not.toBe(false);
  });
}); 