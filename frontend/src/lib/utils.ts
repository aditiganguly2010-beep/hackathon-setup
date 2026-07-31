import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString()
}

export function formatRelativeTime(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}

export function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'text-danger-600 bg-danger-50'
    case 'high':
      return 'text-warning-600 bg-warning-50'
    case 'medium':
      return 'text-primary-600 bg-primary-50'
    case 'low':
      return 'text-success-600 bg-success-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

export function getHealthScoreColor(score: number): string {
  if (score >= 80) return 'text-success-600'
  if (score >= 60) return 'text-warning-600'
  return 'text-danger-600'
}

export function getHealthScoreBgColor(score: number): string {
  if (score >= 80) return 'bg-success-500'
  if (score >= 60) return 'bg-warning-500'
  return 'bg-danger-500'
}
