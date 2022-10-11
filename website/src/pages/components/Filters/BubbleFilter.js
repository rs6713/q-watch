import {useState} from 'react';
import Switch from '../Switch';
import ExpandableBubbles from '../ExpandableBubbles';

function BubbleFilter({filter, updateFilters, filters}){

  const [switchState, setSwitchState] = useState(false);

  function bubbleSelect(itemId, filter){
    let currentIds = filters[filter['id']] || [];
    // Toggle item in/out of filter list
    if(currentIds.indexOf(itemId) !== -1){
      currentIds.splice(currentIds.indexOf(itemId))
      if(currentIds.length === 0){
        updateFilters({[filter['id']]: null});
      }else{
        updateFilters({[filter['id']]: currentIds});
      }
    }else{
      updateFilters({[filter['id']]: [...currentIds, itemId]})
    }
  }

  let onMessage = <div>I want a movie that matches <b>all</b> of these labels.</div>
  let offMessage = <div>I want a movie that matches <b>any</b> of these labels.</div>

  return (
    <div className='LabelFilter'>
      <ExpandableBubbles
        title={filter.title}
        aside={filter.warning || ""}
        items={filter.filters}
        clickAction={(itemId) => {bubbleSelect(itemId, filter)}}
        expandable={filter.expandable || false}
        subtitle={filter.subtitle}
      />
      <Switch state={switchState} setState={setSwitchState} onMessage={onMessage} offMessage={offMessage}/>
    </div>
  )
}

export default BubbleFilter