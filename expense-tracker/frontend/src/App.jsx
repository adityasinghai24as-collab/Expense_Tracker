import { useState, useEffect } from 'react'

export default function App() {
  const [isConnected, setIsConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        setLoading(true)
        const response = await fetch('/api/health')
        if (response.ok) {
          const data = await response.json()
          setIsConnected(data.status === 'ok')
          setError(null)
        } else {
          setIsConnected(false)
          setError('Backend returned status: ' + response.status)
        }
      } catch (err) {
        setIsConnected(false)
        setError('Failed to connect to backend: ' + err.message)
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 5000)
    return () => clearInterval(interval)
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
