import React from 'react'

interface AgentRun {
  agent_name: string
  status: string
  duration_ms: number | null
  tokens_used: number | null
  model_used: string | null
}

interface Props {
  agents: AgentRun[]
}

export default function MetricsBar({ agents }: Props) {
  const totalTokens = agents.reduce((s, a) => s + (a.tokens_used ?? 0), 0)
  const totalDuration = agents.reduce((s, a) => s + (a.duration_ms ?? 0), 0)
  const estimatedCost = agents.reduce((s, a) => {
    const tokens = a.tokens_used ?? 0
    const rate = a.model_used?.includes('mini') ? 0.0003 : 0.005
    return s + (tokens / 1000) * rate
  }, 0)
  const done = agents.filter(a => a.status === 'done').length

  return (
    <div className="flex items-center gap-5 px-5 py-2 bg-white border-b border-gray-100 text-xs text-gray-500">
      <span className="flex items-center gap-1.5">
        <span className="text-gray-300">●</span>
        <span className="font-medium text-gray-700">{done}</span>/7 agents
      </span>
      <span className="flex items-center gap-1.5">
        <span className="text-gray-300">●</span>
        <span className="font-medium text-gray-700">{totalTokens.toLocaleString()}</span> tokens
      </span>
      <span className="flex items-center gap-1.5">
        <span className="text-gray-300">●</span>
        Est. <span className="font-medium text-gray-700">${estimatedCost.toFixed(3)}</span>
      </span>
      <span className="flex items-center gap-1.5">
        <span className="text-gray-300">●</span>
        <span className="font-medium text-gray-700">{(totalDuration / 1000).toFixed(0)}s</span> total
      </span>
    </div>
  )
}
