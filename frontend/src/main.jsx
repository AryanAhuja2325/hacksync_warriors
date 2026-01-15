import { StrictMode, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import AuthPage from './components/AuthPage.jsx'

function Root() {
  const [authenticated, setAuthenticated] = useState(!!localStorage.getItem('token'))
  return authenticated ? (
    <App />
  ) : (
    <AuthPage onAuthSuccess={() => setAuthenticated(true)} />
  )
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Root />
  </StrictMode>,
)
