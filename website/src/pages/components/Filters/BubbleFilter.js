import React from 'react';
import {useEffect, useState} from 'react';
import Switch from '../Switch';
import ExpandableBubbles from '../ExpandableBubbles';

function BubbleFilter({filter, updateFilters}){

  const [switchState, setSwitchState] = useState(false);

  useEffect(()=>{

    if(filter.switchType === 'include'){
      let currentIds = filter.filters.filter(f => f.active).map(f => f.ID);
      if(currentIds.length > 0){
        updateFilters(
          {
            [filter['id']]: {
              'TYPE': 'INCLUDE',
              'RULE': switchState? 'AND' : 'OR',
              'VALUE': currentIds//filters[filter['id']]['VALUE']
            }
          }
        )
        }
    }
  }, [switchState])

  function bubbleSelect(itemId){
    let currentIds = filter.filters.filter(f => f.active).map(f => f.ID);

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