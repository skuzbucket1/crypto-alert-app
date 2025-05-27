// frontend/src/App.tsx
import { useEffect, useState } from 'react'
import ConfigForm from './components/ConfigForm'
import AlertsList from './components/AlertsList'
import { subscribeToAlerts } from './services/alerts'

function App() {
  const [alerts, setAlerts] = useState<any[]>([])
  useEffect(() => {
    const unsubscribe = subscribeToAlerts(newAlert => 
      setAlerts(prev => [newAlert, ...prev])
    )
    return unsubscribe
  }, [])
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Crypto Alert Dashboard</h1>
      <ConfigForm />
      <AlertsList alerts={alerts} />
    </div>
  )
}
export default App
