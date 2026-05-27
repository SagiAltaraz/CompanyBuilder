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

interface Props { statuses: Record<string, AgentStatus> }

function StatusDot({ status }: { status: AgentStatus | undefined }) {
  if (!status || status === 'waiting') return <span className="w-2 h-2 rounded-full bg-slate-300 shrink-0" />
  if (status === 'running')             return <span className="w-2 h-2 rounded-full bg-brand-500 shrink-0 pulse-running" />
  if (status === 'done')                return <span className="text-emerald-500 shrink-0 text-xs leading-none">✓</span>
  return <span className="text-red-400 shrink-0 text-xs leading-none">✕</span>
}

function StatusLabel({ status }: { status: AgentStatus | undefined }) {
  if (!status || status === 'waiting') return <span className="text-[11px] text-slate-400">Waiting</span>
  if (status === 'running')             return <span className="text-[11px] text-brand-600 font-medium">Running…</span>
  if (status === 'done')                return <span className="text-[11px] text-emerald-600 font-medium">Done</span>
  return <span className="text-[11px] text-red-500 font-medium">Error</span>
}

export default function AgentProgress({ statuses }: Props) {
  const doneCount = AGENTS.filter(a => statuses[a.key] === 'done').length
  const pct = (doneCount / AGENTS.length) * 100

  return (
    <aside className="w-64 shrink-0 bg-white border-r border-slate-100 flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="px-4 py-4 border-b border-slate-100">
        <div className="flex items-center gap-2 mb-3">
          <div className="brand-mark !w-7 !h-7 !text-xs">F</div>
          <div className="leading-tight flex-1">
            <div className="font-display font-bold text-ink text-sm">FounderAI</div>
            <div className="text-[10px] text-slate-400 uppercase tracking-wider">Live pipeline</div>
          </div>
        </div>
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Agents</span>
          <span className="text-xs font-mono font-semibold text-brand-600">{doneCount}/{AGENTS.length}</span>
        </div>
        {/* Progress bar */}
        <div className="relative h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-brand-gradient rounded-full transition-all duration-700 ease-out"
            style={{ width: `${pct}%` }}
          />
          {pct > 0 && pct < 100 && (
            <div
              className="absolute top-0 h-full w-6 bg-white/50 blur-md animate-shimmer"
              style={{ left: `${Math.max(0, pct - 8)}%` }}
            />
          )}
        </div>
      </div>

      {/* Parallel badge */}
      <div className="mx-4 mt-3 mb-2 flex items-start gap-1.5 text-[11px] text-gold-600 bg-gold-400/10 border border-gold-400/30 rounded-lg px-2.5 py-2 leading-snug">
        <span className="text-sm leading-none mt-px">⚡</span>
        <span><strong className="font-semibold">Parallel fan-out</strong> — agents 2, 3 &amp; 4 run simultaneously</span>
      </div>

      {/* Agent list */}
      <div className="flex-1 px-3 py-2 space-y-1 relative">
        {AGENTS.map((agent, idx) => {
          const status = statuses[agent.key]
          const isParallel = idx === 1 || idx === 2 || idx === 3
          const isRunning = status === 'running'
          const isDone = status === 'done'
          const isFinal = idx === AGENTS.length - 1

          return (
            <div
              key={agent.key}
              className={`
                relative rounded-xl px-3 py-2.5 transition-all duration-200
                ${isParallel ? 'ml-3 border-l-2 border-gold-400/60' : ''}
                ${isRunning ? 'bg-brand-50 ring-1 ring-brand-200 shadow-sm' : ''}
                ${isDone ? 'bg-emerald-50/40' : ''}
                ${isFinal && isDone ? '!bg-gradient-to-r from-brand-50 to-gold-400/10 ring-1 ring-brand-200' : ''}
                ${!status || status === 'waiting' ? 'opacity-55' : ''}
              `}
            >
              <div className="flex items-center gap-2">
                <span className="text-base w-5 text-center shrink-0">{agent.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-xs font-semibold text-ink-soft truncate">{agent.label}</span>
                    <StatusDot status={status} />
                  </div>
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-[11px] text-slate-400 truncate">{agent.desc}</span>
                    <StatusLabel status={status} />
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Model legend */}
      <div className="px-4 py-3 border-t border-slate-100 space-y-1.5 bg-slate-50/50">
        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Models</div>
        <div className="flex items-center gap-2 text-[11px] text-slate-500">
          <span className="w-2 h-2 rounded-full bg-brand-300 shrink-0" />
          <span className="font-mono">gpt-4o-mini</span>
          <span className="text-slate-400">· fast tasks</span>
        </div>
        <div className="flex items-center gap-2 text-[11px] text-slate-500">
          <span className="w-2 h-2 rounded-full bg-brand-600 shrink-0" />
          <span className="font-mono">gpt-4o</span>
          <span className="text-slate-400">· synthesis</span>
        </div>
      </div>
    </aside>
  )
}
