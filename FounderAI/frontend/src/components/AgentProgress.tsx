import React from 'react'
import type { AgentStatus } from '../hooks/useWebSocket'

const AGENTS = [
  { key: 'idea_refiner',           label: 'Idea Refiner',        model: 'gpt-4o-mini', icon: '💡', desc: 'Clarifies your concept' },
  { key: 'market_analyst',         label: 'Market Analyst',      model: 'gpt-4o-mini', icon: '📊', desc: 'TAM, competitors, trends' },
  { key: 'legal_agent',            label: 'Legal & Compliance',  model: 'gpt-4o-mini', icon: '⚖️', desc: 'Structure, grants, tax' },
  { key: 'location_analyst',       label: 'Location Analyst',    model: 'gpt-4o-mini', icon: '📍', desc: 'Best areas & demand map' },
  { key: 'team_architect',         label: 'Team Architect',      model: 'gpt-4o-mini', icon: '👥', desc: 'Hiring plan & costs' },
  { key: 'financial_planner',      label: 'Financial Planner',   model: 'gpt-4o',      icon: '💰', desc: 'Budget & runway' },
  { key: 'alternatives_optimizer', label: 'Cost Optimizer',      model: 'gpt-4o-mini', icon: '🔄', desc: 'Budget alternatives' },
  { key: 'report_synthesizer',     label: 'Report Synthesizer',  model: 'gpt-4o',      icon: '📋', desc: 'Full blueprint' },
]

interface Props {
  statuses: Record<string, AgentStatus>
}

function StatusDot({ status }: { status: AgentStatus | undefined }) {
  if (!status || status === 'waiting') return (
    <span className="w-2 h-2 rounded-full bg-gray-300 shrink-0" />
  )
  if (status === 'running') return (
    <span className="w-2 h-2 rounded-full bg-indigo-500 shrink-0 pulse-running" />
  )
  if (status === 'done') return (
    <span className="text-emerald-500 shrink-0 text-xs">✓</span>
  )
  return <span className="text-red-400 shrink-0 text-xs">✕</span>
}

function StatusLabel({ status }: { status: AgentStatus | undefined }) {
  if (!status || status === 'waiting') return <span className="text-xs text-gray-400">Waiting</span>
  if (status === 'running') return <span className="text-xs text-indigo-600 font-medium">Running...</span>
  if (status === 'done') return <span className="text-xs text-emerald-600 font-medium">Done</span>
  return <span className="text-xs text-red-500 font-medium">Error</span>
}

export default function AgentProgress({ statuses }: Props) {
  const doneCount = AGENTS.filter(a => statuses[a.key] === 'done').length

  return (
    <aside className="w-64 shrink-0 bg-white border-r border-gray-100 flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="px-4 py-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Agents</span>
          <span className="text-xs font-semibold text-indigo-600">{doneCount}/8</span>
        </div>
        {/* Progress bar */}
        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 rounded-full transition-all duration-500"
            style={{ width: `${(doneCount / 8) * 100}%` }}
          />
        </div>
      </div>

      {/* Parallel badge */}
      <div className="mx-4 mt-3 mb-2 flex items-center gap-1.5 text-xs text-gray-400 bg-amber-50 border border-amber-100 rounded-lg px-2.5 py-1.5">
        <span>⚡</span>
        <span>Agents 2, 3 & 4 run in parallel</span>
      </div>

      {/* Agent list */}
      <div className="flex-1 px-3 py-2 space-y-1">
        {AGENTS.map((agent, idx) => {
          const status = statuses[agent.key]
          const isParallel = idx === 1 || idx === 2 || idx === 3
          const isRunning = status === 'running'
          const isDone = status === 'done'

          return (
            <div
              key={agent.key}
              className={`
                rounded-lg px-3 py-2.5 transition-all duration-200
                ${isParallel ? 'ml-3 border-l-2 border-amber-200' : ''}
                ${isRunning ? 'bg-indigo-50 border border-indigo-200 shadow-sm' : ''}
                ${isDone ? 'bg-emerald-50/50' : ''}
                ${!status || status === 'waiting' ? 'opacity-60' : ''}
              `}
            >
              <div className="flex items-center gap-2">
                <span className="text-base w-5 text-center shrink-0">{agent.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-xs font-semibold text-gray-700 truncate">{agent.label}</span>
                    <StatusDot status={status} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400 truncate">{agent.desc}</span>
                    <StatusLabel status={status} />
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Model legend */}
      <div className="px-4 py-3 border-t border-gray-100 space-y-1">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span className="w-2 h-2 rounded-full bg-indigo-300 shrink-0" />
          gpt-4o-mini — fast structured tasks
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span className="w-2 h-2 rounded-full bg-indigo-600 shrink-0" />
          gpt-4o — complex synthesis
        </div>
      </div>
    </aside>
  )
}
