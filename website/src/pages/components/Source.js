import React, {Component} from 'react';
import {ReactComponent as ThumbDown} from '../../static/icons/thumbdown.svg';
import {ReactComponent as ThumbUp} from '../../static/icons/thumbup.svg';

const source = {
  img: "/sources/netflix.png",
  subtype: "UK",
  votes: 46,
  url: "netflix.com"
}

class Source extends Component {
  constructor(props){
    super(props)
    this.state = {
    
    }
  }
  

  componentDidMount(){
    // TODO get source  - by id
    // How to determine if user has already voted?
    this.setState({
      img: source.img,
      subtype: source.subtype,
      votes: source.votes,
      url: source.url,
      voted: undefined
    })
  }

  vote(val){
    if (this.state.voted !== val){
      this.setState({
        voted: val,
        votes: this.state.votes + val * (this.state.voted===undefined ? 1 : 2)
      })
    }
    if (this.state.voted === val){
      this.setState({
        voted: undefined,
        votes: this.state.votes - val
      })
    }
  }

  render(){
    return (
      <div className="source">
        <img src={this.state.img} alt={"Movie can be found at " + this.state.url + (this.state.subtype? " (" + this.state.subtype + ")" : "" )}/>
        <span id="votes">{this.state.votes}</span>
        <span id="voter" className={this.state.voted !== undefined ? "active": ""}>
          <span className={this.state.voted==-1 ? "active": ""}><ThumbDown  onClick={()=>{this.vote(-1)}} /></span>
          <span className={this.state.voted==1 ? "active": ""}><ThumbUp onClick={()=>{this.vote(1)}} /></span>
        </span>
      </div>
    )
  }
}

export default Source