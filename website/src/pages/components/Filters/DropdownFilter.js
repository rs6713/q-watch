import React from 'react';
import {useEffect, useState} from 'react';
import {formatLanguage} from '../../../utils';


function DropDownFilter({filter, updateFilters, filters}){

  const [dropdownActive, setDropdownActive] = useState(false)

  if(filter.filters === null){
    return <></>
  }
  function selectItem(item){
    
    if(filters[filter['id']] !== undefined){
      if(filters[filter['id']].indexOf(item) === -1){
        updateFilters({
          [filter['id']]: [...filters[filter['id']], item]
        })
      }else{
        let reducedList = filters[filter['id']].filter(i => i != item)
        updateFilters({
          [filter['id']]: reducedList.length > 0? reducedList : undefined
        })
      }
    }else{
      updateFilters({
        [filter['id']]: [item]
      })
    }
  }

  function getItemClass(item){
    if(filters[filter['id']] !== undefined && filters[filter['id']].indexOf(item) !== -1){
      return 'active DropDownOption'
    }
    return 'DropDownOption'
  }

  function processItem(f){
    if(filter.title === 'Language'){
      return formatLanguage(f) || f
    }
    return f
  }

  return <div className='DropDownFilter' >
    <h2>{filter.title}</h2>
    <div className={'DropDownContainer' + (dropdownActive? ' active': '')} onMouseLeave={()=>{setDropdownActive(false)}} >
      <div onClick={()=>{setDropdownActive(!dropdownActive)}}>{filter.placeholder}</div>
      <div className={'DropDownOptions' + (dropdownActive? ' active': '')}>
        {filter.filters.sort((a, b) => processItem(a) > processItem(b) ? 1 : -1).map((f, idx) => <div className={getItemClass(f)} onClick={()=>{selectItem(f)}} key={`dropdown_${idx}`}>
          {processItem(f)}
        </div>)}
      </div>
    </div>
  </div>
}

export default DropDownFilter