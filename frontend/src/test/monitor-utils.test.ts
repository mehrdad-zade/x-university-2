/**
 * Tests for monitoring dashboard utility functions and components
 */
import { describe, it, expect } from 'vitest'

// Test utility functions that would be extracted from MonitorPage
describe('Monitor Utilities', () => {
  describe('formatBytes', () => {
    const formatBytes = (bytes: number): string => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      // Ensure we don't exceed array bounds
      const sizeIndex = Math.min(i, sizes.length - 1)
      return parseFloat((bytes / Math.pow(k, sizeIndex)).toFixed(2)) + ' ' + sizes[sizeIndex]
    }

    it('formats zero bytes correctly', () => {
      expect(formatBytes(0)).toBe('0 B')
    })

    it('formats bytes correctly', () => {
      expect(formatBytes(512)).toBe('512 B')
      expect(formatBytes(1023)).toBe('1023 B')
    })

    it('formats kilobytes correctly', () => {
      expect(formatBytes(1024)).toBe('1 KB')
      expect(formatBytes(1536)).toBe('1.5 KB')
      expect(formatBytes(1048575)).toBe('1024 KB')
    })

    it('formats megabytes correctly', () => {
      expect(formatBytes(1048576)).toBe('1 MB')
      expect(formatBytes(1572864)).toBe('1.5 MB')
    })

    it('formats gigabytes correctly', () => {
      expect(formatBytes(1073741824)).toBe('1 GB')
      expect(formatBytes(1610612736)).toBe('1.5 GB')
    })

    it('formats terabytes correctly', () => {
      expect(formatBytes(1099511627776)).toBe('1 TB')
      expect(formatBytes(1649267441664)).toBe('1.5 TB')
    })

    it('handles very large numbers', () => {
      expect(formatBytes(1125899906842624)).toBe('1 PB')
    })
  })

  describe('formatUptime', () => {
    const formatUptime = (seconds: number): string => {
      const days = Math.floor(seconds / 86400)
      const hours = Math.floor((seconds % 86400) / 3600)
      const mins = Math.floor((seconds % 3600) / 60)
      return `${days}d ${hours}h ${mins}m`
    }

    it('formats seconds correctly', () => {
      expect(formatUptime(0)).toBe('0d 0h 0m')
      expect(formatUptime(59)).toBe('0d 0h 0m')
    })

    it('formats minutes correctly', () => {
      expect(formatUptime(60)).toBe('0d 0h 1m')
      expect(formatUptime(3599)).toBe('0d 0h 59m')
    })

    it('formats hours correctly', () => {
      expect(formatUptime(3600)).toBe('0d 1h 0m')
      expect(formatUptime(7260)).toBe('0d 2h 1m')
      expect(formatUptime(86399)).toBe('0d 23h 59m')
    })

    it('formats days correctly', () => {
      expect(formatUptime(86400)).toBe('1d 0h 0m')
      expect(formatUptime(90000)).toBe('1d 1h 0m')
      expect(formatUptime(180000)).toBe('2d 2h 0m')
    })

    it('handles large uptimes', () => {
      expect(formatUptime(2592000)).toBe('30d 0h 0m')
      expect(formatUptime(31536000)).toBe('365d 0h 0m')
    })
  })

  describe('getStatusColor', () => {
    const getStatusColor = (status: string): string => {
      switch (status.toLowerCase()) {
        case 'healthy':
        case 'running':
          return 'bg-green-100 text-green-800'
        case 'unhealthy':
        case 'exited':
        case 'error':
          return 'bg-red-100 text-red-800'
        case 'starting':
        case 'created':
          return 'bg-yellow-100 text-yellow-800'
        default:
          return 'bg-gray-100 text-gray-800'
      }
    }

    it('returns green classes for healthy status', () => {
      expect(getStatusColor('healthy')).toBe('bg-green-100 text-green-800')
      expect(getStatusColor('running')).toBe('bg-green-100 text-green-800')
      expect(getStatusColor('HEALTHY')).toBe('bg-green-100 text-green-800')
    })

    it('returns red classes for error status', () => {
      expect(getStatusColor('unhealthy')).toBe('bg-red-100 text-red-800')
      expect(getStatusColor('exited')).toBe('bg-red-100 text-red-800')
      expect(getStatusColor('error')).toBe('bg-red-100 text-red-800')
      expect(getStatusColor('ERROR')).toBe('bg-red-100 text-red-800')
    })

    it('returns yellow classes for transitional status', () => {
      expect(getStatusColor('starting')).toBe('bg-yellow-100 text-yellow-800')
      expect(getStatusColor('created')).toBe('bg-yellow-100 text-yellow-800')
      expect(getStatusColor('STARTING')).toBe('bg-yellow-100 text-yellow-800')
    })

    it('returns gray classes for unknown status', () => {
      expect(getStatusColor('unknown')).toBe('bg-gray-100 text-gray-800')
      expect(getStatusColor('custom-status')).toBe('bg-gray-100 text-gray-800')
      expect(getStatusColor('')).toBe('bg-gray-100 text-gray-800')
    })
  })

  describe('getLogLevelColor', () => {
    const getLogLevelColor = (level: string): string => {
      switch (level.toUpperCase()) {
        case 'ERROR':
          return 'text-red-600 bg-red-50'
        case 'WARNING':
        case 'WARN':
          return 'text-yellow-600 bg-yellow-50'
        case 'INFO':
          return 'text-blue-600 bg-blue-50'
        case 'DEBUG':
          return 'text-gray-600 bg-gray-50'
        default:
          return 'text-gray-800 bg-gray-50'
      }
    }

    it('returns red classes for error level', () => {
      expect(getLogLevelColor('ERROR')).toBe('text-red-600 bg-red-50')
      expect(getLogLevelColor('error')).toBe('text-red-600 bg-red-50')
    })

    it('returns yellow classes for warning level', () => {
      expect(getLogLevelColor('WARNING')).toBe('text-yellow-600 bg-yellow-50')
      expect(getLogLevelColor('WARN')).toBe('text-yellow-600 bg-yellow-50')
      expect(getLogLevelColor('warning')).toBe('text-yellow-600 bg-yellow-50')
    })

    it('returns blue classes for info level', () => {
      expect(getLogLevelColor('INFO')).toBe('text-blue-600 bg-blue-50')
      expect(getLogLevelColor('info')).toBe('text-blue-600 bg-blue-50')
    })

    it('returns gray classes for debug level', () => {
      expect(getLogLevelColor('DEBUG')).toBe('text-gray-600 bg-gray-50')
      expect(getLogLevelColor('debug')).toBe('text-gray-600 bg-gray-50')
    })

    it('returns default gray classes for unknown level', () => {
      expect(getLogLevelColor('TRACE')).toBe('text-gray-800 bg-gray-50')
      expect(getLogLevelColor('CUSTOM')).toBe('text-gray-800 bg-gray-50')
      expect(getLogLevelColor('')).toBe('text-gray-800 bg-gray-50')
    })
  })

  describe('getProgressBarColor', () => {
    const getProgressBarColor = (percent: number): string => {
      if (percent < 60) return 'bg-green-500'
      if (percent < 80) return 'bg-yellow-500'
      return 'bg-red-500'
    }

    it('returns green for low usage', () => {
      expect(getProgressBarColor(0)).toBe('bg-green-500')
      expect(getProgressBarColor(30)).toBe('bg-green-500')
      expect(getProgressBarColor(59.9)).toBe('bg-green-500')
    })

    it('returns yellow for medium usage', () => {
      expect(getProgressBarColor(60)).toBe('bg-yellow-500')
      expect(getProgressBarColor(70)).toBe('bg-yellow-500')
      expect(getProgressBarColor(79.9)).toBe('bg-yellow-500')
    })

    it('returns red for high usage', () => {
      expect(getProgressBarColor(80)).toBe('bg-red-500')
      expect(getProgressBarColor(90)).toBe('bg-red-500')
      expect(getProgressBarColor(100)).toBe('bg-red-500')
    })
  })

  describe('validateMonitorData', () => {
    const validateMonitorData = (data: any): boolean => {
      if (!data || typeof data !== 'object') return false
      
      const requiredKeys = ['timestamp', 'system', 'docker', 'services', 'logs']
      for (const key of requiredKeys) {
        if (!(key in data)) return false
      }
      
      // Validate system structure
      if (!data.system?.metrics) return false
      if (!data.system.metrics.cpu) return false
      if (!data.system.metrics.memory) return false
      if (!data.system.metrics.disk) return false
      if (!data.system.metrics.network) return false
      
      // Validate services structure
      if (!data.services?.backend) return false
      
      // Validate logs structure
      if (!Array.isArray(data.logs?.backend)) return false
      if (!Array.isArray(data.logs?.frontend)) return false
      
      return true
    }

    it('validates correct monitor data structure', () => {
      const validData = {
        timestamp: '2025-08-12T22:30:00.000Z',
        system: {
          metrics: {
            cpu: { usage_percent: 25 },
            memory: { usage_percent: 50 },
            disk: { usage_percent: 75 },
            network: { bytes_sent: 1000 }
          }
        },
        docker: { containers: [] },
        services: { backend: { service: 'healthy' } },
        logs: { backend: [], frontend: [] }
      }
      
      expect(validateMonitorData(validData)).toBe(true)
    })

    it('rejects invalid data', () => {
      expect(validateMonitorData(null)).toBe(false)
      expect(validateMonitorData(undefined)).toBe(false)
      expect(validateMonitorData('string')).toBe(false)
      expect(validateMonitorData({})).toBe(false)
      expect(validateMonitorData({ timestamp: '2025-08-12' })).toBe(false)
    })

    it('rejects data missing required keys', () => {
      const incompleteData = {
        timestamp: '2025-08-12T22:30:00.000Z',
        system: { metrics: {} }
        // Missing other required keys
      }
      
      expect(validateMonitorData(incompleteData)).toBe(false)
    })

    it('rejects data with invalid nested structure', () => {
      const invalidData = {
        timestamp: '2025-08-12T22:30:00.000Z',
        system: {}, // Missing metrics
        docker: { containers: [] },
        services: { backend: { service: 'healthy' } },
        logs: { backend: [], frontend: [] }
      }
      
      expect(validateMonitorData(invalidData)).toBe(false)
    })
  })

  describe('calculatePercentage', () => {
    const calculatePercentage = (value: number, max: number): number => {
      if (max === 0) return 0
      return Math.min((value / max) * 100, 100)
    }

    it('calculates percentage correctly', () => {
      expect(calculatePercentage(25, 100)).toBe(25)
      expect(calculatePercentage(50, 100)).toBe(50)
      expect(calculatePercentage(75, 100)).toBe(75)
      expect(calculatePercentage(100, 100)).toBe(100)
    })

    it('handles values over maximum', () => {
      expect(calculatePercentage(150, 100)).toBe(100)
      expect(calculatePercentage(200, 100)).toBe(100)
    })

    it('handles zero maximum', () => {
      expect(calculatePercentage(50, 0)).toBe(0)
    })

    it('handles decimal values', () => {
      expect(calculatePercentage(33.33, 100)).toBe(33.33)
      expect(calculatePercentage(66.67, 100)).toBe(66.67)
    })

    it('handles different scales', () => {
      expect(calculatePercentage(512, 1024)).toBe(50)
      expect(calculatePercentage(256, 1024)).toBe(25)
      expect(calculatePercentage(768, 1024)).toBe(75)
    })
  })
})
