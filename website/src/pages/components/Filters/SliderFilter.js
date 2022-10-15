import {useEffect, useState} from 'react';
import {Icon} from '../Image'

function SliderFilter({filter, updateFilters, filters}){


  const [selectedOption, setSelectedOption] = useState(
    filter !== null && filter.filters !== null ? filter.filters[0]: null
  )


  const [toggleActive, setToggleActive] = useState(false);
  const [toggleLeft, setToggleLeft] = useState(0);

  useEffect(()=>{
    if(filter !== null && filter.filters !== null && filter.filters.length > 0){
      setSelectedOption(filter.filters[0])
    }
  }, [filter])

  if(selectedOption === null){
    return <></>
  }

  function chooseOption(option){
    setSelectedOption(option);
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
    console.log(i)

    let optionX = document.getElementById(filter.filters[nearestOptionIdx].ID).getBoundingClientRect();
    let sliderLeft = document.getElementById('bar').getBoundingClientRect().left;
    let toggleWidth = document.getElementById('toggle').clientWidth;

    setToggleActive(false);
    chooseOption(filter.filters[nearestOptionIdx]);
    setToggleLeft(
      `${(optionX.left + optionX.right) / 2 - sliderLeft - (toggleWidth/2)}px`
    )
  }

  return (
    <div className='SliderFilter'>
      <h2>{filter.title}</h2>
      <div className='Slider' onMouseMove={moveToggle} onMouseUp={releaseToggle}>
        <h3>{selectedOption.LABEL}</h3>
        <p>{selectedOption.DESCRIP}</p>
        <div id='bar'>
          <div id='barOverlay'/>
          <div id='toggle' onMouseDown={()=>{setToggleActive(true)}}  style={{'left': toggleLeft}}></div>
        </div>
        <div className='SliderOptions'>
        {filter.filters.map((option) => {
          return <div className={getOptionClass(option)} id={option.ID} key={option.ID} onClick={()=>chooseOption(option)}>
              {Icon(option.ICON, 'icon')}
            </div>
          })}
        </div>
      </div>
    </div>
  )
}

export default SliderFilter