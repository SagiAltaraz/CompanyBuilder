import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const EXAMPLES = [
  { emoji: '☕', label: 'Coffee cart in Tel Aviv', idea: 'I want to open a mobile coffee cart business in Tel Aviv targeting office workers and tourist areas.' },
  { emoji: '💻', label: 'Web design agency',       idea: 'A web design agency for small and medium businesses in Israel — websites, landing pages, SEO.' },
  { emoji: '🍕', label: 'SaaS for restaurants',    idea: 'SaaS platform for restaurant management — orders, staff scheduling, inventory, and loyalty program.' },
  { emoji: '💍', label: 'Handmade jewelry store',  idea: 'Online store selling handmade jewelry to a global audience, focusing on unique artisan pieces.' },
  { emoji: '📱', label: 'סוכנות שיווק דיגיטלי',     idea: 'אני רוצה להקים סוכנות שיווק דיגיטלי לעסקים קטנים בישראל, כולל ניהול רשתות חברתיות, SEO ופרסום ממומן.' },
]

const FEATURES = [
  { icon: '📊', title: 'Market Research',  desc: 'TAM/SAM/SOM, top competitors, positioning gaps.' },
  { icon: '📍', title: 'Location Strategy', desc: 'Best neighborhoods, rent ₪/sqm, demand mapping.' },
  { icon: '💰', title: 'Financial Plan',    desc: 'Burn rate, runway, grants, funding paths.' },
  { icon: '🇮🇱', title: 'Israel-Aware',      desc: 'Innovation Authority, Tnufa, VAT, osek murshe.' },
]

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function Dashboard() {
  const [idea, setIdea] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const submit = async () => {
    const trimmed = idea.trim()
    if (!trimmed) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/blueprints`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea: trimmed }),
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      navigate(`/blueprint/${data.blueprint_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen bg-mesh flex flex-col overflow-hidden">
      {/* Decorative blueprint grid overlay */}
      <div className="absolute inset-0 bg-blueprint opacity-60 pointer-events-none" />

      {/* Animated gradient blobs */}
      <div className="blob bg-brand-300 w-[420px] h-[420px] -top-32 -left-32 animate-blob-slow" />
      <div className="blob bg-gold-400/60 w-[360px] h-[360px] top-24 -right-24 animate-blob-slower" />
      <div className="blob bg-brand-500/40 w-[480px] h-[480px] bottom-[-160px] left-1/3 animate-blob-slow" />

      {/* ── Header ── */}
      <header className="relative z-10 px-8 py-4 flex items-center justify-between backdrop-blur-md bg-white/60 border-b border-white/40">
        <div className="flex items-center gap-3">
          <div className="brand-mark">F</div>
          <div className="leading-tight">
            <div className="font-display font-extrabold text-ink text-lg tracking-tight">FounderAI</div>
            <div className="text-[11px] text-slate-500 font-medium tracking-wide uppercase hidden sm:block">
              AI Strategic Co-Founder
            </div>
          </div>
        </div>
        <a
          href="https://github.com/sagialtaraz/CompanyBuilder"
          target="_blank"
          rel="noreferrer"
          className="btn-ghost"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.52-1.32-1.28-1.67-1.28-1.67-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.71 1.26 3.37.96.1-.75.4-1.26.74-1.55-2.55-.29-5.24-1.28-5.24-5.7 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.47.11-3.07 0 0 .97-.31 3.18 1.18a11.05 11.05 0 0 1 5.78 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.6.23 2.78.11 3.07.74.81 1.19 1.84 1.19 3.1 0 4.43-2.69 5.41-5.26 5.69.41.36.77 1.05.77 2.13v3.15c0 .31.21.66.8.55C20.21 21.39 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5z"/></svg>
          GitHub
        </a>
      </header>

      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 py-16">
        {/* ── Hero ── */}
        <div className="max-w-2xl w-full text-center mb-10 animate-fade-up">
          <div className="chip-gold mb-5">
            <span className="w-1.5 h-1.5 bg-gold-500 rounded-full animate-pulse" />
            8 AI Agents · Parallel Analysis · Hebrew &amp; English
          </div>
          <h1 className="font-display text-5xl sm:text-6xl font-extrabold text-ink mb-5 leading-[1.05] tracking-tight">
            From idea to{' '}
            <span className="text-gradient">company blueprint</span>
            <br className="hidden sm:block" />
            <span className="text-ink-soft font-bold"> in minutes.</span>
          </h1>
          <p className="text-lg text-slate-500 max-w-xl mx-auto leading-relaxed">
            Describe any business idea. Eight specialized AI agents deliver market research,
            legal setup, location strategy, financials, and a 12-month roadmap — built for Israeli founders.
          </p>
        </div>

        {/* ── Input card ── */}
        <div className="w-full max-w-2xl animate-fade-up" style={{ animationDelay: '0.08s' }}>
          <div className="card-highlight p-6 sm:p-7">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Your business idea
            </label>
            <textarea
              value={idea}
              onChange={e => setIdea(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit() }}
              rows={4}
              placeholder="Example: I want to open a coffee cart in Tel Aviv targeting tech workers near Rothschild…"
              className="w-full bg-slate-50/60 border border-slate-200 rounded-xl px-4 py-3 text-ink placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/60 focus:border-transparent focus:bg-white resize-none text-sm transition-all"
              dir="auto"
            />

            {/* Examples */}
            <div className="mt-3 flex flex-wrap gap-2">
              {EXAMPLES.map(ex => (
                <button
                  key={ex.label}
                  onClick={() => setIdea(ex.idea)}
                  className="text-xs bg-white hover:bg-brand-50 hover:text-brand-700 text-slate-600 px-3 py-1.5 rounded-full border border-slate-200 hover:border-brand-200 transition-all flex items-center gap-1.5 hover:-translate-y-0.5 hover:shadow-sm"
                >
                  <span>{ex.emoji}</span>
                  {ex.label}
                </button>
              ))}
            </div>

            {error && (
              <p className="mt-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              onClick={submit}
              disabled={loading || !idea.trim()}
              className="mt-5 w-full btn-primary py-3.5 text-base disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Starting analysis…
                </>
              ) : (
                <>
                  Generate Company Blueprint
                  <span aria-hidden>→</span>
                </>
              )}
            </button>
            <p className="text-center text-xs text-slate-400 mt-3">
              <kbd className="font-mono bg-slate-100 border border-slate-200 rounded px-1.5 py-0.5 text-[10px]">⌘</kbd>
              {' '}+{' '}
              <kbd className="font-mono bg-slate-100 border border-slate-200 rounded px-1.5 py-0.5 text-[10px]">Enter</kbd>
              {' '}to submit · Hebrew &amp; English supported
            </p>
          </div>
        </div>

        {/* ── Feature grid ── */}
        <div className="mt-14 grid grid-cols-2 lg:grid-cols-4 gap-3 max-w-3xl w-full animate-fade-up" style={{ animationDelay: '0.16s' }}>
          {FEATURES.map(f => (
            <div
              key={f.title}
              className="group bg-white/80 backdrop-blur border border-slate-200/70 rounded-2xl p-4 shadow-sm hover:shadow-lift hover:-translate-y-0.5 transition-all"
            >
              <div className="text-2xl mb-2 group-hover:scale-110 transition-transform inline-block">{f.icon}</div>
              <div className="font-display font-bold text-ink text-sm mb-1">{f.title}</div>
              <div className="text-slate-500 text-xs leading-relaxed">{f.desc}</div>
            </div>
          ))}
        </div>
      </main>

      <footer className="relative z-10 text-center py-6 text-xs text-slate-400">
        <span className="inline-flex items-center gap-1.5">
          <span className="w-1 h-1 rounded-full bg-brand-400" />
          Powered by GPT-4o &amp; LangGraph
          <span className="w-1 h-1 rounded-full bg-brand-400" />
          Full strategic analysis in 2–4 minutes
          <span className="w-1 h-1 rounded-full bg-brand-400" />
        </span>
      </footer>
    </div>
  )
}
