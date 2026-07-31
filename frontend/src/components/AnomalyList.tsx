import { AlertTriangle, CheckCircle, X } from 'lucide-react'
import { Anomaly } from '../lib/api'
import { getSeverityColor, formatRelativeTime } from '../lib/utils'
import api from '../lib/api'

interface AnomalyListProps {
  anomalies: Anomaly[]
  onRefresh: () => void
}

export default function AnomalyList({ anomalies, onRefresh }: AnomalyListProps) {
  const handleAcknowledge = async (anomalyId: number) => {
    try {
      await api.acknowledgeAnomaly(anomalyId)
      onRefresh()
    } catch (error) {
      console.error('Failed to acknowledge anomaly:', error)
    }
  }

  const handleFalsePositive = async (anomalyId: number) => {
    try {
      await api.markFalsePositive(anomalyId)
      onRefresh()
    } catch (error) {
      console.error('Failed to mark as false positive:', error)
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <AlertTriangle className="w-5 h-5 text-warning-600 mr-2" />
          Detected Anomalies
        </h3>
        <span className="text-sm text-gray-500">{anomalies.length} found</span>
      </div>

      {anomalies.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CheckCircle className="w-12 h-12 mx-auto text-success-500 mb-2" />
          <p>No anomalies detected</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {anomalies.map(anomaly => (
            <div
              key={anomaly.id}
              className={`p-4 rounded-lg border ${
                anomaly.acknowledged ? 'bg-gray-50 border-gray-200' : 'bg-white border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(anomaly.severity)}`}>
                      {anomaly.severity}
                    </span>
                    <span className="text-sm text-gray-500">{anomaly.anomaly_type}</span>
                  </div>
                  <p className="text-sm text-gray-900 mb-2">{anomaly.description}</p>
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span>Confidence: {(anomaly.confidence_score * 100).toFixed(0)}%</span>
                    <span>{formatRelativeTime(anomaly.detected_at)}</span>
                  </div>
                </div>
                {!anomaly.acknowledged && (
                  <div className="flex space-x-2 ml-4">
                    <button
                      onClick={() => handleAcknowledge(anomaly.id)}
                      className="p-2 text-success-600 hover:bg-success-50 rounded"
                      title="Acknowledge"
                    >
                      <CheckCircle className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleFalsePositive(anomaly.id)}
                      className="p-2 text-gray-600 hover:bg-gray-100 rounded"
                      title="Mark as false positive"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
