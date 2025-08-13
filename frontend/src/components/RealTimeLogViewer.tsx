import React, { useState, useEffect, useRef } from 'react'

export interface LogEntry {
  timestamp: string
  level: string
  message: string
  service: string
}

interface RealTimeLogViewerProps {
  service: string
  title: string
  maxLines?: number
  autoScroll?: boolean
}

const RealTimeLogViewer: React.FC<RealTimeLogViewerProps> = ({ 
  service, 
  title, 
  maxLines = 500, 
  autoScroll = true 
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isPaused, setIsPaused] = useState(false)
  const [autoScrollEnabled, setAutoScrollEnabled] = useState(autoScroll)
  const logContainerRef = useRef<HTMLDivElement>(null)
  const eventSourceRef = useRef<EventSource | null>(null)

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    })
  }

  const getLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
        return 'text-red-600 bg-red-50'
      case 'warning':
      case 'warn':
        return 'text-yellow-600 bg-yellow-50'
      case 'debug':
        return 'text-blue-600 bg-blue-50'
      default:
        return 'text-gray-700 bg-gray-50'
    }
  }

  const connectToStream = () => {
    // Prevent multiple connections
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }
    
    const baseUrl = window.location.origin.replace(/:\d+/, ':8000')
    const url = `${baseUrl}/api/v1/monitor/logs/stream/${service}`
    
    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    eventSource.onopen = () => {
      setIsConnected(true)
      setError(null)
    }

    eventSource.onmessage = (event) => {
      if (isPaused) return
      
      try {
        const logEntry: LogEntry = JSON.parse(event.data)
        
        setLogs(prevLogs => {
          const newLogs = [...prevLogs, logEntry]
          // Keep only the last maxLines entries
          if (newLogs.length > maxLines) {
            return newLogs.slice(-maxLines)
          }
          return newLogs
        })
      } catch (err) {
        console.error('Failed to parse log entry:', err)
      }
    }

    eventSource.onerror = (event) => {
      console.error('EventSource error:', event)
      setIsConnected(false)
      setError('Connection to log stream failed')
      
      // Don't auto-reconnect aggressively to prevent overwhelming the server
      // Only reconnect if user manually resumes
    }
  }

  const disconnectFromStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    setIsConnected(false)
  }

  const scrollToBottom = () => {
    if (logContainerRef.current && autoScrollEnabled) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }

  const clearLogs = () => {
    setLogs([])
  }

  const togglePause = () => {
    setIsPaused(!isPaused)
    if (isPaused) {
      // Resume - reconnect if needed
      if (!isConnected) {
        connectToStream()
      }
    }
  }

  const manualReconnect = () => {
    setError(null)
    connectToStream()
  }

  const downloadLogs = () => {
    const logText = logs.map(log => 
      `[${log.timestamp}] ${log.level.toUpperCase()} [${log.service}] ${log.message}`
    ).join('\n')
    
    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${service}-logs-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Auto-scroll when new logs arrive
  useEffect(() => {
    scrollToBottom()
  }, [logs])

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connectToStream()
    
    return () => {
      disconnectFromStream()
    }
  }, [service])

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-medium text-gray-900">{title}</h3>
            <div className="flex items-center space-x-1">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className={`text-xs ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                {isConnected ? 'Live' : 'Disconnected'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={togglePause}
              className={`px-3 py-1 text-xs font-medium rounded-md ${
                isPaused 
                  ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                  : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
              }`}
            >
              {isPaused ? '▶️ Resume' : '⏸️ Pause'}
            </button>

            {!isConnected && (
              <button
                onClick={manualReconnect}
                className="px-3 py-1 text-xs font-medium rounded-md bg-blue-100 text-blue-700 hover:bg-blue-200"
              >
                🔄 Reconnect
              </button>
            )}
            
            <button
              onClick={() => setAutoScrollEnabled(!autoScrollEnabled)}
              className={`px-3 py-1 text-xs font-medium rounded-md ${
                autoScrollEnabled 
                  ? 'bg-blue-100 text-blue-700 hover:bg-blue-200' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              📜 Auto-scroll: {autoScrollEnabled ? 'On' : 'Off'}
            </button>
            
            <button
              onClick={clearLogs}
              className="px-3 py-1 text-xs font-medium rounded-md bg-red-100 text-red-700 hover:bg-red-200"
            >
              🗑️ Clear
            </button>
            
            <button
              onClick={downloadLogs}
              className="px-3 py-1 text-xs font-medium rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
            >
              💾 Download
            </button>
          </div>
        </div>
        
        {error && (
          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            {error}
          </div>
        )}
        
        <div className="mt-2 text-xs text-gray-500">
          {logs.length} lines • Max: {maxLines} • Service: {service}
        </div>
      </div>

      {/* Log Content */}
      <div 
        ref={logContainerRef}
        className="h-96 overflow-y-auto bg-gray-900 text-green-400 font-mono text-xs"
      >
        {logs.length === 0 ? (
          <div className="p-4 text-center text-gray-400">
            {isConnected ? 'Waiting for logs...' : 'Not connected to log stream'}
          </div>
        ) : (
          <div className="p-4 space-y-1">
            {logs.map((log, index) => (
              <div 
                key={index}
                className="flex space-x-2 hover:bg-gray-800 px-2 py-1 rounded"
              >
                <span className="text-gray-400 w-20 flex-shrink-0">
                  {formatTimestamp(log.timestamp)}
                </span>
                <span className={`w-12 flex-shrink-0 text-center px-1 rounded text-xs ${getLevelColor(log.level)}`}>
                  {log.level}
                </span>
                <span className="text-blue-400 w-16 flex-shrink-0">
                  [{log.service}]
                </span>
                <span className="text-green-400 flex-1 break-words">
                  {log.message}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500 flex justify-between items-center">
        <div>
          Last updated: {logs.length > 0 ? formatTimestamp(logs[logs.length - 1]?.timestamp || '') : 'Never'}
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={scrollToBottom}
            className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
          >
            ⬇️ Bottom
          </button>
        </div>
      </div>
    </div>
  )
}

export default RealTimeLogViewer
