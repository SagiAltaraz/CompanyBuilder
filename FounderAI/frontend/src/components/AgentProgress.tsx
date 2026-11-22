/**
 * ProgressNav — sticky sidebar that doubles as pipeline-progress tracker
 * and table-of-contents.
 *
 * Shows nine agents with status icons; each row is a link that scrolls to
 * the matching section once it's available. The active section (based on
 * scroll position, set by the parent) gets a left-accent highlight.
 */
import type { AgentStatus } from '../hooks/useWebSocket'

const AGENTS: Array<{ key: string; label: string; group?: 'parallel' }> = [
  { key: 'idea_refiner',           label: 'Refined brief' },
  { key: 'market_analyst',         label: 'Market analysis',       group: 'parallel' },
  { key: 'legal_agent',            label: 'Legal & grants',        group: 'parallel' },
  { key: 'location_analyst',       label: 'Location strategy',     group: 'parallel' },
  { key: 'team_architect',         label: 'Team plan' },
  { key: 'financial_planner',      label: 'Financial plan' },
  { key: 'alternatives_optimizer', label: 'Budget alternatives' },
  { key: 'report_synthesizer',     label: 'Final blueprint' },
  { key: 'critic',                 label: 'Consistency check' },
]

function pad(n: number) { return n < 10 ? `0${n}` : `${n}` }

function StepIcon({ status }: { status: AgentStatus | 'waiting' }) {
  if (status === 'done') {
    return (
      <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true" fill="none">
        <path d="M2.5 6.2 L5 8.7 L9.7 3.8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  }
  if (status === 'error') return <span aria-hidden="true">!</span>
  if (status === 'running') {
    return (
      <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true" className="animate-spin">
        <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth="1.5" fill="none" strokeDasharray="20" strokeDashoffset="8" strokeLinecap="round" />
      </svg>
    )
  }
  return null
}

interface Props {
  statuses: Record<string, AgentStatus>
  availableKeys: Set<string>
  activeKey: string | null
  onJump: (key: string) => void
}

export default function AgentProgress({ statuses, availableKeys, activeKey, onJump }: Props) {
  const doneCount  = AGENTS.filter(a => statuses[a.key] === 'done').length
  const errorCount = AGENTS.filter(a => statuses[a.key] === 'error').length
  const percent    = Math.round((doneCount / AGENTS.length) * 100)
  const running    = AGENTS.find(a => statuses[a.key] === 'running')

  return (
    <aside
      className="w-64 shrink-0 h-full border-r border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 overflow-y-auto"
      aria-labelledby="progress-heading"
    >
      <div className="px-5 pt-6 pb-4 border-b border-slate-200 dark:border-slate-800">
        <h2 id="progress-heading" className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Blueprint
        </h2>
        <div className="mt-2 flex items-baseline justify-between">
          <span className="text-[14px] font-semibold text-slate-900 dark:text-slate-100">
            {doneCount}/{AGENTS.length} sections
          </span>
          <span className="text-[12px] text-slate-500 dark:text-slate-400 tabular-nums">{percent}%</span>
        </div>
        <div
          className="progress mt-2"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={AGENTS.length}
          aria-valuenow={doneCount}
          aria-valuetext={`${doneCount} of ${AGENTS.length} sections complete`}
        >
          <div className="progress-bar" style={{ width: `${percent}%` }} />
        </div>
        {running && (
          <div className="mt-2 text-[12px] text-slate-600 dark:text-slate-300 truncate" aria-live="polite" title={running.label}>
            Working on: <span className="font-medium">{running.label}</span>
          </div>
        )}
        {errorCount > 0 && (
          <div className="mt-2 badge badge-danger">{errorCount} error{errorCount > 1 ? 's' : ''}</div>
        )}
      </div>

      <nav aria-label="Blueprint sections" className="py-3">
        <ol className="space-y-0.5 px-2">
          {AGENTS.map((a, i) => {
            const status = statuses[a.key] ?? 'waiting'
            const available = availableKeys.has(a.key)
            const isActive = activeKey === a.key
            const base =
              'w-full text-left flex items-center gap-2.5 px-3 py-2 rounded-md transition-colors text-[13.5px] '
            const stateClass = isActive
              ? 'bg-white dark:bg-slate-800 text-primary-700 dark:text-primary-300 font-medium border-l-2 border-primary-600 dark:border-primary-400 pl-[10px]'
              : available
                ? 'text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-800'
                : 'text-slate-400 dark:text-slate-500 cursor-default'

            return (
              <li key={a.key}>
                <button
                  type="button"
                  disabled={!available}
                  onClick={() => available && onJump(a.key)}
                  aria-current={isActive ? 'true' : undefined}
                  className={base + stateClass}
                >
                  <span className={`step-dot ${status}`} aria-hidden="true">
                    {status === 'waiting' ? pad(i + 1) : <StepIcon status={status} />}
                  </span>
                  <span className="flex-1 min-w-0 truncate">{a.label}</span>
                  {a.group === 'parallel' && status === 'waiting' && (
                    <span className="text-[10px] text-slate-400 dark:text-slate-500">∥</span>
                  )}
                </button>
              </li>
            )
          })}
        </ol>
      </nav>

      <div className="mt-2 mx-4 pt-3 pb-5 border-t border-slate-200 dark:border-slate-800 text-[11px] text-slate-500 dark:text-slate-400">
        Claude 5.5 · LangGraph
      </div>
    </aside>
  )
}
