
function Switch({state, setState, onMessage, offMessage}){

  return <div className="Switch">
    <div id="Toggle" className={state? 'active': ''} onClick={()=>{setState(!state)}}>
      <span className={state? 'active' : ''}></span>
    </div>
    {state && onMessage}
    {!state && offMessage}
  </div>
}

export default Switch