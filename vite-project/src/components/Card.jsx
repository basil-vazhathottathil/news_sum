import React from 'react';

const Card = ({title,summary,link,index}) => {
  return (
    <div className='p-4 bg-gray-300 h-100 w-150 shadow-md rounded-lg flex flex-col justify-between'>
      <div>
        <h2 className='text-xl text-center text-gray-900 font-bold mb-2'>Title</h2>
        <p className='text-gray-600 mb-4 text-center'>this is where the summary is going to be at</p>
      </div>
      <div className='flex flex-col items-center'>
        
        <div className='flex space-x-30 justify-center'>
          <button  className='w-24 px-4 py-2 bg-blue-500 text-white rounded'>Previous</button>
          <a href= '/' className='text-blue-500 mb-4 block'>src article</a>
          <button   className='w-24 px-4 py-2 bg-gray-500 text-white rounded'>Next</button>
        </div>
      </div>
    </div>
  );
}

export default Card;
