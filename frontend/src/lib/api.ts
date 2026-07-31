import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface SystemLog {
  id: number
  source_system: string
  log_level: string
  message: string
  timestamp: string
  created_at: string
}

export interface PerformanceMetric {
  id: number
  source_system: string
  metric_type: string
  metric_value: number
  unit: string
  timestamp: string
  created_at: string
}

export interface Anomaly {
  id: number
  source_system: string
  anomaly_type: string
  severity: string
  confidence_score: number
  description: string
  detected_at: string
  acknowledged: boolean
  is_false_positive: boolean
}

export interface HealthScore {
  id: number
  source_system: string
  overall_score: number
  cpu_score: number
  memory_score: number
  disk_score: number
  network_score: number
  log_anomaly_score: number
  calculated_at: string
  trend: string
}

export interface MaintenanceAction {
  id: number
  source_system: string
  action_type: string
  priority: number
  title: string
  description: string
  estimated_effort: string
  status: string
  due_date: string
  completed_at: string | null
}

export interface SystemSummary {
  source_system: string
  generated_at: string
  summary: string
  status: string
  key_issues: string[]
  recommendations: string[]
  health_score: number
  trend: string
}

// API Functions
export const api = {
  // Health
  getHealth: () => apiClient.get('/health'),
  
  // Logs
  getLogs: (params?: { source_system?: string; log_level?: string; limit?: number }) =>
    apiClient.get<SystemLog[]>('/logs', { params }),
  getRecentLogs: (source_system: string, hours: number = 24, limit: number = 50) =>
    apiClient.get<SystemLog[]>(`/logs/recent?source_system=${source_system}&hours=${hours}&limit=${limit}`),
  
  // Metrics
  getMetrics: (params?: { source_system?: string; metric_type?: string; limit?: number }) =>
    apiClient.get<PerformanceMetric[]>('/metrics', { params }),
  getAggregatedMetrics: (source_system: string, metric_type: string, hours: number = 24) =>
    apiClient.get(`/metrics/aggregate?source_system=${source_system}&metric_type=${metric_type}&hours=${hours}`),
  
  // Anomalies
  getAnomalies: (params?: { source_system?: string; severity?: string; limit?: number }) =>
    apiClient.get<Anomaly[]>('/anomalies', { params }),
  detectAnomalies: (source_system: string, hours: number = 24) =>
    apiClient.post(`/anomalies/detect?source_system=${source_system}&hours=${hours}`),
  acknowledgeAnomaly: (anomalyId: number) =>
    apiClient.put(`/anomalies/${anomalyId}/acknowledge`),
  markFalsePositive: (anomalyId: number) =>
    apiClient.put(`/anomalies/${anomalyId}/false-positive`),
  
  // Health Scores
  getHealthScores: () => apiClient.get<HealthScore[]>('/health-scores'),
  getHealthScore: (source_system: string) =>
    apiClient.get<HealthScore>(`/health-scores/${source_system}`),
  calculateHealthScore: (source_system: string, hours: number = 24) =>
    apiClient.post(`/health-scores/calculate?source_system=${source_system}&hours=${hours}`),
  
  // Maintenance Actions
  getMaintenanceActions: (params?: { source_system?: string; status?: string; limit?: number }) =>
    apiClient.get<MaintenanceAction[]>('/maintenance-actions', { params }),
  generateMaintenanceActions: (source_system: string, hours: number = 24) =>
    apiClient.post(`/maintenance-actions/generate?source_system=${source_system}&hours=${hours}`),
  updateActionStatus: (actionId: number, status: string) =>
    apiClient.put(`/maintenance-actions/${actionId}/status?status=${status}`),
  
  // Summaries
  getSystemSummary: (source_system: string, hours: number = 24) =>
    apiClient.get<SystemSummary>(`/summaries/system?source_system=${source_system}&hours=${hours}`),
}

export default api
