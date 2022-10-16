import {useEffect, useState} from 'react';

function DropDownFilter({filter, updateFilters}){

  if(filter.filters === null){
    return <></>
  }
  return <div className='DropDownFilter'>
    <h2>{filter.title}</h2>
    {filter.filters.map((f) => <div className='dropdownOption'>
      {f}
    </div>)}
  </div>
}

export default DropDownFilter