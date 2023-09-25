import React from 'react';
import {ReactComponent as QuoteLeft} from '../../static/icons/quote-left.svg';
import {ReactComponent as QuoteRight} from '../../static/icons/quote-right.svg';
import HTMLString from 'react-html-string';

function Opinion({opinion}){
  if(opinion === null || opinion === undefined || opinion.length === 0){
    return <></>
  }

  return (
    <div id="opinion">
      <QuoteLeft id='quoteleft' />
      <QuoteRight id='quoteright' />
      <HTMLString html={opinion}/>
    </div>
  )
}

export default Opinion