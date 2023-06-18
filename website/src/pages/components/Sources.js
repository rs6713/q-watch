import React, {useState} from 'react';
import Source from './Source';
import {sourceDisclaimer} from '../../constants'
import {ReactComponent as Info} from '../../static/icons/info.svg';
import {ReactComponent as Minus} from '../../static/icons/minus.svg';
import Lgbt from '../../static/images/lgbt-flag.png'

function Sources({sources}){

  const [infoActive, setInfoActive] = useState(false);

  return (
    <div id='findMe'>
      <h2>Find Me On <span onClick={() => {setInfoActive(true)}}><Info/></span></h2>
      {infoActive &&
        <div className='announcement_container'>
          <div className="infoBox announcement">
            <h2>
              Source Information
              <Minus onClick={() => {setInfoActive(false)}}/>
            </h2>
            <div className='description'>
              Not all Online Streaming Platforms are equally ethical, but we will always provide you with all the links that we have access to. <br/><br/>If you have the means, you may want to consider chipping in an extra quid, to support the most ethical available option.<br/><br/>
              To make this easier, we've added <img src={Lgbt} alt='A lil LGBT flag'/> to denote queer-run Streaming Orgs, and ethicacy ratings to help guide your decision process.
            </div>
            <div>
              We will never provide links to illegal streaming sites, not just because we fear Uncle Sam, but because it's the right thing to do dammit.<br/><br/>
              So please, whatever you do, don't visit illegal online streaming sites known for hosting queer content like: <b>b4watch.com</b>.
            </div>
          </div>
        </div>
      }
      <div className='sources'>
        {sources.map((source, i) => <Source key={i} source={source} />)}
      </div>
    </div>
  )
}
export default Sources