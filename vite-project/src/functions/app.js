async function getData(){
    try{
        const response= await fetch('https://news-sum-sjw4.onrender.com/summaries');

        const data=  await response.json();
        console.log(data);
        return data.summaries;
        
    }catch{
        console.error('shit didnt work')
    }
}

export default getData;

