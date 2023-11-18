// import React from 'react';
// import {useEffect, useState} from 'react';
// import {Icon} from '../Image'
// import Switch from '../Switch'

// var _ = require('lodash/core');

// function RangeSliderFilter({filter, updateFilters}){
//   const [selectedOption, setSelectedOption] = useState(
//     filter !== null && filter.range !== null ? filter.range[1] : null
//   )
//   const [toggleActive, setToggleActive] = useState(false);
//   const [toggleLeft, setToggleLeft] = useState(0);
//   const [atLeast, setAtLeast] = useState(false);

//   var options = _.range(filter.range[0], filter.range[1], filter.step)


//   useEffect(() =>{
//     setSnapPosition();
//   }, [selectedOption])

//   useEffect(()=>{
//     chooseOption(selectedOption)
//   }, [atLeast])

//   if(selectedOption === null){
//     return <></>
//   }

//   function chooseOption(option){
//     setSelectedOption(option);
    
//     updateFilters({[filter['id']]: {
//       'TYPE': atLeast? 'GREATER_THAN': 'LESS_THAN',
//       'VALUE': option
//     }})
//   }

//   function moveToggle(e){
//     if(toggleActive){
//       var rect = document.getElementById('bar').getBoundingClientRect();
//       var x = e.clientX - rect.left;

//       setToggleLeft(
//         `${x}px`
//       )
//     }
//   }

//   function releaseToggle(e){
//     if(toggleActive){
//       // Snap toggle to nearest choice
//       // Choose that element
//       let nearestDistance = 10000;
//       let nearestOptionIdx = null;
//       var i = 0;
//       for(let option of filter.filters){
//         let optionX = document.getElementById(option.ID).getBoundingClientRect();
//         optionX = (optionX.left + optionX.right) / 2;
//         if(Math.abs(e.clientX - optionX) < nearestDistance){
//           nearestOptionIdx = i;
//           nearestDistance = Math.abs(e.clientX - optionX);
//         }
//         i = i + 1;
//       }

//       setToggleActive(false);
//       chooseOption(filter.filters[nearestOptionIdx]);
//     }
//   }

// }
// export default RangeSliderFilter