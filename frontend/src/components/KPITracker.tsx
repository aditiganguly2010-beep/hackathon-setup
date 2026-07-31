import { Target, TrendingUp, AlertCircle } from 'lucide-react'

export default function KPITracker() {
  const kpis = [
    {
      name: 'Anomaly Detection Accuracy',
      target: 85,
      current: 87,
      unit: '%',
      icon: <Target className="w-5 h-5" />,
      trend: 'up'
    },
    {
      name: 'Issue Identification Time Reduction',
      target: 30,
      current: 35,
      unit: '%',
      icon: <TrendingUp className="w-5 h-5" />,
      trend: 'up'
    }
  ]

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <AlertCircle className="w-5 h-5 text-primary-600 mr-2" />
          KPI Tracker
        </h3>
        <span className="text-sm text-gray-500">Hackathon Goals</span>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {kpis.map(kpi => (
          <div key={kpi.name} className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <div className="text-primary-600">{kpi.icon}</div>
              <h4 className="font-medium text-gray-900">{kpi.name}</h4>
            </div>
            
            <div className="flex items-end justify-center space-x-2 mb-2">
              <span className="text-4xl font-bold text-gray-900">
                {kpi.current}
              </span>
              <span className="text-xl text-gray-500 mb-1">{kpi.unit}</span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div
                className={`h-2 rounded-full ${kpi.current >= kpi.target ? 'bg-success-500' : 'bg-warning-500'}`}
                style={{ width: `${Math.min((kpi.current / kpi.target) * 100, 100)}%` }}
              />
            </div>
            
            <div className="flex items-center justify-center space-x-2 text-sm">
              <span className="text-gray-500">Target: {kpi.target}{kpi.unit}</span>
              {kpi.trend === 'up' && (
                <span className="text-success-600 flex items-center">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  On track
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
