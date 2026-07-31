import { describe, it, expect } from 'vitest'
import { cn, formatTimestamp, formatRelativeTime, getSeverityColor, getHealthScoreColor, getHealthScoreBgColor } from '../lib/utils'

describe('Utility Functions', () => {
  describe('cn', () => {
    it('should merge class names correctly', () => {
      expect(cn('foo', 'bar')).toBe('foo bar')
      expect(cn('foo', null, 'bar')).toBe('foo bar')
      expect(cn('foo', false, 'bar')).toBe('foo bar')
    })
  })

  describe('formatTimestamp', () => {
    it('should format ISO timestamp to locale string', () => {
      const timestamp = '2024-01-01T12:00:00Z'
      const result = formatTimestamp(timestamp)
      expect(result).toBeTruthy()
      expect(typeof result).toBe('string')
    })
  })

  describe('formatRelativeTime', () => {
    it('should return "Just now" for very recent timestamps', () => {
      const now = new Date()
      const timestamp = new Date(now.getTime() - 10000).toISOString() // 10 seconds ago
      expect(formatRelativeTime(timestamp)).toBe('Just now')
    })

    it('should return minutes ago for recent timestamps', () => {
      const now = new Date()
      const timestamp = new Date(now.getTime() - 5 * 60000).toISOString() // 5 minutes ago
      expect(formatRelativeTime(timestamp)).toBe('5m ago')
    })

    it('should return hours ago for older timestamps', () => {
      const now = new Date()
      const timestamp = new Date(now.getTime() - 3 * 3600000).toISOString() // 3 hours ago
      expect(formatRelativeTime(timestamp)).toBe('3h ago')
    })

    it('should return days ago for old timestamps', () => {
      const now = new Date()
      const timestamp = new Date(now.getTime() - 2 * 86400000).toISOString() // 2 days ago
      expect(formatRelativeTime(timestamp)).toBe('2d ago')
    })
  })

  describe('getSeverityColor', () => {
    it('should return correct color for critical severity', () => {
      expect(getSeverityColor('critical')).toBe('text-danger-600 bg-danger-50')
    })

    it('should return correct color for high severity', () => {
      expect(getSeverityColor('high')).toBe('text-warning-600 bg-warning-50')
    })

    it('should return correct color for medium severity', () => {
      expect(getSeverityColor('medium')).toBe('text-primary-600 bg-primary-50')
    })

    it('should return correct color for low severity', () => {
      expect(getSeverityColor('low')).toBe('text-success-600 bg-success-50')
    })

    it('should return default color for unknown severity', () => {
      expect(getSeverityColor('unknown')).toBe('text-gray-600 bg-gray-50')
    })
  })

  describe('getHealthScoreColor', () => {
    it('should return success color for high health scores', () => {
      expect(getHealthScoreColor(85)).toBe('text-success-600')
      expect(getHealthScoreColor(90)).toBe('text-success-600')
    })

    it('should return warning color for medium health scores', () => {
      expect(getHealthScoreColor(70)).toBe('text-warning-600')
      expect(getHealthScoreColor(60)).toBe('text-warning-600')
    })

    it('should return danger color for low health scores', () => {
      expect(getHealthScoreColor(50)).toBe('text-danger-600')
      expect(getHealthScoreColor(30)).toBe('text-danger-600')
    })
  })

  describe('getHealthScoreBgColor', () => {
    it('should return success background for high health scores', () => {
      expect(getHealthScoreBgColor(85)).toBe('bg-success-500')
    })

    it('should return warning background for medium health scores', () => {
      expect(getHealthScoreBgColor(70)).toBe('bg-warning-500')
    })

    it('should return danger background for low health scores', () => {
      expect(getHealthScoreBgColor(50)).toBe('bg-danger-500')
    })
  })
})
