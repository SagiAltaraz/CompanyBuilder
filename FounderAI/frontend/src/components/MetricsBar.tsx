/**
 * MetricsBar — a thin, honest summary strip above the report.
 *
 * Shows runtime, tokens used, and an approximate cost. No uppercase mono
 * typography; just small labels and tabular figures with real units.
 */

interface Agent {
  agent_name: string
  duration_ms: number | null
  tokens_used: number | null
  model_used: string | null
}

interface Props {
  agents: Agent[]
  blueprintId?: string
  ideaOneLine?: string
}

const BLENDED_USD_PER_MTOK: Record<string, number> = {
  'claude-haiku-5-5':  3.0,
  'claude-sonnet-5-5': 9.0,
  'claude-opus-5-5':  45.0,
}

function estimateCostUsd(agents: Agent[]): number {
  return agents.reduce((sum, a) => {
    const rate = BLENDED_USD_PER_MTOK[a.model_used ?? ''] ?? 9.0
    return sum + ((a.tokens_used ?? 0) * rate) / 1_000_000
  }, 0)
}

function fmt(n: number): string {
  return new Intl.NumberFormat('en-US').format(n)
}

export default function MetricsBar({ agents, blueprintId, ideaOneLine }: Props) {
  const totalMs     = agents.reduce((s, a) => s + (a.duration_ms ?? 0), 0)
  const totalTokens = agents.reduce((s, a) => s + (a.tokens_used ?? 0), 0)
  const costUsd     = estimateCostUsd(agents)
  const mins = Math.floor(totalMs / 60000)
  const secs = Math.floor((totalMs % 60000) / 1000)

  return (
    <div className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 px-6 py-3">
      <dl className="flex flex-wrap items-baseline gap-x-8 gap-y-2 text-[13px]">
        {blueprintId && (
          <div className="flex items-baseline gap-2">
            <dt className="text-slate-500 dark:text-slate-400">ID</dt>
            <dd className="font-mono text-slate-700 dark:text-slate-300">{blueprintId.slice(0, 8)}</dd>
          </div>
        )}
        {ideaOneLine && (
          <div className="flex items-baseline gap-2 min-w-0">
            <dt className="text-slate-500 dark:text-slate-400 flex-none">Idea</dt>
            <dd className="text-slate-700 dark:text-slate-300 truncate max-w-[42ch]" title={ideaOneLine}>{ideaOneLine}</dd>
          </div>
        )}
        <div className="flex items-baseline gap-2">
          <dt className="text-slate-500 dark:text-slate-400">Runtime</dt>
          <dd className="text-slate-700 dark:text-slate-300 tabular-nums">{mins}m {String(secs).padStart(2, '0')}s</dd>
        </div>
        <div className="flex items-baseline gap-2">
          <dt className="text-slate-500 dark:text-slate-400">Tokens</dt>
          <dd className="text-slate-700 dark:text-slate-300 tabular-nums">{fmt(totalTokens)}</dd>
        </div>
        <div className="flex items-baseline gap-2">
          <dt className="text-slate-500 dark:text-slate-400">Est. cost</dt>
          <dd className="text-slate-700 dark:text-slate-300 tabular-nums">${costUsd.toFixed(2)}</dd>
        </div>
      </dl>
    </div>
  )
}
