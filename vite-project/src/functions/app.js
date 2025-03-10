async function getData(){
    try{
        const response= await fetch('http://127.0.0.1:3000/summaries');

        const data=  await response.json();
        console.log(data);
        return data.summaries;
        
    }catch{
        console.error('shit didnt work')
    }
}

export default getData;

