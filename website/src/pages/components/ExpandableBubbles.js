import {useState} from 'react';
import Bubbles from './Bubbles.js';
import React from 'react';
import {ReactComponent as Plus} from '../../static/icons/plus.svg'
import {ReactComponent as Minus} from '../../static/icons/minus.svg'

function ExpandableBubbles({expandable, title, aside, subtitle, items, clickAction}){
  const [active, setActive] = useState(expandable? false : true)

  if(items === null || items.length === 0){
    return <></>
  }

  const Minimize = active ? <Minus title="" aria-label={"Click to hide " + title} onClick={()=>{setActive(false)}}/> : <Plus title="" aria-label={"Click to see " + title} onClick={()=>{setActive(true)}} />;

  return (
    <div className="expandable_bubbles">
      <h2>{title}

      {expandable !== false && <span className='explainer'>
        {Minimize}
        {!active && <span> {aside}</span>}
      </span>}

      {/* {aside && (!active || !expandable) && <span className='explainer'><span>{aside}</span></span>}
       */}
      </h2>
      {subtitle && <p>{subtitle}</p>}
      {active && 
        <Bubbles items={items} clickAction={clickAction} />
      }
    </div>
  )
}

export default ExpandableBubbles