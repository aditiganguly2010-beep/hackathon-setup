import { useQuery } from 'react-query'
import { Cpu, Memory, HardDrive, Network } from 'lucide-react'
import api, { PerformanceMetric } from '../lib/api'
import { formatRelativeTime } from '../lib/utils'

interface MetricsPanelProps {
  sourceSystem: string
}

export default function MetricsPanel({ sourceSystem }: MetricsPanelProps) {
  const { data: metrics, isLoading } = useQuery(
    ['metrics', sourceSystem],
    () => api.getMetrics({ source_system: sourceSystem, limit: 50 }).then(res => res.data),
    { refetchInterval: 30000 }
  )

  const getIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'cpu': return <Cpu className="w-5 h-5" />
      case 'memory': return <Memory className="w-5 h-5" />
      case 'disk': return <HardDrive className="w-5 h-5" />
      case 'network': return <Network className="w-5 h-5" />
      default: return <Cpu className="w-5 h-5" />
    }
  }

  const getLatestMetric = (type: string) => {
    if (!metrics) return null
    return metrics.filter(m => m.metric_type === type)[0]
  }

  const metricTypes = ['CPU', 'Memory', 'Disk', 'Network']

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
      
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="animate-pulse">
              <div className="h-12 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {metricTypes.map(type => {
            const metric = getLatestMetric(type)
            return (
              <div key={type} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="text-primary-600">
                    {getIcon(type)}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{type}</p>
                    <p className="text-xs text-gray-500">
                      {metric ? formatRelativeTime(metric.timestamp) : 'No data'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-900">
                    {metric ? `${metric.metric_value.toFixed(1)}${metric.unit}` : '--'}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
