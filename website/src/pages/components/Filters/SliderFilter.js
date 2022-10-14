import {useEffect, useState} from 'react';

function SliderFilter({filter, updateFilters, filters}){

  function chooseOption(itemId){

  }

  if(filter.filters === null || filter.filters.length === 0){
    return <></>
  }

  return (
    <div className='SliderFilter'>
      <h2>{filter.title}</h2>
      <div className='Slider'>
        <div id='bar'>
          <div id='toggle'></div>
        </div>
        {filter.filters.map((option) => {
          return <div className='sliderOption' onClick={()=>chooseOption(option.ID)}>
              {option.LABEL}
            </div>
        })}
      </div>
    </div>
  )
}

export default SliderFilter