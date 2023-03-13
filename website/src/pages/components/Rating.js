import React from 'react';
import {useState, useEffect} from 'react';
import {ReactComponent as Scissor} from '../../static/icons/scissor.svg';
import {ReactComponent as Trans} from '../../static/icons/trans.svg';
import {ReactComponent as Paw} from '../../static/icons/paw.svg';
import {ReactComponent as Rainbow} from '../../static/icons/rainbow.svg';
import {ReactComponent as Ace} from '../../static/icons/ace.svg';
import {ReactComponent as Bicycle} from '../../static/icons/bicycle.svg';
import {ReactComponent as Intersect} from '../../static/icons/intersect.svg';
import {ReactComponent as Polygon} from '../../static/icons/polygon.svg';
// import {ReactComponent as ReactLogo} from './logo.svg';
//import '../../App.scss';

export function getIcon(movieTypes){
  var Icon = Rainbow;

  if(movieTypes == null){
    return Icon;
  }

  // Random Selection of Icon
  let typ = movieTypes[Math.floor(Math.random() * movieTypes.length)]

  if(typ.LABEL == "Gay"){
    Icon = Paw;
  }
  if(typ.LABEL == "Lesbian"){
    Icon = Scissor;
  }
  if(typ.LABEL == "Transgender"){
    Icon = Trans;
  }
  if(typ.LABEL == "Bisexual"){
    Icon = Bicycle;
  }
  if(typ.LABEL == "Ace/Aro"){
    Icon = Ace;
  }
  if(typ.LABEL == "Intersex"){
    Icon = Intersect;
  }
  if(typ.LABEL == "Polyamory"){
    Icon = Polygon;
  }
  return Icon;
}

function Rating({id, rating, rotated, movieTypes, votable}){
  const [active, setActive] = useState(false);
  const [vote, setVote] = useState(null);
  const [newVote, updateNewVote] = useState(null);
  const [Icon, setIcon] = useState(Rainbow);
  const maxRating = 5;


  //TODO: Check local stored variables in session - set vote
  //TODO: When place vote, update/insert vote in db. Store vote locally on success

  useEffect(()=>{
    setIcon(getIcon(movieTypes));
  }, [movieTypes])

  function setNewVote(v){
    if(votable){
      updateNewVote(v)
    }
  }

  var classname = "yourvote";
  if((!active && vote < rating) || (active && newVote < rating) || !rating){
    classname += " front";
  }

    // Conditional creation of currentvote infront of existing rating
  var yourVote = <></>;
  if(vote !== null || active){
    yourVote = <div className={classname} aria-label={"Your current vote is: " + (active? newVote : vote)}>
      {[...Array(maxRating)].map((_, idx) => <div onMouseOver={() => {setNewVote(idx + 1)}}>
          <Icon key={idx} style={{visibility: (active? newVote : vote) > idx ? 'visible':'hidden'}} />
        </div>)
      }
    </div>
  }


  return (
    <div className="rating" onMouseLeave={()=>{setActive(false)}} onMouseEnter={()=>{setActive(true)}} onClick={()=>{setVote(newVote)}}>
      {yourVote}
      {!rating && votable && <div>
          {[...Array(maxRating)].map((_, idx) => {
            return <div key={idx} onMouseOver={() => {setNewVote(idx+1)}}><Icon style={{fill: 'lightgrey'}} /></div>
          })
        }
        </div>
      }
      { rating > 0 &&
      <div aria-label={"The current rating is: " + rating} >
      
      {[...Array(maxRating)].map((_, idx) => {
        if (Math.ceil(rating) < (1+idx)){
          return <div key={idx} onMouseOver={() => {setNewVote(idx+1)}}><Icon style={{visibility: 'hidden'}} /></div>
        }
        if (Math.ceil(rating) == (1+idx)){
          if(rotated){
            return <div key={idx} onMouseOver={() => {setNewVote(idx + 1)}}><Icon style={{clipPath: 'inset(0 '+ (rating - Math.floor(rating))*100 + '% 0 0)'}} /></div>
          }else{
            return <div key={idx} onMouseOver={() => {setNewVote(idx + 1)}}><Icon style={{clipPath: 'inset(0 0 '+ (rating - Math.floor(rating))*100 + '% 0)'}} /></div>
          }
        }
        return <div key={idx} onMouseOver={() => {setNewVote(idx + 1)}}><Icon /></div>
      }
      )}
    </div>
}
  </div>
  )

}

// class Rating extends Component {
//   constructor(props){
//     super(props)
//     this.state = {
//       active: false,
//       voted: false,
//     }
//   }

//   componentDidMount(){
//     // TODO: Get whether person voted before
//   }

//   currentVote(idx){
//     if( (idx+1) != this.state.currentVote){
//       this.setState({
//         currentVote: idx+1,
//         voted: 0
//       })
//     }
//   }

//   makeVote(){
//     if(this.state.currentVote != this.state.voted){
//       this.setState({
//         voted: this.state.currentVote
//       })
//     }
//   }
//   setMode(active){
//     this.setState({
//       active: active
//     })
//   }

//   render(){

//     var max_score = 5;

//     var icon = Scissor;
//     if(props.movieType == "")

//     return (
//       <div className="rating" onMouseLeave={()=>{this.setMode(false)}} onMouseEnter={()=>{this.setMode(true)}} onClick={()=>{this.makeVote()}}>
//         {(this.state.voted || this.state.active) && <div className={(!this.state.active && this.state.voted < this.props.score) || (this.state.active && this.state.currentVote < this.props.score)? "yourvote front": "yourvote"}>
//           {[...Array(max_score )].map((_, idx) => <div onMouseOver={() => {this.currentVote(idx)}}>
//             <Scissor key={idx} style={{visibility: (this.state.active? this.state.currentVote : this.state.voted) > idx ? 'visible':'hidden'}} />
            
//           </div>)}
//         </div>}
//         <div aria-label={"The current rating is: " + this.props.score} >
//           {[...Array(max_score)].map((_, idx) => {
//             if (Math.ceil(this.props.score) < (1+idx)){
//               return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor style={{visibility: 'hidden'}} /></div>
//             }
//             if (Math.ceil(this.props.score) == (1+idx)){
//               if(this.props.rotated){
//                 return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor style={{clipPath: 'inset(0 '+ (this.props.score - Math.floor(this.props.score))*100 + '% 0 0)'}} /></div>
//               }else{
//                 return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor style={{clipPath: 'inset(0 0 '+ (this.props.score - Math.floor(this.props.score))*100 + '% 0)'}} /></div>
//               }
//             }
//             return <div key={idx} onMouseOver={() => {this.currentVote(idx)}}><Scissor /></div>
//           }
//           )}
//         </div>
//       </div>
//     )
//   }
// }
export default Rating