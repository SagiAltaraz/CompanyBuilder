import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const EXAMPLES = [
  { emoji: '☕', label: 'Coffee cart in Tel Aviv', idea: 'I want to open a mobile coffee cart business in Tel Aviv targeting office workers and tourist areas.' },
  { emoji: '💻', label: 'Web design agency', idea: 'A web design agency for small and medium businesses in Israel — websites, landing pages, SEO.' },
  { emoji: '🍕', label: 'SaaS for restaurants', idea: 'SaaS platform for restaurant management — orders, staff scheduling, inventory, and loyalty program.' },
  { emoji: '💍', label: 'Handmade jewelry store', idea: 'Online store selling handmade jewelry to a global audience, focusing on unique artisan pieces.' },
  { emoji: '📱', label: 'סוכנות שיווק דיגיטלי', idea: 'אני רוצה להקים סוכנות שיווק דיגיטלי לעסקים קטנים בישראל, כולל ניהול רשתות חברתיות, SEO ופרסום ממומן.' },
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
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex flex-col">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur border-b border-gray-100 px-8 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
          F
        </div>
        <span className="font-bold text-gray-900 text-lg">FounderAI</span>
        <span className="text-gray-400 text-sm hidden sm:block">— Strategic Business Advisor</span>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        {/* Hero */}
        <div className="max-w-2xl w-full text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-indigo-100 text-indigo-700 text-xs font-semibold px-3 py-1.5 rounded-full mb-5">
            <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full" />
            7 AI Agents · Parallel Analysis · Hebrew & English
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-4 leading-tight tracking-tight">
            Your AI{' '}
            <span className="text-indigo-600">Strategic Advisor</span>
          </h1>
          <p className="text-lg text-gray-500 max-w-xl mx-auto leading-relaxed">
            Describe any business idea. Get a full company blueprint in minutes —
            market research, legal setup, team plan, financial projections, and a 12-month roadmap.
          </p>
        </div>

        {/* Input card */}
        <div className="w-full max-w-2xl">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Describe your business idea
            </label>
            <textarea
              value={idea}
              onChange={e => setIdea(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit() }}
              rows={4}
              placeholder="Example: I want to open a coffee cart in Tel Aviv targeting office workers..."
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none text-sm transition-all"
              dir="auto"
            />

            {/* Examples */}
            <div className="mt-3 flex flex-wrap gap-2">
              {EXAMPLES.map(ex => (
                <button
                  key={ex.label}
                  onClick={() => setIdea(ex.idea)}
                  className="text-xs bg-gray-50 hover:bg-indigo-50 hover:text-indigo-700 text-gray-600 px-3 py-1.5 rounded-full border border-gray-200 hover:border-indigo-200 transition-all flex items-center gap-1"
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
              className="mt-4 w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors text-sm flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Starting analysis...
                </>
              ) : (
                <>Generate Company Blueprint →</>
              )}
            </button>
            <p className="text-center text-xs text-gray-400 mt-2">⌘+Enter to submit · Hebrew & English supported</p>
          </div>
        </div>

        {/* Feature grid */}
        <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl w-full">
          {[
            { icon: '📊', title: 'Market Research', desc: 'TAM/SAM/SOM, top competitors, positioning opportunities.' },
            { icon: '💰', title: 'Financial Plan', desc: 'Monthly burn, runway calculator, grants, funding paths.' },
            { icon: '🇮🇱', title: 'Israel-Aware', desc: 'Innovation Authority grants, Tnufa, VAT rules, osek murshe.' },
          ].map(f => (
            <div key={f.title} className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
              <div className="text-2xl mb-2">{f.icon}</div>
              <div className="font-semibold text-gray-800 text-sm mb-1">{f.title}</div>
              <div className="text-gray-500 text-xs leading-relaxed">{f.desc}</div>
            </div>
          ))}
        </div>
      </main>

      <footer className="text-center py-5 text-xs text-gray-400">
        FounderAI · Powered by GPT-4o + LangGraph · Strategic analysis in 2–4 minutes
      </footer>
    </div>
  )
}
