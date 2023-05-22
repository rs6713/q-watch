import React from 'react';
import {useState, useEffect} from 'react';

function Labels({labels, labelType, updateLabel, label}){
  //const [labels, setLabels] = useState([]);
  label = label || null

  // Fetching labels called once at mount
  // useEffect(() => {
  //   fetch('/api/movie/labels').then(res => res.json()).then(data => {
  //     setLabels(data[labelType]);
  //   });
  // }, []);

  const labelName = labelType.slice(0, -1)

  function chooseLabel(lbl){
    updateLabel({
      [labelType]: lbl
    })
  }

  return (
    <div id="Categories">
        {labels && labels.length ? <div className={label==null? 'active': ''} onClick={()=>{chooseLabel(null)}}>All</div> : <></>}
        {labels && labels.map(l => (
          <div key={l['ID']} className={label === l["ID"]? 'active' : ''} onClick={()=>{chooseLabel(l['ID'])}} >{l['LABEL']}</div>
        ))}
    </div>
  )
}

export default Labels