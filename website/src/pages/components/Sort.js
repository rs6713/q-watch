import React from 'react';
import {ReactComponent as Caret} from '../../static/icons/caret.svg'
import {useState} from 'react';

const SORT = {
  "Most Popular": ["NUM_RATING", -1],
  "Least Popular": ["NUM_RATING", 1],
  "Highest Rating": ["AVG_RATING", -1],
  "Lowest Rating": ["AVG_RATING", 1],
  "Most Recent Release": ["YEAR", -1],
  "Least Recent Release": ["YEAR", 1],
}

function Sort({updateSort, sort}){
  function clickSort(sortKey){
    updateSort(SORT[sortKey]);
  }

  return (
    <div id="Sort">
      <div>Sort <Caret/></div>
      <ul id="SortOptions">
        {Object.keys(SORT).map(key => (
          <li key={key} className={(sort[0] === SORT[key][0] && sort[1] === SORT[key][1]) ? 'active' : ''} onClick={()=>{clickSort(key)}}>{key}</li>
        ))}
      </ul>
    </div>
  )
}

export default Sort
