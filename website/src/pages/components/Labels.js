import React from 'react';
import {useState, useEffect} from 'react';

function Labels({labelType, updateLabel}){
  const [labels, setLabels] = useState([]);
  const [label, setLabel] = useState(null);

  // Fetching labels called once at mount
  useEffect(() => {
    fetch('/api/movie/labels').then(res => res.json()).then(data => {
      setLabels(data[labelType]);
    });
  }, []);

  const labelName = labelType.slice(0, -1)

  function chooseLabel(lbl){
    setLabel(lbl);
    updateLabel({
      [labelType]: lbl
    })
    console.log(labelName, lbl)
  }

  return (
    <div id="Categories">
        {labels.length ? <div className={label==null? 'active': ''} onClick={()=>{chooseLabel(null)}}>All</div> : <></>}
        {labels.map(l => (
          <div key={l['ID']} className={label === l["ID"]? 'active' : ''} onClick={()=>{chooseLabel(l['ID'])}} >{l['LABEL']}</div>
        ))}
    </div>
  )
}

export default Labels