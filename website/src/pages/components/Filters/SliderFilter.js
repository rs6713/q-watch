import React from 'react';
import {useEffect, useState} from 'react';
import Filters from '../Filters';
import {Icon} from '../Image'
import Switch from '../Switch'

function SliderFilter({
  filter,
  updateFilters,
  filters,
  randomIdx}){

  const [toggleActive, setToggleActive] = useState(false);
  
  let currentSelectedOption = getSelectedOption();
  console.log('SliderFilter currentselectedoption: ', filter['id'], currentSelectedOption)
  const atLeast = currentSelectedOption[1];
  const [selectedOption, setSelectedOption] = useState(
    currentSelectedOption[0]
  )
  const [active, setActive] = useState(false)
  console.log('Current selected option 0: ', currentSelectedOption[0])
  const [toggleLeft, setToggleLeft] = useState(
    currentSelectedOption[0]? getOptionTogglePosition(currentSelectedOption[0]) : 0
  );
  // if(filters[filter['id']]){
  //   setSnapPosition(selectedOption)
  // }

  useEffect(()=>{
    let cso = getSelectedOption();
    setSelectedOption(cso[0]);
    //setAtLeast = cso[1]
  }, [filters, filter])
  useEffect(() => {
    setToggleLeft(
      getOptionTogglePosition(selectedOption)
    )
  }, [selectedOption])

  console.log('SlideFilter: ', filter,  filter['id'], filters[filter['id']])

  function getSelectedOption(){
    let currentOption = filters[filter['id']];
    if(currentOption){
      console.log('selected slidefilter: ', currentOption)

      //atLeast? 'EXCLUDE': 'INCLUDE',
      let top_id = Array.isArray(currentOption['VALUE'])?Math.max(...currentOption['VALUE']): currentOption['VALUE']
      console.log('Available filters: ', filter.filters, top_id)
      let topOption = filter.filters.filter(f=> f.ID == top_id)[0]
      console.log('Topoption: ', topOption)
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
    return [filter && filter.filters ? filter.filters[filter.filters.length - 1]: null, false]
  }

  useEffect(()=>{
    if(active){
      chooseOption(selectedOption)
    }
  }, [atLeast])

  function updateFiltersOption(option, atLeast){
    var validIds = [];
    if(filter.type === 'slider'){
      
      for(let filterOption of filter.filters){
        if(filterOption.ID === option.ID){
          if(!atLeast){
            validIds.push(filterOption.ID)
          }
          break;
        }
        validIds.push(filterOption.ID)
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

  function chooseOption(option){
    setActive(true)
    setSelectedOption(option);
    setSnapPosition(option);

    updateFiltersOption(option, atLeast)

  }
  function setAtLeast(atLeast){
    updateFiltersOption(selectedOption, atLeast)
  }

  function getOptionClass(option){
    let cls = 'SliderOption';
    if(selectedOption && option.ID === selectedOption.ID){
      cls += " active"
    }
    if(option.ICON){
      return cls + ' SliderIcon'
    }else{
      return cls// + ' SliderDot'
    }
  }

  function moveToggle(e){
    
    if(toggleActive){
      var rect = document.getElementById('bar').getBoundingClientRect();
      var x = e.clientX - rect.left;
      setToggleLeft(
        `${x}px`
      )
    }
  }

  let nearestOptionIdx = null;
  function releaseToggle(e){
    
    if(toggleActive){
      // Snap toggle to nearest choice
      // Choose that element
      let nearestDistance = 10000;
      
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
      setToggleActive(false);
      chooseOption(filter.filters[nearestOptionIdx]);
    }
  }

  function getOptionTogglePosition(selectedOption){
    if(selectedOption && document.getElementById('bar') && document.getElementById(String(selectedOption.ID + randomIdx))){
    let optionX = document.getElementById(String(selectedOption.ID + randomIdx)).getBoundingClientRect();
    let sliderLeft = document.getElementById('bar').getBoundingClientRect().left;
    let toggleWidth = document.getElementById('toggle').clientWidth;
    return  `${(optionX.left + optionX.right) / 2 - sliderLeft - (toggleWidth/2)}px`
    }
  }


  function setSnapPosition(selectedOption){
    if(selectedOption !== null){

      setToggleLeft(
       getOptionTogglePosition(selectedOption)
      )
    }
  }

  function getBarStyle(){
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
  let mm, mu, mo;
  useEffect(()=>{
    if(toggleActive){
      document.addEventListener('mousemove', moveToggle);
      document.addEventListener('mouseup', releaseToggle);
    }
      //document.addEventListener('mouseout', releaseToggle);
    // }else{
    //   console.log('removing movetoggle')
    //   document.removeEventListener('mouemove', moveToggle)
    // }
    // }else{

    //     console.log('Event Listeners removing')
    //     //document.removeEventListener('mousemove', moveToggle);
    //     document.removeEventListener('mouseup', releaseToggle);
    //     document.removeEventListener('mouseout', releaseToggle);
        

    // }


    // return function (){
    //   document.removeEventListener(mm);
    //   document.removeEventListener(mu);
    //   document.removeEventListener(mo);
    // }
  }, [toggleActive])//toggleActive


  if(selectedOption === null || !filter.filters){
    return <></>
  }
  console.log('Trying ot generate optiondescription: ', selectedOption)
  let optionDescription = selectedOption && selectedOption.LABEL?<><h3>{selectedOption.LABEL}</h3>
  <p>{selectedOption.DESCRIP}</p></> : null;

  function mouseDown(){
    if(!active){
      setActive(true);
    }
    setToggleActive(true)
  }


  //document.onMouseUp = releaseToggle;
  //document.onmouseout = releaseToggle;
  //document.onmousemove = moveToggle;
  //onMouseMove={moveToggle} 
  //onMouseUp={releaseToggle}
  return (
    <div className='SliderFilter'>
      <h2>
        {filter.title}
      </h2>
      <div className='Slider' >
        {optionDescription}
        <div id='bar'>
          <div id='barOverlay' style={getBarStyle()} />
          <div id='toggle' onMouseDown={mouseDown}  style={{'left': toggleLeft}}></div>
        </div>
        <div className='SliderOptions'>
        {filter.filters.map((option) => {
          return <div className={getOptionClass(option)} id={String(option.ID + randomIdx)} key={option.ID} onClick={()=>chooseOption(option)}>
              {option.ICON && <Icon name={option.ICON} className={'icon'} label={option.LABEL} />}
              {!option.ICON && option.ID}
            </div>
          })}
        </div>
        <Switch state={atLeast} setState={setAtLeast} onMessage={<div>{filter.onMessage}</div>} offMessage={<div>{filter.offMessage}</div>}/>
      </div>
    </div>
  )
}

export default SliderFilter