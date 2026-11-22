/**
 * ChatPanel — ask follow-up questions once the blueprint is ready.
 * Plain, accessible chat UI: labeled input, button with loading state,
 * screen-reader-announced new answers.
 */
import { useEffect, useRef, useState } from 'react'

interface Props {
  blueprintId: string
}

interface Exchange {
  q: string
  a: string | null
}

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function ChatPanel({ blueprintId }: Props) {
  const [input, setInput]     = useState('')
  const [history, setHistory] = useState<Exchange[]>([])
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [history])

  const send = async (e?: React.FormEvent) => {
    e?.preventDefault()
    const message = input.trim()
    if (!message || loading) return
    setLoading(true)
    setHistory(h => [...h, { q: message, a: null }])
    setInput('')
    try {
      const res = await fetch(`${API_BASE}/blueprints/${blueprintId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      })
      const data = await res.json()
      const answer = data.answer ?? data.detail ?? 'No answer.'
      setHistory(h => {
        const copy = [...h]
        copy[copy.length - 1] = { q: message, a: answer }
        return copy
      })
    } catch (err) {
      setHistory(h => {
        const copy = [...h]
        copy[copy.length - 1] = { q: message, a: `Error: ${(err as Error).message}` }
        return copy
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <aside className="h-full flex flex-col bg-slate-50 dark:bg-slate-900/50" aria-labelledby="chat-heading">
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
        <h2 id="chat-heading" className="text-[14px] font-semibold text-slate-900 dark:text-slate-100">
          Follow-up questions
        </h2>
        <p className="text-[12px] text-slate-500 dark:text-slate-400 mt-0.5">
          Ask anything about the blueprint.
        </p>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4" aria-live="polite" aria-atomic="false">
        {history.length === 0 && (
          <p className="text-[13px] text-slate-500 dark:text-slate-400 leading-relaxed">
            Examples: <em>"Which licence should I apply for first?"</em> · <em>"What breaks if a competitor cuts prices 20%?"</em>
          </p>
        )}
        {history.map((ex, i) => (
          <div key={i} className="mb-5 animate-fade-in">
            <div className="text-[13px] font-medium text-slate-900 dark:text-slate-100 mb-1.5">
              You
            </div>
            <div className="text-[14px] text-slate-700 dark:text-slate-300 mb-3">
              {ex.q}
            </div>
            <div className="text-[13px] font-medium text-primary-700 dark:text-primary-300 mb-1.5">
              Advisor
            </div>
            <div className="text-[14px] text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
              {ex.a ?? <span className="text-slate-400">Drafting a reply…</span>}
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={send} className="border-t border-slate-200 dark:border-slate-800 p-3">
        <label htmlFor="chat-input" className="sr-only">Your question</label>
        <div className="flex items-end gap-2">
          <textarea
            id="chat-input"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) send()
            }}
            rows={2}
            placeholder="Ask about the blueprint…"
            className="textarea flex-1 text-[14px]"
            dir="auto"
          />
          <button type="submit" disabled={loading || !input.trim()} className="btn-primary">
            {loading ? 'Sending…' : 'Send'}
          </button>
        </div>
      </form>
    </aside>
  )
}
