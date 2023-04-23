import React from 'react';
import {ReactComponent as Caret} from '../../static/icons/caret.svg'
import {useState} from 'react';


function Options({name, updateOption, option, options, multi}){
  function clickOption(optionKey){
    if(multi === true){
      if(option !== null){
        if(option.indexOf(options[optionKey]) !== -1){
          let newOption = [];
          for(let opt of option){
            if(opt !== options[optionKey]){
              newOption.push(opt)
            }
          }
          updateOption(newOption);
        }else{
          updateOption([...option, options[optionKey]]);
        }
      }else{
        updateOption([options[optionKey]]);
      }
    }else{
      updateOption(options[optionKey]);
    }
  }

  function optionMatch(option, key){

    if(multi === true){
      if(option === null){
        return false;
      }
      for(let opt of option){
        if(opt === options[key]){
          return true;
        }
      }
      return false;
    }else{
      return (option === options[key])
    }
  }

  

  return (
    <div id="Options">
      <div><span>{name}</span> <Caret/></div>
      <ul id="Options">
        {Object.keys(options).map(key => (
          <li key={key} className={optionMatch(option, key) ? 'active' : ''} onClick={()=>{clickOption(key)}}>{key}</li>
        ))}
      </ul>
    </div>
  )
}

export default Options