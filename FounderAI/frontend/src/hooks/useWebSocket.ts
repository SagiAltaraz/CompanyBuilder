import { useEffect, useRef, useState, useCallback } from 'react'

export type AgentStatus = 'waiting' | 'running' | 'done' | 'error'

export interface AgentUpdate {
  type: 'agent_update'
  agent: string
  status: AgentStatus
  output: string
}

export interface CompletedEvent {
  type: 'completed'
  report: string
}

export interface ErrorEvent {
  type: 'error'
  message: string
}

export type WsEvent = AgentUpdate | CompletedEvent | ErrorEvent

interface UseWebSocketReturn {
  agentStatuses: Record<string, AgentStatus>
  agentOutputs: Record<string, string>
  report: string | null
  error: string | null
  isConnected: boolean
  isComplete: boolean
}

const WS_BASE = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

export function useWebSocket(blueprintId: string | null): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null)
  const [agentStatuses, setAgentStatuses] = useState<Record<string, AgentStatus>>({})
  const [agentOutputs, setAgentOutputs] = useState<Record<string, string>>({})
  const [report, setReport] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isComplete, setIsComplete] = useState(false)

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data: WsEvent = JSON.parse(event.data)
      if (data.type === 'agent_update') {
        setAgentStatuses(prev => ({ ...prev, [data.agent]: data.status }))
        if (data.output) {
          setAgentOutputs(prev => ({ ...prev, [data.agent]: data.output }))
        }
      } else if (data.type === 'completed') {
        setReport(data.report)
        // Store full (untruncated) report so the section card shows the complete blueprint
        setAgentOutputs(prev => ({ ...prev, report_synthesizer: data.report }))
        setIsComplete(true)
      } else if (data.type === 'error') {
        setError(data.message)
        setIsComplete(true)
      }
    } catch {
      // ignore parse errors
    }
  }, [])

  useEffect(() => {
    if (!blueprintId) return

    // React 18 StrictMode double-invokes effects in dev.
    // Delaying via setTimeout(0) lets the StrictMode cleanup fire and cancel
    // the timer before the WebSocket is created — so only one real connection is made.
    let ws: WebSocket | null = null

    const timer = setTimeout(() => {
      ws = new WebSocket(`${WS_BASE}/ws/${blueprintId}`)
      wsRef.current = ws

      ws.onopen = () => setIsConnected(true)
      ws.onmessage = handleMessage
      ws.onerror = () => setError('WebSocket connection error')
      ws.onclose = () => setIsConnected(false)
    }, 0)

    return () => {
      clearTimeout(timer)
      if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
        ws.close()
      }
    }
  }, [blueprintId, handleMessage])

  return { agentStatuses, agentOutputs, report, error, isConnected, isComplete }
}
