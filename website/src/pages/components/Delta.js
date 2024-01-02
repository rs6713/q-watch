import react from 'react';
import {ReactComponent as Caret} from '../../static/icons/direction.svg'
import {ReactComponent as Neutral} from '../../static/icons/neutral.svg'
import Loader from './Loader'

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

function calculatePercent(dataset, dataChoice, value){
  var percent = '?'

  try{
    if(Array.isArray(value)){
      let total = Object.keys(dataset).indexOf('TOTAL') !== -1 ? dataset['TOTAL']: (
        Object.values(dataset[dataChoice]).reduce((a, b) => (a + b), 0)
      );
      let subtotal = value.map(v=> dataset[dataChoice][v] || 0).reduce((a,b)=> a+b)
      percent = (subtotal / total * 100).toFixed(2)
    }else{
      let total = Object.keys(dataset).indexOf('TOTAL') !== -1 ? dataset['TOTAL']: (
        Object.values(dataset[dataChoice]).reduce((a, b) => (a + b), 0)
      )
      let subtotal = dataset[dataChoice][value]
      percent = (subtotal / total * 100).toFixed(2)
    }
  }catch(err){

  }

  return percent
}

function PercentDelta({dataset, dataChoice, value1, value2, statement, substatement}){
  let percent = ''
  var numPercent = '';
  let symbol = <Neutral />
  if(dataset !== null && dataset !== undefined){
    percent = calculatePercentChange(dataset, dataChoice, value1, value2);
    if(percent < 0 || percent > 0){
      symbol = <Caret />
    }
    numPercent = percent > 0 ? percent : percent * -1;
  }else if (dataset===null){
    numPercent = '?';
  }

  

  return (
    <h3 className={'percent delta' + (percent < 0 ? ' down': percent == 0? '' : ' up')}>
      <div>
        {symbol}
        <span>
          {dataset === undefined && <Loader isLoading={dataset==undefined}/>}
          {numPercent}%
        </span>
      </div>
      <span>
        <div>{statement}</div>
        {substatement ? <div>{substatement}</div>: <div></div>}
      </span>
    </h3>
  )
}

function PercentAbsolute({dataset, dataChoice, value, statement, substatement}){
  let percent = dataset === null ? '?' : '';

  if(dataset !== null && dataset !== undefined){
    percent = calculatePercent(dataset, dataChoice, value);
    //percent = percent > 0 ? percent : percent * -1
  }
  // let percent = dataset !== null ? (
  //   calculatePercent(dataset, dataChoice, value)
  // ): '?';

  return (
    <h3 className='percent absolute'>
      <div>
        <span>
          {dataset === undefined && <Loader isLoading={dataset==undefined}/>}
          {percent}%
        </span>
      </div>
      <span>
        <div>{statement}</div>
        {substatement ? <div>{substatement}</div>: <div></div>}
      </span>
    </h3>
  )
}

function Absolute({value, statement, substatement}){

  return (
    <h3 className='percent absolute'>
      <div>
        {value === undefined && <Loader isLoading={true}/>}
        {value !== undefined && <span>{value === null ? '?': value}</span>}
      </div>
      <span>
        <div>{statement}</div>
        {substatement ? <div>{substatement}</div>: <div></div>}
      </span>
    </h3>
  )
}

function PercentAlert({dataset, dataChoice, value, statement}){
  let percent = dataset !== null ? calculatePercent(dataset, dataChoice, value): '?';

  return (
    <h3 className='percent alert'>
      {statement(percent, dataChoice, value)}
    </h3>
  )
}
export {
  Absolute,
  PercentAbsolute,
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
