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
              Not all Online Streaming Platforms are equally ethical, but we will always provide you with all the links that we have access to. <br/><br/><b>Supporting, and renting from Queer Run Organisations (denoted <img src={Lgbt} alt='A lil LGBT flag'/>), if you have the means, can be a great way to give love back to the community.</b> 
            </div>
            <div>
              There's an argument we've heard on the grapevine &#127815;, that illegal streaming by individuals who never had the means to purchase, deprives nothing of the media creator. <br/><br/>
              Of course, we could never legally endorse such ideas, so please make sure you avoid sites known for hosting free queer content like: <b>b4watch.com</b>. &#128521;
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