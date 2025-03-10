import { useEffect, useState } from 'react'
import './App.css'
import Card from './components/card'
import getData from './functions/app'

function App() {
  const [data, setData] = useState([])

  useEffect(() => {
    async function fetchData() {
      const result= await getData();
      setData(result);
    }
    fetchData();
  }, []);
  


  return (
    <>
      <div className="flex items-center justify-center rounded-lg w-screen h-screen ">
        {data.map((item,index)=> (
          <Card key={index} title={item.title} summary={item.summary} link={item.link}/>
        ))}
        </div>
    </>
  )
}

export default App
