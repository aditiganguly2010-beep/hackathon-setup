import { Sparkles } from 'lucide-react'
import { SystemSummary } from '../lib/api'
import { formatRelativeTime } from '../lib/utils'

interface SummaryPanelProps {
  summary: SystemSummary
  onRefresh: () => void
}

export default function SummaryPanel({ summary, onRefresh }: SummaryPanelProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy': return 'text-success-600 bg-success-50'
      case 'degraded': return 'text-warning-600 bg-warning-50'
      case 'critical': return 'text-danger-600 bg-danger-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Sparkles className="w-5 h-5 text-primary-600 mr-2" />
          AI System Summary
        </h3>
        <button
          onClick={onRefresh}
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          Refresh
        </button>
      </div>

      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(summary.status)}`}>
            {summary.status.toUpperCase()}
          </span>
          <span className="text-sm text-gray-500">
            Generated {formatRelativeTime(summary.generated_at)}
          </span>
        </div>

        <p className="text-gray-700 leading-relaxed">{summary.summary}</p>

        {summary.key_issues && summary.key_issues.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Key Issues</h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
              {summary.key_issues.map((issue, index) => (
                <li key={index}>{issue}</li>
              ))}
            </ul>
          </div>
        )}

        {summary.recommendations && summary.recommendations.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Recommendations</h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
              {summary.recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
