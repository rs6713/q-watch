import React, { Component, useState, useEffect} from 'react';

import {
  generateCriteriaDescription,
} from '../search';
import {ReactComponent as Copy} from '../../static/icons/copy.svg'
import {ReactComponent as Minus} from '../../static/icons/minus.svg'

function Share({nMatches, setShareActive, labels, criteria}){
  const [linkCopied, setLinkCopied] = useState(false);
  return (
    <div className='announcement_container'>
      <div className='announcement'>
        <h2>
          Share Search - {nMatches} 
          <Minus onClick={()=>{setShareActive(false)}}/>
        </h2>
        <table className='description'>
            {generateCriteriaDescription(labels, criteria).map(item => {
              return <tr>
                <td>{item.TITLE}</td>
                <td>{item.DESCRIP}</td>
              </tr>
            })}
            {Object.keys(criteria).length == 0 && <div>
              <div>No Criteria</div>
              <br/>
              <span><b>Woww...</b> So you just like a little bit of everything, right?? &#128539;</span>
            </div>}
        </table>
        <div className='callToAction' onClick={()=>{navigator.clipboard.writeText(window.location.href); setLinkCopied(true);}}>
          <Copy/>
          <span>{linkCopied? 'Link Copied!' : 'Copy Link to Search'}</span>
        </div><br/>
        {!nMatches && <div>
            Look, we can't stop you from sharing a link to an empty list, but it's a cruel thing to do. &#128514;
        </div>}
      </div>
    </div>
  )
}
export default Share