import { useState, useEffect } from 'react'

export default function App() {
  const [isConnected, setIsConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const checkHealth = async () => {
      // TODO: SDE-2 Task 7 - Frontend to Backend Connection
      // 1. Implement a fetch call to the backend health endpoint (e.g., '/api/health').
      // 2. Handle the response and update the component state (isConnected, error).
      // 3. Implement error handling (try/catch) for the fetch call.
      
      // TODO: SDE-2 Task 32 - Frontend Enterprise Readiness
      // 1. Initialize an error tracking SDK (e.g., Sentry) at the root of the app.
      // 2. Add structured analytics tracking for key user flows (e.g., "Expense Added").
      // 3. Implement proper client-side caching (e.g., React Query / SWR) for API requests.
      
      try {
        setLoading(true)
        const response = await fetch('/api/health')
        if (!response.ok) {
          throw new Error(`Backend returned ${response.status}`)
        }
        const data = await response.json()
        setIsConnected(data.status === 'ok')
        setError(null)
      } catch (err) {
        setIsConnected(false)
        setError('Failed to connect to backend: ' + err.message)
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
    // TODO: Consider if you want to poll the backend periodically (e.g., using setInterval)
    // const interval = setInterval(checkHealth, 5000)
    // return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full">
          <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
            Expense Tracker
          </h1>

          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
              <span className="text-gray-700 font-medium">
                {loading ? 'Checking connection...' : isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3 text-red-700 text-sm">
                {error}
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
              <p className="text-blue-900 text-sm">
                Backend status: <span className="font-mono text-blue-700">{isConnected ? 'Running' : 'Offline'}</span>
              </p>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-center text-gray-500 text-xs">
              Monorepo shell ready. Add your application logic here.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
