import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../hooks/useTheme'

const BIZ_MODELS = [
  { value: 'b2b',         title: 'B2B',         sub: 'Sell to businesses' },
  { value: 'b2c',         title: 'B2C',         sub: 'Sell to consumers' },
  { value: 'b2b2c',       title: 'B2B2C',       sub: 'Business → consumer' },
  { value: 'marketplace', title: 'Marketplace', sub: 'Connect two sides' },
]
const MARKETS = [
  { value: 'israel',  title: 'Israel',  sub: 'Local market' },
  { value: 'global',  title: 'Global',  sub: 'Worldwide' },
  { value: 'region',  title: 'Region',  sub: 'EU / US / other' },
]
const STAGES = [
  { value: 'idea',           title: 'Just an idea',   sub: 'Not built yet' },
  { value: 'mvp',            title: 'MVP',            sub: 'Prototype built' },
  { value: 'early_revenue',  title: 'Early revenue',  sub: 'First customers' },
  { value: 'scaling',        title: 'Scaling',        sub: 'Growing fast' },
]

const EXAMPLES = [
  { label: 'Mobile café',       text: 'A mobile coffee cart in Tel Aviv targeting tech workers around Rothschild and Sarona on weekdays, and weekend markets.' },
  { label: 'Design studio',     text: 'A boutique web design agency for small and medium Israeli businesses — websites, landing pages, and a simple SEO retainer.' },
  { label: 'Restaurant SaaS',   text: 'A Hebrew-first SaaS for Israeli restaurants: orders, scheduling, inventory, and a small loyalty program.' },
  { label: 'סוכנות דיגיטל',      text: 'אני רוצה להקים סוכנות שיווק דיגיטלי לעסקים קטנים בישראל, כולל ניהול רשתות חברתיות, SEO ופרסום ממומן.' },
]

const DELIVERABLES = [
  { title: 'Market analysis',    body: 'TAM/SAM/SOM, top competitors, positioning gaps.' },
  { title: 'Legal & grants',     body: 'Entity, licenses, VAT, Innovation Authority programs.' },
  { title: 'Location & team',    body: 'Neighborhood rents or GTM markets · hiring plan with real salaries.' },
  { title: 'Finances & roadmap', body: 'Setup cost, monthly burn, runway, 12-month revenue + milestones.' },
]

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function Dashboard() {
  const [idea, setIdea]       = useState('')
  const [model, setModel]     = useState<string>('b2c')
  const [market, setMarket]   = useState<string>('israel')
  const [stage, setStage]     = useState<string>('idea')
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<string | null>(null)
  const navigate = useNavigate()
  const { theme, toggle } = useTheme()

  const canSubmit = idea.trim().length >= 20 && !loading
  const ideaLen = idea.trim().length

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!canSubmit) return
    setLoading(true)
    setError(null)
    // Concatenate the structured answers into the brief sent to the backend.
    // The idea_refiner will read the labels and fill the typed RefinedIdea fields.
    const briefing = `Business idea: ${idea.trim()}

Business model: ${model}
Target market: ${market}
Stage: ${stage}`

    try {
      const res = await fetch(`${API_BASE}/blueprints`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea: briefing }),
      })
      if (!res.ok) throw new Error(await res.text() || 'Server error')
      const data = await res.json()
      navigate(`/blueprint/${data.blueprint_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <a href="/" className="logo">
            <span className="logo-mark" aria-hidden>F</span>
            <span className="logo-text">FounderAI</span>
          </a>
          <nav className="flex items-center gap-1" aria-label="Primary">
            <a href="https://github.com/sagialtaraz/CompanyBuilder" target="_blank" rel="noreferrer" className="btn-ghost">
              GitHub
            </a>
            <button
              type="button"
              onClick={toggle}
              className="btn-ghost"
              aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
              aria-pressed={theme === 'dark'}
            >
              {theme === 'dark' ? 'Light mode' : 'Dark mode'}
            </button>
          </nav>
        </div>
      </header>

      <main id="main" className="max-w-3xl mx-auto px-4 sm:px-6 py-10 sm:py-14">
        {/* Intro */}
        <div className="animate-slide-up">
          <h1 className="text-[28px] sm:text-[34px] font-semibold tracking-tight text-slate-900 dark:text-slate-100 leading-tight">
            Plan your business, step by step.
          </h1>
          <p className="mt-3 text-[16px] text-slate-600 dark:text-slate-400 leading-relaxed max-w-prose">
            Answer four short questions. In about two minutes, nine agents build you a tailored blueprint —
            market, legal, location, team, and finances — in Hebrew or English.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={submit} className="mt-10 card p-5 sm:p-7 animate-slide-up" noValidate>
          {/* Idea */}
          <div className="field">
            <label htmlFor="idea" className="field-label field-required">
              What's your business idea?
            </label>
            <textarea
              id="idea"
              name="idea"
              value={idea}
              onChange={e => setIdea(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit(e as unknown as React.FormEvent) }}
              rows={4}
              required
              minLength={20}
              placeholder="One or two sentences. What is the business, who buys from it, and where. English or Hebrew."
              className="textarea"
              dir="auto"
              aria-describedby="idea-help idea-count"
            />
            <div className="flex items-center justify-between mt-1.5">
              <span id="idea-help" className="field-help">
                20 characters or more. The more specific, the better the plan.
              </span>
              <span
                id="idea-count"
                className={'text-[12px] tabular-nums ' + (ideaLen >= 20 ? 'text-slate-500' : 'text-slate-400')}
                aria-live="polite"
              >
                {ideaLen} / 20
              </span>
            </div>

            {/* Example chips */}
            <div className="mt-3 flex flex-wrap gap-2" role="group" aria-label="Example ideas">
              {EXAMPLES.map(ex => (
                <button
                  key={ex.label}
                  type="button"
                  onClick={() => setIdea(ex.text)}
                  className="text-[13px] px-3 py-1.5 rounded-full border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
                >
                  {ex.label}
                </button>
              ))}
            </div>
          </div>

          <hr className="my-6 border-slate-100 dark:border-slate-800" />

          {/* Business model */}
          <fieldset className="field">
            <legend className="field-label">Who are your customers?</legend>
            <div className="choice-grid mt-1" role="radiogroup" aria-labelledby="model-help">
              {BIZ_MODELS.map(opt => (
                <label key={opt.value} className="choice">
                  <input
                    type="radio" name="model" value={opt.value}
                    checked={model === opt.value}
                    onChange={() => setModel(opt.value)}
                  />
                  <div className="choice-body">
                    <div className="choice-title">{opt.title}</div>
                    <div className="choice-sub">{opt.sub}</div>
                  </div>
                </label>
              ))}
            </div>
            <span id="model-help" className="field-help">Pick the closest match — you can refine later.</span>
          </fieldset>

          {/* Market */}
          <fieldset className="field mt-5">
            <legend className="field-label">Where will you operate?</legend>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mt-1" role="radiogroup">
              {MARKETS.map(opt => (
                <label key={opt.value} className="choice">
                  <input
                    type="radio" name="market" value={opt.value}
                    checked={market === opt.value}
                    onChange={() => setMarket(opt.value)}
                  />
                  <div className="choice-body">
                    <div className="choice-title">{opt.title}</div>
                    <div className="choice-sub">{opt.sub}</div>
                  </div>
                </label>
              ))}
            </div>
          </fieldset>

          {/* Stage */}
          <fieldset className="field mt-5">
            <legend className="field-label">Where are you today?</legend>
            <div className="choice-grid mt-1" role="radiogroup">
              {STAGES.map(opt => (
                <label key={opt.value} className="choice">
                  <input
                    type="radio" name="stage" value={opt.value}
                    checked={stage === opt.value}
                    onChange={() => setStage(opt.value)}
                  />
                  <div className="choice-body">
                    <div className="choice-title">{opt.title}</div>
                    <div className="choice-sub">{opt.sub}</div>
                  </div>
                </label>
              ))}
            </div>
          </fieldset>

          {error && (
            <div role="alert" className="mt-5 rounded-lg border border-danger-500/40 bg-danger-500/10 px-3.5 py-2.5 text-[14px] text-danger-700 dark:text-danger-500">
              {error}
            </div>
          )}

          {/* Submit */}
          <div className="mt-7 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
            <button type="submit" disabled={!canSubmit} className="btn-primary btn-lg w-full sm:w-auto">
              {loading ? 'Starting agents…' : 'Generate my blueprint'}
            </button>
            <span className="text-[13px] text-slate-500 dark:text-slate-400">
              Takes about 2 minutes · Press <kbd className="font-mono text-[11px] px-1.5 py-0.5 border border-slate-300 dark:border-slate-600 rounded">⌘</kbd>
              <span className="mx-1">+</span>
              <kbd className="font-mono text-[11px] px-1.5 py-0.5 border border-slate-300 dark:border-slate-600 rounded">Enter</kbd>
            </span>
          </div>
        </form>

        {/* What you get */}
        <section className="mt-10 animate-fade-in" aria-labelledby="deliverables-heading">
          <h2 id="deliverables-heading" className="text-[13px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-3">
            What you'll get
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {DELIVERABLES.map(d => (
              <div key={d.title} className="card p-4">
                <div className="text-[14px] font-semibold text-slate-900 dark:text-slate-100">{d.title}</div>
                <div className="text-[13px] text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">{d.body}</div>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 dark:border-slate-800 mt-16 py-6">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-[13px] text-slate-500 dark:text-slate-400 flex flex-wrap items-center justify-between gap-2">
          <span>Nine agents · Claude 5.5 · LangGraph</span>
          <span>Hebrew & English supported</span>
        </div>
      </footer>
    </div>
  )
}
