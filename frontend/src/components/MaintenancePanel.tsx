import { Wrench, Clock, CheckCircle } from 'lucide-react'
import { MaintenanceAction } from '../lib/api'
import { formatRelativeTime } from '../lib/utils'
import api from '../lib/api'

interface MaintenancePanelProps {
  actions: MaintenanceAction[]
  onRefresh: () => void
}

export default function MaintenancePanel({ actions, onRefresh }: MaintenancePanelProps) {
  const handleStatusUpdate = async (actionId: number, status: string) => {
    try {
      await api.updateActionStatus(actionId, status)
      onRefresh()
    } catch (error) {
      console.error('Failed to update action status:', error)
    }
  }

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1: return 'text-danger-600 bg-danger-50'
      case 2: return 'text-warning-600 bg-warning-50'
      case 3: return 'text-primary-600 bg-primary-50'
      case 4: return 'text-gray-600 bg-gray-100'
      case 5: return 'text-gray-500 bg-gray-50'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'text-success-600'
      case 'in progress': return 'text-primary-600'
      case 'scheduled': return 'text-warning-600'
      default: return 'text-gray-600'
    }
  }

  const sortedActions = [...actions].sort((a, b) => a.priority - b.priority)

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Wrench className="w-5 h-5 text-primary-600 mr-2" />
          Maintenance Actions
        </h3>
        <span className="text-sm text-gray-500">{actions.length} pending</span>
      </div>

      {sortedActions.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CheckCircle className="w-12 h-12 mx-auto text-success-500 mb-2" />
          <p>No pending actions</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {sortedActions.map(action => (
            <div
              key={action.id}
              className={`p-4 rounded-lg border ${
                action.status === 'Completed' ? 'bg-gray-50 border-gray-200' : 'bg-white border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(action.priority)}`}>
                    P{action.priority}
                  </span>
                  <span className={`text-xs font-medium ${getStatusColor(action.status)}`}>
                    {action.status}
                  </span>
                </div>
                {action.estimated_effort && (
                  <div className="flex items-center text-xs text-gray-500">
                    <Clock className="w-3 h-3 mr-1" />
                    {action.estimated_effort}
                  </div>
                )}
              </div>
              
              <h4 className="font-medium text-gray-900 text-sm mb-1">{action.title}</h4>
              <p className="text-xs text-gray-600 mb-2">{action.description}</p>
              
              {action.due_date && (
                <p className="text-xs text-gray-500">
                  Due: {formatRelativeTime(action.due_date)}
                </p>
              )}

              {action.status !== 'Completed' && (
                <div className="mt-3 flex space-x-2">
                  <button
                    onClick={() => handleStatusUpdate(action.id, 'In Progress')}
                    className="text-xs px-2 py-1 bg-primary-100 text-primary-700 rounded hover:bg-primary-200"
                  >
                    Start
                  </button>
                  <button
                    onClick={() => handleStatusUpdate(action.id, 'Completed')}
                    className="text-xs px-2 py-1 bg-success-100 text-success-700 rounded hover:bg-success-200"
                  >
                    Complete
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
