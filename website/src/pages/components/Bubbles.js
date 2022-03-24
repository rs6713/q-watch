import React from 'react';


const Bubbles = (props) => {

  var id = "id" in props ? props.id : ""
  var clickAction = "onClick" in props ? props.onClick : ()=>{}

  return (
    <div className="bubbles" id={id}>
      {
        props.items.map((item, i) => (
        <div className="bubble" onClick={() => {return clickAction(item)}} key={i}>
          {typeof item === 'string' ? item : item.label}
        </div>)
      )}
    </div>
  )
}

export default Bubbles