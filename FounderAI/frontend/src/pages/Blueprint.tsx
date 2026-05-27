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
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* ── Left sidebar ── */}
      <AgentProgress statuses={agentStatuses} />

      {/* ── Main area ── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <div className="bg-white border-b border-gray-100 px-5 py-2.5 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <Link to="/" className="text-xs text-gray-400 hover:text-indigo-600 transition-colors flex items-center gap-1">
              ← New blueprint
            </Link>
            <span className="text-gray-200">|</span>
            <span className="text-xs font-mono text-gray-400 hidden sm:block">{id?.slice(0, 8)}...</span>
          </div>
          <div className="flex items-center gap-3">
            {isComplete && !error && (
              <>
                <button
                  onClick={() => setShowChat(c => !c)}
                  className={`text-xs font-medium px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 ${
                    showChat
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'bg-white text-indigo-600 border-indigo-200 hover:bg-indigo-50'
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
              <span className="text-xs text-indigo-600 font-medium flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" />
                Agents running...
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
                    <div key={key} className={`card overflow-hidden ${isFinal ? 'ring-2 ring-indigo-200' : ''}`}>
                      <div className="card-header">
                        <span className={`text-sm font-semibold ${isFinal ? 'text-indigo-800' : 'text-indigo-700'}`}>
                          {AGENT_LABELS[key] ?? key}
                        </span>
                        <span className="ml-auto text-xs text-emerald-600 font-medium">Done ✓</span>
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
                    <span className="w-4 h-4 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin shrink-0" />
                    <span className="text-sm text-gray-500">Next agent is running...</span>
                  </div>
                )}
              </div>
            )}

            {/* Empty state — shown only before any agent completes */}
            {visibleSections.length === 0 && !error && (
              <div className="max-w-xl mx-auto text-center py-24">
                <div className="w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center text-2xl mx-auto mb-4">⚡</div>
                <h2 className="text-lg font-semibold text-gray-800 mb-2">Analysis in progress</h2>
                <p className="text-gray-400 text-sm leading-relaxed">
                  8 AI agents are analyzing your business idea.<br />
                  Market, Legal & Location agents run in parallel.<br />
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
