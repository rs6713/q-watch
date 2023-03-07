import React from 'react';
import {useState} from 'react';

function Bubbles({items, clickAction, id}){

  const [activeItems, setActiveItems] = useState({});

  function chooseItem(item, i){
    return () => {
      if(clickAction){
        setActiveItems({...activeItems, [i]: !activeItems[i]})
        clickAction(item)
      }
    }
  }

  if(items === null || items.length == 0){
    return <></>
  }
  return (
    <div className="bubbles" id={id || ""}>
      {
        items.map((item, i) => (
          <div className={"bubble" + (activeItems[i]? " active": "")} title={item.DESCRIP || ""} onClick={chooseItem(item.ID, i)} key={i}>
            {typeof item === 'string' ? item : item.LABEL}
            {typeof item !== 'string' && Object.keys(item).indexOf('MAIN') !== -1 && item.MAIN === 0 ? '*' : ''}
          </div>
        )
      )}
    </div>
  )
}

// class Bubbles extends Component {
//   constructor(props){
//     super(props)

//     this.state = {
//       items: this.props.items
//     }
//   }

//   clickAction(item, i){
//     return () => {
//       if(this.props.clickAction){
//         var items = this.state.items;
//         items[i] = {...this.state.items[i], active: !items[i].active}
//         this.setState({
//           items: items
//         })
//         this.props.clickAction(item)
//       }
//     }
//   }

//   render(){
//     return (
//       <div className="bubbles" id={this.props.id || ""}>
//         {
//           this.state.items.map((item, i) => (
//             <div className={"bubble" + (item.active? " active": "")} title={item.DESCRIP || ""} onClick={this.clickAction(item.ID, i)} key={i}>
//               {typeof item === 'string' ? item : item.LABEL}
//             </div>
//           )
//         )}
//       </div>
//     )
//   }
// }

export default Bubbles