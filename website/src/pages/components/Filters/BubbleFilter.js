import React from 'react';
import {useEffect, useState} from 'react';
import Switch from '../Switch';
import ExpandableBubbles from '../ExpandableBubbles';

function BubbleFilter({filter, updateFilters, filters}){

  //const [switchState, setSwitchState] = useState(false);
  const switchState = filters[filter['id']] !== undefined && filters[filter['id']]['RULE'] == 'AND' ? true: false
  const requireSwitchState = filters[filter['id']] !== undefined && filters[filter['id']][filter['requirement']] ? true: false
  //console.log('Bubblefilter ', filters[filter['id']])

  const bubbleItems = filter.filters;

  // useEffect(()=>{

  //   if(filter.switchType === 'include'){
  //     let currentIds = filter.filters.filter(f => f.active).map(f => f.ID);
  //     let newFilters = {
  //       [filter['id']]: {
  //         'TYPE': 'INCLUDE',
  //         'RULE': switchState? 'AND' : 'OR',
  //         'VALUE': currentIds//filters[filter['id']]['VALUE']
  //       }
  //     }
  //     if(requireSwitchState && filter['requirement']){
  //       newFilters[filter['id']]['REQUIREMENT'] = filter['requirement']
  //     }
  //     if(currentIds.length > 0){
  //       console.log(newFilters)
  //       updateFilters(
  //         newFilters
  //       )
  //     }
  //   }
  // }, [switchState, requireSwitchState])

  function setSwitchState(switchState){
    let newFilters = filters[filter['id']]
    if(newFilters === undefined) return;
    newFilters['RULE'] = switchState ? 'AND': 'OR'
    updateFilters({
      [filter['id']]: newFilters
    })
  }
  function setRequireSwitchState(newState){
    let newFilters = filters[filter['id']];
    if(newFilters === undefined) return;
    if(newState){
      newFilters[filter['requirement']] = 1
    }else{
      newFilters[filter['requirement']] = null;
    }
    
    updateFilters({
      [filter['id']]: newFilters
    })
  }


  function bubbleSelect(itemId){
    let currentIds = filters[filter['id']] === undefined? []: filters[filter['id']]['VALUE'];
    let req = {};
    if(filter['requirement']){
      req = {[filter['requirement']]: requireSwitchState? 1: null}
    }

    let rule = switchState? 'AND' : 'OR';

    if(filter["switchType"] === "include"){
      // Toggle item in/out of filter list
      if(currentIds.indexOf(itemId) !== -1){
        currentIds.splice(currentIds.indexOf(itemId), 1)
        if(currentIds.length === 0){
          updateFilters({[filter['id']]: null});
        }else{
          updateFilters({[filter['id']]: {'TYPE': 'INCLUDE', 'RULE': rule, 'VALUE': currentIds, ...req}});
        }
      }else{
        updateFilters({[filter['id']]: {'TYPE': 'INCLUDE', 'RULE': rule, 'VALUE':[...currentIds, itemId], ...req}})
      }
    }
    //{VALUE: [1,2], TYPE: 'INCLUDE', RULE: 'ALL'}
    if(filter["switchType"] === "exclude"){
      if(currentIds.indexOf(itemId) !== -1){
        currentIds.splice(currentIds.indexOf(itemId), 1)
        if(currentIds.length === 0){
          updateFilters({[filter['id']]: null});
        }else{
          updateFilters({[filter['id']]: {'TYPE': 'EXCLUDE', 'VALUE': currentIds, ...req}});
        }
      }else{
        updateFilters({[filter['id']]: {'TYPE': 'EXCLUDE', 'VALUE': [...currentIds, itemId], ...req}})
      }
    }
  }

  let onMessage = <div>I want a movie that matches <b>all</b> of these labels.</div>
  let offMessage = <div>I want a movie that matches <b>any</b> of these labels.</div>

  let requireSwitch = <></>;
  if(filter["requirement"] !== undefined){
    requireSwitch = <Switch state={requireSwitchState} setState={setRequireSwitchState} onMessage={filter['onRequirementMessage']} offMessage={filter["offRequirementMessage"]}/>
  }

  return (
    <div className='LabelFilter'>
      <ExpandableBubbles
        title={filter.title}
        aside={filter.warning || ""}
        items={bubbleItems}
        clickAction={bubbleSelect}
        expandable={filter.expandable || false}
        subtitle={filter.subtitle}
      />
      {filter.switchType === 'include' &&
        <Switch state={switchState} setState={setSwitchState} onMessage={onMessage} offMessage={offMessage}/>
      }
      {requireSwitch}
    </div>
  )
}

export default BubbleFilter