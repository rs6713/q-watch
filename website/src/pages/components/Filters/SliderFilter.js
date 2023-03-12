import React from 'react';
import {useEffect, useState} from 'react';
import {Icon} from '../Image'
import Switch from '../Switch'

function SliderFilter({filter, updateFilters, filters, randomIdx}){
  console.log('Slider: ', filter.filters)
  
  const [toggleActive, setToggleActive] = useState(false);
  const [toggleLeft, setToggleLeft] = useState(0);
  const [atLeast, setAtLeast] = useState(false);
  const [selectedOption, setSelectedOption] = useState(
    filter !== null && filter.filters !== null  ? filter.filters[filter.filters.length-1]: null
  )
  const [active, setActive] = useState(false)

  useEffect(()=>{
    console.log('choosing option due to atleast')
    if(active){
      chooseOption(selectedOption)
    }
  }, [atLeast])

  function chooseOption(option){
    setActive(true)
    setSelectedOption(option);
    setSnapPosition(option);
    
    var validIds = [];
    console.log('Selected Option:', option)
    if(filter.type === 'slider'){
      
      for(let filterOption of filter.filters){
        console.log(filterOption.ID, option.ID)
        if(filterOption.ID === option.ID){
          if(!atLeast){
            validIds.push(filterOption.ID)
          }
          break;
        }
        validIds.push(filterOption.ID)
      }
      console.log(filter.title, 'ValidIds: ', validIds)
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
    if(option.ID === selectedOption.ID){
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
      console.log('movetoggle')
      var rect = document.getElementById('bar').getBoundingClientRect();
      var x = e.clientX - rect.left;
      console.log(x)
      setToggleLeft(
        `${x}px`
      )
    }else{
      console.log('move toggle no active')
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
        console.log(String(option.ID + randomIdx))
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


  function setSnapPosition(selectedOption){
    if(selectedOption !== null){
      let optionX = document.getElementById(String(selectedOption.ID + randomIdx)).getBoundingClientRect();
      let sliderLeft = document.getElementById('bar').getBoundingClientRect().left;
      let toggleWidth = document.getElementById('toggle').clientWidth;

      
      setToggleLeft(
        `${(optionX.left + optionX.right) / 2 - sliderLeft - (toggleWidth/2)}px`
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


  if(selectedOption === null){
    return <></>
  }
  let optionDescription = selectedOption.LABEL?<><h3>{selectedOption.LABEL}</h3>
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