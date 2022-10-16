import {useEffect, useState} from 'react';
import {Icon} from '../Image'
import Switch from '../Switch'

function SliderFilter({filter, updateFilters}){
  const [selectedOption, setSelectedOption] = useState(
    filter !== null && filter.filters !== null ? filter.filters[filter.filters.length-1]: null
  )
  const [toggleActive, setToggleActive] = useState(false);
  const [toggleLeft, setToggleLeft] = useState(0);
  const [atLeast, setAtLeast] = useState(false);

  useEffect(()=>{
    if(filter !== null && filter.filters !== null && filter.filters.length > 0){
      chooseOption(filter.filters[filter.filters.length-1])
    }
  }, [filter])

  useEffect(() =>{
    setSnapPosition();
  }, [selectedOption])

  useEffect(()=>{
    chooseOption(selectedOption)
  }, [atLeast])

  if(selectedOption === null){
    return <></>
  }

  function chooseOption(option){
    setSelectedOption(option);
    
    var validIds = [];
    console.log(option)
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
    console.log('ValidIds: ', validIds)
    updateFilters({[filter['id']]: {
      'TYPE': atLeast? 'EXCLUDE': 'INCLUDE',
      'VALUE': validIds
    }})
  }

  function getOptionClass(option){
    if(option.ID === selectedOption.ID){
      return "active SliderOption"
    }
    return 'SliderOption'
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

  function releaseToggle(e){
    if(toggleActive){
      // Snap toggle to nearest choice
      // Choose that element
      let nearestDistance = 10000;
      let nearestOptionIdx = null;
      var i = 0;
      for(let option of filter.filters){
        let optionX = document.getElementById(option.ID).getBoundingClientRect();
        optionX = (optionX.left + optionX.right) / 2;
        if(Math.abs(e.clientX - optionX) < nearestDistance){
          nearestOptionIdx = i;
          nearestDistance = Math.abs(e.clientX - optionX);
        }
        i = i + 1;
      }

      setToggleActive(false);
      chooseOption(filter.filters[nearestOptionIdx]);
    }
  }



  function setSnapPosition(){
    if(selectedOption !== null){
      let optionX = document.getElementById(selectedOption.ID).getBoundingClientRect();
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

  return (
    <div className='SliderFilter'>
      <h2>{filter.title}</h2>
      <div className='Slider' onMouseMove={moveToggle} onMouseUp={releaseToggle}>
        <h3>{selectedOption.LABEL}</h3>
        <p>{selectedOption.DESCRIP}</p>
        <div id='bar'>
          <div id='barOverlay' style={getBarStyle()} />
          <div id='toggle' onMouseDown={()=>{setToggleActive(true)}}  style={{'left': toggleLeft}}></div>
        </div>
        <div className='SliderOptions'>
        {filter.filters.map((option) => {
          return <div className={getOptionClass(option)} id={option.ID} key={option.ID} onClick={()=>chooseOption(option)}>
              {Icon(option.ICON, 'icon')}
            </div>
          })}
        </div>
        <Switch state={atLeast} setState={setAtLeast} onMessage="I'm a person.... A person with needs" offMessage='No more than this please. (Think of the children!)'/>
      </div>
    </div>
  )
}

export default SliderFilter