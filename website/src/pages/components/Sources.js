import React from 'react';
import Source from './Source';
import {sourceDisclaimer} from '../../constants'
import {ReactComponent as Info} from '../../static/icons/info.svg';

function Sources({sources}){
  return (
    <div id='findMe'>
      <h2>Find Me On <Info/></h2>
      {/* <span className="disclaimer">({sourceDisclaimer})</span> */}
      <div className='sources'>
        {sources.map((source, i) => <Source key={i} source={source} />)}
      </div>
    </div>
  )
}
export default Sources