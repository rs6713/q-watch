import {useState} from 'react';

function Indexer({index, updateIndex, nIndexes}){
  if(nIndexes === null){
    return (<></>);
  }

  function changeIndex(newIndex){
    if(newIndex==0) return;
    if(newIndex > nIndexes) return;

    updateIndex(newIndex);
  }

  return (
    <div>
      <div onClick={()=>{changeIndex(index - 1)}}>Previous</div>
      <div>Page {index} of {nIndexes}</div>
      <div onClick={()=>{changeIndex(index + 1)}}>Next</div>
    </div>
  )
}

export default Indexer