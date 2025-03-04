import { useState } from 'react'
import './App.css'
import Card from './components/card'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div className="flex items-center justify-center rounded-lg w-screen h-screen ">
        <Card/>
        </div>
    </>
  )
}

export default App
