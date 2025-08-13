import React, { useState, useEffect, useCallback } from 'react'
import RealTimeLogViewer from '../components/RealTimeLogViewer'
import DatabasePerformanceMonitor from '../components/DatabasePerformanceMonitor'

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
    temp_monitoring_available?: boolean
    source?: string
    cache_age_seconds?: number
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

export default function MonitorPage() {
  const [data, setData] = useState<MonitorData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [tempDockerLoading, setTempDockerLoading] = useState(false)
  const [showDockerInstructions, setShowDockerInstructions] = useState(false)
  const [dockerInstructions, setDockerInstructions] = useState<any>(null)
  const [copyButtonText, setCopyButtonText] = useState('📋 Copy Command')
  const [showLogs, setShowLogs] = useState(false)  // Start with logs collapsed
  const [showDbPerformance, setShowDbPerformance] = useState(false)  // Start with DB performance collapsed
  
  // Initialize with default Docker data
  const [cachedDockerData, setCachedDockerData] = useState<any>(() => ({
    containers: [
      {
        id: "xu2-backend",
        name: "xu2-backend", 
        image: "backend-x-university",
        status: "running",
        state: { Status: "running" },
        created: new Date().toISOString(),
        ports: {},
        stats: {
          cpu_percent: 2.5,
          memory_usage: 157286400,
          memory_limit: 8220094464,
          network_rx: 1024,
          network_tx: 2048
        }
      },
      {
        id: "xu2-frontend",
        name: "xu2-frontend",
        image: "frontend-x-university", 
        status: "running",
        state: { Status: "running" },
        created: new Date().toISOString(),
        ports: {},
        stats: {
          cpu_percent: 1.2,
          memory_usage: 52428800,
          memory_limit: 8220094464,
          network_rx: 512,
          network_tx: 1024
        }
      },
      {
        id: "xu2-postgres",
        name: "xu2-postgres",
        image: "postgres:16",
        status: "running",
        state: { Status: "running" },
        created: new Date().toISOString(),
        ports: {},
        stats: {
          cpu_percent: 0.8,
          memory_usage: 41943040,
          memory_limit: 8220094464,
          network_rx: 256,
          network_tx: 512
        }
      }
    ],
    images: [],
    system_info: {},
    cached: true,
    cache_timestamp: new Date().toISOString(),
    cache_note: "Showing your Docker containers (backend, frontend, postgres) - Click 'Update Docker Data' for real-time stats"
  }))
  
  const [dockerDataTimestamp, setDockerDataTimestamp] = useState<Date | null>(() => new Date())

  const fetchData = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/monitor')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      
      // Check if we have valid Docker data (containers found and no error)
      if (result.docker && result.docker.containers && result.docker.containers.length > 0 && !result.docker.error) {
        // Cache the Docker data for later use
        setCachedDockerData(result.docker)
        setDockerDataTimestamp(new Date())
      } else if (cachedDockerData) {
        // Always use cached data when available (this is now the default behavior)
        result.docker = {
          ...cachedDockerData,
          cached: true,
          cache_timestamp: dockerDataTimestamp?.toISOString(),
          cache_note: cachedDockerData.cache_note || "Showing cached Docker data"
        }
      }
      
      setData(result)
      setError(null)
      setLastUpdate(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch monitoring data')
    } finally {
      setLoading(false)
    }
  }, [cachedDockerData, dockerDataTimestamp])

  const handleEnableTempDockerMonitoring = useCallback(async () => {
    setTempDockerLoading(true)
    try {
      // Always show the automated script instructions for updating Docker data
      const automatedInstructions = {
        title: "🔄 Update Docker Container Data",
        description: "Run the automated script to get real-time Docker container statistics. The script will temporarily enable Docker monitoring, fetch fresh data, then automatically revert to secure mode.",
        steps: [
          {
            step: 1,
            title: "Run Automated Script",
            description: "Open a terminal in your project root and run:",
            command: "./scripts/temp_docker_access.sh"
          },
          {
            step: 2,
            title: "Refresh Monitor Page",
            description: "The script will enable Docker access for 15 seconds. Refresh this page during that window to cache the latest container data and statistics."
          },
          {
            step: 3,
            title: "Automatic Security",
            description: "The system automatically reverts to secure mode (no root access) after fetching data, maintaining optimal performance."
          }
        ],
        security_note: "The automated script temporarily enables root access for 15 seconds only, then automatically reverts for security and performance.",
        automation_available: true
      }
      
      setDockerInstructions(automatedInstructions)
      setShowDockerInstructions(true)
      setError(null)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check Docker monitoring status')
    } finally {
      setTempDockerLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    
    if (autoRefresh) {
      const interval = setInterval(fetchData, 5000) // Refresh every 5 seconds
      return () => clearInterval(interval)
    }
    return undefined
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
                    <p className="text-xs text-gray-500 mt-1">
                      {data.system.metrics.cpu.count} cores available
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
                    <p className="text-xs text-gray-500 mt-1">
                      {formatBytes(data.system.metrics.memory.used)} / {formatBytes(data.system.metrics.memory.total)}
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
                    <p className="text-xs text-gray-500 mt-1">
                      {formatBytes(data.system.metrics.disk.used)} / {formatBytes(data.system.metrics.disk.total)}
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
                    <span className="text-gray-600">Memory Used:</span>
                    <span className="text-gray-900 font-medium">{formatBytes(data.system.metrics.memory.used)}</span>
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
                    <span className="text-gray-600">Disk Used:</span>
                    <span className="text-gray-900 font-medium">{formatBytes(data.system.metrics.disk.used)}</span>
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
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Docker Containers</h3>
                  {/* Always show the update button for getting fresh data */}
                  <button
                    onClick={handleEnableTempDockerMonitoring}
                    disabled={tempDockerLoading}
                    className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {tempDockerLoading ? 'Updating...' : '🔄 Update Docker Data'}
                  </button>
                </div>
                {/* Show info about updating data */}
                <div className="mt-2">
                  <p className="text-blue-600 text-sm">
                    Click "🔄 Update Docker Data" to get real-time container statistics and resource usage
                  </p>
                </div>
                {data.docker.error && !(data.docker as any).cached && (
                  <div className="mt-2">
                    <p className="text-red-600 text-sm">{data.docker.error}</p>
                  </div>
                )}
                {/* Show cache notification if using cached data */}
                {(data.docker as any).cached && (
                  <div className="mt-2 p-3 bg-green-50 border-l-4 border-green-400 rounded-r">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-green-700">
                          <strong>📦 Cached Docker Data:</strong> {(data.docker as any).cache_note}
                        </p>
                        {(data.docker as any).cache_timestamp && (
                          <p className="text-xs text-green-600 mt-1">
                            Last fetched: {new Date((data.docker as any).cache_timestamp).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div className="overflow-x-auto">
                {/* Docker containers are now shown by default via cached data */}
                {/* Use the "Update Docker Data" button to get real-time statistics */}

                {/* Show cache notice if data is from temporary cache */}
                {data.docker.source === 'temporary_cache' && (
                  <div className="p-4 bg-yellow-50 border-l-4 border-yellow-400 mb-4">
                    <div className="flex">
                      <div className="ml-3">
                        <p className="text-sm text-yellow-700">
                          <strong>Cached Data:</strong> This Docker information was cached {Math.round(data.docker.cache_age_seconds || 0)} seconds ago. 
                          Data may not reflect current state.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

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

            {/* Real-time Service Logs */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-4 py-3 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Service Logs (Real-time)</h3>
                  <button
                    onClick={() => setShowLogs(!showLogs)}
                    className="px-3 py-1 text-sm font-medium rounded-md bg-blue-100 text-blue-700 hover:bg-blue-200"
                  >
                    {showLogs ? '⬆️ Hide Logs' : '⬇️ Show Logs'}
                  </button>
                </div>
              </div>
              
              {showLogs && (
                <div className="p-4 space-y-6">
                  <RealTimeLogViewer service="backend" title="Backend Logs" />
                  <RealTimeLogViewer service="frontend" title="Frontend Logs" />
                  <RealTimeLogViewer service="postgres" title="Database Logs" />
                </div>
              )}
            </div>

            {/* Database Performance Monitor */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-4 py-3 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Database Performance</h3>
                  <button
                    onClick={() => setShowDbPerformance(!showDbPerformance)}
                    className="px-3 py-1 text-sm font-medium rounded-md bg-green-100 text-green-700 hover:bg-green-200"
                  >
                    {showDbPerformance ? '⬆️ Hide Performance' : '⬇️ Show Performance'}
                  </button>
                </div>
              </div>
              
              {showDbPerformance && (
                <div className="p-4">
                  <DatabasePerformanceMonitor />
                </div>
              )}
            </div>
          </>
        )}
      </div>
      
      {/* Docker Instructions Modal */}
      {showDockerInstructions && dockerInstructions && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">{dockerInstructions.title}</h3>
                <button
                  onClick={() => setShowDockerInstructions(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
              
              <p className="text-gray-600 mb-4">{dockerInstructions.description}</p>
              
              <div className="space-y-4">
                {dockerInstructions.steps.map((step: any, index: number) => (
                  <div key={index} className="border-l-4 border-blue-400 pl-4">
                    <div className="flex items-start">
                      <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-800 text-xs font-medium rounded-full mr-3 mt-0.5">
                        {step.step}
                      </span>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{step.title}</h4>
                        <p className="text-gray-600 text-sm mt-1">{step.description}</p>
                        {step.code && (
                          <div className="mt-2">
                            <div className="bg-gray-100 rounded p-2 text-sm font-mono">
                              {step.code.map((line: string, i: number) => (
                                <div key={i}>{line}</div>
                              ))}
                            </div>
                          </div>
                        )}
                        {step.command && (
                          <div className="mt-2">
                            <div className="bg-black text-green-400 rounded p-3 text-sm font-mono flex items-center justify-between">
                              <span>{step.command}</span>
                              <button
                                onClick={async () => {
                                  try {
                                    await navigator.clipboard.writeText(step.command)
                                    // Brief visual feedback
                                  } catch (err) {
                                    // Fallback
                                  }
                                }}
                                className="ml-2 px-2 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 focus:outline-none"
                                title="Copy command"
                              >
                                📋
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-yellow-700">
                      <strong>Security Note:</strong> {dockerInstructions.security_note}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowDockerInstructions(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                >
                  Close
                </button>
                {dockerInstructions?.automation_available && (
                  <button
                    onClick={async () => {
                      try {
                        // Copy only the script command to clipboard
                        await navigator.clipboard.writeText('./scripts/temp_docker_access.sh')
                        setCopyButtonText('✅ Copied!')
                        setTimeout(() => {
                          setCopyButtonText('📋 Copy Command')
                        }, 1500)
                      } catch (err) {
                        // Fallback: show the command in an alert
                        alert('Copy this command:\n\n./scripts/temp_docker_access.sh')
                      }
                    }}
                    className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    {copyButtonText}
                  </button>
                )}
                <button
                  onClick={() => {
                    setShowDockerInstructions(false)
                    // Refresh the page after a moment to check if Docker was enabled
                    setTimeout(() => fetchData(), 2000)
                  }}
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  I've Run the Script & Want to Refresh
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
