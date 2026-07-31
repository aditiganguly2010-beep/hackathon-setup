import { describe, it, expect } from 'vitest'
import { api } from '../lib/api'

describe('API Client', () => {
  describe('API Functions', () => {
    it('should have getHealthScores function', () => {
      expect(typeof api.getHealthScores).toBe('function')
    })

    it('should have getAnomalies function', () => {
      expect(typeof api.getAnomalies).toBe('function')
    })

    it('should have getMetrics function', () => {
      expect(typeof api.getMetrics).toBe('function')
    })

    it('should have getSystemSummary function', () => {
      expect(typeof api.getSystemSummary).toBe('function')
    })

    it('should have getMaintenanceActions function', () => {
      expect(typeof api.getMaintenanceActions).toBe('function')
    })

    it('should have acknowledgeAnomaly function', () => {
      expect(typeof api.acknowledgeAnomaly).toBe('function')
    })

    it('should have markFalsePositive function', () => {
      expect(typeof api.markFalsePositive).toBe('function')
    })

    it('should have updateActionStatus function', () => {
      expect(typeof api.updateActionStatus).toBe('function')
    })
  })
})
