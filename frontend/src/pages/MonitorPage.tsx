import React, { useState, useEffect, useCallback } from 'react'

interface SystemMetrics {
  cpu: {
    usage_percent: number
    count: number
    load_average: {
      '1min': number
      '5min': number
      '15min': number
    }
  }
  memory: {
    total: number
    available: number
    used: number
    usage_percent: number
    swap_total: number
    swap_used: number
    swap_percent: number
  }
  disk: {
    total: number
    used: number
    free: number
    usage_percent: number
    read_bytes: number
    write_bytes: number
    read_count: number
    write_count: number
  }
  network: {
    bytes_sent: number
    bytes_recv: number
    packets_sent: number
    packets_recv: number
    errin: number
    errout: number
    dropin: number
    dropout: number
  }
}

interface DockerContainer {
  id: string
  name: string
  image: string
  status: string
  state: any
  created: string
  ports: any
  stats: {
    cpu_percent: number
    memory_usage: number
    memory_limit: number
    network_rx: number
    network_tx: number
  }
}

interface LogEntry {
  timestamp: string
  level: string
  message: string
  service: string
}

interface MonitorData {
  timestamp: string
  system: {
    os: any
    python_version: string
    metrics: SystemMetrics
  }
  docker: {
    containers: DockerContainer[]
    images: any[]
    system_info: any
    error?: string
  }
  services: {
    backend: {
      service: string
      database: {
        status: string
        error?: string
      }
      timestamp: string
      uptime: number
    }
  }
  logs: {
    backend: LogEntry[]
    frontend: LogEntry[]
  }
}

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatUptime = (seconds: number) => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  return `${days}d ${hours}h ${mins}m`
}

const StatusBadge: React.FC<{ status: string; className?: string }> = ({ status, className = '' }) => {
  const getStatusColor = (status: string) => {
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

  return (
    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(status)} ${className}`}>
      {status}
    </span>
  )
}

const ProgressBar: React.FC<{ value: number; max?: number; className?: string; showLabel?: boolean }> = ({ 
  value, 
  max = 100, 
  className = '', 
  showLabel = true 
}) => {
  const percentage = Math.min((value / max) * 100, 100)
  
  const getColorClass = (percent: number) => {
    if (percent < 60) return 'bg-green-500'
    if (percent < 80) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className={`w-full ${className}`}>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${getColorClass(percentage)}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-xs text-gray-600 mt-1 block">
          {percentage.toFixed(1)}%
        </span>
      )}
    </div>
  )
}

const LogViewer: React.FC<{ logs: LogEntry[]; title: string }> = ({ logs, title }) => {
  const getLogLevelColor = (level: string) => {
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

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      <div className="max-h-64 overflow-y-auto">
        {logs.length === 0 ? (
          <div className="p-4 text-center text-gray-500">No logs available</div>
        ) : (
          <div className="divide-y divide-gray-100">
            {logs.slice(-10).reverse().map((log, index) => (
              <div key={index} className="px-4 py-2 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getLogLevelColor(log.level)}`}>
                      {log.level}
                    </span>
                    <span className="text-sm text-gray-600">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {log.service}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-800 mt-1 break-words">{log.message}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function MonitorPage() {
  const [data, setData] = useState<MonitorData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [autoRefresh, setAutoRefresh] = useState(true)

  const fetchData = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/monitor')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      setData(result)
      setError(null)
      setLastUpdate(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch monitoring data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    
    if (autoRefresh) {
      const interval = setInterval(fetchData, 5000) // Refresh every 5 seconds
      return () => clearInterval(interval)
    }
  }, [fetchData, autoRefresh])

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading monitoring data...</p>
        </div>
      </div>
    )
  }

  if (error && !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <svg className="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-gray-900 font-semibold">Failed to load monitoring data</p>
          <p className="text-gray-600 mt-2">{error}</p>
          <button
            onClick={fetchData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">System Monitor</h1>
              <p className="text-gray-600 mt-1">
                Last updated: {lastUpdate.toLocaleString()}
                {error && <span className="text-red-600 ml-2">({error})</span>}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Auto-refresh</span>
              </label>
              <button
                onClick={fetchData}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium"
              >
                Refresh Now
              </button>
            </div>
          </div>
        </div>

        {data && (
          <>
            {/* System Health Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">CPU Usage</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {data.system.metrics.cpu.usage_percent.toFixed(1)}%
                    </p>
                  </div>
                  <div className="w-16">
                    <ProgressBar value={data.system.metrics.cpu.usage_percent} showLabel={false} />
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Memory Usage</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {data.system.metrics.memory.usage_percent.toFixed(1)}%
                    </p>
                  </div>
                  <div className="w-16">
                    <ProgressBar value={data.system.metrics.memory.usage_percent} showLabel={false} />
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Disk Usage</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {data.system.metrics.disk.usage_percent.toFixed(1)}%
                    </p>
                  </div>
                  <div className="w-16">
                    <ProgressBar value={data.system.metrics.disk.usage_percent} showLabel={false} />
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Backend Status</p>
                    <StatusBadge status={data.services.backend.service} />
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Database</p>
                    <StatusBadge status={data.services.backend.database.status} />
                  </div>
                </div>
              </div>
            </div>

            {/* System Details */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Information</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">OS:</span>
                    <span className="text-gray-900 font-medium">
                      {data.system.os.system || 'Unknown'} {data.system.os.release || ''}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">CPU Cores:</span>
                    <span className="text-gray-900 font-medium">{data.system.metrics.cpu.count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Load Average:</span>
                    <span className="text-gray-900 font-medium">
                      {data.system.metrics.cpu.load_average['1min'].toFixed(2)} / 
                      {data.system.metrics.cpu.load_average['5min'].toFixed(2)} / 
                      {data.system.metrics.cpu.load_average['15min'].toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Memory Total:</span>
                    <span className="text-gray-900 font-medium">{formatBytes(data.system.metrics.memory.total)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Memory Available:</span>
                    <span className="text-gray-900 font-medium">{formatBytes(data.system.metrics.memory.available)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Disk Total:</span>
                    <span className="text-gray-900 font-medium">{formatBytes(data.system.metrics.disk.total)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Disk Free:</span>
                    <span className="text-gray-900 font-medium">{formatBytes(data.system.metrics.disk.free)}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Network I/O</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Bytes Sent:</span>
                    <span className="text-gray-900 font-medium">{formatBytes(data.system.metrics.network.bytes_sent)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Bytes Received:</span>
                    <span className="text-gray-900 font-medium">{formatBytes(data.system.metrics.network.bytes_recv)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Packets Sent:</span>
                    <span className="text-gray-900 font-medium">{data.system.metrics.network.packets_sent.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Packets Received:</span>
                    <span className="text-gray-900 font-medium">{data.system.metrics.network.packets_recv.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Errors In:</span>
                    <span className={`font-medium ${data.system.metrics.network.errin > 0 ? 'text-red-600' : 'text-gray-900'}`}>
                      {data.system.metrics.network.errin}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Errors Out:</span>
                    <span className={`font-medium ${data.system.metrics.network.errout > 0 ? 'text-red-600' : 'text-gray-900'}`}>
                      {data.system.metrics.network.errout}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Docker Containers */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Docker Containers</h3>
                {data.docker.error && (
                  <p className="text-red-600 text-sm mt-1">{data.docker.error}</p>
                )}
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Container
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Image
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Memory
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Network
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.docker.containers.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                          No containers found
                        </td>
                      </tr>
                    ) : (
                      data.docker.containers.map((container) => (
                        <tr key={container.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{container.name}</div>
                              <div className="text-sm text-gray-500">{container.id}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {container.image}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <StatusBadge status={container.status} />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {container.stats.memory_usage > 0 && container.stats.memory_limit > 0 ? (
                              <div>
                                <div>{formatBytes(container.stats.memory_usage)}</div>
                                <div className="w-16">
                                  <ProgressBar 
                                    value={container.stats.memory_usage} 
                                    max={container.stats.memory_limit} 
                                    showLabel={false}
                                    className="mt-1"
                                  />
                                </div>
                              </div>
                            ) : (
                              'N/A'
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <div>RX: {formatBytes(container.stats.network_rx)}</div>
                            <div>TX: {formatBytes(container.stats.network_tx)}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(container.created).toLocaleString()}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Service Logs */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <LogViewer logs={data.logs.backend} title="Backend Logs" />
              <LogViewer logs={data.logs.frontend} title="Frontend Logs" />
            </div>
          </>
        )}
      </div>
    </div>
  )
}
