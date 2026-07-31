import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { Activity, AlertTriangle, CheckCircle, TrendingUp, Download } from 'lucide-react'
import api, { HealthScore, Anomaly, SystemSummary, MaintenanceAction } from '../lib/api'
import { getHealthScoreColor, getHealthScoreBgColor, formatRelativeTime } from '../lib/utils'
import HealthGauge from './HealthGauge'
import MetricsPanel from './MetricsPanel'
import AnomalyList from './AnomalyList'
import SummaryPanel from './SummaryPanel'
import MaintenancePanel from './MaintenancePanel'
import KPITracker from './KPITracker'

const SOURCE_SYSTEMS = ['legacy-crm', 'legacy-erp', 'legacy-inventory', 'legacy-payroll', 'legacy-hris']

export default function Dashboard() {
  const [selectedSystem, setSelectedSystem] = useState(SOURCE_SYSTEMS[0])
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Fetch health scores
  const { data: healthScores, refetch: refetchHealthScores } = useQuery(
    'healthScores',
    () => api.getHealthScores().then(res => res.data),
    { refetchInterval: autoRefresh ? 30000 : false }
  )

  // Fetch anomalies
  const { data: anomalies, refetch: refetchAnomalies } = useQuery(
    ['anomalies', selectedSystem],
    () => api.getAnomalies({ source_system: selectedSystem, limit: 10 }).then(res => res.data),
    { refetchInterval: autoRefresh ? 30000 : false }
  )

  // Fetch system summary
  const { data: summary, refetch: refetchSummary } = useQuery(
    ['summary', selectedSystem],
    () => api.getSystemSummary(selectedSystem).then(res => res.data),
    { refetchInterval: autoRefresh ? 60000 : false }
  )

  // Fetch maintenance actions
  const { data: maintenanceActions, refetch: refetchActions } = useQuery(
    ['maintenance', selectedSystem],
    () => api.getMaintenanceActions({ source_system: selectedSystem, limit: 10 }).then(res => res.data),
    { refetchInterval: autoRefresh ? 60000 : false }
  )

  const selectedHealthScore = healthScores?.find(h => h.source_system === selectedSystem)

  const handleExportReport = () => {
    // TODO: Implement report export
    console.log('Exporting report for', selectedSystem)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Activity className="w-8 h-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">Legacy System Health Monitor</h1>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedSystem}
                onChange={(e) => setSelectedSystem(e.target.value)}
                className="input"
              >
                {SOURCE_SYSTEMS.map(system => (
                  <option key={system} value={system}>
                    {system.replace('-', ' ').toUpperCase()}
                  </option>
                ))}
              </select>
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`btn ${autoRefresh ? 'btn-primary' : 'btn-secondary'}`}
              >
                {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
              </button>
              <button
                onClick={handleExportReport}
                className="btn btn-secondary flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export Report</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        {/* Health Score Header */}
        {selectedHealthScore && (
          <div className="mb-6">
            <div className="card">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                  <HealthGauge score={selectedHealthScore.overall_score} />
                  <div>
                    <h2 className="text-3xl font-bold text-gray-900">
                      {selectedHealthScore.source_system.replace('-', ' ').toUpperCase()}
                    </h2>
                    <p className="text-gray-600 mt-1">
                      Overall Health Score: <span className={`font-bold ${getHealthScoreColor(selectedHealthScore.overall_score)}`}>
                        {selectedHealthScore.overall_score}/100
                      </span>
                    </p>
                    <div className="flex items-center space-x-2 mt-2">
                      {selectedHealthScore.trend === 'Stable' ? (
                        <CheckCircle className="w-5 h-5 text-success-600" />
                      ) : (
                        <TrendingUp className="w-5 h-5 text-warning-600" />
                      )}
                      <span className={`font-medium ${selectedHealthScore.trend === 'Stable' ? 'text-success-600' : 'text-warning-600'}`}>
                        {selectedHealthScore.trend}
                      </span>
                      <span className="text-gray-500">• Last updated {formatRelativeTime(selectedHealthScore.calculated_at)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex space-x-8">
                  <div className="text-center">
                    <p className="text-sm text-gray-500">CPU</p>
                    <p className={`text-2xl font-bold ${getHealthScoreColor(selectedHealthScore.cpu_score || 0)}`}>
                      {selectedHealthScore.cpu_score || 0}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-500">Memory</p>
                    <p className={`text-2xl font-bold ${getHealthScoreColor(selectedHealthScore.memory_score || 0)}`}>
                      {selectedHealthScore.memory_score || 0}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-500">Disk</p>
                    <p className={`text-2xl font-bold ${getHealthScoreColor(selectedHealthScore.disk_score || 0)}`}>
                      {selectedHealthScore.disk_score || 0}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-500">Network</p>
                    <p className={`text-2xl font-bold ${getHealthScoreColor(selectedHealthScore.network_score || 0)}`}>
                      {selectedHealthScore.network_score || 0}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Dashboard Grid */}
        <div className="grid grid-cols-12 gap-6">
          {/* Left Panel - Metrics */}
          <div className="col-span-3">
            <MetricsPanel sourceSystem={selectedSystem} />
          </div>

          {/* Center Panel - Anomalies & Summary */}
          <div className="col-span-6 space-y-6">
            <AnomalyList anomalies={anomalies || []} onRefresh={refetchAnomalies} />
            {summary && <SummaryPanel summary={summary} onRefresh={refetchSummary} />}
          </div>

          {/* Right Panel - Maintenance Actions */}
          <div className="col-span-3">
            <MaintenancePanel actions={maintenanceActions || []} onRefresh={refetchActions} />
          </div>
        </div>

        {/* Bottom Panel - KPI Tracker */}
        <div className="mt-6">
          <KPITracker />
        </div>
      </main>
    </div>
  )
}
