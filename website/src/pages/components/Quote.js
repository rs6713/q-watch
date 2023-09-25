import React from 'react';
import HTMLString from 'react-html-string';

function Quote({quote}){
  if(quote === null || quote === undefined || quote.length === 0){
    return <></>
  }

  return (
    <div id="quote"> &#x1f60d;
      <HTMLString html={'<p>' + quote + '</p>'}/>
    </div>
  )
}

export default Quote