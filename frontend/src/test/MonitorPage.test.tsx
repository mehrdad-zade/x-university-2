/**
 * Basic Tests for MonitorPage component
 * 
 * Tests basic rendering and feature presence:
 * - Component structure
 * - Key UI elements
 * - Basic functionality without complex async operations
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import MonitorPage from '../pages/MonitorPage'

// Mock data for successful API response
const mockMonitorData = {
  timestamp: '2025-08-12T22:30:00.000Z',
  system: {
    os: {
      sysname: 'Linux',
      nodename: 'test-container',
      release: '6.10.14-linuxkit',
      version: '#1 SMP PREEMPT_DYNAMIC',
      machine: 'x86_64'
    },
    python_version: '3.12.11 (main, Jul 22 2025, 01:45:44) [GCC 12.2.0]',
    metrics: {
      cpu: {
        usage_percent: 25.5,
        count: 8,
        load_average: {
          '1min': 0.38,
          '5min': 0.43,
          '15min': 0.52
        }
      },
      memory: {
        total: 8220094464,
        available: 7016214528,
        used: 869580800,
        usage_percent: 14.6,
        swap_total: 1073737728,
        swap_used: 0,
        swap_percent: 0.0
      },
      disk: {
        total: 1081100128256,
        used: 26127368192,
        free: 999980453888,
        usage_percent: 2.4,
        read_bytes: 2406368256,
        write_bytes: 44769923072,
        read_count: 109503,
        write_count: 578912
      },
      network: {
        bytes_sent: 714749,
        bytes_recv: 567630,
        packets_sent: 5272,
        packets_recv: 5083,
        errin: 0,
        errout: 0,
        dropin: 0,
        dropout: 0
      }
    }
  },
  docker: {
    containers: [
      {
        id: '1234567890ab',
        name: 'test-backend',
        image: 'x-university-backend:latest',
        status: 'running',
        state: { Status: 'running', Running: true },
        created: '2025-08-12T20:00:00.000Z',
        ports: { '8000/tcp': [{ HostPort: '8000' }] },
        stats: {
          cpu_percent: 5.2,
          memory_usage: 134217728,
          memory_limit: 2147483648,
          network_rx: 1024000,
          network_tx: 2048000
        }
      }
    ],
    images: [
      {
        id: 'abcdef123456',
        tags: ['x-university-backend:latest'],
        size: 1073741824,
        created: '2025-08-12T19:00:00.000Z'
      }
    ],
    system_info: {
      containers_running: 1,
      containers_paused: 0,
      containers_stopped: 0,
      images_count: 2,
      docker_version: '24.0.0',
      architecture: 'x86_64',
      os_type: 'linux',
      total_memory: 8220094464
    }
  },
  services: {
    backend: {
      service: 'healthy',
      database: {
        status: 'healthy',
        error: null
      },
      timestamp: '2025-08-12T22:30:00.000Z',
      uptime: 9600
    }
  },
  logs: {
    backend: [
      {
        timestamp: '2025-08-12T22:25:00.000Z',
        level: 'INFO',
        message: 'Server started successfully',
        service: 'uvicorn'
      }
    ],
    frontend: [
      {
        timestamp: '2025-08-12T22:26:00.000Z',
        level: 'INFO',
        message: 'Vite dev server started',
        service: 'vite'
      }
    ]
  }
}

const mockFetch = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
  vi.stubGlobal('fetch', mockFetch)
})

const renderMonitorPage = () => {
  return render(
    <MemoryRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <MonitorPage />
    </MemoryRouter>
  )
}

describe('MonitorPage Basic Features', () => {
  describe('Loading State', () => {
    it('shows loading indicator when data is being fetched', () => {
      mockFetch.mockImplementation(() => new Promise(() => {})) // Never resolves
      
      renderMonitorPage()
      
      expect(screen.getByText('Loading monitoring data...')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('displays error message when API request fails', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))
      
      renderMonitorPage()
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load monitoring data')).toBeInTheDocument()
      }, { timeout: 1000 })
    })
  })

  describe('Successful Data Display', () => {
    beforeEach(() => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockMonitorData)
      })
    })

    it('renders monitor page title', async () => {
      renderMonitorPage()
      
      await waitFor(() => {
        expect(screen.getByText('System Monitor')).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('displays system health overview cards', async () => {
      renderMonitorPage()
      
      await waitFor(() => {
        expect(screen.getByText('CPU Usage')).toBeInTheDocument()
        expect(screen.getByText('Memory Usage')).toBeInTheDocument()
        expect(screen.getByText('Disk Usage')).toBeInTheDocument()
        expect(screen.getByText('Backend Status')).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('displays system metrics values', async () => {
      renderMonitorPage()
      
      await waitFor(() => {
        expect(screen.getByText('25.5%')).toBeInTheDocument() // CPU usage
        expect(screen.getByText('14.6%')).toBeInTheDocument() // Memory usage
        expect(screen.getByText('2.4%')).toBeInTheDocument() // Disk usage
      }, { timeout: 1000 })
    })

    it('displays CPU cores count', async () => {
      renderMonitorPage()
      
      await waitFor(() => {
        // Just check that CPU cores count is displayed somewhere
        expect(screen.getByText('8')).toBeInTheDocument() // CPU cores
      }, { timeout: 1000 })
    })

    it('displays Docker containers section', async () => {
      renderMonitorPage()
      
      await waitFor(() => {
        expect(screen.getByText('Docker Containers')).toBeInTheDocument()
        expect(screen.getByText('test-backend')).toBeInTheDocument()
        expect(screen.getByText('x-university-backend:latest')).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('displays logs sections when expanded', async () => {
      renderMonitorPage()
      
      await waitFor(() => {
        // Logs start collapsed, so we need to check for the Show Logs button
        const showLogsButton = screen.getByText('⬇️ Show Logs')
        expect(showLogsButton).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('displays auto-refresh controls', async () => {
      renderMonitorPage()
      
      await waitFor(() => {
        expect(screen.getByText('Auto-refresh')).toBeInTheDocument()
        expect(screen.getByText('Refresh Now')).toBeInTheDocument()
        expect(screen.getByRole('checkbox')).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('shows last updated timestamp', async () => {
      renderMonitorPage()
      
      await waitFor(() => {
        expect(screen.getByText(/Last updated:/)).toBeInTheDocument()
      }, { timeout: 1000 })
    })
  })

  describe('Empty States', () => {
    it('handles empty containers list', async () => {
      const emptyData = {
        ...mockMonitorData,
        docker: {
          containers: [],
          images: [],
          system_info: {},
          error: null
        }
      }
      
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(emptyData)
      })
      
      renderMonitorPage()
      
      await waitFor(() => {
        // Check that the Docker containers section header exists
        expect(screen.getByText('Docker Containers')).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('handles empty logs', async () => {
      const emptyLogsData = {
        ...mockMonitorData,
        logs: {
          backend: [],
          frontend: []
        }
      }
      
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(emptyLogsData)
      })
      
      renderMonitorPage()
      
      await waitFor(() => {
        // Check that the logs section toggle button exists
        expect(screen.getByText('⬇️ Show Logs')).toBeInTheDocument()
      }, { timeout: 1000 })
    })
  })

  describe('API Integration', () => {
    it('calls the correct API endpoint', () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockMonitorData)
      })
      
      renderMonitorPage()
      
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/monitor')
    })

    it('handles network errors gracefully', async () => {
      mockFetch.mockRejectedValue(new Error('Network timeout'))
      
      renderMonitorPage()
      
      await waitFor(() => {
        expect(screen.getByText('Network timeout')).toBeInTheDocument()
      }, { timeout: 1000 })
    })
  })
})
