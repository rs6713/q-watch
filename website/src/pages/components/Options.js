import React from 'react';
import {ReactComponent as Caret} from '../../static/icons/caret.svg'
import {useState} from 'react';


function Options({name, updateOption, option, options, multi}){
  let isArray = Array.isArray(options)

  function clickDictOption(optionKey){
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

  function clickOption(newOption){
    if(multi === true){
      if(option !== null){

        if(option.indexOf(newOption) !== -1){
          let newOptions = [];
          for(let opt of option){
            if(opt !== newOption){
              newOptions.push(opt)
            }
          }
          updateOption(newOptions);
        }else{
          updateOption([...option, newOption]);
        }
      }else{
        updateOption([newOption]);
      }
    }else{
      updateOption(newOption);
    }
  }

  function optionDictMatch(option, key){

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

  function optionMatch(option, newOption){

    if(multi === true){
      if(option === null){
        return false;
      }
      for(let opt of option){
        if(opt === newOption){
          return true;
        }
      }
      return false;
    }else{
      return (option === newOption)
    }
  }

  if(isArray){
    return (
      <div id="Options">
        <div><span>{name}</span> <Caret/></div>
        <ul id="Options">
          {options.map(o => (
            <li key={o} className={optionMatch(option, o) ? 'active' : ''} onClick={()=>{clickOption(o)}}>{o}</li>
          ))}
        </ul>
      </div>
    )
  }
  

  return (
    <div id="Options">
      <div><span>{name}</span> <Caret/></div>
      <ul id="Options">
        {Object.keys(options).map(key => (
          <li key={key} className={optionDictMatch(option, key) ? 'active' : ''} onClick={()=>{clickDictOption(key)}}>{key}</li>
        ))}
      </ul>
    </div>
  )
}

export default Options