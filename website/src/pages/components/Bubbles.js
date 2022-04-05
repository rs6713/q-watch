import React, {Component} from 'react';


class Bubbles extends Component {
  constructor(props){
    super(props)

    this.state = {
      items: this.props.items
    }
  }

  clickAction(item, i){
    return () => {
      if(this.props.clickAction){
        var items = this.state.items;
        items[i] = {...this.state.items[i], active: !items[i].active}
        this.setState({
          items: items
        })
        console.log(this.state.items)
        this.props.clickAction(item)
      }
    }
  }

  render(){
    return (
      <div className="bubbles" id={this.props.id || ""}>
        {
          this.state.items.map((item, i) => (
            <div className={"bubble" + (item.active? " active": "")} title={item.descrip || ""} onClick={this.clickAction(item.id, i)} key={i}>
              {typeof item === 'string' ? item : item.label}
            </div>
          )
        )}
      </div>
    )
  }
}

export default Bubbles