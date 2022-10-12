import {useEffect, useState} from 'react';
import Switch from '../Switch';
import ExpandableBubbles from '../ExpandableBubbles';

function BubbleFilter({filter, updateFilters, filters}){

  const [switchState, setSwitchState] = useState(false);

  useEffect(()=>{
    if(filter.switchType === 'include'){
      if(filters[filter['id']] !== undefined){
        updateFilters(
          {
            [filter['id']]: {
              'TYPE': 'INCLUDE',
              'RULE': switchState? 'AND' : 'OR',
              'VALUE': filters[filter['id']]['VALUE']
            }
          }
        )
        }
    }
  }, [switchState])

  function bubbleSelect(itemId){
    console.log('bubbleselect')
    let currentIds = filters[filter['id']] !== undefined? (filters[filter['id']]['VALUE'] || []) : [];
    console.log(currentIds)
    let rule = switchState? 'AND' : 'OR';

    if(filter["switchType"] === "include"){
      // Toggle item in/out of filter list
      if(currentIds.indexOf(itemId) !== -1){
        currentIds.splice(currentIds.indexOf(itemId))
        if(currentIds.length === 0){
          updateFilters({[filter['id']]: null});
        }else{
          updateFilters({[filter['id']]: {'TYPE': 'INCLUDE', 'RULE': rule, 'VALUE': currentIds}});
        }
      }else{
        updateFilters({[filter['id']]: {'TYPE': 'INCLUDE', 'RULE': rule, 'VALUE':[...currentIds, itemId]}})
      }
    }
    //{VALUE: [1,2], TYPE: 'INCLUDE', RULE: 'ALL'}
    if(filter["switchType"] === "exclude"){
      console.log('exclude')
      if(currentIds.indexOf(itemId) !== -1){
        currentIds.splice(currentIds.indexOf(itemId))
        if(currentIds.length === 0){
          updateFilters({[filter['id']]: null});
        }else{
          updateFilters({[filter['id']]: {'TYPE': 'EXCLUDE', 'VALUE': currentIds}});
        }
      }else{
        updateFilters({[filter['id']]: {'TYPE': 'EXCLUDE', 'VALUE': [...currentIds, itemId]}})
      }
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
        clickAction={bubbleSelect}
        expandable={filter.expandable || false}
        subtitle={filter.subtitle}
      />
      {filter.switchType === 'include' &&
        <Switch state={switchState} setState={setSwitchState} onMessage={onMessage} offMessage={offMessage}/>
      }
    </div>
  )
}

export default BubbleFilter