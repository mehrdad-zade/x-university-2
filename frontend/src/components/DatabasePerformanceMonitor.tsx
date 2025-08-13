import React, { useState, useEffect } from 'react';

// Create a simple API client for database monitoring
const api = {
  get: async (endpoint: string) => {
    const response = await fetch(`http://localhost:8000${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return { data: await response.json() };
  }
};

interface ConnectionPoolStats {
  pool_size: number;
  checked_in: number;
  checked_out: number;
  overflow: number;
  total_connections: number;
  utilization_percent: number;
}

interface DatabaseStats {
  database_size_bytes: number;
  database_size_mb: number;
  active_connections: number;
  running_queries: number;
  max_connections: number;
  connection_usage_percent: number;
  tables: Array<{
    schema: string;
    table: string;
    total_size_bytes: number;
    total_size_mb: number;
    table_size_bytes: number;
    table_size_mb: number;
    total_changes: number;
    live_rows: number;
    dead_rows: number;
    dead_row_percent: number;
    last_vacuum: string | null;
    last_autovacuum: string | null;
    last_analyze: string | null;
    last_autoanalyze: string | null;
  }>;
  indexes: Array<{
    schema: string;
    table: string;
    index: string;
    scans: number;
    tuples_read: number;
    tuples_fetched: number;
    size: string;
  }>;
}

interface SlowQuery {
  query?: string;
  calls?: number;
  avg_time_ms?: number;
  max_time_ms?: number;
  cache_hit_percent?: number;
  error?: string;
}

interface DatabasePerformanceData {
  timestamp: string;
  connection_pool: ConnectionPoolStats;
  database_stats: DatabaseStats;
  slow_queries: SlowQuery[];
  recommendations: string[];
  health: {
    status: string;
    issues: string[];
    warnings: string[];
  };
}

const DatabasePerformanceMonitor: React.FC = () => {
  const [performanceData, setPerformanceData] = useState<DatabasePerformanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchPerformanceData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/monitor/database/performance');
      setPerformanceData(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching database performance data:', err);
      setError(err.response?.data?.detail || 'Failed to fetch database performance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPerformanceData();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchPerformanceData, 10000); // Refresh every 10 seconds
      return () => clearInterval(interval);
    }
    return undefined;
  }, [autoRefresh]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getUtilizationColor = (percent: number) => {
    if (percent > 90) return 'bg-red-500';
    if (percent > 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading && !performanceData) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading database performance data...</span>
      </div>
    );
  }

  if (error && !performanceData) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error Loading Database Performance</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
            <button
              onClick={fetchPerformanceData}
              className="mt-2 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!performanceData) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Database Performance Monitor</h2>
        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">Auto Refresh (10s)</span>
          </label>
          <button
            onClick={fetchPerformanceData}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Health Status */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Database Health</h3>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(performanceData.health.status)}`}>
            {performanceData.health.status.toUpperCase()}
          </div>
        </div>
        
        {performanceData.health.issues.length > 0 && (
          <div className="mb-4">
            <h4 className="font-medium text-red-600 mb-2">Issues:</h4>
            <ul className="list-disc list-inside space-y-1">
              {performanceData.health.issues.map((issue, index) => (
                <li key={index} className="text-red-600 text-sm">{issue}</li>
              ))}
            </ul>
          </div>
        )}

        {performanceData.health.warnings.length > 0 && (
          <div className="mb-4">
            <h4 className="font-medium text-yellow-600 mb-2">Warnings:</h4>
            <ul className="list-disc list-inside space-y-1">
              {performanceData.health.warnings.map((warning, index) => (
                <li key={index} className="text-yellow-600 text-sm">{warning}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Connection Pool Stats */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Connection Pool</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-2xl font-bold text-blue-600">
              {performanceData.connection_pool.utilization_percent}%
            </div>
            <div className="text-sm text-gray-600">Pool Utilization</div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className={`h-2 rounded-full ${getUtilizationColor(performanceData.connection_pool.utilization_percent)}`}
                style={{ width: `${performanceData.connection_pool.utilization_percent}%` }}
              ></div>
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-2xl font-bold text-gray-900">
              {performanceData.connection_pool.checked_out}/{performanceData.connection_pool.total_connections}
            </div>
            <div className="text-sm text-gray-600">Active/Total</div>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-2xl font-bold text-gray-900">
              {performanceData.connection_pool.pool_size}
            </div>
            <div className="text-sm text-gray-600">Pool Size</div>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-2xl font-bold text-gray-900">
              {performanceData.connection_pool.overflow}
            </div>
            <div className="text-sm text-gray-600">Overflow</div>
          </div>
        </div>
      </div>

      {/* Database Statistics */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Database Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-2xl font-bold text-blue-600">
              {performanceData.database_stats.database_size_mb} MB
            </div>
            <div className="text-sm text-gray-600">Database Size</div>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-2xl font-bold text-gray-900">
              {performanceData.database_stats.active_connections}
            </div>
            <div className="text-sm text-gray-600">Active Connections</div>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-2xl font-bold text-gray-900">
              {performanceData.database_stats.running_queries}
            </div>
            <div className="text-sm text-gray-600">Running Queries</div>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-2xl font-bold text-gray-900">
              {performanceData.database_stats.connection_usage_percent}%
            </div>
            <div className="text-sm text-gray-600">DB Connection Usage</div>
          </div>
        </div>
      </div>

      {/* Tables */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Table Statistics</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Table</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size (MB)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Live Rows</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dead Rows %</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Vacuum</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {performanceData.database_stats.tables.slice(0, 10).map((table, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{table.table}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{table.total_size_mb}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{table.live_rows?.toLocaleString() || 0}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className={table.dead_row_percent > 25 ? 'text-red-600 font-medium' : ''}>
                      {table.dead_row_percent}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {table.last_autovacuum ? new Date(table.last_autovacuum).toLocaleString() : 'Never'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Slow Queries */}
      {performanceData.slow_queries.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Slow Queries</h3>
          <div className="space-y-4">
            {performanceData.slow_queries.slice(0, 5).map((query, index) => (
              <div key={index} className="border rounded p-4">
                {query.error ? (
                  <div className="text-yellow-600 bg-yellow-50 p-3 rounded">
                    <p className="font-medium">Query Monitoring Unavailable</p>
                    <p className="text-sm mt-1">{query.error}</p>
                  </div>
                ) : (
                  <>
                    <div className="flex justify-between items-start mb-2">
                      <div className="text-sm font-mono text-gray-800 bg-gray-100 p-2 rounded flex-1 mr-4">
                        {query.query}
                      </div>
                      <div className="text-right text-sm">
                        <div className="font-medium text-red-600">{query.avg_time_ms?.toFixed(2) || 0}ms avg</div>
                        <div className="text-gray-500">{query.calls || 0} calls</div>
                      </div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Max: {query.max_time_ms?.toFixed(2) || 0}ms</span>
                      <span>Cache Hit: {query.cache_hit_percent?.toFixed(1) || 0}%</span>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {performanceData.recommendations.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Recommendations</h3>
          <ul className="space-y-2">
            {performanceData.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start">
                <svg className="h-5 w-5 text-blue-500 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm text-gray-700">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Timestamp */}
      <div className="text-center text-xs text-gray-500">
        Last updated: {new Date(performanceData.timestamp).toLocaleString()}
      </div>
    </div>
  );
};

export default DatabasePerformanceMonitor;
