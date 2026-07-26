import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { FeatureFlagProvider } from './context/FeatureFlagContext'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <FeatureFlagProvider>
          <App />
        </FeatureFlagProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
