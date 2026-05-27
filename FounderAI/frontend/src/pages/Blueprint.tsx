import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import AgentProgress from '../components/AgentProgress'
import ReportRenderer from '../components/ReportRenderer'
import MetricsBar from '../components/MetricsBar'
import ChatPanel from '../components/ChatPanel'
import { useWebSocket } from '../hooks/useWebSocket'

const AGENT_LABELS: Record<string, string> = {
  idea_refiner:           '💡 Refined Business Concept',
  market_analyst:         '📊 Market Analysis',
  legal_agent:            '⚖️ Legal & Compliance',
  location_analyst:       '📍 Location Strategy',
  team_architect:         '👥 Team Structure',
  financial_planner:      '💰 Financial Plan',
  alternatives_optimizer: '🔄 Budget Alternatives',
  report_synthesizer:     '📋 Full Company Blueprint',
}

const AGENT_ORDER = [
  'idea_refiner', 'market_analyst', 'legal_agent', 'location_analyst',
  'team_architect', 'financial_planner', 'alternatives_optimizer', 'report_synthesizer',
]

interface AgentRun {
  agent_name: string; status: string
  duration_ms: number | null; tokens_used: number | null; model_used: string | null
}

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function Blueprint() {
  const { id } = useParams<{ id: string }>()
  const { agentStatuses, agentOutputs, report, error, isComplete } = useWebSocket(id ?? null)
  const [agentRuns, setAgentRuns] = useState<AgentRun[]>([])
  const [showChat, setShowChat] = useState(false)

  // Poll for metrics once complete
  useEffect(() => {
    if (!id || !isComplete) return
    fetch(`${API_BASE}/blueprints/${id}`)
      .then(r => r.json())
      .then(d => setAgentRuns(d.agents ?? []))
      .catch(() => {})
  }, [id, isComplete])

  const visibleSections = AGENT_ORDER.filter(k => agentOutputs[k])

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* ── Left sidebar ── */}
      <AgentProgress statuses={agentStatuses} />

      {/* ── Main area ── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <div className="bg-white/80 backdrop-blur border-b border-slate-100 px-5 py-2.5 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <Link to="/" className="btn-ghost">
              <span aria-hidden>←</span> New blueprint
            </Link>
            <span className="text-slate-200">|</span>
            <span className="text-xs font-mono text-slate-400 hidden sm:block">{id?.slice(0, 8)}…</span>
          </div>
          <div className="flex items-center gap-3">
            {isComplete && !error && (
              <>
                <button
                  onClick={() => setShowChat(c => !c)}
                  className={`text-xs font-medium px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 ${
                    showChat
                      ? 'bg-brand-gradient text-white border-transparent shadow-glow-brand'
                      : 'bg-white text-brand-600 border-brand-200 hover:bg-brand-50'
                  }`}
                >
                  💬 {showChat ? 'Hide chat' : 'Ask advisor'}
                </button>
                <span className="text-xs text-emerald-600 font-medium flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                  Complete
                </span>
              </>
            )}
            {!isComplete && !error && (
              <span className="text-xs font-medium flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-brand-500 rounded-full animate-pulse" />
                <span className="shimmer-text">Agents running…</span>
              </span>
            )}
            {error && <span className="text-xs text-red-500 font-medium">Pipeline error</span>}
          </div>
        </div>

        {/* Metrics bar */}
        {agentRuns.length > 0 && <MetricsBar agents={agentRuns} />}

        {/* Content + optional chat */}
        <div className="flex-1 flex overflow-hidden">
          {/* Report / progress area */}
          <div className={`flex-1 overflow-y-auto p-6 ${showChat ? 'border-r border-gray-100' : ''}`}>
            {error && (
              <div className="max-w-2xl mx-auto bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
                <strong>Pipeline error:</strong> {error}
              </div>
            )}

            {/* Section-by-section reveal — stays visible through completion */}
            {visibleSections.length > 0 && (
              <div className="max-w-4xl mx-auto space-y-4">
                {visibleSections.map(key => {
                  const isFinal = key === 'report_synthesizer'
                  return (
                    <div key={key} className={`overflow-hidden animate-fade-up ${isFinal ? 'card-highlight' : 'card'}`}>
                      <div className="card-header">
                        <span className={`font-display text-sm font-bold tracking-tight ${isFinal ? 'text-gradient' : 'text-brand-700'}`}>
                          {AGENT_LABELS[key] ?? key}
                        </span>
                        <span className="ml-auto chip-success !py-0.5 !text-[11px]">Done ✓</span>
                      </div>
                      <div className={isFinal ? 'px-6 py-6 sm:px-8' : 'px-6 py-4'}>
                        <ReportRenderer content={agentOutputs[key]} isFinalReport={isFinal && isComplete} />
                      </div>
                    </div>
                  )
                })}

                {/* Spinner while next agent runs */}
                {!isComplete && (
                  <div className="card px-6 py-4 flex items-center gap-3">
                    <span className="w-4 h-4 border-2 border-brand-200 border-t-brand-600 rounded-full animate-spin shrink-0" />
                    <span className="text-sm shimmer-text">Next agent is running…</span>
                  </div>
                )}
              </div>
            )}

            {/* Empty state — shown only before any agent completes */}
            {visibleSections.length === 0 && !error && (
              <div className="max-w-xl mx-auto text-center py-24 animate-fade-up">
                <div className="relative w-20 h-20 mx-auto mb-5">
                  <div className="absolute inset-0 bg-brand-gradient rounded-2xl rotate-6 opacity-20 blur-xl" />
                  <div className="relative w-full h-full bg-brand-gradient rounded-2xl flex items-center justify-center text-3xl shadow-glow-brand">⚡</div>
                </div>
                <h2 className="font-display text-xl font-bold text-ink mb-2 tracking-tight">Analysis in progress</h2>
                <p className="text-slate-500 text-sm leading-relaxed">
                  8 AI agents are analyzing your business idea.<br />
                  <span className="text-gold-600 font-medium">Market, Legal &amp; Location</span> agents run in parallel.<br />
                  First results appear in ~15 seconds.
                </p>
              </div>
            )}
          </div>

          {/* Chat panel */}
          {showChat && id && (
            <div className="w-80 shrink-0 flex flex-col overflow-hidden border-l border-gray-100">
              <ChatPanel blueprintId={id} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
