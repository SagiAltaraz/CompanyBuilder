import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import AgentProgress  from '../components/AgentProgress'
import ReportRenderer from '../components/ReportRenderer'
import MetricsBar     from '../components/MetricsBar'
import ChatPanel      from '../components/ChatPanel'
import { useWebSocket } from '../hooks/useWebSocket'
import { useLanguageDir, useTheme } from '../hooks/useTheme'

const SECTIONS: Array<{ key: string; title: string }> = [
  { key: 'idea_refiner',           title: 'The brief, refined' },
  { key: 'market_analyst',         title: 'Market analysis' },
  { key: 'legal_agent',            title: 'Legal & grants' },
  { key: 'location_analyst',       title: 'Location strategy' },
  { key: 'team_architect',         title: 'Team plan' },
  { key: 'financial_planner',      title: 'Financial plan' },
  { key: 'alternatives_optimizer', title: 'Budget alternatives' },
  { key: 'report_synthesizer',     title: 'Final blueprint' },
  { key: 'critic',                 title: 'Consistency check' },
]

interface AgentRun {
  agent_name: string
  status: string
  duration_ms: number | null
  tokens_used: number | null
  model_used: string | null
}

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function Blueprint() {
  const { id } = useParams<{ id: string }>()
  const {
    agentStatuses, agentNarratives, agentOutputs,
    error, isComplete,
  } = useWebSocket(id ?? null)

  const refined = agentOutputs['idea_refiner'] as { language?: string; concept?: string } | undefined
  useLanguageDir(refined?.language)

  const { theme, toggle } = useTheme()
  const [agentRuns, setAgentRuns] = useState<AgentRun[]>([])
  const [showChat, setShowChat]   = useState(false)
  const [metaIdea, setMetaIdea]   = useState<string>('')
  const [activeKey, setActiveKey] = useState<string | null>(null)

  const scrollRef  = useRef<HTMLDivElement | null>(null)
  const sectionRefs = useRef<Record<string, HTMLElement | null>>({})

  useEffect(() => {
    if (!id || !isComplete) return
    fetch(`${API_BASE}/blueprints/${id}`)
      .then(r => r.json())
      .then(d => {
        setAgentRuns(d.agents ?? [])
        setMetaIdea(d.raw_input ?? '')
      })
      .catch(() => {})
  }, [id, isComplete])

  const availableKeys = useMemo(
    () => new Set(Object.keys(agentNarratives).filter(k => agentNarratives[k])),
    [agentNarratives],
  )
  const visible = SECTIONS.filter(s => agentNarratives[s.key])
  const ideaOneLine = refined?.concept ?? metaIdea.split('\n')[0] ?? ''

  // Scroll-spy: highlight whichever section's top is nearest the viewport top.
  useEffect(() => {
    const root = scrollRef.current
    if (!root || visible.length === 0) return

    const io = new IntersectionObserver(
      entries => {
        // Keep the topmost intersecting section as active.
        const intersecting = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (intersecting[0]) {
          const key = intersecting[0].target.getAttribute('data-section-key')
          if (key) setActiveKey(key)
        }
      },
      {
        root,
        rootMargin: '-10% 0px -70% 0px',  // triggers when section top is in upper third
        threshold: 0,
      },
    )
    visible.forEach(s => {
      const el = sectionRefs.current[s.key]
      if (el) io.observe(el)
    })
    return () => io.disconnect()
  }, [visible])

  // Default active to first available section.
  useEffect(() => {
    if (!activeKey && visible[0]) setActiveKey(visible[0].key)
  }, [activeKey, visible])

  const jumpTo = (key: string) => {
    const el = sectionRefs.current[key]
    const root = scrollRef.current
    if (!el || !root) return
    const offset = el.offsetTop - 16
    root.scrollTo({ top: offset, behavior: 'smooth' })
    setActiveKey(key)
  }

  return (
    <div className="flex h-screen overflow-hidden bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100">
      <AgentProgress
        statuses={agentStatuses}
        availableKeys={availableKeys}
        activeKey={activeKey}
        onJump={jumpTo}
      />

      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Top bar */}
        <header className="flex items-center justify-between px-5 py-3 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-3 min-w-0">
            <Link to="/" className="btn-ghost">← New plan</Link>
            <span className="text-[13px] text-slate-500 dark:text-slate-400 font-mono">
              {id?.slice(0, 8)}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {!isComplete && !error && (
              <span className="badge badge-info">Working…</span>
            )}
            {isComplete && !error && (
              <span className="badge badge-success">
                <svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true">
                  <path d="M2 5.5L4 7.5L8 2.5" stroke="currentColor" strokeWidth="1.6" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Complete
              </span>
            )}
            {error && <span className="badge badge-danger">Error</span>}
            {isComplete && !error && (
              <button
                type="button"
                onClick={() => setShowChat(c => !c)}
                className={showChat ? 'btn-primary' : 'btn-secondary'}
                aria-pressed={showChat}
              >
                {showChat ? 'Hide chat' : 'Ask advisor'}
              </button>
            )}
            <button
              type="button"
              onClick={toggle}
              className="btn-ghost"
              aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
            >
              {theme === 'dark' ? 'Light' : 'Dark'}
            </button>
          </div>
        </header>

        {/* Summary strip */}
        {agentRuns.length > 0 && (
          <MetricsBar agents={agentRuns} blueprintId={id} ideaOneLine={ideaOneLine} />
        )}

        {/* Content + chat */}
        <div className="flex-1 flex overflow-hidden">
          <div
            ref={scrollRef}
            className={'flex-1 overflow-y-auto ' + (showChat ? 'border-r border-slate-200 dark:border-slate-800' : '')}
          >
            <main id="main" className="max-w-3xl mx-auto px-5 sm:px-8 py-8">
              {error && (
                <div role="alert" className="mb-6 rounded-lg border border-danger-500/40 bg-danger-500/10 px-4 py-3 text-[14px] text-danger-700 dark:text-danger-500">
                  <strong className="font-semibold">Pipeline error · </strong>{error}
                </div>
              )}

              {visible.length === 0 && !error && (
                <div className="mt-20 text-center">
                  <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-primary-50 dark:bg-primary-500/10 text-primary-700 dark:text-primary-300 mb-4">
                    <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" className="animate-spin">
                      <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="2" fill="none" strokeDasharray="34" strokeDashoffset="14" strokeLinecap="round" />
                    </svg>
                  </div>
                  <h2 className="text-[18px] font-semibold text-slate-900 dark:text-slate-100">
                    Preparing your blueprint
                  </h2>
                  <p className="mt-2 text-[14px] text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
                    First sections appear in about fifteen seconds. You can stay here or come back later.
                  </p>
                </div>
              )}

              {visible.map((section, idx) => {
                const isFinal = section.key === 'report_synthesizer'
                return (
                  <article
                    key={section.key}
                    id={`section-${section.key}`}
                    data-section-key={section.key}
                    ref={el => { sectionRefs.current[section.key] = el }}
                    className={'card p-6 sm:p-7 mb-5 animate-slide-up scroll-mt-4 ' + (isFinal ? 'card-highlight' : '')}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="section-eyebrow">Section {String(idx + 1).padStart(2, '0')}</span>
                      <span className="badge badge-success text-[11px]">Ready</span>
                    </div>
                    <h2 className="section-title mb-4">{section.title}</h2>
                    <ReportRenderer
                      content={agentNarratives[section.key]}
                      isFinalReport={isFinal && isComplete}
                    />
                  </article>
                )
              })}

              {!isComplete && visible.length > 0 && (
                <div className="text-[13px] text-slate-500 dark:text-slate-400 mt-4 flex items-center gap-2">
                  <svg width="12" height="12" viewBox="0 0 12 12" className="animate-spin" aria-hidden="true">
                    <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth="1.5" fill="none" strokeDasharray="20" strokeDashoffset="8" strokeLinecap="round" />
                  </svg>
                  Next section coming…
                </div>
              )}
            </main>
          </div>

          {showChat && id && (
            <div className="w-80 shrink-0 flex flex-col overflow-hidden">
              <ChatPanel blueprintId={id} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
