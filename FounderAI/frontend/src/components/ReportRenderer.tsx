/**
 * ReportRenderer — markdown → prose, with copy + print for the final report.
 */
import { useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Props {
  content: string
  isFinalReport?: boolean
}

export default function ReportRenderer({ content, isFinalReport = false }: Props) {
  const handleCopy  = useCallback(() => { navigator.clipboard.writeText(content) }, [content])
  const handlePrint = useCallback(() => { window.print() }, [])

  return (
    <div>
      <div className="prose max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </div>
      {isFinalReport && (
        <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-800 flex flex-wrap gap-2 no-print">
          <button type="button" onClick={handleCopy}  className="btn-secondary">
            Copy markdown
          </button>
          <button type="button" onClick={handlePrint} className="btn-secondary">
            Print or save PDF
          </button>
        </div>
      )}
    </div>
  )
}
