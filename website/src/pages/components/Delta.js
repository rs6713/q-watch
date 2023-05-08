import react from 'react';
import {ReactComponent as Caret} from '../../static/icons/direction.svg'
import {ReactComponent as Neutral} from '../../static/icons/neutral.svg'

function calculatePercentChange(dataset, dataChoice, value1, value2){
  var percentChange = '?'

  try{
    if(Array.isArray(value1)){
      let value1_total = value1.map(v=> dataset[dataChoice][v] || 0).reduce((a,b)=> a+b)
      let value2_total = value2.map(v=> dataset[dataChoice][v] || 0).reduce((a,b)=> a+b)
      if(value1_total == 0){
        return Infinity;
      }
      percentChange = ((value2_total - value1_total) / value1_total * 100).toFixed(2);
    }else{
      if((dataset[dataChoice][value1] || 0) == 0){
        return Infinity;
      }
      percentChange = ((
        (dataset[dataChoice][value2] || 0) - (dataset[dataChoice][value1] || 0)
      )/ (dataset[dataChoice][value1] || 0) * 100).toFixed(2)
    }
  }catch(err){
    console.log(err)
  }
  return percentChange
}

function calculatePercent({dataset, dataChoice, value}){
  let percent = '?'

  try{
    if(Array.isArray(value)){
      let total = dataset['TOTAL']
      let subtotal = value.map(v=> dataset[dataChoice][v] || 0).reduce((a,b)=> a+b)
      percent = (subtotal / total * 100).toFixed(2)
    }else{
      let total = dataset['TOTAL']
      let subtotal = dataset[dataChoice][value]
      percent = (subtotal / total * 100).toFixed(2)
    }
  }catch(err){

  }
  return percent
}

function PercentDelta({dataset, dataChoice, value1, value2, statement, substatement}){
  let percent = '?'
  if(dataset !== null){
    percent = calculatePercentChange(dataset, dataChoice, value1, value2);
  }

  let symbol = <Neutral />
  if(percent < 0 || percent > 0){
    symbol = <Caret />
  }
  return (
    <h3 className={'percent delta' + (percent < 0 ? ' down': percent == 0? '' : ' up')}>
      <div>
        {symbol}
        <span>{percent > 0 ? percent : percent * -1}%</span>
      </div>
      <span>
        <div>{statement}</div>
        {substatement && <div>{substatement}</div>}
      </span>
    </h3>
  )
}

function PercentAlert({dataset, dataChoice, value, statement}){

  let percent = calculatePercent(dataset, dataChoice, value);

  return (
    <h3 className='percent alert'>
      {statement(percent, dataChoice, value)}
    </h3>
  )
}
export {
  PercentAlert,
  PercentDelta
}

export const thresholdStatement = (threshold) => {
  return (percent, dataChoice, value) => {
    if(percent < threshold){
      return `Only ${percent}% of movies include ${value}`
    }else{
      return `Over ${percent}% of movies include ${value}`
    }
  }
}
