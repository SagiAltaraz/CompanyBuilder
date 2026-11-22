/** Reusable textarea (kept for compat — Dashboard has its own form). */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function IdeaInput() {
  const [idea, setIdea]       = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<string | null>(null)
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
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
      if (!res.ok) throw new Error(await res.text() || 'Server error')
      const data = await res.json()
      navigate(`/blueprint/${data.blueprint_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} className="w-full max-w-2xl mx-auto">
      <label htmlFor="idea-plain" className="field-label">Your business idea</label>
      <textarea
        id="idea-plain"
        value={idea}
        onChange={e => setIdea(e.target.value)}
        rows={4}
        placeholder="One paragraph. English or Hebrew."
        className="textarea"
        dir="auto"
      />
      {error && (
        <p role="alert" className="mt-2 text-[13px] text-danger-700 dark:text-danger-500">{error}</p>
      )}
      <button type="submit" disabled={loading || !idea.trim()} className="mt-4 btn-primary btn-lg">
        {loading ? 'Starting agents…' : 'Generate blueprint'}
      </button>
    </form>
  )
}
