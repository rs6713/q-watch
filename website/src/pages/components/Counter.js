import React, { useState, useEffect } from 'react';


function Counter({total}){

  const [count, setCount] = useState(100);
  

  function incrementCounter(){
    if(count < total){
      if((total - count) > 20){
        setCount(count + 5);
      }else{
        setCount(count + 1)
      }
    }
  }
  useEffect(()=>{
    if(count > 100 && count < total){
      if((total - count) < 20){
        setTimeout(incrementCounter, 100 - ((total - count)* 4.5))
      }else{
        setTimeout(incrementCounter, 20);
      }
    }
  }, [count])

  function monitorScroll(){
    var element = document.getElementById('Counter');
    var position = element.getBoundingClientRect();

    if(position.top >= 0 && position.top <= window.innerHeight) {
      if(count === 100){
        window.removeEventListener('wheel', monitorScroll);
        incrementCounter();
      }
    }

  }

  useEffect(()=>{
    window.addEventListener('wheel', monitorScroll);

    return () => window.removeEventListener('wheel', monitorScroll)
  }, []);



  return <span id='Counter'>{count >0 ? count : ''}</span>
}

export default Counter