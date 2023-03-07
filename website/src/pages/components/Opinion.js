import React from 'react';
import {ReactComponent as QuoteLeft} from '../../static/icons/quote-left.svg';
import {ReactComponent as QuoteRight} from '../../static/icons/quote-right.svg';


function Opinion({opinion}){
  if(opinion === null || opinion === undefined || opinion.length === 0){
    return <></>
  }

  return (
    <div id="opinion">
      <QuoteLeft id='quoteleft' />
      <QuoteRight id='quoteright' />
      {opinion}
    </div>
  )
}

export default Opinion