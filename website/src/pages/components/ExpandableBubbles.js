import {useState} from 'react';
import Bubbles from './Bubbles.js';
import {ReactComponent as Plus} from '../../static/icons/plus.svg'
import {ReactComponent as Minus} from '../../static/icons/minus.svg'

function ExpandableBubbles({expandable, title, aside, subtitle, items, clickAction}){
  const [active, setActive] = useState(expandable? false : true)

  if(items.length === 0){
    return <></>
  }

  return (
    <div className="expandable_bubbles">
      <h2>{title}
      {expandable !== false && active && <Minus title="" aria-label={"Click to hide " + title} onClick={()=>{setActive(false)}}/>}
      {expandable !== false && !active && <Plus title="" aria-label={"Click to see " + title} onClick={()=>{setActive(true)}} />}
      {aside && (!active || !expandable) && <span>{aside}</span>}
      
      </h2>
      {subtitle && <p>{subtitle}</p>}
      {active && 
        <Bubbles items={items} clickAction={clickAction} />
      }
    </div>
  )
}

export default ExpandableBubbles