import React from 'react';


function Button({ text, onClick, symbol}){

  return <div className='button' onClick={onClick}>
    {text}
    {symbol}
  </div>

}

export default Button