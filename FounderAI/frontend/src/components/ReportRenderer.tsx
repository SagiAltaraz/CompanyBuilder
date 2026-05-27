import React, { useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Props {
  content: string
  isFinalReport?: boolean
}

export default function ReportRenderer({ content, isFinalReport = false }: Props) {
  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(content)
  }, [content])

  const handlePrint = useCallback(() => {
    window.print()
  }, [])

  return (
    <div>
      {isFinalReport && (
        <div className="flex gap-2 mb-5 no-print">
          <button onClick={handleCopy} className="btn-secondary flex items-center gap-1.5">
            <span>📋</span> Copy Markdown
          </button>
          <button onClick={handlePrint} className="btn-primary flex items-center gap-1.5">
            <span>📄</span> Download PDF
          </button>
        </div>
      )}
      <div className="prose max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>
    </div>
  )
}
