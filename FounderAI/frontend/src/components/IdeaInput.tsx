import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const EXAMPLES = [
  { label: 'Web design agency for SMBs', idea: 'I want to start a web design agency targeting small and medium businesses in Israel.' },
  { label: 'SaaS for restaurant management', idea: 'Building a SaaS platform to help restaurant owners manage orders, staff, and inventory from a single dashboard.' },
  { label: 'E-commerce for handmade jewelry', idea: 'Online store selling handmade jewelry to a global audience, focusing on unique artisan pieces.' },
  { label: 'סוכנות שיווק דיגיטלי', idea: 'אני רוצה להקים סוכנות שיווק דיגיטלי לעסקים קטנים בישראל, כולל ניהול רשתות חברתיות, SEO ופרסום ממומן.' },
]

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function IdeaInput() {
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
    <div className="w-full max-w-2xl mx-auto">
      <textarea
        value={idea}
        onChange={e => setIdea(e.target.value)}
        onKeyDown={e => {
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit()
        }}
        rows={5}
        placeholder="Describe your business idea... (English or Hebrew)&#10;&#10;Press ⌘+Enter to generate your blueprint"
        className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none text-base"
        dir="auto"
      />

      <div className="mt-3 flex flex-wrap gap-2">
        {EXAMPLES.map(ex => (
          <button
            key={ex.label}
            onClick={() => setIdea(ex.idea)}
            className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-gray-200 px-3 py-1.5 rounded-full border border-gray-700 transition-colors"
          >
            {ex.label}
          </button>
        ))}
      </div>

      {error && (
        <p className="mt-3 text-sm text-red-400 bg-red-950/30 border border-red-800 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <button
        onClick={submit}
        disabled={loading || !idea.trim()}
        className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors text-base"
      >
        {loading ? 'Starting agents...' : 'Generate Company Blueprint →'}
      </button>
    </div>
  )
}
