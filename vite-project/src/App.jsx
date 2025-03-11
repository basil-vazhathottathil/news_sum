import { useEffect, useState } from 'react';
import './App.css';
import Card from './components/Card';
import getData from './functions/app';

function App() {
  const [data, setData] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    async function fetchData() {
      const result = await getData();
      setData(result || []);  // Ensure data is always an array
    }
    fetchData();
  }, []);

  const handlePrevious = () => {
    if (data.length > 0) {
      setCurrentIndex((prevIndex) => (prevIndex > 0 ? prevIndex - 1 : data.length - 1));
    }
  };

  const handleNext = () => {
    if (data.length > 0) {
      setCurrentIndex((prevIndex) => (prevIndex < data.length - 1 ? prevIndex + 1 : 0));
    }
  };

  return (
    <div className="flex items-center justify-center rounded-lg w-screen h-screen">
      {data.length > 0 ? (
        <Card
          title={data[currentIndex].title}
          summary={data[currentIndex].summary}
          link={data[currentIndex].link}
          onPrevious={handlePrevious}
          onNext={handleNext}
        />
      ) : (
        <p>Loading...</p>  // Show a loading message or something else while the data is being fetched
      )}
    </div>
  );
}

export default App;
