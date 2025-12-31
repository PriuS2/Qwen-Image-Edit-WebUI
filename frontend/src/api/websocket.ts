import type { ProgressMessage } from '@/types'

type ProgressCallback = (message: ProgressMessage) => void
type ErrorCallback = (error: Event) => void
type CloseCallback = () => void

export class JobProgressWebSocket {
  private ws: WebSocket | null = null
  private jobId: string
  private pingInterval: number | null = null
  private onProgress: ProgressCallback
  private onError?: ErrorCallback
  private onClose?: CloseCallback

  constructor(
    jobId: string,
    onProgress: ProgressCallback,
    options: {
      onError?: ErrorCallback
      onClose?: CloseCallback
    } = {}
  ) {
    this.jobId = jobId
    this.onProgress = onProgress
    this.onError = options.onError
    this.onClose = options.onClose
  }

  connect(): void {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/ws/progress/${this.jobId}`

    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log(`[WebSocket] Connected to job ${this.jobId}`)
      this.startPing()
    }

    this.ws.onmessage = (event) => {
      // Ignore ping/pong messages
      if (event.data === 'pong' || event.data === 'ping') {
        return
      }
      
      try {
        const data: ProgressMessage = JSON.parse(event.data)
        this.onProgress(data)

        // Auto-close on completion or failure
        if (data.status === 'completed' || data.status === 'failed') {
          this.close()
        }
      } catch (e) {
        console.error('[WebSocket] Failed to parse message:', e, 'Raw data:', event.data)
      }
    }

    this.ws.onerror = (event) => {
      console.error('[WebSocket] Error:', event)
      this.onError?.(event)
    }

    this.ws.onclose = () => {
      console.log(`[WebSocket] Disconnected from job ${this.jobId}`)
      this.stopPing()
      this.onClose?.()
    }
  }

  private startPing(): void {
    this.pingInterval = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send('ping')
      }
    }, 25000)
  }

  private stopPing(): void {
    if (this.pingInterval !== null) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }

  close(): void {
    this.stopPing()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

/**
 * Create a WebSocket connection for job progress
 */
export function createJobProgressSocket(
  jobId: string,
  onProgress: ProgressCallback,
  options: {
    onError?: ErrorCallback
    onClose?: CloseCallback
  } = {}
): JobProgressWebSocket {
  const socket = new JobProgressWebSocket(jobId, onProgress, options)
  socket.connect()
  return socket
}
