import { WSEvent } from '../types';

type EventCallback = (event: WSEvent) => void;

class WebSocketClient {
  private socket: WebSocket | null = null;
  private listeners: Set<EventCallback> = new Set();
  private reconnectInterval: number = 3000;
  private isConnecting: boolean = false;

  public connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isConnecting = true;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/events`;

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log('[EOC WebSocket] Connected to real-time disaster event stream');
        this.isConnecting = false;
      };

      this.socket.onmessage = (message) => {
        try {
          const parsed: WSEvent = JSON.parse(message.data);
          this.listeners.forEach((callback) => callback(parsed));
        } catch (e) {
          console.warn('[EOC WebSocket] Non-JSON payload received:', message.data);
        }
      };

      this.socket.onclose = () => {
        this.isConnecting = false;
        setTimeout(() => this.connect(), this.reconnectInterval);
      };

      this.socket.onerror = (err) => {
        console.warn('[EOC WebSocket] Connection error, reconnecting...', err);
        this.socket?.close();
      };
    } catch (err) {
      this.isConnecting = false;
      setTimeout(() => this.connect(), this.reconnectInterval);
    }
  }

  public subscribe(callback: EventCallback) {
    this.listeners.add(callback);
    return () => {
      this.listeners.delete(callback);
    };
  }

  public send(message: string) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(message);
    }
  }
}

export const wsClient = new WebSocketClient();
