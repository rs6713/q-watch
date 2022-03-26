import React, {Component} from 'react';
import Bubbles from './Bubbles.js';
import {ReactComponent as Plus} from '../../static/icons/plus.svg'
import {ReactComponent as Minus} from '../../static/icons/minus.svg'

class ExpandableBubbles extends Component {
  constructor(props){
    super(props)
    this.state = {
      active: this.props.expandable == false? true : false
    }
  }


  render () {
    return (
    <div className="expandable_bubbles">
      <h2>{this.props.title}
      {this.props.expandable !== false && this.state.active && <Minus onClick={()=>{this.setState({active: false})}}/>}
      {this.props.expandable !== false && !this.state.active && <Plus onClick={()=>{this.setState({active: true})}} />}
      {this.props.aside && (!this.state.active || !this.props.expandable) && <span>{this.props.aside}</span>}
      
      </h2>
      {this.props.subtitle && <p>{this.props.subtitle}</p>}
      {this.state.active && 
        <Bubbles items={this.props.items} />
      }
    </div>
    )
  }
}

export default ExpandableBubbles