import { useCallback, useEffect, useRef, useState } from 'react'

export type AgentStatus = 'waiting' | 'running' | 'done' | 'error'

export interface AgentUpdate {
  type: 'agent_update'
  agent: string
  status: AgentStatus
  output: string           // typed object as JSON string
  narrative: string        // markdown narrative extracted from the typed output
  metadata?: { duration_ms?: number; tokens_used?: number; model_used?: string; cost_usd?: number }
}

export interface CompletedEvent { type: 'completed'; report: string }
export interface ErrorEvent     { type: 'error'; message: string }
export interface CancelledEvent { type: 'cancelled' }

export type WsEvent = AgentUpdate | CompletedEvent | ErrorEvent | CancelledEvent

export interface AgentMeta {
  duration_ms?: number
  tokens_used?: number
  model_used?: string
  cost_usd?: number
}

interface UseWebSocketReturn {
  agentStatuses:   Record<string, AgentStatus>
  agentOutputs:    Record<string, unknown>   // typed object (parsed JSON)
  agentNarratives: Record<string, string>    // markdown narrative per agent
  agentMeta:       Record<string, AgentMeta>
  report:          string | null
  error:           string | null
  isConnected:     boolean
  isComplete:      boolean
}

const WS_BASE = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

export function useWebSocket(blueprintId: string | null): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null)
  const [agentStatuses,   setAgentStatuses]   = useState<Record<string, AgentStatus>>({})
  const [agentOutputs,    setAgentOutputs]    = useState<Record<string, unknown>>({})
  const [agentNarratives, setAgentNarratives] = useState<Record<string, string>>({})
  const [agentMeta,       setAgentMeta]       = useState<Record<string, AgentMeta>>({})
  const [report,      setReport]      = useState<string | null>(null)
  const [error,       setError]       = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isComplete,  setIsComplete]  = useState(false)

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data) as WsEvent
      if (data.type === 'agent_update') {
        setAgentStatuses(prev => ({ ...prev, [data.agent]: data.status }))
        if (data.output) {
          try {
            const parsed = JSON.parse(data.output)
            setAgentOutputs(prev => ({ ...prev, [data.agent]: parsed }))
          } catch {
            /* keep previous */
          }
        }
        if (data.narrative) {
          setAgentNarratives(prev => ({ ...prev, [data.agent]: data.narrative }))
        }
        if (data.metadata) {
          setAgentMeta(prev => ({ ...prev, [data.agent]: data.metadata ?? {} }))
        }
      } else if (data.type === 'completed') {
        setReport(data.report)
        setAgentNarratives(prev => ({ ...prev, report_synthesizer: data.report }))
        setIsComplete(true)
      } else if (data.type === 'error') {
        setError(data.message)
        setIsComplete(true)
      } else if (data.type === 'cancelled') {
        setError('Pipeline cancelled.')
        setIsComplete(true)
      }
    } catch {
      /* ignore parse errors */
    }
  }, [])

  useEffect(() => {
    if (!blueprintId) return
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

  return {
    agentStatuses, agentOutputs, agentNarratives, agentMeta,
    report, error, isConnected, isComplete,
  }
}
