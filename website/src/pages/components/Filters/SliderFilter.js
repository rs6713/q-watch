import React from 'react';
import {useEffect, useState} from 'react';
import Filters from '../Filters';
import {Icon} from '../Image'
import Switch from '../Switch'

function SliderFilter({
  filter, // Filter specification
  updateFilters, // Update selected filter options
  filters, // Filters currently selected
  randomIdx}){

  const [selectedOption, atLeast] = getSelectedOption();

  // The current position of the toggle
  // (depends on selectedOption (filters input) & whether user moving toggle)
  const [toggleLeft, setToggleLeft] = useState(
    getOptionTogglePosition(selectedOption)
  );

  // On changed selectedOption toggle switches to that position.
  useEffect(() => {
    setToggleLeft(
      getOptionTogglePosition(selectedOption)
    )
  }, [selectedOption])

  function getSelectedOption(){
    /* Get [selectedOption, atLeastMode] to be used by UI*/
    let currentOption = filters[filter['id']];
    if(currentOption){

      let top_id = Array.isArray(currentOption['VALUE'])? Math.max(...currentOption['VALUE']): currentOption['VALUE'];

      // For Exclude the true top id is above
      if(currentOption['TYPE'] == 'EXCLUDE'){
        for(let filterOption of filter.filters){
          if(filterOption.ID > top_id || top_id === undefined){
            top_id = filterOption.ID
            break;
          }
        }
      }
      let topOption = filter.filters.filter(f=> f.ID == top_id)[0]
      if(filter['type'] === 'slider' ){
        return [
          topOption,
          currentOption['TYPE'] == 'INCLUDE' ? false: true // atLeast
        ]
      }
      if(filter['type'] === 'rangeslider'){
        return [
          topOption,
          currentOption['TYPE'] == 'LESS_THAN' ? false: true // atLeast
        ]
      }
    }
    // Include all filter options upto/including final option, include, by default
    return [filter && filter.filters ? filter.filters[filter.filters.length - 1]: null, false]
  }


  function updateFiltersOption(option, atLeast){
    /* Update filter options selected, with option & atLeast mode */
    var validIds = [];
    if(filter.type === 'slider'){
      
      for(let filterOption of filter.filters){
        if(filterOption.ID < option.ID){
            validIds.push(filterOption.ID)
        }
        // Include
        if(!atLeast && filterOption.ID == option.ID){
          validIds.push(filterOption.ID)
        }
      }
      updateFilters({[filter['id']]: {
        'TYPE': atLeast? 'EXCLUDE': 'INCLUDE',
        'VALUE': validIds
      }})
    }
    if(filter.type === 'rangeslider'){
      updateFilters({[filter['id']]: {
        'TYPE': atLeast? 'GREATER_THAN': 'LESS_THAN',
        'VALUE': option.ID,
      }})
    }
  }

  function getOptionClass(option){
    let cls = 'SliderOption';
    if(selectedOption && option.ID === selectedOption.ID){
      cls += " active"
    }
    if(option.ICON){
      return cls + ' SliderIcon'
    }else{
      return cls
    }
  }

  function moveToggle(e){
    /* Move toggle when mode active according to user movement */
    //if(toggleActive){
      var rect = document.getElementById('bar').getBoundingClientRect();
      var x = e.clientX - rect.left;
      setToggleLeft(
        `${x}px`
      )
    //}
  }

  function releaseToggle(e){
    // Snap toggle to nearest choice
    // Choose that element
    let nearestDistance = 10000;
    let nearestOptionIdx = null;
    var i = 0;
    for(let option of filter.filters){
      let optionX = document.getElementById(String(option.ID + randomIdx)).getBoundingClientRect();
      optionX = (optionX.left + optionX.right) / 2;
      if(Math.abs(e.clientX - optionX) < nearestDistance){
        nearestOptionIdx = i;
        nearestDistance = Math.abs(e.clientX - optionX);
      }
      i = i + 1;
    }
    document.removeEventListener('mousemove', moveToggle);
    document.removeEventListener('mouseup', releaseToggle);
    updateFiltersOption(filter.filters[nearestOptionIdx], atLeast);
  }

  function getOptionTogglePosition(selectedOption){
    /* Calculate left position (for toggle) based on selected option */
    if(selectedOption && document.getElementById('bar') && document.getElementById(String(selectedOption.ID + randomIdx))){
      let optionX = document.getElementById(String(selectedOption.ID + randomIdx)).getBoundingClientRect();
      let sliderLeft = document.getElementById('bar').getBoundingClientRect().left;
      let toggleWidth = document.getElementById('toggle').clientWidth;
      return  `${(optionX.left + optionX.right) / 2 - sliderLeft - (toggleWidth/2)}px`
    }
    return 0
  }

  function getBarStyle(){
    /* Which part of the bar is highlighted depends on whether atLeast mode is true */
    if(atLeast){
      return {
        'left': toggleLeft,
      }
    }
    return {
      'width': toggleLeft,
      'left': 0
    }
  }
  function turnOnToggle(){
    document.addEventListener('mousemove', moveToggle);
    document.addEventListener('mouseup', releaseToggle);
  }

  if(selectedOption === null || !filter.filters){
    return <></>
  }
  let optionDescription = selectedOption && selectedOption.LABEL?<><h3>{selectedOption.LABEL}</h3>
  <p>{selectedOption.DESCRIP}</p></> : null;

  

  return (
    <div className='SliderFilter'>
      <h2>
        {filter.title}
      </h2>
      <div className='Slider' >
        {optionDescription}
        <div id='bar'>
          <div id='barOverlay' style={getBarStyle()} />
          <div id='toggle' onMouseDown={turnOnToggle}  style={{'left': toggleLeft}}></div>
        </div>
        <div className='SliderOptions'>
        {filter.filters.map((option) => {
          return <div className={getOptionClass(option)} id={String(option.ID + randomIdx)} key={option.ID} onClick={()=>updateFiltersOption(option, atLeast)}>
              {option.ICON && <Icon name={option.ICON} className={'icon'} label={option.LABEL} />}
              {!option.ICON && option.ID}
            </div>
          })}
        </div>
        <Switch state={atLeast} setState={(al) => {updateFiltersOption(selectedOption, al)}} onMessage={<div>{filter.onMessage}</div>} offMessage={<div>{filter.offMessage}</div>}/>
      </div>
    </div>
  )
}

export default SliderFilter