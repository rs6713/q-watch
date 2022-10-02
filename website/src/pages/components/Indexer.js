import {useState} from 'react';
import {ReactComponent as Caret} from '../../static/icons/caret.svg'

function Indexer({index, updateIndex, nIndexes}){
  const [selectorActive, setSelectorActive] = useState(false);

  if(nIndexes === null){
    return (<></>);
  }

  function changeIndex(newIndex){
    if(newIndex==0) return;
    if(newIndex > nIndexes) return;

    updateIndex(newIndex);
  }

  return (
    <div className="PageIndexer">
      <div className="ChangeIndex" onClick={()=>{changeIndex(index - 1)}}>Previous</div>
      <div className="SelectIndex">
        <p>Page <span onClick={()=>{setSelectorActive(!selectorActive)}} title="Navigate to Page">{index}<Caret />
        <div className={selectorActive? 'active': 'inactive'}>
          {[...Array(nIndexes).keys()].map(i => (
            <div key={i} onClick={()=>{changeIndex(i+1)}}>{i+1}</div>
          ))
        }
        </div>
        </span> of {nIndexes}</p>
        
      </div>
      <div className="ChangeIndex" onClick={()=>{changeIndex(index + 1)}}>Next</div>
    </div>
  )
}

export default Indexer