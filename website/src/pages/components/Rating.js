import React, {Component} from 'react';
import {ReactComponent as Scissor} from '../../static/icons/scissor.svg';
// import {ReactComponent as ReactLogo} from './logo.svg';
//import '../../App.scss';

class Rating extends Component {
  constructor(props){
    super(props)
    this.state = {
      active: false,
      voted: false,
    }
  }

  componentDidMount(){
    // TODO: Get whether person voted before
  }

  currentVote(idx){
    if( (idx+1) != this.state.currentVote){
      this.setState({
        currentVote: idx+1,
        voted: 0
      })
    }
  }

  makeVote(){
    if(this.state.currentVote != this.state.voted){
      this.setState({
        voted: this.state.currentVote
      })
    }
  }
  setMode(active){
    this.setState({
      active: active
    })
  }

  render(){

    var max_score = 5;

    return (
      <div className="rating" onMouseLeave={()=>{this.setMode(false)}} onMouseEnter={()=>{this.setMode(true)}} onClick={()=>{this.makeVote()}}>
        {(this.state.voted || this.state.active) && <div className={(!this.state.active && this.state.voted < this.props.score) || (this.state.active && this.state.currentVote < this.props.score)? "yourvote front": "yourvote"}>
          {[...Array(max_score )].map((_, idx) => <div onMouseOver={() => {this.currentVote(idx)}}>
            <Scissor key={idx} style={{visibility: (this.state.active? this.state.currentVote : this.state.voted) > idx ? 'visible':'hidden'}} />
            
          </div>)}
        </div>}
        <div aria-label={"The current rating is: " + this.props.score} >
          {[...Array(max_score)].map((_, idx) => {
            if (Math.ceil(this.props.score) < (1+idx)){
              return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor style={{visibility: 'hidden'}} /></div>
            }
            if (Math.ceil(this.props.score) == (1+idx)){
              if(this.props.rotated){
                return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor style={{clipPath: 'inset(0 '+ (this.props.score - Math.floor(this.props.score))*100 + '% 0 0)'}} /></div>
              }else{
                return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor style={{clipPath: 'inset(0 0 '+ (this.props.score - Math.floor(this.props.score))*100 + '% 0)'}} /></div>
              }
            }
            return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor /></div>
          }
          )}
        </div>
      </div>
    )
  }
}
export default Rating